"""
Provide definition of the base SlurmUserMapper class.
"""
import abc

from cluster_agent.settings import Settings


class SlurmUserMapper(metaclass=abc.ABCMeta):
    """
    Provide a base class for classes that map Armada users to local Slurm users.

    Define two methods that must be overridden in base classes:

    - configure(): Configure the mapper given the app settings
    - find_username(): Map a provided email address to a local slurm user.
    """

    async def configure(self, settings: Settings):
        """
        Configure the mapper instance.

        May be overridden by any derived class
        """
        pass

    @abc.abstractmethod
    async def find_username(self, email: str) -> str:
        """
        Find a slurm user name given an email.

        Must be implemented by any derived class.
        """
        raise NotImplementedError
