from typing import List

from loguru import logger

from cluster_agent.utils.exception import JobbergateApiError
from cluster_agent.jobbergate.schemas import PendingJobSubmission, ActiveJobSubmission
from cluster_agent.jobbergate.constants import JobSubmissionStatus
from cluster_agent.identity.cluster_api import backend_client


async def fetch_pending_submissions() -> List[PendingJobSubmission]:
    """
    Retrieve a list of pending job_submissions.
    """
    response = await backend_client.get("/jobbergate/job-submissions/agent/pending")

    JobbergateApiError.require_condition(
        response.status_code == 200,
        f"Failed to fetch pending job submissions: {response.text}",
    )

    with JobbergateApiError.handle_errors(
        "Failed to deserialize pending job submission data"
    ):
        pending_job_submissions = [
            PendingJobSubmission(**pjs) for pjs in response.json()
        ]
    logger.debug(f"Retrieved {len(pending_job_submissions)} pending job submissions")

    return pending_job_submissions


async def fetch_active_submissions() -> List[ActiveJobSubmission]:
    """
    Retrieve a list of active job_submissions.
    """

    response = await backend_client.get("jobbergate/job-submissions/agent/active")

    JobbergateApiError.require_condition(
        response.status_code == 200,
        f"Failed to fetch pending job submissions: {response.text}",
    )

    with JobbergateApiError.handle_errors(
        "Failed to deserialize active job submission data"
    ):
        active_job_submissions = [ActiveJobSubmission(**ajs) for ajs in response.json()]
    logger.debug(f"Retrieved {len(active_job_submissions)} active job submissions")

    return active_job_submissions


async def mark_as_submitted(job_submission_id: int, slurm_job_id: int):
    """
    Mark job_submission as submitted in the Jobbergate API.
    """
    logger.debug(f"Marking job submission {job_submission_id} as submitted")
    response = await backend_client.put(
        f"jobbergate/job-submissions/agent/{job_submission_id}",
        json=dict(
            new_status=JobSubmissionStatus.SUBMITTED,
            slurm_job_id=slurm_job_id,
        ),
    )

    JobbergateApiError.require_condition(
        response.status_code == 200,
        f"Could not mark job submission {job_submission_id} as updated via the API",
    )


async def update_status(job_submission_id: int, status: JobSubmissionStatus):
    """
    Update a job submission with a status
    """
    logger.debug(f"Updating job submission {job_submission_id} with status {status}")
    response = await backend_client.put(
        f"jobbergate/job-submissions/agent/{job_submission_id}",
        json=dict(new_status=status),
    )

    JobbergateApiError.require_condition(
        response.status_code == 200,
        f"Could not update status for job submission {job_submission_id} via the API",
    )
