"""
Describe the settings that are needed/used in setting up Slurm user mapping.
"""

import sys
from functools import lru_cache
from typing import Optional

from pydantic import BaseSettings, root_validator
from pydantic.error_wrappers import ValidationError

from cluster_agent.identity.slurm_user.constants import MapperType, LDAPAuthType
from cluster_agent.utils.logging import logger
from cluster_agent.settings import SETTINGS


class SlurmUserSettings(BaseSettings):
    """
    Settings class for Slurm user mapping.

    Contain only settings that are needed/used by the Slurm user mappers.
    """

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
            values["SINGLE_USER_SUBMITTER"] = SETTINGS.X_SLURM_USER_NAME

        return values

    class Config:

        env_file = ".env"
        env_prefix = "CLUSTER_AGENT_"


@lru_cache()
def init_settings() -> SlurmUserSettings:
    try:
        return SlurmUserSettings()
    except ValidationError as e:
        logger.error(e)
        sys.exit(1)


SLURM_USER_SETTINGS = init_settings()
