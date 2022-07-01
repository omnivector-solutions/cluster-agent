from typing import List

from buzz import DoExceptParams
from cluster_agent.identity.cluster_api import backend_client
from cluster_agent.jobbergate.constants import JobSubmissionStatus
from cluster_agent.jobbergate.schemas import ActiveJobSubmission, PendingJobSubmission
from cluster_agent.utils.exception import JobbergateApiError
from cluster_agent.utils.logging import log_error
from loguru import logger


async def fetch_pending_submissions() -> List[PendingJobSubmission]:
    """
    Retrieve a list of pending job_submissions.
    """
    with JobbergateApiError.handle_errors(
        "Failed to fetch pending job submissions",
        do_except=log_error,
    ):
        response = await backend_client.get("/jobbergate/job-submissions/agent/pending")
        response.raise_for_status()
        pending_job_submissions = [
            PendingJobSubmission(**pjs) for pjs in response.json()
        ]

    logger.debug(f"Retrieved {len(pending_job_submissions)} pending job submissions")
    return pending_job_submissions


async def fetch_active_submissions() -> List[ActiveJobSubmission]:
    """
    Retrieve a list of active job_submissions.
    """
    with JobbergateApiError.handle_errors(
        "Failed to fetch active job submissions",
        do_except=log_error,
    ):
        response = await backend_client.get("jobbergate/job-submissions/agent/active")
        response.raise_for_status()
        active_job_submissions = [ActiveJobSubmission(**ajs) for ajs in response.json()]

    logger.debug(f"Retrieved {len(active_job_submissions)} active job submissions")
    return active_job_submissions


async def mark_as_submitted(job_submission_id: int, slurm_job_id: int):
    """
    Mark job_submission as submitted in the Jobbergate API.
    """
    logger.debug(
        f"Marking job {job_submission_id=} as {JobSubmissionStatus.SUBMITTED} ({slurm_job_id=})"
    )

    with JobbergateApiError.handle_errors(
        f"Could not mark job submission {job_submission_id} as updated via the API",
        do_except=log_error,
    ):
        response = await backend_client.put(
            f"jobbergate/job-submissions/agent/{job_submission_id}",
            json=dict(
                new_status=JobSubmissionStatus.SUBMITTED,
                slurm_job_id=slurm_job_id,
            ),
        )
        response.raise_for_status()


async def notify_submission_aborted(
    params: DoExceptParams, job_submission_id: int
) -> None:
    """
    Notify Jobbergate that a job submission has been aborted.
    """
    log_error(params)
    logger.debug("Informing Jobbergate that job-submission was aborted")
    await update_status(
        job_submission_id,
        JobSubmissionStatus.ABORTED,
        reported_message=params.final_message,
    )


async def update_status(
    job_submission_id: int, status: JobSubmissionStatus, *, reported_message: str = ""
) -> None:
    """
    Update a job submission with a status
    """
    logger.debug(f"Updating {job_submission_id=} with status={status}")

    with JobbergateApiError.handle_errors(
        f"Could not update status for job submission {job_submission_id} via the API",
        do_except=log_error,
    ):
        response = await backend_client.put(
            f"jobbergate/job-submissions/agent/{job_submission_id}",
            json=dict(new_status=status, reported_message=reported_message),
        )
        response.raise_for_status()
