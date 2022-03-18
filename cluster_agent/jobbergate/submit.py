import json
from typing import cast

import snick
from loguru import logger

from cluster_agent.jobbergate.schemas import PendingJobSubmission, SlurmSubmitResponse, SlurmJobSubmission, SlurmJobParams
from cluster_agent.jobbergate.api import fetch_pending_submissions, mark_as_submitted
from cluster_agent.jobbergate.constants import JobSubmissionStatus
from cluster_agent.identity.slurmrestd import backend_client as slurmrestd_client
from cluster_agent.utils.exception import JobSubmissionError, JobbergateApiError
from cluster_agent.utils.logging import log_error
from cluster_agent.settings import SETTINGS


async def submit_job_script(pending_job_submission: PendingJobSubmission) -> int:
    """
    Submit a Job Script to slurm via the Slurm REST API.

    :param: pending_job_submission: A job_submission with fields needed to submit.
    :returns: The ``slurm_job_id`` for the submitted job
    """
    job_script_name = pending_job_submission.job_script_name
    unpacked_data = json.loads(pending_job_submission.job_script_data_as_string)

    # TODO: Using Slurm REST API, we don't need to embed sbatch params.
    #       Instead, we could put them in a prameter payload and send them in via
    #       `job_properties`

    job_script = None
    for (filename, data) in unpacked_data.items():
        if filename == "application.sh":
            job_script = data
            filename = f"{job_script_name}.job"

    JobSubmissionError.require_condition(
        job_script is not None,
        "Could not find an executable script in retrieved job script data.",
    )

    payload = SlurmJobSubmission(
        script=job_script,
        job=SlurmJobParams(
            name=pending_job_submission.application_name,
            current_working_directory=SETTINGS.DEFAULT_SLURM_WORK_DIR,
        ),
    )
    logger.debug(f"Submitting pending job submission {pending_job_submission.id} to slurm with payload {payload}")
    response = await slurmrestd_client.post("/slurm/v0.0.36/job/submit", json=payload.dict())

    try:
        sub_data = SlurmSubmitResponse(**response.json())
    except Exception as err:
        raise JobSubmissionError(f"Couldn't unpack response from Slurm: {err}")

    JobSubmissionError.require_condition(
        response.status_code == 200,
        snick.dedent(
            f"""
            Slurmrestd rejected job submission with status {response.status_code}
              URL:       {response.url}
              Payload:   {payload}
              Response:  {json.dumps(sub_data.dict(), indent=2)}
            """,
        )
    )

    # Make static type checkers happy.
    slurm_job_id = cast(int, sub_data.job_id)
    logger.debug(f"Received slurm job id {slurm_job_id} for job submission {pending_job_submission.id}")

    return slurm_job_id


async def submit_pending_jobs():
    """
    Submit all pending jobs and update them with ``SUBMITTED`` status and slurm_job_id.

    :returns: The ``slurm_job_id`` for the submitted job
    """
    logger.debug("Started submitting pending jobs...")

    logger.debug("Fetching pending jobs...")
    with JobbergateApiError.handle_errors(
        "Could not retrieve pending job submissions",
        do_except=log_error,
    ):
        pending_job_submissions = await fetch_pending_submissions()

    for pending_job_submission in pending_job_submissions:
        logger.debug(f"Submitting pending job_submission {pending_job_submission.id}")
        slurm_job_id = None

        # Will only log errors. Does not re-raise
        with JobSubmissionError.handle_errors(
            f"Could not submit job_submission {pending_job_submission.id}",
            do_except=log_error,
            re_raise=False,
        ):
            slurm_job_id = await submit_job_script(pending_job_submission)

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
            await mark_as_submitted(pending_job_submission.id, slurm_job_id)
    logger.debug("...Finished submitting pending jobs")
