import json
from typing import Any, Dict, cast

from cluster_agent.identity.slurm_user.factory import manufacture
from cluster_agent.identity.slurm_user.mappers import SlurmUserMapper
from cluster_agent.identity.slurmrestd import backend_client as slurmrestd_client
from cluster_agent.identity.slurmrestd import inject_token
from cluster_agent.jobbergate.api import (
    SubmissionNotifier,
    fetch_pending_submissions,
    mark_as_submitted,
)
from cluster_agent.jobbergate.constants import JobSubmissionStatus
from cluster_agent.jobbergate.schemas import (
    PendingJobSubmission,
    SlurmJobParams,
    SlurmJobSubmission,
    SlurmSubmitResponse,
)
from cluster_agent.settings import SETTINGS
from cluster_agent.utils.exception import (
    JobSubmissionError,
    SlurmParameterParserError,
    SlurmrestdError,
    handle_errors_async,
)
from cluster_agent.utils.logging import log_error
from loguru import logger


def get_job_script(pending_job_submission: PendingJobSubmission) -> str:
    """
    Get the job script from a PendingJobSubmission object.
    Raise JobSubmissionError if no job script is found or if its empty.
    """
    job_script = pending_job_submission.job_script_files.files.get(
        pending_job_submission.job_script_files.main_file_path, ""
    )

    JobSubmissionError.require_condition(
        bool(job_script),
        "Could not find an executable script in retrieved job script data.",
    )

    return job_script


def get_job_parameters(slurm_parameters: Dict[str, Any], **kwargs) -> SlurmJobParams:
    """
    Obtain the job parameters from the slurm_parameters dict and additional values.

    Extra keyword arguments can be used to supply default values for any parameter
    (like name or current_working_directory). Note they may be overwritten by
    values from slurm_parameters.
    """
    merged_parameters = {**kwargs, **slurm_parameters}
    return SlurmJobParams(**merged_parameters)


async def submit_job_script(
    pending_job_submission: PendingJobSubmission,
    user_mapper: SlurmUserMapper,
) -> int:
    """
    Submit a Job Script to slurm via the Slurm REST API.

    :param: pending_job_submission: A job_submission with fields needed to submit.
    :returns: The ``slurm_job_id`` for the submitted job
    """

    notify_submission_rejected = SubmissionNotifier(
        pending_job_submission.id, JobSubmissionStatus.REJECTED
    )

    async with handle_errors_async(
        "An internal error occurred while processing the job-submission",
        raise_exc_class=JobSubmissionError,
        do_except=notify_submission_rejected.report_error,
    ):

        email = pending_job_submission.job_submission_owner_email
        name = pending_job_submission.application_name
        mapper_class_name = user_mapper.__class__.__name__
        logger.debug(
            f"Fetching username for email {email} with mapper {mapper_class_name}"
        )
        username = await user_mapper.find_username(email)
        logger.debug(f"Using local slurm user {username} for job submission")

        job_script = get_job_script(pending_job_submission)

        submit_dir = (
            pending_job_submission.execution_directory
            or SETTINGS.DEFAULT_SLURM_WORK_DIR
        )

        for path, file_content in pending_job_submission.job_script_files.files.items():
            local_script_path = submit_dir / path
            local_script_path.parent.mkdir(parents=True, exist_ok=True)
            local_script_path.write_text(file_content)
            logger.debug(f"Copied job script file to {local_script_path}")

    async with handle_errors_async(
        "Failed to extract Slurm parameters",
        raise_exc_class=SlurmParameterParserError,
        do_except=notify_submission_rejected.report_error,
    ):

        job_parameters = get_job_parameters(
            pending_job_submission.execution_parameters,
            name=pending_job_submission.application_name,
            current_working_directory=submit_dir,
            standard_output=submit_dir / f"{name}.out",
            standard_error=submit_dir / f"{name}.err",
        )

    payload = SlurmJobSubmission(script=job_script, job=job_parameters)
    logger.debug(
        f"Submitting pending job submission {pending_job_submission.id} "
        f"to slurm with payload {payload}"
    )

    async with handle_errors_async(
        "Failed to submit job to slurm",
        raise_exc_class=SlurmrestdError,
        do_except=notify_submission_rejected.report_error,
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
        with JobSubmissionError.handle_errors(
            (
                f"Failed to submit pending job_submission {pending_job_submission.id}"
                "...skipping to next pending job"
            ),
            do_except=log_error,
            do_else=lambda: logger.debug(
                f"Finished submitting pending job_submission {pending_job_submission.id}"
            ),
            re_raise=False,
        ):

            slurm_job_id = await submit_job_script(pending_job_submission, user_mapper)

            await mark_as_submitted(pending_job_submission.id, slurm_job_id)

    logger.debug("...Finished submitting pending jobs")
