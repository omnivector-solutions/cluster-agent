import json
import subprocess
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Optional

from cluster_agent.jobbergate.schemas import JobScriptResponse
from cluster_agent.utils.exception import JobSubmissionError
from cluster_agent.settings import SETTINGS


def submit_job_script(
    job_script_data: JobScriptResponse,
    application_name: str,
    build_path: Optional[Path] = None,
) -> int:
    """
    Submit a Job Script to slurm via ``sbatch``.

    :param: job_script_data:  A JobScriptResponse including the script and its configuration
    :param: application_name: The name of the application to pass to ``sbatch``
    :param: build_path:       An optional directory where the job script templates and job script should be unpacked
    :returns: The ``slurm_job_id`` for the submitted job
    """
    JobSubmissionError.require_condition(
        SETTINGS.SBATCH_PATH.exists(),
        f"sbatch executable was not found at {SETTINGS.SBATCH_PATH}",
    )

    job_script_name = job_script_data.job_script_name
    unpacked_data = json.loads(job_script_data.job_script_data_as_string)

    if build_path is None:
        temp_build_dir = TemporaryDirectory()
        build_path = Path(temp_build_dir.name)
    else:
        JobSubmissionError.require_condition(
            build_path.exists(),
            f"The supplied build directory does not exist: {build_path}",
        )

    script_path = None
    for (filename, data) in unpacked_data.items():
        if filename == "application.sh":
            filename = f"{job_script_name}.job"
            script_path = build_path / filename

        file_path = build_path / filename
        file_path.write_text(data)

    JobSubmissionError.require_condition(
        script_path is not None,
        f"Could not find an executable script in retrieved job script data.",
    )

    # Make static type checkers happy
    assert SETTINGS.SBATCH_PATH is not None
    assert script_path is not None

    cmd = [SETTINGS.SBATCH_PATH, script_path, application_name]
    proc = subprocess.run(cmd, capture_output=True, text=True, input="sbatch output")

    JobSubmissionError.require_condition(
        proc.returncode == 0,
        f"Failed to execute job submission with error: {proc.stderr}.",
    )
    slurm_job_id = int(proc.stdout.split()[-1])
    return slurm_job_id
