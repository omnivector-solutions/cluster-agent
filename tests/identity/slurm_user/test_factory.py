import pytest

from cluster_agent.identity.slurm_user.exceptions import MapperFactoryError
from cluster_agent.identity.slurm_user.factory import manufacture
from cluster_agent.identity.slurm_user.settings import LOCAL_USER_SETTINGS
from cluster_agent.identity.slurm_user.constants import MapperType


def test_manufacture__with_valid_mapper_name(tweak_slurm_user_settings, mocker):
    mocked_ldap_instance = mocker.MagicMock()
    mocked_ldap_class = mocker.MagicMock(return_value=mocked_ldap_instance)
    mocker.patch.dict(
        "cluster_agent.identity.slurm_user.factory.mapper_map",
        {MapperType.LDAP: mocked_ldap_class},
    )
    with tweak_slurm_user_settings(LOCAL_USER_MAPPER=MapperType.LDAP):
        manufacture()
        mocked_ldap_instance.configure.assert_called_once_with(LOCAL_USER_SETTINGS)


def test_manufacture__with_invalid_mapper_name(tweak_slurm_user_settings, mocker):
    mocker.patch.dict(
        "cluster_agent.identity.slurm_user.factory.mapper_map",
        {"REAL": mocker.MagicMock()},
    )
    with tweak_slurm_user_settings(LOCAL_USER_MAPPER="FAKE"):
        with pytest.raises(MapperFactoryError, match="Couldn't find a mapper class"):
            manufacture()
