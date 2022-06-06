import asyncio
import logging

from sentry_sdk.integrations.logging import LoggingIntegration
from sentry_sdk.utils import BadDsn
import sentry_sdk

from cluster_agent.utils.logging import logger, log_error
from cluster_agent.utils.exception import ProcessExecutionError
from cluster_agent.settings import SETTINGS
from cluster_agent import agent
from cluster_agent.jobbergate.submit import submit_pending_jobs
from cluster_agent.jobbergate.finish import finish_active_jobs


async def collect_diagnostics():
    """
    Insert cluster diagnostics.
    """
    res = await agent.update_diagnostics()
    logger.debug(f"Collect diagnostic repsponse: {res}")


async def collect_partitions():
    """
    Upsert cluster partitions.
    """
    res = await agent.upsert_partitions()
    logger.debug(f"Upsert partitions repsponse: {res}")


async def collect_nodes():
    """
    Upsert cluster nodes.
    """
    res = await agent.upsert_nodes()
    logger.debug(f"Upsert nodes repsponse: {res}")


async def collect_jobs():
    """
    Upsert cluster jobs.
    """
    res = await agent.upsert_jobs()
    logger.debug(f"Upsert jobs repsponse: {res}")


async def submit_jobs():
    """
    Submit pending jobs.
    """
    await submit_pending_jobs()


async def finish_jobs():
    """
    Mark finished jobs.
    """
    await finish_active_jobs()


try:
    sentry_logging = LoggingIntegration(level=logging.INFO, event_level=logging.ERROR)

    sentry_sdk.init(
        dsn=SETTINGS.SENTRY_DSN,
        integrations=[sentry_logging],
        traces_sample_rate=1.0,
        environment=SETTINGS.SENTRY_ENV,
    )

    logger.debug("##### Enabled Sentry since a valid DSN key was provided.")
except BadDsn as e:
    logger.debug("##### Sentry could not be enabled: {}".format(e))


async def run_agent():
    """Run task functions for the agent"""
    logger.info("Starting Cluster Agent")

    operations = [
        # collect_diagnostics,
        # collect_partitions,
        # collect_nodes,
        # collect_jobs,
        submit_jobs,
        finish_jobs,
    ]

    for operation in operations:
        docstring = (operation.__doc__ or operation.__name__).strip()
        logger.info(f">>>> Start: {docstring}")
        finish_status = "!!!! Failed"
        with ProcessExecutionError.handle_errors(
            f"Operation {operation.__name__} failed",
            do_except=log_error,
            do_finally=lambda: logger.info(f"{finish_status}: {docstring}"),
            re_raise=False,
        ):
            await operation()
            finish_status = "<<<< Completed"

    logger.info("Cluster Agent run successfully, exiting...")


def main():
    asyncio.run(run_agent())


if __name__ == "__main__":
    main()
