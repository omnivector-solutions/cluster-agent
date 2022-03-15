from typing import List

import httpx

from cluster_agent.settings import SETTINGS
from cluster_agent.utils.exception import JobbergateApiError
from cluster_agent.jobbergate.schemas import JobScriptResponse, JobSubmissionResponse


def fetch_job_script_data(
    job_script_id: int,
) -> JobScriptResponse:
    """
    Retrieve a job_script from the API by its id.
    """

    response = httpx.get(f"{SETTINGS.JOBBERGATE_API_URL}/job-scripts/{job_script_id}")

    JobbergateApiError.require_condition(
        response.status_code == 200,
        f"Failed to fetch job_script {job_script_id} from API: {response.text}",
    )

    with JobbergateApiError.handle_errors("Failed to deserialize job_script data"):
        job_script_data = JobScriptResponse(**response.json())

    return job_script_data


def fetch_pending_submissions(
) -> List[JobSubmissionResponse]:
    """
    Retrieve a job_script from the API by its id.
    """

    response = httpx.get(
        f"{SETTINGS.JOBBERGATE_API_URL}/job-submissions/{job_script_id}"
    )

    JobbergateApiError.require_condition(
        response.status_code == 200,
        f"Failed to fetch job_script {job_script_id} from API: {response.text}",
    )

    with JobbergateApiError.handle_errors("Failed to deserialize job_script data"):
        job_script_data = JobScriptResponse(**response.json())

    return job_script_data
