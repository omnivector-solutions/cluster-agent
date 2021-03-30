from pydantic.error_wrappers import ValidationError
from pydantic import BaseSettings

from armada_agent.utils.logging import logger

import sys


class Settings(BaseSettings):
    # slurmrestd info
    base_scraper_url: str
    x_slurm_user_name: str
    x_slurm_user_token: str

    # armada api info
    base_api_url: str
    api_key: str

    # scraper info
    stage: str = "prod"


    class Config:

        env_file = ".env"


def init_settings() -> Settings:
    try:
        return Settings()
    except ValidationError as e:
        logger.error(e)
        sys.exit(1)


SETTINGS = init_settings()