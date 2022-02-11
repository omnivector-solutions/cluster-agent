"""Core module for exception related operations"""
from buzz import Buzz


class ProcessExecutionError(Exception):
    """Raise exception when execution command returns an error"""


class AuthTokenError(Buzz):
    """Raise exception when there are connection issues with the backend"""


class SlurmrestdError(Buzz):
    """Raise exception when slurmrestd raises any error"""
