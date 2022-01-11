from armada_agent.settings import SETTINGS, ARMADA_API_HEADER
from armada_agent.utils.request import (
    async_req,
    general_slurmrestd_request,
)

import hostlist
import requests
import json

# [nest-asyncio docs](https://pypi.org/project/nest-asyncio/)
import nest_asyncio

nest_asyncio.apply()


def armada_api_header():

    return {"Content-Type": "application/json", "Authorization": SETTINGS.API_KEY}


async def upsert_partitions():

    partitions = await general_slurmrestd_request("/slurm/v0.0.36/partitions")

    # arguments passed to async request handler
    urls = list()
    methods = list()
    params = list()
    data = list()
    header = ARMADA_API_HEADER

    for partition in partitions["partitions"]:

        # transform nodes names string into a list
        # e.g. "juju-54c58e-[67,45]" -> ["juju-54c58e-67", "juju-54c58e-45"]
        partition["nodes"] = hostlist.expand_hostlist(partition["nodes"])

        payload = {
            "meta": partitions["meta"],
            "errors": partitions["errors"],
            "partition": partition,
        }

        urls.append(SETTINGS.BASE_API_URL + f"/agent/partitions/{partition['name']}")
        methods.append("PUT")
        params.append(None)
        data.append(json.dumps(payload))

    responses = await async_req(urls, methods, header, params, data)

    # return a list containing just the responses' status, e.g. [200, 400]
    return [response.status for response in responses]


async def upsert_nodes():

    nodes = await general_slurmrestd_request("/slurm/v0.0.36/nodes")

    # arguments passed to async request handler
    urls = list()
    methods = list()
    params = list()
    data = list()
    header = ARMADA_API_HEADER

    for node in nodes["nodes"]:

        payload = {
            "meta": nodes["meta"],
            "errors": nodes["errors"],
            "node": node,
        }

        urls.append(SETTINGS.BASE_API_URL + f"/agent/nodes/{node['name']}")
        methods.append("PUT")
        params.append(None)
        data.append(json.dumps(payload))

    responses = await async_req(urls, methods, header, params, data)

    # return a list containing just the responses' status, e.g. [200, 400]
    return [response.status for response in responses]


async def update_diagnostics():

    diagnostics = await general_slurmrestd_request("/slurm/v0.0.36/diag/")

    response = requests.post(
        SETTINGS.BASE_API_URL + "/agent/diagnostics",
        headers=ARMADA_API_HEADER,
        data=json.dumps(diagnostics),
    )

    # return a list container the status code response, e.g. [200]
    return [response.status_code]


async def upsert_jobs():

    jobs = await general_slurmrestd_request("/slurm/v0.0.36/jobs")

    # arguments passed to async request handler
    urls = list()
    methods = list()
    params = list()
    data = list()
    header = ARMADA_API_HEADER

    for job in jobs["jobs"]:

        payload = {
            "meta": jobs["meta"],
            "errors": jobs["errors"],
            "job": job,
        }

        urls.append(SETTINGS.BASE_API_URL + f"/agent/jobs/{job['job_id']}")
        methods.append("PUT")
        params.append(None)
        data.append(json.dumps(payload))

    responses = await async_req(urls, methods, header, params, data)

    # return a list container the status code response, e.g. [200]
    return [response.status for response in responses]
