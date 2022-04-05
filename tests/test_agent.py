"""
placeholder for future tests
"""
from unittest import mock

import asynctest
import pytest
from hostlist import expand_hostlist

from cluster_agent.agent import (
    update_diagnostics,
    upsert_partitions,
    upsert_nodes,
    upsert_jobs,
)
from cluster_agent.settings import SETTINGS
from cluster_agent.utils.exception import SlurmrestdError


@pytest.mark.parametrize(
    "nodes_names_string",
    [
        ("ip-172-31-81-142,ip-172-25-81-172"),
        ("juju-54c58e-[48,49,50],ip-172-25-81-172,ip-172-25-81-[172,183,183]"),
        ("juju-54c58e-[48,49,50]"),
        (""),
    ],
)
@mock.patch("cluster_agent.agent.asyncio")
@mock.patch("cluster_agent.agent.cluster_api_client")
@mock.patch("cluster_agent.agent.slurmrestd_client")
@pytest.mark.asyncio
async def test_upsert_partitions(
    mock_slurmrestd_client,
    mock_cluster_api_client,
    mock_asyncio,
    random_word,
    nodes_names_string,
):
    """
    Verify whether the partitions are upserted correctly. Also, checks if the
    function returns a list of integers.
    """

    partition_name = random_word()
    mock_response_body = {
        "meta": dict(),
        "errors": list(),
        "partitions": [{"nodes": nodes_names_string, "name": partition_name}],
    }

    mock_slurmrestd_client.get = asynctest.CoroutineMock()
    mock_slurmrestd_client.get.return_value.json.return_value = mock_response_body
    mock_slurmrestd_client.get.return_value.status_code = 200
    mock_slurmrestd_client.get.return_value.url = (
        SETTINGS.BASE_SLURMRESTD_URL + "/slurm/v0.0.36/partitions"
    )
    mock_slurmrestd_client.get.return_value.text = "no error"

    mock_response_status = mock.Mock()
    mock_response_status.status_code = 200

    mock_asyncio.gather = asynctest.CoroutineMock()
    mock_asyncio.gather.return_value = [mock_response_status]

    mock_cluster_api_client.put = asynctest.CoroutineMock()

    test_response = await upsert_partitions()

    assert mock_cluster_api_client.put.mock_calls == [
        mock.call(
            f"/cluster/agent/partitions/{partition_name}",
            json=dict(
                meta=dict(),
                errors=list(),
                partition=dict(
                    nodes=expand_hostlist(nodes_names_string), name=partition_name
                ),
            ),
        )
    ]
    mock_slurmrestd_client.get.assert_awaited_with("/slurm/v0.0.36/partitions")
    mock_asyncio.gather.assert_awaited_once()
    assert test_response == [200]


@mock.patch("cluster_agent.agent.asyncio")
@mock.patch("cluster_agent.agent.cluster_api_client")
@mock.patch("cluster_agent.agent.slurmrestd_client")
@pytest.mark.parametrize("response_status_code", [400, 500])
@pytest.mark.asyncio
async def test_upsert_partitions__raise_error_in_case_slurmrestd_returns_4xx_or_5xx(
    mock_slurmrestd_client, mock_cluster_api_client, mock_asyncio, response_status_code
):
    """
    Verify if an error is raised in case the slurmrestd request fails
    """

    error_message = "dummy error message"
    url = SETTINGS.BASE_SLURMRESTD_URL + "/slurm/v0.0.36/partitions"

    mock_slurmrestd_client.get = asynctest.CoroutineMock()
    mock_slurmrestd_client.get.return_value.status_code = response_status_code
    mock_slurmrestd_client.get.return_value.url = url
    mock_slurmrestd_client.get.return_value.text = error_message

    mock_response_status = mock.Mock()
    mock_response_status.status_code = 200

    mock_asyncio.gather = asynctest.CoroutineMock()
    mock_asyncio.gather.return_value = [mock_response_status]

    mock_cluster_api_client.put = asynctest.CoroutineMock()

    with pytest.raises(SlurmrestdError) as e:
        await upsert_partitions()

    assert (
        str(e.value)
        == f"Slurmrestd returned {response_status_code} when calling {url}: {error_message}"
    )


@mock.patch("cluster_agent.agent.asyncio")
@mock.patch("cluster_agent.agent.cluster_api_client")
@mock.patch("cluster_agent.agent.slurmrestd_client")
@pytest.mark.asyncio
async def test_upsert_nodes(
    mock_slurmrestd_client,
    mock_cluster_api_client,
    mock_asyncio,
    random_word,
):
    """
    Verify whether nodes are upserted correctly. Also, check is the
    function returns a list of integers
    """

    node_name = random_word()
    mock_response_body = {
        "meta": dict(),
        "errors": list(),
        "nodes": [{"node": dict(), "name": node_name}],
    }

    mock_slurmrestd_client.get = asynctest.CoroutineMock()
    mock_slurmrestd_client.get.return_value.json.return_value = mock_response_body
    mock_slurmrestd_client.get.return_value.status_code = 200
    mock_slurmrestd_client.get.return_value.url = (
        SETTINGS.BASE_SLURMRESTD_URL + "/slurm/v0.0.36/nodes"
    )
    mock_slurmrestd_client.get.return_value.text = "no error"

    mock_response_status = mock.Mock()
    mock_response_status.status_code = 200

    mock_asyncio.gather = asynctest.CoroutineMock()
    mock_asyncio.gather.return_value = [mock_response_status]

    mock_cluster_api_client.put = asynctest.CoroutineMock()

    test_response = await upsert_nodes()

    assert mock_cluster_api_client.put.mock_calls == [
        mock.call(
            f"/cluster/agent/nodes/{node_name}",
            json=dict(
                meta=dict(),
                errors=list(),
                node=dict(node=dict(), name=node_name),
            ),
        )
    ]
    mock_slurmrestd_client.get.assert_awaited_with("/slurm/v0.0.36/nodes")
    mock_asyncio.gather.assert_awaited_once()
    assert test_response == [200]


@mock.patch("cluster_agent.agent.asyncio")
@mock.patch("cluster_agent.agent.cluster_api_client")
@mock.patch("cluster_agent.agent.slurmrestd_client")
@pytest.mark.parametrize("response_status_code", [400, 500])
@pytest.mark.asyncio
async def test_upsert_nodes__raise_error_in_case_slurmrestd_returns_4xx_or_5xx(
    mock_slurmrestd_client, mock_cluster_api_client, mock_asyncio, response_status_code
):
    """
    Verify if an error is raised in case the slurmrestd request fails
    """

    error_message = "dummy error message"
    url = SETTINGS.BASE_SLURMRESTD_URL + "/slurm/v0.0.36/nodes"

    mock_slurmrestd_client.get = asynctest.CoroutineMock()
    mock_slurmrestd_client.get.return_value.status_code = response_status_code
    mock_slurmrestd_client.get.return_value.url = url
    mock_slurmrestd_client.get.return_value.text = error_message

    mock_response_status = mock.Mock()
    mock_response_status.status_code = 200

    mock_asyncio.gather = asynctest.CoroutineMock()
    mock_asyncio.gather.return_value = [mock_response_status]

    mock_cluster_api_client.put = asynctest.CoroutineMock()

    with pytest.raises(SlurmrestdError) as e:
        await upsert_nodes()

    assert (
        str(e.value)
        == f"Slurmrestd returned {response_status_code} when calling {url}: {error_message}"
    )


@mock.patch("cluster_agent.agent.cluster_api_client")
@mock.patch("cluster_agent.agent.slurmrestd_client")
@pytest.mark.asyncio
async def test_update_diagnostics(
    mock_slurmrestd_client,
    mock_cluster_api_client,
):
    """
    Verify whether diagnostics are upserted correctly. Also, checks if the
    return value is a integer matching the response code from Cluster API call
    """

    mock_diagnostics_response_body = dict(
        meta=dict(), errors=dict(), statistics=dict(parts_packed=1)
    )

    mock_slurmrestd_client.get = asynctest.CoroutineMock()
    mock_slurmrestd_client.get.return_value.json.return_value = (
        mock_diagnostics_response_body
    )
    mock_slurmrestd_client.get.return_value.status_code = 200
    mock_slurmrestd_client.get.return_value.url = (
        SETTINGS.BASE_SLURMRESTD_URL + "/slurm/v0.0.36/diag/"
    )
    mock_slurmrestd_client.get.return_value.text = "no error"

    mock_cluster_api_client.post = asynctest.CoroutineMock()
    mock_cluster_api_client.post.return_value.status_code = 200

    test_response = await update_diagnostics()

    mock_cluster_api_client.post.assert_awaited_once_with(
        "/cluster/agent/diagnostics", json=mock_diagnostics_response_body
    )
    mock_slurmrestd_client.get.assert_awaited_once_with("/slurm/v0.0.36/diag/")

    assert test_response == 200


@mock.patch("cluster_agent.agent.asyncio")
@mock.patch("cluster_agent.agent.cluster_api_client")
@mock.patch("cluster_agent.agent.slurmrestd_client")
@pytest.mark.parametrize("response_status_code", [400, 500])
@pytest.mark.asyncio
async def test_update_diagnostics__raise_error_in_case_slurmrestd_returns_4xx_or_5xx(
    mock_slurmrestd_client, mock_cluster_api_client, mock_asyncio, response_status_code
):
    """
    Verify if an error is raised in case the slurmrestd request fails
    """

    error_message = "dummy error message"
    url = SETTINGS.BASE_SLURMRESTD_URL + "/slurm/v0.0.36/diag/"

    mock_slurmrestd_client.get = asynctest.CoroutineMock()
    mock_slurmrestd_client.get.return_value.status_code = response_status_code
    mock_slurmrestd_client.get.return_value.url = url
    mock_slurmrestd_client.get.return_value.text = error_message

    mock_response_status = mock.Mock()
    mock_response_status.status_code = 200

    mock_asyncio.gather = asynctest.CoroutineMock()
    mock_asyncio.gather.return_value = [mock_response_status]

    mock_cluster_api_client.put = asynctest.CoroutineMock()

    with pytest.raises(SlurmrestdError) as e:
        await update_diagnostics()

    assert (
        str(e.value)
        == f"Slurmrestd returned {response_status_code} when calling {url}: {error_message}"
    )


@mock.patch("cluster_agent.agent.asyncio")
@mock.patch("cluster_agent.agent.cluster_api_client")
@mock.patch("cluster_agent.agent.slurmrestd_client")
@pytest.mark.asyncio
async def test_upsert_jobs(
    mock_slurmrestd_client, mock_cluster_api_client, mock_asyncio
):
    """
    Verify whether nodes are upserted correctly. Also, check is the
    function returns a list of integers
    """

    job_id = 123456
    mock_response_body = {
        "meta": dict(),
        "errors": list(),
        "jobs": [{"job_id": job_id}],
    }

    mock_slurmrestd_client.get = asynctest.CoroutineMock()
    mock_slurmrestd_client.get.return_value.json.return_value = mock_response_body
    mock_slurmrestd_client.get.return_value.status_code = 200
    mock_slurmrestd_client.get.return_value.url = (
        SETTINGS.BASE_SLURMRESTD_URL + "/slurm/v0.0.36/jobs"
    )
    mock_slurmrestd_client.get.return_value.text = "no error"

    mock_response_status = mock.Mock()
    mock_response_status.status_code = 200

    mock_asyncio.gather = asynctest.CoroutineMock()
    mock_asyncio.gather.return_value = [mock_response_status]

    mock_cluster_api_client.put = asynctest.CoroutineMock()

    test_response = await upsert_jobs()

    assert mock_cluster_api_client.put.mock_calls == [
        mock.call(
            f"/cluster/agent/jobs/{job_id}",
            json=dict(
                meta=dict(),
                errors=list(),
                job=dict(job_id=job_id),
            ),
        )
    ]
    mock_slurmrestd_client.get.assert_awaited_with("/slurm/v0.0.36/jobs")
    mock_asyncio.gather.assert_awaited_once()
    assert test_response == [200]


@mock.patch("cluster_agent.agent.asyncio")
@mock.patch("cluster_agent.agent.cluster_api_client")
@mock.patch("cluster_agent.agent.slurmrestd_client")
@pytest.mark.parametrize("response_status_code", [400, 500])
@pytest.mark.asyncio
async def test_upsert_jobs__raise_error_in_case_slurmrestd_returns_4xx_or_5xx(
    mock_slurmrestd_client, mock_cluster_api_client, mock_asyncio, response_status_code
):
    """
    Verify if an error is raised in case the slurmrestd request fails
    """

    error_message = "dummy error message"
    url = SETTINGS.BASE_SLURMRESTD_URL + "/slurm/v0.0.36/jobs"

    mock_slurmrestd_client.get = asynctest.CoroutineMock()
    mock_slurmrestd_client.get.return_value.status_code = response_status_code
    mock_slurmrestd_client.get.return_value.url = url
    mock_slurmrestd_client.get.return_value.text = error_message

    mock_response_status = mock.Mock()
    mock_response_status.status_code = 200

    mock_asyncio.gather = asynctest.CoroutineMock()
    mock_asyncio.gather.return_value = [mock_response_status]

    mock_cluster_api_client.put = asynctest.CoroutineMock()

    with pytest.raises(SlurmrestdError) as e:
        await upsert_jobs()

    assert (
        str(e.value)
        == f"Slurmrestd returned {response_status_code} when calling {url}: {error_message}"
    )
