import sys
from functools import lru_cache
from pathlib import Path
from typing import Optional

from pydantic import BaseSettings, Field
from pydantic.error_wrappers import ValidationError

from cluster_agent.utils.logging import logger


_URL_REGEX = r"http[s]?://.+"


class Settings(BaseSettings):
    # slurmrestd info
    BASE_SLURMRESTD_URL: str = Field("http://127.0.0.1:6820", regex=_URL_REGEX)
    X_SLURM_USER_NAME: str = Field("root")
    X_SLURM_USER_TOKEN: Optional[str]

    # cluster api info
    BASE_API_URL: str = Field("https://rats.omnivector.solutions", regex=_URL_REGEX)

    SENTRY_DSN: str = Field("https://rats.sentry.com", regex=_URL_REGEX)

    # Auth0 config for machine-to-machine security
    AUTH0_DOMAIN: str = Field("omnivector.auth0.com")
    AUTH0_AUDIENCE: str = Field("https://domain.omnivector.solutions")
    AUTH0_CLIENT_ID: str = Field("abcde12345")
    AUTH0_CLIENT_SECRET: str = Field("abcde12345")

    CACHE_DIR = Path.home() / ".cache/cluster-agent"

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
