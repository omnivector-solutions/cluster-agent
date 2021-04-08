from armada_agent.utils.request import check_request_status
from armada_agent.utils.request import request_exception

import json

import grequests
import requests

class SlurmrestdScraperAgent:

    def __init__(self, config) -> None:

        self.config = config

    def slurmrestd_header(self):

        return {
            "X-SLURM-USER-NAME": self.config.x_slurm_user_name,
            "X-SLURM-USER-TOKEN": self.config.x_slurm_user_token
        }
    
    def armada_api_header(self):

        return {
            "Content-Type": "application/json",
            "Authorization": self.config.api_key
        }

    def upsert_partition_and_node_records(self):

        partition_endpoint = "/slurm/v0.0.36/partitions"
        node_endpoint = "/slurm/v0.0.36/nodes"

        # get partition data
        response = requests.get(
            self.config.base_scraper_url + partition_endpoint,
            headers=self.slurmrestd_header(),
            data={}
        )

        partitions = check_request_status(response)

        # get node data
        response = requests.get(
            self.config.base_scraper_url + node_endpoint,
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
                self.config.base_api_url + "/agent/upsert/partition",
                headers=self.armada_api_header(),
                data=json.dumps(payload)
            ))

        responses = list(grequests.imap(reqs, exception_handler=request_exception))

        return responses

    def update_cluster_diagnostics(self):

        endpoint = "/slurm/v0.0.36/diag/"

        response = requests.get(
            self.config.base_scraper_url + endpoint,
            headers=self.slurmrestd_header(),
            data={}
        )

        diagnostics = check_request_status(response)

        payload = {
            "diagnostics": diagnostics
        }

        response = requests.post(
            self.config.base_api_url + "/agent/insert/diagnostics",
            headers=self.armada_api_header(),
            data=json.dumps(payload)
        )

        return response
