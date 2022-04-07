"""
Provide definition of the base slurm user mapper class.
"""
import abc

from cluster_agent.identity.slurm_user.settings import SlurmUserSettings


class SlurmUserMapper:
    """
    Provide a base class for classes that map Armada users to local Slurm/Unix users.

    Define two methods that must be overridden in base classes:

    - configure(): Configure the mapper given the app settings
    - find_username(): Map a provided email address to a local slurm/unix user.
    """

    @abc.abstractmethod
    def configure(self, settings: SlurmUserSettings):
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
