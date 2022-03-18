import asyncio
import logging

from sentry_sdk.integrations.logging import LoggingIntegration
from sentry_sdk.utils import BadDsn
import sentry_sdk

from cluster_agent.utils.logging import logger
from cluster_agent.settings import SETTINGS
from cluster_agent import agent
from cluster_agent.jobbergate.submit import submit_pending_jobs
from cluster_agent.jobbergate.finish import finish_active_jobs


async def collect_diagnostics():
    logger.info("##### Calling insertion of cluster diagnostics #####")

    res = await agent.update_diagnostics()

    logger.debug(
        "##### Response information ({}): {} #####".format(
            collect_diagnostics.__name__, res
        )
    )

    logger.info(f"##### {collect_diagnostics.__name__} run successfully #####")


async def collect_partitions():
    logger.info("##### Calling upsertion of cluster partitions #####")

    res = await agent.upsert_partitions()

    logger.debug(
        "##### Response information ({}): {} #####".format(
            collect_partitions.__name__, res
        )
    )

    logger.info(f"##### {collect_partitions.__name__} run successfully #####")


async def collect_nodes():
    logger.info("##### Calling upsertion of cluster nodes #####")

    res = await agent.upsert_nodes()

    logger.debug(
        "##### Response information ({}): {} #####".format(collect_nodes.__name__, res)
    )

    logger.info(f"##### {collect_nodes.__name__} run successfully #####")


async def collect_jobs():
    logger.info("##### Calling upsertion of cluster jobs #####")

    res = await agent.upsert_jobs()

    logger.debug(
        "##### Response information ({}): {} #####".format(collect_jobs.__name__, res)
    )

    logger.info(f"##### {collect_jobs.__name__} run successfully #####")


def submit_jobs():
    logger.info("##### Submitting pending Jobbergate jobs #####")

    submit_pending_jobs()

    logger.info("##### Finished submitting pending Jobbergate jobs #####")


def finish_jobs():
    logger.info("##### Marking finished slurm jobs as finished in Jobbergate #####")

    finish_active_jobs()

    logger.info(
        "##### Finished marking finished slurm jobs as finished in Jobbergate #####"
    )


try:
    sentry_logging = LoggingIntegration(level=logging.INFO, event_level=logging.ERROR)

    sentry_sdk.init(
        dsn=SETTINGS.SENTRY_DSN,
        integrations=[sentry_logging],
        traces_sample_rate=1.0,
    )

    logger.debug("##### Enabled Sentry since a valid DSN key was provided.")
except BadDsn as e:
    logger.debug("##### Sentry could not be enabled: {}".format(e))


async def run_agent():
    """Run task functions for the agent"""
    logger.info("Starting Cluster Agent")
    await collect_diagnostics()
    await collect_partitions()
    await collect_nodes()
    await collect_jobs()
    submit_jobs()
    finish_jobs()
    logger.info("Cluster Agent run successfully, exiting...")


def main():
    asyncio.run(run_agent())


if __name__ == "__main__":
    main()
