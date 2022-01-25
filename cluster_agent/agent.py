import asyncio

from cluster_agent.identity.cluster_api import backend_client as cluster_api_client
from cluster_agent.identity.slurmrestd import backend_client as slurmrestd_client

import hostlist


async def upsert_partitions():

    r = await slurmrestd_client.get("/slurm/v0.0.36/partitions")
    partitions = r.json()

    tasks = list()

    for partition in partitions["partitions"]:

        # transform nodes names string into a list
        # e.g. "juju-54c58e-[67,45]" -> ["juju-54c58e-67", "juju-54c58e-45"]
        partition["nodes"] = hostlist.expand_hostlist(partition["nodes"])

        payload = {
            "meta": partitions["meta"],
            "errors": partitions["errors"],
            "partition": partition,
        }

        tasks.append(
            cluster_api_client.put(
                f"/cluster/agent/partitions/{partition['name']}",
                json=payload,
            )
        )

    responses = await asyncio.gather(*tasks)

    # return a list containing just the responses' status, e.g. [200, 400]
    return [response.status_code for response in responses]


async def upsert_nodes():

    r = await slurmrestd_client.get("/slurm/v0.0.36/nodes")
    nodes = r.json()

    tasks = list()

    for node in nodes["nodes"]:

        payload = {
            "meta": nodes["meta"],
            "errors": nodes["errors"],
            "node": node,
        }

        tasks.append(
            cluster_api_client.put(
                f"/cluster/agent/nodes/{node['name']}",
                json=payload,
            )
        )

    responses = await asyncio.gather(*tasks)

    # return a list containing just the responses' status, e.g. [200, 400]
    return [response.status_code for response in responses]


async def update_diagnostics():

    r = await slurmrestd_client.get("/slurm/v0.0.36/diag/")
    diagnostics = r.json()

    response = await cluster_api_client.post("/cluster/agent/diagnostics", json=diagnostics)

    return response.status_code


async def upsert_jobs():

    r = await slurmrestd_client.get("/slurm/v0.0.36/jobs")
    jobs = r.json()

    tasks = list()

    for job in jobs["jobs"]:

        payload = {
            "meta": jobs["meta"],
            "errors": jobs["errors"],
            "job": job,
        }

        tasks.append(
            cluster_api_client.put(
                f"/cluster/agent/jobs/{job['job_id']}",
                json=payload,
            )
        )

    responses = await asyncio.gather(*tasks)

    # return a list container the status code response, e.g. [200]
    return [response.status_code for response in responses]
