from armada_agent.utils.request import check_request_status
from armada_agent.utils.request import async_req, LOOP
from armada_agent.utils.jwt import generate_jwt_token
from armada_agent.utils.logging import logger
from armada_agent.settings import SETTINGS

import requests
import asyncio
import json

# [nest-asyncio docs](https://pypi.org/project/nest-asyncio/)
import nest_asyncio
nest_asyncio.apply()



async def slurmrestd_header():

    x_slurm_user_token = await generate_jwt_token(test=False)

    return {
        "X-SLURM-USER-NAME": SETTINGS.ARMADA_AGENT_X_SLURM_USER_NAME,
        "X-SLURM-USER-TOKEN": x_slurm_user_token
    }

def armada_api_header():

    return {
        "Content-Type": "application/json",
        "Authorization": SETTINGS.ARMADA_AGENT_API_KEY
    }

async def upsert_partition_and_node_records():

    partition_endpoint = "/slurm/v0.0.36/partitions"
    node_endpoint = "/slurm/v0.0.36/nodes"

    # get partition data
    response = requests.get(
        SETTINGS.ARMADA_AGENT_BASE_SLURMRESTD_URL + partition_endpoint,
        headers=await slurmrestd_header(),
        data={}
    )

    partitions = check_request_status(response)

    # get node data
    response = requests.get(
        SETTINGS.ARMADA_AGENT_BASE_SLURMRESTD_URL + node_endpoint,
        headers=await slurmrestd_header(),
        data={}
    )

    nodes = check_request_status(response)

    # arguments passed to async request handler
    urls = list()
    methods = list()
    params = list()
    data = list()
    header = armada_api_header()

    for partition in partitions["partitions"]:

        payload = {
            "partition": partition,
            "nodes": list(map(
                lambda _node: _node,
                filter(
                    lambda node: node["name"] in partition["nodes"],
                    nodes["nodes"]
                )
            ))
        }

        urls.append(SETTINGS.ARMADA_AGENT_BASE_API_URL +
                    "/agent/upsert/partition")
        methods.append("POST")
        params.append(None)
        data.append(json.dumps(payload))

    future = asyncio.ensure_future(
        async_req(urls, methods, header, params, data), loop=LOOP)
    LOOP.run_until_complete(future)

    responses = future.result()

    # return a list containing just the responses' status, e.g. [200, 400]
    return list(map(lambda response: response.status, responses))


async def update_cluster_diagnostics():

    endpoint = "/slurm/v0.0.36/diag/"

    header = await slurmrestd_header()

    logger.info("##### {}".format(header))
    response = requests.get(
        SETTINGS.ARMADA_AGENT_BASE_SLURMRESTD_URL + endpoint,
        headers=header
    )

    diagnostics = check_request_status(response)

    response = requests.post(
        SETTINGS.ARMADA_AGENT_BASE_API_URL + "/agent/insert/diagnostics",
        headers=armada_api_header(),
        data=json.dumps(diagnostics)
    )

    # return a list container the status code response, e.g. [200]
    return [response.status_code]
