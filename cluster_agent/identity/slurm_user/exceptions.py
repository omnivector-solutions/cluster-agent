"""
Provide custom exceptions that are only used in the slurm_user sub-package.
"""

from cluster_agent.utils.exception import ClusterAgentError


class MapperFactoryError(ClusterAgentError):
    """Raise exception when a local user mapper cannot be manufactured."""


class LDAPError(ClusterAgentError):
    """Raise exception when LDAP communication fails."""


class SingleUserError(ClusterAgentError):
    """Raise exception when there is a problem with single-user submission."""
