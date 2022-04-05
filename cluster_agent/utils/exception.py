"""Core module for exception related operations"""
from buzz import Buzz


class ProcessExecutionError(Buzz):
    """Raise exception when execution command returns an error"""


class AuthTokenError(Buzz):
    """Raise exception when there are connection issues with the backend"""


class SlurmrestdError(Buzz):
    """Raise exception when slurmrestd raises any error"""


class JobbergateApiError(Buzz):
    """Raise exception when communication with Jobbergate API fails"""


class JobSubmissionError(Buzz):
    """Raise exception when a job cannot be submitted raises any error"""


class LDAPError(Buzz):
    """Raise exception when LDAP communication fails."""


class UIDError(Buzz):
    """Raise exception when a UID (and GID) cannot be fetched."""
