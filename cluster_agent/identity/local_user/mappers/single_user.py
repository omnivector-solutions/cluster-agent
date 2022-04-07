from cluster_agent.identity.local_user.exceptions import SingleUserError

from cluster_agent.identity.local_user.mappers.mapper_base import MapperBase
from cluster_agent.identity.local_user.settings import LocalUserSettings


class SingleUserMapper(MapperBase):
    """
    Provide a class to interface with the LDAP server
    """
    submitter = None

    def configure(self, settings: LocalUserSettings):
        """
        Connect to the the LDAP server.
        """
        self.submitter = settings.SINGLE_USER_SUBMITTER

    def find_username(self, *_) -> str:
        """
        Find an active diretory username given a user email.

        Lazily connect to the LDAP server if not already connected.
        """
        SingleUserError.require_condition(
            self.submitter is not None,
            "No username set for single-user job submission.",
        )
        # Keep static type-checkers happy
        assert self.submitter is not None

        return self.submitter
