from unittest import mock
import nest_asyncio
import pytest

from armada_agent.agent import update_cluster_diagnostics
from armada_agent.settings import SETTINGS

nest_asyncio.apply()


@mock.patch("armada_agent.agent.generate_jwt_token")
@mock.patch("armada_agent.agent.requests")
@pytest.mark.asyncio
async def test_update_cluster_diagnostics(
    requests_mock,
    generate_jwt_token_mock,
):
    header = {
        "X-SLURM-USER-NAME": SETTINGS.ARMADA_AGENT_X_SLURM_USER_NAME,
        "X-SLURM-USER-TOKEN": "test_token"
    }
    generate_jwt_token_mock.return_value = "test_token"
    response_mock = mock.Mock()

    breakpoint()

    response_mock.return_value.status_code = 200
    response_mock.json.return_value = {}
    requests_mock.get.return_value = response_mock

    await update_cluster_diagnostics()

    requests_mock.get.assert_called_once_with(
        SETTINGS.ARMADA_AGENT_BASE_SLURMRESTD_URL + "/slurm/v0.0.36/diag/",
        headers=header
    )