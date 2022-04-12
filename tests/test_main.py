import pytest
from unittest import mock

from cluster_agent.main import (
    collect_jobs,
    collect_diagnostics,
    collect_nodes,
    collect_partitions,
    main,
    run_agent,
)


@mock.patch("cluster_agent.agent.update_diagnostics")
@pytest.mark.asyncio
async def test_main__checks_if_main_file_calls_diagnostics_collection(
    mock_agent_update_diagnostics,
):
    """Checks whether the main program calls or not the function to collect cluster diagnostics"""

    mock_agent_update_diagnostics.return_value = 200

    await collect_diagnostics()

    mock_agent_update_diagnostics.assert_awaited_once()


@mock.patch("cluster_agent.agent.upsert_partitions")
@pytest.mark.asyncio
async def test_main__checks_if_main_file_calls_partitions_collection(
    mock_agent_upsert_partitions,
):
    """Checks whether the main program calls or not the function to collect cluster partitions"""

    mock_agent_upsert_partitions.return_value = [200]

    await collect_partitions()

    mock_agent_upsert_partitions.assert_awaited_once()


@mock.patch("cluster_agent.agent.upsert_nodes")
@pytest.mark.asyncio
async def test_main__checks_if_main_file_calls_nodes_collection(
    mock_agent_upsert_nodes,
):
    """Checks whether the main program calls or not the function to collect cluster nodes"""

    mock_agent_upsert_nodes.return_value = [200]

    await collect_nodes()

    mock_agent_upsert_nodes.assert_awaited_once()


@mock.patch("cluster_agent.agent.upsert_jobs")
@pytest.mark.asyncio
async def test_main__checks_if_main_file_calls_jobs_collection(
    mock_agent_upsert_jobs,
):
    """Checks whether the main program calls or not the function to collect slurm jobs"""

    mock_agent_upsert_jobs.return_value = [200]

    await collect_jobs()

    mock_agent_upsert_jobs.assert_awaited_once()


# @mock.patch("cluster_agent.main.collect_diagnostics")
# @mock.patch("cluster_agent.main.collect_jobs")
# @mock.patch("cluster_agent.main.collect_nodes")
# @mock.patch("cluster_agent.main.collect_partitions")
@mock.patch("cluster_agent.main.submit_jobs")
@mock.patch("cluster_agent.main.finish_jobs")
@pytest.mark.asyncio
async def test_main__call_secondary_functions_to_collect_data(*operations):
    """Ensures there is an async function to call all the functions that collect data"""

    # The name of the functions are used for logging. Mocks have no names, so fake it.
    for op in operations:
        op.__name__ = "whatever"

    with mock.patch("cluster_agent.main.logger"):
        await run_agent()

    for op in operations:
        op.assert_awaited_once()


@mock.patch("cluster_agent.main.asyncio")
def test_main__checks_if_agent_coroutine_is_run(mock_asyncio):
    """Checks whether the corountine that runs all data collection functions is called or not"""

    mock_asyncio.run = mock.Mock()

    main()

    mock_asyncio.run.assert_called_once()
