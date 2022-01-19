from pydantic.error_wrappers import ValidationError
from pydantic import BaseSettings, Field

from cluster_agent.utils.logging import logger

from functools import lru_cache
import sys


_URL_REGEX = r"http[s]?://.+"
_API_KEY_REGEX = r"([a-zA-Z0-9])\w+"


class Settings(BaseSettings):
    # slurmrestd info
    BASE_SLURMRESTD_URL: str = Field("http://127.0.0.1:6820", regex=_URL_REGEX)
    X_SLURM_USER_NAME: str = Field("root")

    # cluster api info
    BASE_API_URL: str = Field("https://rats.omnivector.solutions", regex=_URL_REGEX)
    API_KEY: str = Field("ratsratsrats", regex=_API_KEY_REGEX)

    SENTRY_DSN: str = Field("https://rats.sentry.com", regex=_URL_REGEX)

    class Config:

        env_file = ".env"
        env_prefix = "CLUSTER_AGENT_"


@lru_cache()
def init_settings() -> Settings:
    try:
        return Settings()
    except ValidationError as e:
        logger.error(e)
        sys.exit(1)


SETTINGS = init_settings()

CLUSTER_API_HEADER = {
    "Content-Type": "application/json",
    "Authorization": SETTINGS.API_KEY,
}
