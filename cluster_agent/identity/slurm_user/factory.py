"""
Provide a factory method for creating slurm user mappers.
"""

from cluster_agent.identity.slurm_user.constants import MapperType
from cluster_agent.identity.slurm_user.exceptions import MapperFactoryError
from cluster_agent.identity.slurm_user.mappers import (
    LDAPMapper,
    SingleUserMapper,
    SlurmUserMapper,
)
from cluster_agent.settings import SETTINGS

mapper_map = {
    MapperType.LDAP: LDAPMapper,
    MapperType.SINGLE_USER: SingleUserMapper,
}


async def manufacture() -> SlurmUserMapper:
    """
    Create an instance of a Slurm user mapper given the app configuration.

    Map the configured mapper type from the app configuration to an instance of a
    particular SlurmUserMapper.
    """
    mapper_class = mapper_map.get(SETTINGS.SLURM_USER_MAPPER)
    MapperFactoryError.require_condition(
        mapper_class is not None,
        f"Couldn't find a mapper class for {SETTINGS.SLURM_USER_MAPPER}",
    )
    assert mapper_class is not None
    mapper_instance = mapper_class()
    await mapper_instance.configure(SETTINGS)
    return mapper_instance
