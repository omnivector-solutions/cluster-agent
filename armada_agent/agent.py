from armada_agent.utils.request import check_request_status
from armada_agent.utils.request import request_exception
from armada_agent.utils.jwt import generate_jwt_token
from armada_agent.utils.logging import logger
from armada_agent.settings import SETTINGS

# import grequests
# import requests
import asyncio
import json

class SlurmrestdScraperAgent:

    def __init__(self) -> None:

        pass

    async def slurmrestd_header(self):

        x_slurm_user_token = await generate_jwt_token(test=False)

        return {
            "X-SLURM-USER-NAME": SETTINGS.ARMADA_AGENT_X_SLURM_USER_NAME,
            "X-SLURM-USER-TOKEN": x_slurm_user_token
        }
    
    def armada_api_header(self):

        return {
            "Content-Type": "application/json",
            "Authorization": SETTINGS.ARMADA_AGENT_API_KEY
        }

    async def upsert_partition_and_node_records(self):

        partition_endpoint = "/slurm/v0.0.36/partitions"
        node_endpoint = "/slurm/v0.0.36/nodes"

        # get partition data
        response = requests.get(
            SETTINGS.ARMADA_AGENT_BASE_SLURMRESTD_URL + partition_endpoint,
            headers=await self.slurmrestd_header(),
            data={}
        )

        partitions = check_request_status(response)

        # get node data
        response = requests.get(
            SETTINGS.ARMADA_AGENT_BASE_SLURMRESTD_URL + node_endpoint,
            headers=await self.slurmrestd_header(),
            data={}
        )

        nodes = check_request_status(response)

        # [docs for grequests](https://github.com/spyoungtech/grequests)
        reqs = list()

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

            reqs.append(grequests.post(
                SETTINGS.ARMADA_AGENT_BASE_API_URL + "/agent/upsert/partition",
                headers=self.armada_api_header(),
                data=json.dumps(payload)
            ))

        responses = list(grequests.imap(reqs, exception_handler=request_exception))

        return responses

    async def update_cluster_diagnostics(self):

        endpoint = "/slurm/v0.0.36/diag/"

        header = await self.slurmrestd_header()

        logger.info("##### {}".format(header))

        response = requests.get(
            SETTINGS.ARMADA_AGENT_BASE_SLURMRESTD_URL + endpoint,
            headers=await self.slurmrestd_header(),
            data={}
        )

        diagnostics = check_request_status(response)

        response = requests.post(
            SETTINGS.ARMADA_AGENT_BASE_API_URL + "/agent/insert/diagnostics",
            headers=self.armada_api_header(),
            data=json.dumps(diagnostics)
        )

        return response
