from enum import Enum


class MapperType(str, Enum):
    """
    Enumeration of possible job_submission statuses.
    """

    LDAP = "LDAP"
    SINGLE_USER = "SINGLE_USER"


class LDAPAuthType(str, Enum):
    """
    Enumeration of possible job_submission statuses.
    """

    NTLM = "NTLM"
    SIMPLE = "SIMPLE"
