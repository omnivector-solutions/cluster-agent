from subprocess import call
from unittest import mock
import nest_asyncio
import pytest

from armada_agent.agent import update_cluster_diagnostics, upsert_partition_and_node_records
from armada_agent.settings import SETTINGS

nest_asyncio.apply()


@mock.patch("armada_agent.agent.generate_jwt_token")
@mock.patch("armada_agent.agent.requests")
@pytest.mark.asyncio
async def test_update_cluster_diagnostics(
    requests_mock,
    generate_jwt_token_mock
):
    header = {
        "X-SLURM-USER-NAME": SETTINGS.ARMADA_AGENT_X_SLURM_USER_NAME,
        "X-SLURM-USER-TOKEN": "test_token"
    }
    generate_jwt_token_mock.return_value = "test_token"
    response_mock = mock.Mock()

    response_mock.status_code = 200
    response_mock.json.return_value = {}
    requests_mock.get.return_value = response_mock
    requests_mock.post.return_value = response_mock

    test_response = await update_cluster_diagnostics()

    requests_mock.get.assert_called_once_with(
        SETTINGS.ARMADA_AGENT_BASE_SLURMRESTD_URL + "/slurm/v0.0.36/diag/",
        headers=header,
    )

    requests_mock.post.assert_called_once_with(
        SETTINGS.ARMADA_AGENT_BASE_API_URL + "/agent/insert/diagnostics",
        headers={
            "Content-Type": "application/json",
            "Authorization": SETTINGS.ARMADA_AGENT_API_KEY
        },
        data="{}",
    )

    assert test_response == [200], ""

@mock.patch("armada_agent.agent.check_request_status")
@mock.patch("armada_agent.agent.generate_jwt_token")
@mock.patch("armada_agent.agent.async_req")
@mock.patch("armada_agent.agent.requests")
@mock.patch("armada_agent.agent.asyncio")
@mock.patch("armada_agent.agent.LOOP")
@pytest.mark.asyncio
async def test_upsert_partition_and_node_records(
    loop_mock,
    asyncio_mock,
    requests_mock,
    async_req_mock,
    generate_jwt_token_mock,
    check_request_status_mock
):
    header = {
        "X-SLURM-USER-NAME": SETTINGS.ARMADA_AGENT_X_SLURM_USER_NAME,
        "X-SLURM-USER-TOKEN": "test_token"
    }
    generate_jwt_token_mock.return_value = "test_token"

    check_request_status_mock.return_value = {
        'partitions': [
            {
                'nodes': 'ip-172-31-81-142,ip-172-25-81-172'
            }
        ],
        'nodes': [
            {
                'name': 'ip-172-31-81-142'
            },
            {
                'name': 'ip-172-25-81-172'
            }
        ]
    }

    requests_mock.get.return_value = mock.Mock()

    future_result_mock = mock.Mock()
    future_result_mock.status = 200

    asyncio_mock.ensure_future.return_value.result.return_value = [
        future_result_mock
    ]

    test_response = await upsert_partition_and_node_records()

    calls = [
        mock.call(
            SETTINGS.ARMADA_AGENT_BASE_SLURMRESTD_URL + "/slurm/v0.0.36/partitions",
            headers=header,
            data={}
        ),
        mock.call(
            SETTINGS.ARMADA_AGENT_BASE_SLURMRESTD_URL + "/slurm/v0.0.36/nodes",
            headers=header,
            data={},
        )
    ]

    requests_mock.get.assert_has_calls(calls, any_order=True)

    assert test_response == [200], ""