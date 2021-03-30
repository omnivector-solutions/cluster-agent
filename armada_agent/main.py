from fastapi.middleware.cors import CORSMiddleware
from fastapi_utils.tasks import repeat_every
from fastapi import FastAPI, Depends

from functools import lru_cache
import logging

from armada_agent.utils.logging import logger
from armada_agent.agent import ScraperAgent
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
def get_settings():
    return settings.Settings()


@lru_cache()
def get_agent(config: settings.Settings = Depends(get_settings)):

    logger.info(config)

    return ScraperAgent(config)


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
def collect_diagnostics(agent: ScraperAgent = Depends(get_agent)):
    """
    Periodically get diagnostics data and report them to the backend
    """

    logger.info("Run collecting")
    logger.info(agent)

    ## TODO: make diagnostics call asynchronously
    # agent.update_cluster_diagnostics()


@app.on_event("startup")
@repeat_every(
    seconds=60,
    logger=logger,
    raise_exceptions=True,
)
def collect_partition_and_nodes(agent: ScraperAgent = Depends(get_agent)):
    """
    Periodically get partition data and node data then
    report them to the backend
    """

    ## TODO: make partitions and nodes call asynchronously
    # agent.upsert_partition_and_node_records()
