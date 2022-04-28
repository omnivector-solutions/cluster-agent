import pytest

from cluster_agent.identity.slurm_user.exceptions import MapperFactoryError
from cluster_agent.identity.slurm_user.factory import manufacture
from cluster_agent.identity.slurm_user.mappers.ldap import LDAPMapper
from cluster_agent.identity.slurm_user.settings import SLURM_USER_SETTINGS
from cluster_agent.identity.slurm_user.constants import MapperType


async def test_manufacture__with_valid_mapper_name(tweak_slurm_user_settings, mocker):
    mocked_ldap_instance = mocker.AsyncMock(LDAPMapper)
    mocked_ldap_class = mocker.MagicMock(return_value=mocked_ldap_instance)
    mocker.patch.dict(
        "cluster_agent.identity.slurm_user.factory.mapper_map",
        {MapperType.LDAP: mocked_ldap_class},
    )
    with tweak_slurm_user_settings(SLURM_USER_MAPPER=MapperType.LDAP):
        await manufacture()
        mocked_ldap_instance.configure.assert_called_once_with(SLURM_USER_SETTINGS)


async def test_manufacture__with_invalid_mapper_name(tweak_slurm_user_settings, mocker):
    mocker.patch.dict(
        "cluster_agent.identity.slurm_user.factory.mapper_map",
        {"REAL": mocker.MagicMock()},
    )
    with tweak_slurm_user_settings(SLURM_USER_MAPPER="FAKE"):
        with pytest.raises(MapperFactoryError, match="Couldn't find a mapper class"):
            await manufacture()
