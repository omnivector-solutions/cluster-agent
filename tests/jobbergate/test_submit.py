import json
import pathlib

import httpx
import pytest

from cluster_agent.utils.exception import JobSubmissionError
from cluster_agent.jobbergate.schemas import (
    ApplicationResponse,
    JobScriptResponse,
    JobSubmissionResponse,
)
from cluster_agent.jobbergate.submit import submit_job_script


def test_submit_job_script__success(tweak_settings, tmp_path, dummy_job_script_data, mocker):
    sbatch_path = tmp_path / "dummy-sbatch"
    sbatch_path.write_text("whatever")

    build_path = tmp_path / "dummy-build"
    build_path.mkdir()

    job_script_data = JobScriptResponse(**dummy_job_script_data)
    job_script_name = job_script_data.job_script_name

    with tweak_settings(SBATCH_PATH=sbatch_path):
        patched_run = mocker.patch("cluster_agent.jobbergate.submit.subprocess.run")
        patched_run.return_value = mocker.MagicMock(
            returncode=0,
            stdout="only the last value matters and it is 13",
        )
        slurm_job_id = submit_job_script(job_script_data, "dummy-application-name", build_path=build_path)

        assert slurm_job_id == 13
        patched_run.assert_called_once_with(
            [sbatch_path, build_path / f"{job_script_name}.job", "dummy-application-name"],
            capture_output=True,
            text=True,
            input="sbatch output",
        )
        built_script_path = build_path / f"{job_script_name}.job"
        assert built_script_path.exists()
        assert built_script_path.read_text() == json.loads(job_script_data.job_script_data_as_string)["application.sh"]


def test_submit_job_script__raises_exception_if_SBATCH_PATH_does_not_exist(tweak_settings, tmp_path, dummy_job_script_data):
    sbatch_path = pathlib.Path("some/fake/path/to/sbatch")

    build_path = tmp_path / "dummy-build"
    build_path.mkdir()

    job_script_data = JobScriptResponse(**dummy_job_script_data)

    with tweak_settings(SBATCH_PATH=sbatch_path):
        with pytest.raises(JobSubmissionError, match="sbatch executable was not found"):
            submit_job_script(job_script_data, "dummy-application-name", build_path=build_path)


def test_submit_job_script__raises_exception_if_build_path_does_not_exist(tweak_settings, tmp_path, dummy_job_script_data):
    sbatch_path = tmp_path / "dummy-sbatch"
    sbatch_path.write_text("whatever")

    build_path = pathlib.Path("some/fake/build/path")

    job_script_data = JobScriptResponse(**dummy_job_script_data)

    with tweak_settings(SBATCH_PATH=sbatch_path):
        with pytest.raises(JobSubmissionError, match="build directory does not exist"):
            submit_job_script(job_script_data, "dummy-application-name", build_path=build_path)


def test_submit_job_script__uses_temporary_directory_if_build_path_is_None(
    tweak_settings, tmp_path, dummy_job_script_data, mocker,
):
    sbatch_path = tmp_path / "dummy-sbatch"
    sbatch_path.write_text("whatever")

    fake_temp_path = tmp_path / "dummy-build"
    fake_temp_path.mkdir()

    job_script_data = JobScriptResponse(**dummy_job_script_data)
    job_script_name = job_script_data.job_script_name

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
        slurm_job_id = submit_job_script(job_script_data, "dummy-application-name")

        assert slurm_job_id == 13
        patched_run.assert_called_once_with(
            [sbatch_path, fake_temp_path / f"{job_script_name}.job", "dummy-application-name"],
            capture_output=True,
            text=True,
            input="sbatch output",
        )
        built_script_path = fake_temp_path / f"{job_script_name}.job"
        assert built_script_path.exists()
        assert built_script_path.read_text() == json.loads(job_script_data.job_script_data_as_string)["application.sh"]


def test_submit_job_script__raises_exception_if_no_executable_script_was_found(
    tweak_settings, tmp_path, dummy_job_script_data
):
    sbatch_path = tmp_path / "dummy-sbatch"
    sbatch_path.write_text("whatever")

    build_path = tmp_path / "dummy-build"
    build_path.mkdir()

    job_script_data = JobScriptResponse(**dummy_job_script_data)
    job_script_data.job_script_data_as_string = json.dumps(
        {k: v for (k, v) in json.loads(job_script_data.job_script_data_as_string).items() if k != "application.sh"}
    )

    with tweak_settings(SBATCH_PATH=sbatch_path):
        with pytest.raises(JobSubmissionError, match="Could not find an executable"):
            submit_job_script(job_script_data, "dummy-application-name", build_path=build_path)


def test_submit_job_script__raises_exception_if_exit_code_from_sbatch_is_not_0(
    tweak_settings, tmp_path, dummy_job_script_data, mocker
):
    sbatch_path = tmp_path / "dummy-sbatch"
    sbatch_path.write_text("whatever")

    build_path = tmp_path / "dummy-build"
    build_path.mkdir()

    job_script_data = JobScriptResponse(**dummy_job_script_data)

    with tweak_settings(SBATCH_PATH=sbatch_path):
        patched_run = mocker.patch("cluster_agent.jobbergate.submit.subprocess.run")
        patched_run.return_value = mocker.MagicMock(
            returncode=1,
            stdout="won't matter because return code is not 0",
            stderr="BOOM!",
        )
        with pytest.raises(JobSubmissionError, match="job submission with error: BOOM!"):
            submit_job_script(job_script_data, "dummy-application-name", build_path=build_path)
