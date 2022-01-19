"""
placeholder for future tests
"""
import json
from urllib.parse import urljoin
from unittest import mock

from hostlist import expand_hostlist
import pytest

from cluster_agent.agent import update_diagnostics, upsert_partitions, upsert_nodes, upsert_jobs
from cluster_agent.settings import SETTINGS, CLUSTER_API_HEADER


@pytest.mark.parametrize(
    "nodes_names_string",
    [
        ("ip-172-31-81-142,ip-172-25-81-172"),
        ("juju-54c58e-[48,49,50],ip-172-25-81-172,ip-172-25-81-[172,183,183]"),
        ("juju-54c58e-[48,49,50]"),
        (""),
    ],
)
@mock.patch("cluster_agent.agent.async_req")
@mock.patch("cluster_agent.agent.general_slurmrestd_request")
@pytest.mark.asyncio
async def test_upsert_partitions(
    general_slurmrestd_request_mock,
    async_req_mock,
    random_word,
    nodes_names_string,
):
    """
    Verify whether given a list of nodes names the app meet the requirements:

        1. Mount the input body required for the Cluster API correctly;
        2. Handle different cases of the nodes names list;
        3. Await the `async_req` coroutine with the right parameters:
            - endpoint;
            - HTTP method;
            - request header;
            - query string parameters;
            - body paylpad;
        4. The return response is a list of HTTP codes
    """

    partition_name = random_word()
    mock_response_body = {
        "meta": dict(),
        "errors": list(),
        "partitions": [{"nodes": nodes_names_string, "name": partition_name}],
    }
    request_body = {
        "meta": dict(),
        "errors": list(),
        "partition": {"nodes": expand_hostlist(nodes_names_string), "name": partition_name},
    }

    general_slurmrestd_request_mock.return_value = mock_response_body

    response_status_mock = mock.Mock()
    response_status_mock.status = 200

    async_req_mock.return_value = [response_status_mock]

    test_response = await upsert_partitions()

    async_req_mock.assert_awaited_once_with(
        [
            urljoin(
                SETTINGS.BASE_API_URL,
                "/agent/partitions/{partition_name}".format(partition_name=partition_name),
            )
        ],
        ["PUT"],
        CLUSTER_API_HEADER,
        [None],
        [json.dumps(request_body)],
    )

    assert test_response == [200]


@mock.patch("cluster_agent.agent.async_req")
@mock.patch("cluster_agent.agent.general_slurmrestd_request")
@pytest.mark.asyncio
async def test_upsert_nodes(
    general_slurmrestd_request_mock,
    async_req_mock,
    random_word,
):
    """
    Verify whether the app meet the requirements:

        1. Mount the input body required for the Cluster API correctly;
        2. Await the `async_req` coroutine with the right parameters:
            - endpoint;
            - HTTP method;
            - request header;
            - query string parameters;
            - body paylpad;
        3. The return response is a list of HTTP codes
    """

    node_name = random_word()
    mock_response_body = {
        "meta": dict(),
        "errors": list(),
        "nodes": [{"node": dict(), "name": node_name}],
    }
    request_body = {
        "meta": dict(),
        "errors": list(),
        "node": {"node": dict(), "name": node_name},
    }

    general_slurmrestd_request_mock.return_value = mock_response_body

    response_status_mock = mock.Mock()
    response_status_mock.status = 200

    async_req_mock.return_value = [response_status_mock]

    test_response = await upsert_nodes()

    async_req_mock.assert_awaited_once_with(
        [urljoin(SETTINGS.BASE_API_URL, "/agent/nodes/{node_name}".format(node_name=node_name))],
        ["PUT"],
        CLUSTER_API_HEADER,
        [None],
        [json.dumps(request_body)],
    )

    assert test_response == [200], ""


@mock.patch("cluster_agent.agent.general_slurmrestd_request")
@mock.patch("cluster_agent.agent.requests")
@pytest.mark.asyncio
async def test_update_diagnostics(
    requests_mock,
    general_slurmrestd_request_mock,
):
    """
    Verify whether when collecting diagnostics data
    from slurmrestd the app meet the requirements:

        1. The correct request is made to the Cluster API in order to send the data;
        2. The return response is a list of HTTP codes
    """

    general_slurmrestd_request_mock.return_value = dict()

    response_mock = mock.Mock()
    response_mock.status_code = 200
    response_mock.json.return_value = {}

    requests_mock.post.return_value = response_mock

    test_response = await update_diagnostics()

    requests_mock.post.assert_called_once_with(
        urljoin(SETTINGS.BASE_API_URL, "/agent/diagnostics"),
        headers=CLUSTER_API_HEADER,
        data="{}",
    )

    assert test_response == [200]


@mock.patch("cluster_agent.agent.async_req")
@mock.patch("cluster_agent.agent.general_slurmrestd_request")
@pytest.mark.asyncio
async def test_upsert_jobs(
    general_slurmrestd_request_mock,
    async_req_mock,
    random_word,
):
    """
    Verify whether the app meet the requirements:

        1. Mount the input body required for the Cluster API correctly;
        2. Await the `async_req` coroutine with the right parameters:
            - endpoint;
            - HTTP method;
            - request header;
            - query string parameters;
            - body paylpad;
        3. The return response is a list of HTTP codes
    """

    job_id = 123456
    mock_response_body = {
        "meta": dict(),
        "errors": list(),
        "jobs": [{"job_id": job_id}],
    }
    request_body = {
        "meta": dict(),
        "errors": list(),
        "job": {"job_id": job_id},
    }

    general_slurmrestd_request_mock.return_value = mock_response_body

    response_status_mock = mock.Mock()
    response_status_mock.status = 200

    async_req_mock.return_value = [response_status_mock]

    test_response = await upsert_jobs()

    async_req_mock.assert_awaited_once_with(
        [urljoin(SETTINGS.BASE_API_URL, "/agent/jobs/{job_id}".format(job_id=job_id))],
        ["PUT"],
        CLUSTER_API_HEADER,
        [None],
        [json.dumps(request_body)],
    )

    assert test_response == [200], ""
