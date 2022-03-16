"""
Define tests for the submission functions of the jobbergate section.
"""

import json
import pathlib

import httpx
import pytest
import respx

from cluster_agent.utils.exception import JobSubmissionError
from cluster_agent.settings import SETTINGS
from cluster_agent.jobbergate.schemas import PendingJobSubmission
from cluster_agent.jobbergate.submit import submit_job_script, submit_pending_jobs
from cluster_agent.jobbergate.constants import JobSubmissionStatus


def test_submit_job_script__success(tweak_settings, tmp_path, dummy_pending_job_submission_data, mocker):
    """
    Test that the ``submit_job_script()`` function can successfully submit a
    PendingJobSubmission to ``sbatch`` and return the ``slurm_job_id``.
    """
    sbatch_path = tmp_path / "dummy-sbatch"
    sbatch_path.write_text("whatever")

    build_path = tmp_path / "dummy-build"
    build_path.mkdir()

    pending_job_submission = PendingJobSubmission(**dummy_pending_job_submission_data)
    job_script_name = pending_job_submission.job_script_name

    with tweak_settings(SBATCH_PATH=sbatch_path):
        patched_run = mocker.patch("cluster_agent.jobbergate.submit.subprocess.run")
        patched_run.return_value = mocker.MagicMock(
            returncode=0,
            stdout="only the last value matters and it is 13",
        )
        slurm_job_id = submit_job_script(pending_job_submission, build_path=build_path)

        assert slurm_job_id == 13
        patched_run.assert_called_once_with(
            [sbatch_path, build_path / f"{job_script_name}.job", pending_job_submission.application_name],
            capture_output=True,
            text=True,
            input="sbatch output",
        )
        built_script_path = build_path / f"{job_script_name}.job"
        assert built_script_path.exists()
        assert built_script_path.read_text() == json.loads(pending_job_submission.job_script_data_as_string)["application.sh"]


def test_submit_job_script__raises_exception_if_SBATCH_PATH_does_not_exist(tweak_settings, tmp_path, dummy_pending_job_submission_data):
    """
    Test that the ``submit_job_script()`` raises a ``JobSubmissionError`` if the
    ``sbatch`` executable cannot be found at the provided path.
    """
    sbatch_path = pathlib.Path("some/fake/path/to/sbatch")

    build_path = tmp_path / "dummy-build"
    build_path.mkdir()

    pending_job_submission = PendingJobSubmission(**dummy_pending_job_submission_data)

    with tweak_settings(SBATCH_PATH=sbatch_path):
        with pytest.raises(JobSubmissionError, match="sbatch executable was not found"):
            submit_job_script(pending_job_submission, build_path=build_path)


def test_submit_job_script__raises_exception_if_build_path_does_not_exist(tweak_settings, tmp_path, dummy_pending_job_submission_data):
    """
    Test that the ``submit_job_script()`` raises a ``JobSubmissionError`` if the
    provided ``build_path`` does not exist.
    """
    sbatch_path = tmp_path / "dummy-sbatch"
    sbatch_path.write_text("whatever")

    build_path = pathlib.Path("some/fake/build/path")

    pending_job_submission = PendingJobSubmission(**dummy_pending_job_submission_data)

    with tweak_settings(SBATCH_PATH=sbatch_path):
        with pytest.raises(JobSubmissionError, match="build directory does not exist"):
            submit_job_script(pending_job_submission, build_path=build_path)


def test_submit_job_script__uses_temporary_directory_if_build_path_is_None(
    tweak_settings, tmp_path, dummy_pending_job_submission_data, mocker,
):
    """
    Test that the ``submit_job_script()`` will build the job script in a temporary
    diretory if not provided with a ``build_path``.
    """
    sbatch_path = tmp_path / "dummy-sbatch"
    sbatch_path.write_text("whatever")

    fake_temp_path = tmp_path / "dummy-build"
    fake_temp_path.mkdir()

    pending_job_submission = PendingJobSubmission(**dummy_pending_job_submission_data)
    job_script_name = pending_job_submission.job_script_name

    with tweak_settings(SBATCH_PATH=sbatch_path):
        patched_temp_dir = mocker.patch("cluster_agent.jobbergate.submit.TemporaryDirectory")
        magic_dir = mocker.MagicMock()
        magic_dir.configure_mock(name=str(fake_temp_path))
        patched_temp_dir.return_value = magic_dir

        patched_run = mocker.patch("cluster_agent.jobbergate.submit.subprocess.run")
        patched_run.return_value = mocker.MagicMock(
            returncode=0,
            stdout="only the last value matters and it is 13",
        )
        slurm_job_id = submit_job_script(pending_job_submission)

        assert slurm_job_id == 13
        patched_run.assert_called_once_with(
            [sbatch_path, fake_temp_path / f"{job_script_name}.job", pending_job_submission.application_name],
            capture_output=True,
            text=True,
            input="sbatch output",
        )
        built_script_path = fake_temp_path / f"{job_script_name}.job"
        assert built_script_path.exists()
        assert built_script_path.read_text() == json.loads(pending_job_submission.job_script_data_as_string)["application.sh"]


def test_submit_job_script__raises_exception_if_no_executable_script_was_found(
    tweak_settings, tmp_path, dummy_pending_job_submission_data
):
    """
    Test that the ``submit_job_script()`` will raise a JobSubmissionError if it cannot
    find an executable job script in the retrieved pending job submission data.
    """
    sbatch_path = tmp_path / "dummy-sbatch"
    sbatch_path.write_text("whatever")

    build_path = tmp_path / "dummy-build"
    build_path.mkdir()

    pending_job_submission = PendingJobSubmission(**dummy_pending_job_submission_data)
    pending_job_submission.job_script_data_as_string = json.dumps(
        {k: v for (k, v) in json.loads(pending_job_submission.job_script_data_as_string).items() if k != "application.sh"}
    )

    with tweak_settings(SBATCH_PATH=sbatch_path):
        with pytest.raises(JobSubmissionError, match="Could not find an executable"):
            submit_job_script(pending_job_submission, build_path=build_path)


def test_submit_job_script__raises_exception_if_exit_code_from_sbatch_is_not_0(
    tweak_settings, tmp_path, dummy_pending_job_submission_data, mocker
):
    """
    Test that the ``submit_job_script()`` will raise a JobSubmissionError if it the
    return code from the ``sbatch`` executable is not 0.
    """
    sbatch_path = tmp_path / "dummy-sbatch"
    sbatch_path.write_text("whatever")

    build_path = tmp_path / "dummy-build"
    build_path.mkdir()

    pending_job_submission = PendingJobSubmission(**dummy_pending_job_submission_data)

    with tweak_settings(SBATCH_PATH=sbatch_path):
        patched_run = mocker.patch("cluster_agent.jobbergate.submit.subprocess.run")
        patched_run.return_value = mocker.MagicMock(
            returncode=1,
            stdout="won't matter because return code is not 0",
            stderr="BOOM!",
        )
        with pytest.raises(JobSubmissionError, match="job submission with error: BOOM!"):
            submit_job_script(pending_job_submission, build_path=build_path)


def test_submit_pending_jobs(tweak_settings, tmp_path, mocker, dummy_template_source):
    """
    Test that the ``submit_pending_jobs()`` function can fetch pending job submissions,
    submit each to slurm, and update the job submission via the API.
    """
    sbatch_path = tmp_path / "dummy-sbatch"
    sbatch_path.write_text("whatever")

    build_path = tmp_path / "dummy-build"
    build_path.mkdir()

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
        with tweak_settings(SBATCH_PATH=sbatch_path):
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

            def _fake_run(cmd, *_, **__):
                application_name = cmd[-1]
                fake_slurm_job_id = int(application_name.replace("app", "")) * 11
                if application_name == "app3":
                    raise RuntimeError("BOOM!")
                else:
                    return mocker.MagicMock(
                        returncode=0,
                        stdout=f"only the last value matters and it is {fake_slurm_job_id}",
                    )

            patched_run = mocker.patch("cluster_agent.jobbergate.submit.subprocess.run")
            patched_run.side_effect = _fake_run

            submit_pending_jobs(build_path=build_path)

            patched_run.assert_has_calls([
                mocker.call(
                    [sbatch_path, build_path / f"script1.job", "app1"],
                    capture_output=True,
                    text=True,
                    input="sbatch output",
                ),
                mocker.call(
                    [sbatch_path, build_path / f"script2.job", "app2"],
                    capture_output=True,
                    text=True,
                    input="sbatch output",
                ),
                mocker.call(
                    [sbatch_path, build_path / f"script3.job", "app3"],
                    capture_output=True,
                    text=True,
                    input="sbatch output",
                ),
            ])

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
