from armada_agent.utils.request import check_request_status
from armada_agent.utils.request import request_exception
from armada_agent.utils.jwt import generate_jwt_token

import json

import grequests
import requests

class SlurmrestdScraperAgent:

    def __init__(self, config) -> None:

        self.config = config

    def slurmrestd_header(self):

        x_slurm_user_token = generate_jwt_token()

        return {
            "X-SLURM-USER-NAME": self.config.ARMADA_AGENT_X_SLURM_USER_NAME,
            "X-SLURM-USER-TOKEN": x_slurm_user_token
        }
    
    def armada_api_header(self):

        return {
            "Content-Type": "application/json",
            "Authorization": self.config.ARMADA_AGENT_API_KEY
        }

    def upsert_partition_and_node_records(self):

        partition_endpoint = "/slurm/v0.0.36/partitions"
        node_endpoint = "/slurm/v0.0.36/nodes"

        # get partition data
        response = requests.get(
            self.config.ARMADA_AGENT_BASE_SLURMRESTD_URL + partition_endpoint,
            headers=self.slurmrestd_header(),
            data={}
        )

        partitions = check_request_status(response)

        # get node data
        response = requests.get(
            self.config.ARMADA_AGENT_BASE_SLURMRESTD_URL + node_endpoint,
            headers=self.slurmrestd_header(),
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
                self.config.ARMADA_AGENT_BASE_API_URL + "/agent/upsert/partition",
                headers=self.armada_api_header(),
                data=json.dumps(payload)
            ))

        responses = list(grequests.imap(reqs, exception_handler=request_exception))

        return responses

    def update_cluster_diagnostics(self):

        endpoint = "/slurm/v0.0.36/diag/"

        response = requests.get(
            self.config.ARMADA_AGENT_BASE_SLURMRESTD_URL + endpoint,
            headers=self.slurmrestd_header(),
            data={}
        )

        diagnostics = check_request_status(response)

        response = requests.post(
            self.config.ARMADA_AGENT_BASE_API_URL + "/agent/insert/diagnostics",
            headers=self.armada_api_header(),
            data=json.dumps(diagnostics)
        )

        return response
