from cluster_agent.identity.slurm_user.exceptions import SingleUserError

from cluster_agent.identity.slurm_user.mappers.mapper_base import SlurmUserMapper
from cluster_agent.identity.slurm_user.settings import SlurmUserSettings


class SingleUserMapper(SlurmUserMapper):
    """
    Provide a class to interface with the LDAP server
    """
    submitter = None

    def configure(self, settings: SlurmUserSettings):
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
