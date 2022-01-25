from pydantic.error_wrappers import ValidationError
from pydantic import BaseSettings, Field

from cluster_agent.utils.logging import logger

from functools import lru_cache
import sys


_URL_REGEX = r"http[s]?://.+"


class Settings(BaseSettings):
    # slurmrestd info
    BASE_SLURMRESTD_URL: str = Field("http://127.0.0.1:6820", regex=_URL_REGEX)
    X_SLURM_USER_NAME: str = Field("root")

    # cluster api info
    BASE_API_URL: str = Field("https://rats.omnivector.solutions", regex=_URL_REGEX)

    SENTRY_DSN: str = Field("https://rats.sentry.com", regex=_URL_REGEX)

    # Auth0 config for machine-to-machine security
    AUTH0_DOMAIN: str
    AUTH0_AUDIENCE: str
    AUTH0_CLIENT_ID: str
    AUTH0_CLIENT_SECRET: str

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
