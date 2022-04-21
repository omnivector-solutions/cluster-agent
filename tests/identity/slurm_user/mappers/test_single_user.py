"""
Define tests for the single-user mapper.
"""

import pytest

from cluster_agent.identity.slurm_user.exceptions import SingleUserError
from cluster_agent.identity.slurm_user.mappers import single_user
from cluster_agent.identity.slurm_user.settings import SLURM_USER_SETTINGS


async def test_configure__success(mocker, tweak_slurm_user_settings):
    """
    Test that a SingleUserMapper instance ``configures()`` correctly.
    """
    mapper = single_user.SingleUserMapper()

    with tweak_slurm_user_settings(SINGLE_USER_SUBMITTER="dummy-user"):
        await mapper.configure(SLURM_USER_SETTINGS)
    assert mapper.submitter == "dummy-user"


async def test_find_username__success(mocker, tweak_slurm_user_settings):
    """
    Test that the ``find_username()`` uses the single user as the submit username.
    """
    mapper = single_user.SingleUserMapper()

    with tweak_slurm_user_settings(SINGLE_USER_SUBMITTER="dummy-user"):
        await mapper.configure(SLURM_USER_SETTINGS)
        username = await mapper.find_username("does.not@matter.com")
    assert username == "dummy-user"


async def test_find_username__fails_mapper_is_not_configured(mocker, tweak_slurm_user_settings):
    """
    Test that the ``find_username()`` fails if the mapper is not configured.
    """
    mapper = single_user.SingleUserMapper()
    with pytest.raises(SingleUserError, match="No username set"):
        await mapper.find_username("dummy_user@dummy.domain.com")
