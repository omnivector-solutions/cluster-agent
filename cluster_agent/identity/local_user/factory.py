from cluster_agent.identity.local_user.settings import LOCAL_USER_SETTINGS
from cluster_agent.identity.local_user.exceptions import MapperFactoryError
from cluster_agent.identity.local_user.constants import MapperType
from cluster_agent.identity.local_user.mappers import (
    MapperBase,
    LDAPMapper,
    SingleUserMapper,
)


mapper_map = {
    MapperType.LDAP: LDAPMapper,
    MapperType.SINGLE_USER: SingleUserMapper,
}


def manufacture() -> MapperBase:
    mapper_class = mapper_map.get(LOCAL_USER_SETTINGS.LOCAL_USER_MAPPER)
    MapperFactoryError.require_condition(
        mapper_class is not None,
        "Couldn't find a mapper class for {LOCAL_USER_SETTINGS.LOCAL_USER_MAPPER}",
    )
    assert mapper_class is not None
    mapper_instance = mapper_class()
    mapper_instance.configure(LOCAL_USER_SETTINGS)
    return mapper_instance
