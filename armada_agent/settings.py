from pydantic.error_wrappers import ValidationError
from pydantic import BaseSettings, Field

from armada_agent.utils.logging import logger

import sys


_URL_REGEX = r"http[s]?://.+"


class Settings(BaseSettings):
    # slurmrestd info
    ARMADA_AGENT_BASE_SLURMRESTD_URL: str = Field("http://127.1:6820", regex=_URL_REGEX)
    ARMADA_AGENT_X_SLURM_USER_NAME: str = Field("root")

    # armada api info
    ARMADA_AGENT_BASE_API_URL: str
    ARMADA_AGENT_API_KEY: str


    class Config:

        env_file = ".env"


def init_settings() -> Settings:
    try:
        return Settings()
    except ValidationError as e:
        logger.error(e)
        sys.exit(1)


SETTINGS = init_settings()