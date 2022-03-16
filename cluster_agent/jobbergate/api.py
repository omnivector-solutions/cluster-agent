from typing import List

import httpx

from cluster_agent.settings import SETTINGS
from cluster_agent.utils.exception import JobbergateApiError
from cluster_agent.jobbergate.schemas import PendingJobSubmission, ActiveJobSubmission
from cluster_agent.jobbergate.constants import JobSubmissionStatus


def fetch_pending_submissions() -> List[PendingJobSubmission]:
    """
    Retrieve a list of pending job_submissions.
    """

    response = httpx.get(f"{SETTINGS.JOBBERGATE_API_URL}/job-submissions/agent/pending")

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


def fetch_active_submissions() -> List[ActiveJobSubmission]:
    """
    Retrieve a list of active job_submissions.
    """

    response = httpx.get(f"{SETTINGS.JOBBERGATE_API_URL}/job-submissions/agent/active")

    JobbergateApiError.require_condition(
        response.status_code == 200,
        f"Failed to fetch pending job submissions: {response.text}",
    )

    with JobbergateApiError.handle_errors(
        "Failed to deserialize active job submission data"
    ):
        active_job_submissions = [ActiveJobSubmission(**ajs) for ajs in response.json()]

    return active_job_submissions


def mark_as_submitted(job_submission_id: int, slurm_job_id: int):
    """
    Mark job_submission as submitted in the Jobbergate API.
    """
    response = httpx.put(
        f"{SETTINGS.JOBBERGATE_API_URL}/job-submissions/agent/{job_submission_id}",
        json=dict(
            status=JobSubmissionStatus.SUBMITTED,
            slurm_job_id=slurm_job_id,
        ),
    )

    JobbergateApiError.require_condition(
        response.status_code == 200,
        f"Could not mark job submission {job_submission_id} as updated via the API",
    )


def update_status(job_submission_id: int, status: JobSubmissionStatus):
    """
    Update a job submission with a status
    """
    response = httpx.put(
        f"{SETTINGS.JOBBERGATE_API_URL}/job-submissions/agent/{job_submission_id}",
        json=dict(status=status),
    )

    JobbergateApiError.require_condition(
        response.status_code == 200,
        f"Could not update status for job submission {job_submission_id} via the API",
    )
