import abc

from cluster_agent.identity.local_user.settings import LocalUserSettings


class MapperBase:
    """
    Provide a base class for a user-mapper.
    """

    @abc.abstractmethod
    def configure(self, settings: LocalUserSettings):
        """
        Configure the mapper instance.

        Must be implemented by any derived class
        """
        raise NotImplementedError

    @abc.abstractmethod
    def find_username(self, email: str) -> str:
        """
        Find a slurm user name given an email.

        Must be implemented by any derived class.
        """
        raise NotImplementedError
