from sentry_sdk.integrations.aiohttp import AioHttpIntegration
from sentry_sdk.integrations.logging import LoggingIntegration
from sentry_sdk.integrations.asgi import SentryAsgiMiddleware
from fastapi.middleware.cors import CORSMiddleware
from fastapi_utils.tasks import repeat_every
from sentry_sdk.utils import BadDsn
from fastapi import FastAPI
import sentry_sdk

import logging

from armada_agent.utils.logging import logger
from armada_agent.settings import SETTINGS
from armada_agent.utils import response
from armada_agent import agent


app = FastAPI(
    title="Armada Agent",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health():
    """
    Healthcheck, for health monitors in the deployed environment
    """
    return response.OK()


@app.on_event("startup")
@repeat_every(
    seconds=60,
    logger=logger,
    raise_exceptions=False,
)
async def collect_diagnostics():
    """
    Periodically (T=60s) get diagnostics data and report them to the backend
    """

    logger.info("##### Calling insertion of cluster diagnostics #####")

    res = await agent.update_diagnostics()

    logger.debug(
        "##### Response information ({}): {} #####".format(collect_diagnostics.__name__, res)
    )

    logger.info(f"##### {collect_diagnostics.__name__} run successfully #####")


@app.on_event("startup")
@repeat_every(
    seconds=60,
    logger=logger,
    raise_exceptions=False,
)
async def collect_partitions():
    """
    Periodically (T=60s) get partition data then report them to the backend
    """

    logger.info("##### Calling upsertion of cluster partitions #####")

    res = await agent.upsert_partitions()

    logger.debug(
        "##### Response information ({}): {} #####".format(collect_partitions.__name__, res)
    )

    logger.info(f"##### {collect_partitions.__name__} run successfully #####")


@app.on_event("startup")
@repeat_every(
    seconds=60,
    logger=logger,
    raise_exceptions=False,
)
async def collect_nodes():
    """
    Periodically (T=60s) get node data then report them to the backend
    """

    logger.info("##### Calling upsertion of cluster nodes #####")

    res = await agent.upsert_nodes()

    logger.debug("##### Response information ({}): {} #####".format(collect_nodes.__name__, res))

    logger.info(f"##### {collect_nodes.__name__} run successfully #####")


@app.on_event("startup")
@repeat_every(
    seconds=60,
    logger=logger,
    raise_exceptions=False,
)
async def collect_jobs():
    """
    Periodically (T=60s) get jobs data then report them to the backend
    """

    logger.info("##### Calling upsertion of cluster jobs #####")

    res = await agent.upsert_jobs()

    logger.debug("##### Response information ({}): {} #####".format(collect_jobs.__name__, res))

    logger.info(f"##### {collect_jobs.__name__} run successfully #####")


try:
    sentry_logging = LoggingIntegration(level=logging.INFO, event_level=logging.ERROR)

    sentry_sdk.init(
        dsn=SETTINGS.SENTRY_DSN,
        integrations=[sentry_logging, AioHttpIntegration()],
        traces_sample_rate=1.0,
    )

    app = SentryAsgiMiddleware(app)

    logger.debug("##### Enabled Sentry since a valid DSN key was provided.")
except BadDsn as e:

    logger.debug("##### Sentry could not be enabled: {}".format(e))
