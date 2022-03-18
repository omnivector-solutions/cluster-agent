import snick
from loguru import logger

from cluster_agent.jobbergate.api import fetch_active_submissions, update_status
from cluster_agent.jobbergate.constants import JobSubmissionStatus, status_map
from cluster_agent.utils.exception import SlurmrestdError, JobbergateApiError
from cluster_agent.utils.logging import log_error
from cluster_agent.identity.slurmrestd import backend_client as slurmrestd_client


async def fetch_job_status(slurm_job_id: int) -> JobSubmissionStatus:

    logger.debug(f"Fetching slurm job status for slurm job {slurm_job_id}")

    response = await slurmrestd_client.get(f"/slurm/v0.0.36/job/{slurm_job_id}")
    SlurmrestdError.require_condition(
        response.status_code == 200,
        snick.dedent(
            f"""
            Slurmrestd returned {response.status_code} when calling {response.url}:
            {response.text}
            """
        ),
    )
    jobs = response.json()["jobs"]
    SlurmrestdError.require_condition(
        len(jobs) == 1,
        snick.dedent(f"Couldn't find a slurm job matching id {slurm_job_id}"),
    )
    job = jobs.pop()
    slurm_status = job["job_state"]
    logger.debug(f"Slurm status for slurm job {slurm_job_id} is {slurm_status}")
    jobbergate_status = status_map[job["job_state"]]
    logger.debug(f"Jobbergate status for slurm job {slurm_job_id} is {jobbergate_status}")
    return jobbergate_status


async def finish_active_jobs():
    """
    Mark all active jobs that have completed or failed as finished.
    """
    logger.debug("Started marking completed jobs as finished...")

    logger.debug("Fetching active jobs")
    with JobbergateApiError.handle_errors(
        "Could not retrieve active job submissions",
        do_except=log_error,
    ):
        active_job_submissions = await fetch_active_submissions()

    for active_job_submission in active_job_submissions:
        logger.debug(
            f"Fetching status of job_submission {active_job_submission.id} from slurm"
        )

        status = None
        # Will only log errors. Does not re-raise
        with SlurmrestdError.handle_errors(
            "Failed to fetch a job status from Slurm REST API",
            do_except=log_error,
            re_raise=False,
        ):
            status = await fetch_job_status(active_job_submission.slurm_job_id)

        if status is None:
            logger.debug("Fetch status failed...skipping update")
            continue

        if status not in (JobSubmissionStatus.COMPLETED, JobSubmissionStatus.FAILED):
            logger.debug("Job is not complete or failed...skipping update")
            continue

        logger.debug(f"Updating job_submission with {status=}")

        # Will only log errors. Does not re-raise
        with JobbergateApiError.handle_errors(
            "API update failed",
            do_except=log_error,
            re_raise=False,
        ):
            await update_status(active_job_submission.id, status)
    logger.debug("...Finished marking completed jobs as finished")
