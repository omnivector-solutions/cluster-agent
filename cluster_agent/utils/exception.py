"""Core module for exception related operations"""
from buzz import Buzz


class ClusterAgentError(Buzz):
    """Raise exception when execution command returns an error"""


class ProcessExecutionError(ClusterAgentError):
    """Raise exception when execution command returns an error"""


class AuthTokenError(ClusterAgentError):
    """Raise exception when there are connection issues with the backend"""


class SlurmrestdError(ClusterAgentError):
    """Raise exception when slurmrestd raises any error"""


class JobbergateApiError(ClusterAgentError):
    """Raise exception when communication with Jobbergate API fails"""


class JobSubmissionError(ClusterAgentError):
    """Raise exception when a job cannot be submitted raises any error"""
