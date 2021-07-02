from armada_agent.settings import SETTINGS, ARMADA_API_HEADER
from armada_agent.utils.request import check_request_status
from armada_agent.utils.request import async_req, LOOP
from armada_agent.utils.jwt import generate_jwt_token
from armada_agent.utils.logging import logger

import hostlist
import requests
import asyncio
import json

# [nest-asyncio docs](https://pypi.org/project/nest-asyncio/)
import nest_asyncio

nest_asyncio.apply()


async def slurmrestd_header():

    x_slurm_user_token = await generate_jwt_token(test=False)

    return {
        "X-SLURM-USER-NAME": SETTINGS.X_SLURM_USER_NAME,
        "X-SLURM-USER-TOKEN": x_slurm_user_token,
    }


def armada_api_header():

    return {"Content-Type": "application/json", "Authorization": SETTINGS.API_KEY}


async def upsert_partition_and_node_records():

    partition_endpoint = "/slurm/v0.0.36/partitions"
    node_endpoint = "/slurm/v0.0.36/nodes"

    # get partition data
    response = requests.get(
        SETTINGS.BASE_SLURMRESTD_URL + partition_endpoint,
        headers=await slurmrestd_header(),
        data={},
    )

    partitions = check_request_status(response)

    # get node data
    response = requests.get(
        SETTINGS.BASE_SLURMRESTD_URL + node_endpoint,
        headers=await slurmrestd_header(),
        data={},
    )

    nodes = check_request_status(response)

    # arguments passed to async request handler
    urls = list()
    methods = list()
    params = list()
    data = list()
    header = ARMADA_API_HEADER

    for partition in partitions["partitions"]:

        # transform nodes names string into a list
        # e.g. "juju-54c58e-[67,45]" -> ["juju-54c58e-67", "juju-54c58e-45"]
        partition['nodes'] = hostlist.expand_hostlist(partition['nodes'])

        # run through nodes' list and select those that
        # belog to the partition in this case
        # For more information, see the JSON examples in /examples folder
        payload = {
            "partition": partition,
            "nodes": list(
                map(
                    lambda _node: _node,
                    filter(lambda node: node["name"] in partition["nodes"], nodes["nodes"]),
                )
            ),
        }

        urls.append(SETTINGS.BASE_API_URL + "/agent/upsert/partition")
        methods.append("POST")
        params.append(None)
        data.append(json.dumps(payload))

    future = asyncio.ensure_future(async_req(urls, methods, header, params, data), loop=LOOP)
    LOOP.run_until_complete(future)

    responses = future.result()

    # return a list containing just the responses' status, e.g. [200, 400]
    return [response.status for response in responses]


async def update_cluster_diagnostics():

    endpoint = "/slurm/v0.0.36/diag/"

    header = await slurmrestd_header()
    response = requests.get(SETTINGS.BASE_SLURMRESTD_URL + endpoint, headers=header)

    diagnostics = check_request_status(response)

    response = requests.post(
        SETTINGS.BASE_API_URL + "/agent/insert/diagnostics",
        headers=ARMADA_API_HEADER,
        data=json.dumps(diagnostics),
    )

    # return a list container the status code response, e.g. [200]
    return [response.status_code]
