from typing import List, Optional

import httpx
from loguru import logger

from cluster_agent.settings import SETTINGS
from cluster_agent.utils.exception import JobbergateApiError
from cluster_agent.jobbergate.schemas import PendingJobSubmission, ActiveJobSubmission
from cluster_agent.jobbergate.constants import JobSubmissionStatus
from cluster_agent.identity.cluster_api import acquire_token


class AsyncJobbergateClient(httpx.AsyncClient):
    """
    Extends the httpx.AsyncClient class with automatic token acquisition for requests.
    The token is acquired lazily on the first httpx request issued.
    This client should be used for most Jobbergate API requests.
    """

    _token: Optional[str]

    def __init__(self):
        self._token = None
        super().__init__(base_url=SETTINGS.JOBBERGATE_API_URL, auth=self._inject_token)

    def _inject_token(self, request: httpx.Request) -> httpx.Request:
        if self._token is None:
            self._token = acquire_token()
        request.headers["authorization"] = f"Bearer {self._token}"
        return request


jobbergate_client = AsyncJobbergateClient()


async def fetch_pending_submissions() -> List[PendingJobSubmission]:
    """
    Retrieve a list of pending job_submissions.
    """
    logger.debug(f"CLIENT: {jobbergate_client.base_url}")
    logger.debug("PATH: /job-submissions/agent/pending")
    response = await jobbergate_client.get("/job-submissions/agent/pending")

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

    return pending_job_submissions


async def fetch_active_submissions() -> List[ActiveJobSubmission]:
    """
    Retrieve a list of active job_submissions.
    """

    response = await jobbergate_client.get("/job-submissions/agent/active")

    JobbergateApiError.require_condition(
        response.status_code == 200,
        f"Failed to fetch pending job submissions: {response.text}",
    )

    with JobbergateApiError.handle_errors(
        "Failed to deserialize active job submission data"
    ):
        active_job_submissions = [ActiveJobSubmission(**ajs) for ajs in response.json()]

    return active_job_submissions


async def mark_as_submitted(job_submission_id: int, slurm_job_id: int):
    """
    Mark job_submission as submitted in the Jobbergate API.
    """
    response = await jobbergate_client.put(
        f"/job-submissions/agent/{job_submission_id}",
        json=dict(
            status=JobSubmissionStatus.SUBMITTED,
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
    response = await jobbergate_client.put(
        f"/job-submissions/agent/{job_submission_id}",
        json=dict(status=status),
    )

    JobbergateApiError.require_condition(
        response.status_code == 200,
        f"Could not update status for job submission {job_submission_id} via the API",
    )
