import json
import subprocess
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Optional

from loguru import logger

from cluster_agent.jobbergate.schemas import PendingJobSubmission
from cluster_agent.jobbergate.api import fetch_pending_submissions, mark_as_submitted
from cluster_agent.jobbergate.constants import JobSubmissionStatus
from cluster_agent.utils.exception import JobSubmissionError, JobbergateApiError
from cluster_agent.utils.logging import log_error
from cluster_agent.settings import SETTINGS


def submit_job_script(
    pending_job_submission: PendingJobSubmission,
    build_path: Optional[Path] = None,
) -> int:
    """
    Submit a Job Script to slurm via ``sbatch``.

    :param: pending_job_submission: A job_submission with fields needed to submit.
    :param: build_path:             An optional directory where the job script templates
                                   and job script should be unpacked
    :returns: The ``slurm_job_id`` for the submitted job
    """
    JobSubmissionError.require_condition(
        SETTINGS.SBATCH_PATH.exists(),
        f"sbatch executable was not found at {SETTINGS.SBATCH_PATH}",
    )

    job_script_name = pending_job_submission.job_script_name
    unpacked_data = json.loads(pending_job_submission.job_script_data_as_string)

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
        "Could not find an executable script in retrieved job script data.",
    )

    # Make static type checkers happy
    assert SETTINGS.SBATCH_PATH is not None
    assert script_path is not None

    cmd = [SETTINGS.SBATCH_PATH, script_path, pending_job_submission.application_name]
    proc = subprocess.run(cmd, capture_output=True, text=True, input="sbatch output")

    JobSubmissionError.require_condition(
        proc.returncode == 0,
        f"Failed to execute job submission with error: {proc.stderr}.",
    )
    slurm_job_id = int(proc.stdout.split()[-1])
    return slurm_job_id


def submit_pending_jobs(
    build_path: Optional[Path] = None,
):
    """
    Submit all pending jobs and update them with ``SUBMITTED`` status and slurm_job_id.

    :param: build_path: An optional directory where the job script templates and job
                       script should be unpacked
    :returns: The ``slurm_job_id`` for the submitted job
    """
    logger.debug("Started submitting pending jobs...")

    logger.debug("Fetching pending jobs...")
    with JobbergateApiError.handle_errors(
        "Could not retrieve pending job submissions",
        do_except=log_error,
    ):
        pending_job_submissions = fetch_pending_submissions()

    for pending_job_submission in pending_job_submissions:
        logger.debug(f"Submitting pending job_submission {pending_job_submission.id}")
        slurm_job_id = None

        # Will only log errors. Does not re-raise
        with JobSubmissionError.handle_errors(
            "Could not submit job_submission {pending_job_submission.id}",
            do_except=log_error,
            re_raise=False,
        ):
            slurm_job_id = submit_job_script(
                pending_job_submission, build_path=build_path
            )

        if slurm_job_id is None:
            logger.debug("Submit failed...skipping update")
            continue
        else:
            logger.debug(f"Retrieved {slurm_job_id=}")

        logger.debug(
            f"Updating job_submission with '{JobSubmissionStatus.SUBMITTED}' status"
        )

        # Will only log errors. Does not re-raise
        with JobbergateApiError.handle_errors(
            "API update failed",
            do_except=log_error,
            re_raise=False,
        ):
            mark_as_submitted(pending_job_submission.id, slurm_job_id)
    logger.debug("...Finished submitting pending jobs")
