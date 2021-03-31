from fastapi.middleware.cors import CORSMiddleware
from fastapi_utils.tasks import repeat_every
from fastapi import FastAPI, Depends

from functools import lru_cache
import logging

from armada_agent.utils.logging import logger
from armada_agent.agent import ScraperAgent
from armada_agent.settings import SETTINGS
from armada_agent.utils import response
from armada_agent import settings


app = FastAPI(
    title="Armada Agent",
    version="0.1.0"
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


@lru_cache()
def get_agent():

    return ScraperAgent(SETTINGS)


@app.on_event("startup")
def begin_logging():
    """
    Configure logging
    """
    level = getattr(logging, "INFO")
    logger.setLevel(level)

    # as a developer you'll run this with uvicorn,
    # which takes over logging.
    uvicorn = logging.getLogger("uvicorn")
    if uvicorn.handlers:  # pragma: nocover
        logger.addHandler(uvicorn.handlers[0])

@app.on_event("startup")
@repeat_every(
    seconds=60,
    logger=logger,
    raise_exceptions=True,
)
async def collect_diagnostics():
    """
    Periodically get diagnostics data and report them to the backend
    """

    agent = get_agent()

    logger.info("💡💡💡 Calling insertion of cluster diagnostics 💡💡💡")

    res = agent.update_cluster_diagnostics()

    logger.info("Response information ({}): {}".format(collect_diagnostics.__name__, res))

    logger.info(f"✅✅✅ {collect_diagnostics.__name__} run successfully ✅✅✅")


@app.on_event("startup")
@repeat_every(
    seconds=60,
    logger=logger,
    raise_exceptions=True,
)
async def collect_partition_and_nodes():
    """
    Periodically get partition data and node data then
    report them to the backend
    """

    agent = get_agent()

    logger.info("💡💡💡 Calling upsertion of cluster partitions and nodes 💡💡💡")

    res = agent.upsert_partition_and_node_records()

    logger.info("📩📩📩 Response information ({}): {}".format(collect_partition_and_nodes.__name__, res))

    logger.info(f"✅✅✅ {collect_partition_and_nodes.__name__} run successfully ✅✅✅")
