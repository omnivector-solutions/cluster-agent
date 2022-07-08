import json
from typing import cast

from buzz import DoExceptParams, get_traceback, reformat_exception

from cluster_agent.identity.slurm_user.factory import manufacture
from cluster_agent.identity.slurm_user.mappers import SlurmUserMapper
from cluster_agent.identity.slurmrestd import backend_client as slurmrestd_client
from cluster_agent.identity.slurmrestd import inject_token
from cluster_agent.jobbergate.api import (
    fetch_pending_submissions,
    mark_as_submitted,
    notify_submission_rejected,
)

from cluster_agent.jobbergate.schemas import (
    PendingJobSubmission,
    SlurmJobParams,
    SlurmJobSubmission,
    SlurmSubmitResponse,
)
from cluster_agent.settings import SETTINGS
from cluster_agent.utils.exception import (
    JobSubmissionError,
    JobbergateApiError,
    SlurmrestdError,
)
from cluster_agent.utils.job_script_parser import get_job_parameters
from cluster_agent.utils.logging import log_error
from loguru import logger


def get_job_script(pending_job_submission: PendingJobSubmission) -> str:
    """
    Get the job script from a PendingJobSubmission object.
    Raise JobSubmissionError if no job script is found or if its empty.
    """

    try:
        unpacked_data = json.loads(pending_job_submission.job_script_data_as_string)
        job_script = unpacked_data.get("application.sh", "")
    except json.JSONDecodeError:
        job_script = ""

    JobSubmissionError.require_condition(
        bool(job_script),
        "Could not find an executable script in retrieved job script data.",
    )

    return job_script


async def submit_job_script(
    pending_job_submission: PendingJobSubmission,
    user_mapper: SlurmUserMapper,
) -> int:
    """
    Submit a Job Script to slurm via the Slurm REST API.

    :param: pending_job_submission: A job_submission with fields needed to submit.
    :returns: The ``slurm_job_id`` for the submitted job
    """

    email = pending_job_submission.job_submission_owner_email
    name = pending_job_submission.application_name
    mapper_class_name = user_mapper.__class__.__name__
    logger.debug(f"Fetching username for email {email} with mapper {mapper_class_name}")
    username = await user_mapper.find_username(email)
    logger.debug(f"Using local slurm user {username} for job submission")

    job_script = get_job_script(pending_job_submission)

    submit_dir = (
        pending_job_submission.execution_directory or SETTINGS.DEFAULT_SLURM_WORK_DIR
    )

    local_script_path = submit_dir / f"{name}.job"
    local_script_path.write_text(job_script)
    logger.debug(f"Copied job_script to local file {local_script_path}.")

    job_parameters = get_job_parameters(
        job_script,
        name=pending_job_submission.application_name,
        current_working_directory=submit_dir,
        standard_output=submit_dir / f"{name}.out",
        standard_error=submit_dir / f"{name}.err",
    )

    payload = SlurmJobSubmission(
        script=job_script,
        job=SlurmJobParams(**job_parameters),
    )
    logger.debug(
        f"Submitting pending job submission {pending_job_submission.id} "
        f"to slurm with payload {payload}"
    )

    with SlurmrestdError.handle_errors(
        "Failed to submit job to slurm",
        do_except=log_error,
    ):
        response = await slurmrestd_client.post(
            "/slurm/v0.0.36/job/submit",
            auth=lambda r: inject_token(r, username=username),
            json=json.loads(payload.json()),
        )
        logger.debug(f"Slurmrestd response: {response.json()}")
        response.raise_for_status()
        sub_data = SlurmSubmitResponse.parse_raw(response.content)

    # Make static type checkers happy.
    slurm_job_id = cast(int, sub_data.job_id)

    logger.debug(
        f"Received slurm job id {slurm_job_id} for job submission {pending_job_submission.id}"
    )

    return slurm_job_id


async def submit_pending_jobs():
    """
    Submit all pending jobs and update them with ``SUBMITTED`` status and slurm_job_id.

    :returns: The ``slurm_job_id`` for the submitted job
    """
    logger.debug("Started submitting pending jobs...")

    logger.debug("Building user-mapper")
    user_mapper = await manufacture()

    logger.debug("Fetching pending jobs...")
    pending_job_submissions = await fetch_pending_submissions()

    for pending_job_submission in pending_job_submissions:
        logger.debug(f"Submitting pending job_submission {pending_job_submission.id}")
        try:
            slurm_job_id = await submit_job_script(pending_job_submission, user_mapper)
        except Exception as err:
            final_message = reformat_exception(
                (
                    f"Failed to submit pending job_submission {pending_job_submission.id}"
                    "...skipping to next pending job"
                ),
                err,
            )
            with JobbergateApiError.handle_errors(
                f"Could not update status='REJECTED' for {pending_job_submission.id=} via the API",
                do_except=log_error,
                re_raise=False,
            ):
                await notify_submission_rejected(
                    DoExceptParams(
                        JobSubmissionError,
                        final_message=final_message,
                        trace=get_traceback(),
                    ),
                    pending_job_submission.id,
                )
        else:
            with JobbergateApiError.handle_errors(
                f"Could not update status='SUBMITTED' for {pending_job_submission.id=} via the API",
                do_except=log_error,
                re_raise=False,
            ):
                await mark_as_submitted(pending_job_submission.id, slurm_job_id)

        logger.debug(
            f"Finished processing pending job_submission {pending_job_submission.id}"
        )
    logger.debug("...Finished submitting pending jobs")
