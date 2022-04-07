"""
Define constants for the slurm_user subpackage.
"""

from enum import Enum


class MapperType(str, Enum):
    """
    Enumeration of available mapper types.
    """

    LDAP = "LDAP"
    SINGLE_USER = "SINGLE_USER"


class LDAPAuthType(str, Enum):
    """
    Enumeration of possible auth types available with the LDAP mapper.
    """

    NTLM = "NTLM"
    SIMPLE = "SIMPLE"
