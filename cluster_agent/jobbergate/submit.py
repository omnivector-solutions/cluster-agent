import json
from typing import cast

from loguru import logger

from cluster_agent.jobbergate.schemas import (
    PendingJobSubmission,
    SlurmSubmitResponse,
    SlurmJobSubmission,
    SlurmJobParams,
)
from cluster_agent.jobbergate.api import fetch_pending_submissions, mark_as_submitted
from cluster_agent.jobbergate.constants import JobSubmissionStatus
from cluster_agent.identity.slurmrestd import (
    backend_client as slurmrestd_client,
    inject_token,
)
from cluster_agent.utils.exception import JobSubmissionError
from cluster_agent.utils.exception import SlurmrestdError
from cluster_agent.utils.logging import log_error
from cluster_agent.utils.user import ldap
from cluster_agent.settings import SETTINGS


async def submit_job_script(pending_job_submission: PendingJobSubmission) -> int:
    """
    Submit a Job Script to slurm via the Slurm REST API.

    :param: pending_job_submission: A job_submission with fields needed to submit.
    :returns: The ``slurm_job_id`` for the submitted job
    """
    job_script_name = pending_job_submission.job_script_name
    unpacked_data = json.loads(pending_job_submission.job_script_data_as_string)

    # TODO: Using Slurm REST API, we don't need to embed sbatch params.
    #       Instead, we could put them in a prameter payload and send them in via
    #       `job_properties`

    job_script = None
    for (filename, data) in unpacked_data.items():
        if filename == "application.sh":
            job_script = data
            filename = f"{job_script_name}.job"

    if ldap is not None:
        logger.debug("Fetching username from LDAP")
        username = ldap.find_username(pending_job_submission.job_submission_owner_email)
    else:
        logger.debug("LDAP not available. Using {SETTINGS.X_SLURM_USER_NAME} as user.")
        username = SETTINGS.X_SLURM_USER_NAME

    JobSubmissionError.require_condition(
        job_script is not None,
        "Could not find an executable script in retrieved job script data.",
    )

    payload = SlurmJobSubmission(
        script=job_script,
        job=SlurmJobParams(
            name=pending_job_submission.application_name,
            current_working_directory=SETTINGS.DEFAULT_SLURM_WORK_DIR,
        ),
    )
    logger.debug(
        f"Submitting pending job submission {pending_job_submission.id} "
        "to slurm with payload {payload}"
    )

    with SlurmrestdError.handle_errors(
        "Failed to submit job to slurm",
        do_except=log_error,
    ):
        response = await slurmrestd_client.post(
            "/slurm/v0.0.36/job/submit",
            auth=lambda r: inject_token(r, username=username),
            json=payload.dict(),
        )
        response.raise_for_status()
        sub_data = SlurmSubmitResponse(**response.json())

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

    logger.debug("Fetching pending jobs...")
    pending_job_submissions = await fetch_pending_submissions()

    for pending_job_submission in pending_job_submissions:
        logger.debug(f"Submitting pending job_submission {pending_job_submission.id}")
        with JobSubmissionError.handle_errors(
            (
                f"Failed to sumbit pending job_submission {pending_job_submission.id}"
                "...skipping to next pending job"
            ),
            do_except=log_error,
            do_else=lambda: logger.debug(
                "Finished submitting pending job_submission {pending_job_submission.id}"
            ),
            re_raise=False,
        ):

            slurm_job_id = await submit_job_script(pending_job_submission)

            logger.debug(
                "Updating job_submission with "
                f"status='{JobSubmissionStatus.SUBMITTED}' {slurm_job_id=}"
            )

            await mark_as_submitted(pending_job_submission.id, slurm_job_id)

    logger.debug("...Finished submitting pending jobs")
