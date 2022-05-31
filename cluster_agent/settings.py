import os
import sys
from functools import lru_cache
from pathlib import Path
from typing import Optional

from pydantic import AnyHttpUrl, BaseSettings, Field, root_validator
from pydantic.error_wrappers import ValidationError

from cluster_agent.identity.slurm_user.constants import (
    LDAPAuthType,
    MapperType,
)
from cluster_agent.utils.logging import logger


class Settings(BaseSettings):
    # slurmrestd info
    BASE_SLURMRESTD_URL: AnyHttpUrl = Field("http://127.0.0.1:6820")
    X_SLURM_USER_NAME: str = "ubuntu"
    DEFAULT_SLURM_WORK_DIR: Path = Path("/tmp")

    # cluster api info
    BASE_API_URL: AnyHttpUrl = Field("https://armada-k8s.staging.omnivector.solutions")

    SENTRY_DSN: Optional[AnyHttpUrl] = None

    # Auth0 config for machine-to-machine security
    AUTH0_DOMAIN: str = "omnivector.us.auth0.com"
    AUTH0_AUDIENCE: str = "https://armada.omnivector.solutions"
    AUTH0_CLIENT_ID: str
    AUTH0_CLIENT_SECRET: str

    CACHE_DIR = Path.home() / ".cache/cluster-agent"

    # Type of slurm user mapper to use
    SLURM_USER_MAPPER: MapperType = MapperType.SINGLE_USER

    # LDAP server settings
    LDAP_HOST: Optional[str]
    LDAP_DOMAIN: Optional[str]
    LDAP_USERNAME: Optional[str]
    LDAP_PASSWORD: Optional[str]
    LDAP_AUTH_TYPE: LDAPAuthType = LDAPAuthType.SIMPLE

    # Single user submitter settings
    SINGLE_USER_SUBMITTER: Optional[str]

    @root_validator
    def compute_extra_settings(cls, values):
        """
        Compute settings values that are based on other settings values.
        """
        ldap_host = values["LDAP_HOST"]
        ldap_domain = values["LDAP_DOMAIN"]

        # Just use the LDAP domain as the host if host is not set but domain is
        if ldap_domain is not None and ldap_host is None:
            values["LDAP_HOST"] = ldap_domain

        # If using single user, but don't have the setting, use default slurm user
        if values["SINGLE_USER_SUBMITTER"] is None:
            values["SINGLE_USER_SUBMITTER"] = values["X_SLURM_USER_NAME"]

        return values

    class Config:
        """
        Provide configuration for the project settings.

        Note that if the ``Settings()`` object is being invoked in test-mode, loading
        environment from a ".env" file is disabled and non-optional settings values
        are supplied.
        """
        env_prefix = "CLUSTER_AGENT_"

        test_mode = "pytest" in sys.modules
        if not test_mode:
            env_file = ".env"
        else:
            os.environ["CLUSTER_AGENT_AUTH0_CLIENT_ID"] = "DUMMY-TEST-CLIENT-ID"
            os.environ["CLUSTER_AGENT_AUTH0_CLIENT_SECRET"] = "DUMMY-TEST-CLIENT-SECRET"


@lru_cache()
def init_settings() -> Settings:
    try:
        return Settings()
    except ValidationError as e:
        logger.error(e)
        sys.exit(1)


SETTINGS = init_settings()
