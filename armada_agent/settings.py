from pydantic.error_wrappers import ValidationError
from pydantic import BaseSettings, Field

from armada_agent.utils.logging import logger

from functools import lru_cache
import sys


_URL_REGEX = r"http[s]?://.+"
_API_KEY_REGEX = r"([a-zA-Z0-9])\w+"


class Settings(BaseSettings):
    # slurmrestd info
    ARMADA_AGENT_BASE_SLURMRESTD_URL: str = Field("http://127.1:6820", regex=_URL_REGEX)
    ARMADA_AGENT_X_SLURM_USER_NAME: str = Field("root")

    # armada api info
    ARMADA_AGENT_BASE_API_URL: str = Field("https://rats.omnivector.solutions", regex=_URL_REGEX)
    ARMADA_AGENT_API_KEY: str = Field("ratsratsrats", regex=_API_KEY_REGEX)


    class Config:

        env_file = ".env"


@lru_cache()
def init_settings() -> Settings:
    try:
        return Settings()
    except ValidationError as e:
        logger.error(e)
        sys.exit(1)


SETTINGS = init_settings()