"""
Provide a factory method for creating slurm user mappers.
"""

from cluster_agent.identity.slurm_user.settings import SLURM_USER_SETTINGS
from cluster_agent.identity.slurm_user.exceptions import MapperFactoryError
from cluster_agent.identity.slurm_user.constants import MapperType
from cluster_agent.identity.slurm_user.mappers import (
    SlurmUserMapper,
    LDAPMapper,
    SingleUserMapper,
)


mapper_map = {
    MapperType.LDAP: LDAPMapper,
    MapperType.SINGLE_USER: SingleUserMapper,
}


def manufacture() -> SlurmUserMapper:
    """
    Create an instance of a Slurm user mapper given the app configuration.

    Map the configured mapper type from the app configuration to an instance of a
    particular SlurmUserMapper.
    """
    mapper_class = mapper_map.get(SLURM_USER_SETTINGS.SLURM_USER_MAPPER)
    MapperFactoryError.require_condition(
        mapper_class is not None,
        f"Couldn't find a mapper class for {SLURM_USER_SETTINGS.SLURM_USER_MAPPER}",
    )
    assert mapper_class is not None
    mapper_instance = mapper_class()
    mapper_instance.configure(SLURM_USER_SETTINGS)
    return mapper_instance
