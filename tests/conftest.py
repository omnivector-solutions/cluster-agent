import random
import string
from unittest import mock

import httpx
import respx
import pytest

from cluster_agent.settings import SETTINGS


@pytest.fixture
def random_word():
    """
    Fixture to provide a helper method to return a
    random string containing a fixed number of chars
    """

    def _helper(length: int = 30):
        """
        Args:
            length (int): String's  final length
        """
        letters = string.ascii_lowercase
        return "".join(random.choice(letters) for i in range(length))

    return _helper


@pytest.fixture(autouse=True)
def mock_cluster_api_cache_dir(tmp_path):
    _cache_dir = tmp_path / ".cache/cluster-agent/cluster-api"
    with mock.patch("cluster_agent.identity.cluster_api.CACHE_DIR", new=_cache_dir):
        yield _cache_dir


@pytest.fixture(autouse=True)
def mock_slurmrestd_api_cache_dir(tmp_path):
    _cache_dir = tmp_path / ".cache/cluster-agent/slurmrestd"
    with mock.patch("cluster_agent.identity.slurmrestd.CACHE_DIR", new=_cache_dir):
        yield _cache_dir


@pytest.fixture
def respx_mock():
    """
    Run a test in the respx context (similar to respx decorator, but it's a fixture).

    Mocks the auth0 route used to secure a token.
    """
    with respx.mock as mock:
        respx.post(f"https://{SETTINGS.AUTH0_DOMAIN}/oauth/token").mock(
            return_value=httpx.Response(status_code=200, json=dict(access_token="dummy-token"))
        )
        yield mock
