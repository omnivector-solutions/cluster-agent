"""
Define tests for the submission functions of the jobbergate section.
"""

import json
import re

import httpx
import pytest
import respx

from cluster_agent.utils.exception import JobSubmissionError
from cluster_agent.settings import SETTINGS
from cluster_agent.jobbergate.schemas import PendingJobSubmission, SlurmJobSubmission, SlurmJobParams
from cluster_agent.jobbergate.submit import submit_job_script, submit_pending_jobs
from cluster_agent.jobbergate.constants import JobSubmissionStatus


def test_submit_job_script__success(dummy_pending_job_submission_data, dummy_template_source, mocker):
    """
    Test that the ``submit_job_script()`` successfully submits a job.

    Verifies that a PendingJobSubmission instance is submitted via the Slurm REST API
    and that a ``slurm_job_id`` is returned.
    """
    mocker.patch("cluster_agent.identity.slurmrestd.acquire_token", return_value="dummy-token")
    pending_job_submission = PendingJobSubmission(**dummy_pending_job_submission_data)

    with respx.mock:
        submit_route = respx.post(f"{SETTINGS.BASE_SLURMRESTD_URL}/slurm/v0.0.36/job/submit")
        submit_route.mock(
            return_value=httpx.Response(
                status_code=200,
                json=dict(job_id=13),
            )
        )

        slurm_job_id = submit_job_script(pending_job_submission)

        assert slurm_job_id == 13
        assert submit_route.call_count == 1
        last_request = submit_route.calls.last.request
        assert last_request.method == "POST"
        assert json.loads(last_request.content.decode("utf-8")) == SlurmJobSubmission(
            script=dummy_template_source,
            job=SlurmJobParams(
                name=pending_job_submission.application_name,
            ),
        )


def test_submit_job_script__raises_exception_if_no_executable_script_was_found(
    dummy_pending_job_submission_data
):
    """
    Test that the ``submit_job_script()`` will raise a JobSubmissionError if it cannot
    find an executable job script in the retrieved pending job submission data.
    """
    pending_job_submission = PendingJobSubmission(**dummy_pending_job_submission_data)
    pending_job_submission.job_script_data_as_string = json.dumps(
        {k: v for (k, v) in json.loads(pending_job_submission.job_script_data_as_string).items() if k != "application.sh"}
    )

    with pytest.raises(JobSubmissionError, match="Could not find an executable"):
        submit_job_script(pending_job_submission)


def test_submit_job_script__raises_exception_if_submit_call_response_is_not_200(
    dummy_pending_job_submission_data,
    mocker,
):
    """
    Test that ``submit_job_script()`` raises an exception if the response from Slurm
    REST API is nota 200. Verifies that the error message is included in the raised
    exception.
    """
    mocker.patch("cluster_agent.identity.slurmrestd.acquire_token", return_value="dummy-token")
    pending_job_submission = PendingJobSubmission(**dummy_pending_job_submission_data)

    with respx.mock:
        submit_route = respx.post(f"{SETTINGS.BASE_SLURMRESTD_URL}/slurm/v0.0.36/job/submit")
        submit_route.mock(
            return_value=httpx.Response(
                status_code=400,
                json=dict(
                    errors=dict(
                        error="BOOM!",
                        errno=13,
                    ),
                ),
            )
        )

        match_regex = re.compile(
            r"rejected job submission with status 400.*BOOM!",
            re.DOTALL,
        )
        with pytest.raises(
            JobSubmissionError,
            match=match_regex,
        ):
            submit_job_script(pending_job_submission)


def test_submit_job_script__raises_exception_if_response_cannot_be_unpacked(
    dummy_pending_job_submission_data,
    mocker,
):
    """
    Test that ``submit_job_script()`` raises an exception if the response from Slurm
    REST API is nota 200. Verifies that the error message is included in the raised
    exception.
    """
    mocker.patch("cluster_agent.identity.slurmrestd.acquire_token", return_value="dummy-token")
    pending_job_submission = PendingJobSubmission(**dummy_pending_job_submission_data)

    with respx.mock:
        submit_route = respx.post(f"{SETTINGS.BASE_SLURMRESTD_URL}/slurm/v0.0.36/job/submit")
        submit_route.mock(return_value=httpx.Response(
            status_code=200,
            content="BAD DATA",
        ))

        with pytest.raises(JobSubmissionError, match="Couldn't unpack response"):
            submit_job_script(pending_job_submission)


def test_submit_pending_jobs(dummy_template_source):
    """
    Test that the ``submit_pending_jobs()`` function can fetch pending job submissions,
    submit each to slurm via the Slurm REST API, and update the job submission via the
    Jobbergate API.
    """

    pending_job_submissions_data = [
        dict(
            id=1,
            job_submission_name="sub1",
            job_script_id=11,
            job_script_name="script1",
            job_script_data_as_string=json.dumps({"application.sh": dummy_template_source}),
            application_name="app1",
        ),
        dict(
            id=2,
            job_submission_name="sub2",
            job_script_id=22,
            job_script_name="script2",
            job_script_data_as_string=json.dumps({"application.sh": dummy_template_source}),
            application_name="app2",
        ),
        dict(
            id=3,
            job_submission_name="sub3",
            job_script_id=33,
            job_script_name="script3",
            job_script_data_as_string=json.dumps({"application.sh": dummy_template_source}),
            application_name="app3",
        ),
    ]

    with respx.mock:
        fetch_route = respx.get(f"{SETTINGS.JOBBERGATE_API_URL}/job-submissions/agent/pending")
        fetch_route.mock(
            return_value=httpx.Response(
                status_code=200,
                json=pending_job_submissions_data,
            )
        )
        update_1_route = respx.put(f"{SETTINGS.JOBBERGATE_API_URL}/job-submissions/agent/1")
        update_1_route.mock(return_value=httpx.Response(status_code=200))

        update_2_route = respx.put(f"{SETTINGS.JOBBERGATE_API_URL}/job-submissions/agent/2")
        update_2_route.mock(return_value=httpx.Response(status_code=400))

        update_3_route = respx.put(f"{SETTINGS.JOBBERGATE_API_URL}/job-submissions/agent/3")
        update_3_route.mock(return_value=httpx.Response(status_code=200))

        def _submit_side_effect(request):
            req_data = request.content.decode("utf-8")
            name = json.loads(req_data)["job"]["name"]
            fake_slurm_job_id = int(name.replace("app", "")) * 11
            if name == "app3":
                return httpx.Response(
                    status_code=400,
                    json=dict(errors=dict(error="BOOM!")),
                )
            else:
                return httpx.Response(
                    status_code=200,
                    json=dict(job_id=fake_slurm_job_id),
                )

        submit_route = respx.post(f"{SETTINGS.BASE_SLURMRESTD_URL}/slurm/v0.0.36/job/submit")
        submit_route.mock(side_effect=_submit_side_effect)

        submit_pending_jobs()

        assert update_1_route.call_count == 1
        assert update_1_route.calls.last.request.content == json.dumps(dict(
            status=JobSubmissionStatus.SUBMITTED,
            slurm_job_id=11,
        )).encode("utf-8")

        assert update_2_route.call_count == 1
        assert update_2_route.calls.last.request.content == json.dumps(dict(
            status=JobSubmissionStatus.SUBMITTED,
            slurm_job_id=22,
        )).encode("utf-8")

        assert not update_3_route.called
