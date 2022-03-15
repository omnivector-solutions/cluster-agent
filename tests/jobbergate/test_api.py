"""
Define tests for the Jobbergate API interface functions.
"""

import httpx
import pytest
import respx

from cluster_agent.settings import SETTINGS
from cluster_agent.utils.exception import JobSubmissionError, JobbergateApiError
from cluster_agent.jobbergate.schemas import PendingJobSubmission
from cluster_agent.jobbergate.api import fetch_pending_submissions, mark_as_submitted


def test_fetch_pending_submissions__success():
    """
    Test that the ``fetch_pending_submissions()`` function can successfully retrieve
    PendingJobSubmission objects from the API.
    """
    pending_job_submissions_data = [
        dict(
            id=1,
            job_submission_name="sub1",
            job_script_id=11,
            job_script_name="script1",
            job_script_data_as_string="{}",
            application_name="app1",
            slurm_job_id=111,
        ),
        dict(
            id=2,
            job_submission_name="sub2",
            job_script_id=22,
            job_script_name="script2",
            job_script_data_as_string="{}",
            application_name="app2",
            slurm_job_id=222,
        ),
        dict(
            id=3,
            job_submission_name="sub3",
            job_script_id=33,
            job_script_name="script3",
            job_script_data_as_string="{}",
            application_name="app3",
            slurm_job_id=333,
        ),
    ]
    with respx.mock:
        respx.get(f"{SETTINGS.JOBBERGATE_API_URL}/job-submissions/agent/pending").mock(
            return_value=httpx.Response(
                status_code=200,
                json=pending_job_submissions_data,
            )
        )

        pending_job_submissions = fetch_pending_submissions()
        for (i, pending_job_submission) in enumerate(pending_job_submissions):
            assert isinstance(pending_job_submission, PendingJobSubmission)
            assert i + 1 == pending_job_submission.id


def test_fetch_pending_submissions__raises_JobbergateApiError_if_response_is_not_200():
    """
    Test that the ``fetch_pending_submissions()`` function will raise a
    JobbergateApiError if the response from the API is not OK (200).
    """
    with respx.mock:
        respx.get(f"{SETTINGS.JOBBERGATE_API_URL}/job-submissions/agent/pending").mock(
            return_value=httpx.Response(status_code=400)
        )

        with pytest.raises(JobbergateApiError, match="Failed to fetch"):
            fetch_pending_submissions()


def test_fetch_pending_submissions__raises_JobbergateApiError_if_response_cannot_be_deserialized():
    """
    Test that the ``fetch_pending_submissions()`` function will raise a
    JobbergateApiError if it fails to convert the response to a PendingJobSubmission.
    """
    pending_job_submissions_data = [
        dict(bad="data"),
    ]
    with respx.mock as route_mock:
        respx.get(f"{SETTINGS.JOBBERGATE_API_URL}/job-submissions/agent/pending").mock(
            return_value=httpx.Response(
                status_code=200,
                json=pending_job_submissions_data,
            )
        )

        with pytest.raises(JobbergateApiError, match="Failed to deserialize"):
            fetch_pending_submissions()


def test_mark_as_submitted__success():
    """
    Test that the ``mark_as_submitted()`` function will raise a JobbergateApiError if
    it fails to convert the response to a PendingJobSubmission object.
    """
    with respx.mock as route_mock:
        update_route = respx.put(f"{SETTINGS.JOBBERGATE_API_URL}/job-submissions/agent/1")
        update_route.mock(return_value=httpx.Response(status_code=200))

        mark_as_submitted(1, 111)
        assert update_route.called


def test_mark_as_submitted__raises_JobbergateApiError_if_the_response_is_not_200():
    """
    Test that the ``mark_as_submitted()`` function will raise a JobbergateApiError if
    the response from the API is not OK (200).
    """
    with respx.mock as route_mock:
        update_route = respx.put(f"{SETTINGS.JOBBERGATE_API_URL}/job-submissions/agent/1")
        update_route.mock(return_value=httpx.Response(status_code=400))

        with pytest.raises(JobbergateApiError, match="Could not mark job submission 1 as updated"):
            mark_as_submitted(1, 111)
        assert update_route.called
