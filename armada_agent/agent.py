from armada_agent.utils.request import check_request_status

import json

import requests

class ScraperAgent:

    def __init__(self, config) -> None:

        self.config = config

    def hpc_header(self):

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
            headers=self.hpc_header(),
            data={}
        )

        partitions = check_request_status(response)

        # get node data
        response = requests.get(
            self.config.base_scraper_url + node_endpoint,
            headers=self.hpc_header(),
            data={}
        )

        nodes = check_request_status(response)

        responses = list()

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

            # send data to api
            response = requests.post(
                self.config.base_api_url + "/agent/upsert/partition",
                headers=self.armada_api_header(),
                data=json.dumps(payload)
            )

            responses.append(response)

        return responses

    def update_cluster_diagnostics(self):

        endpoint = "/slurm/v0.0.36/diag/"

        response = requests.get(
            self.config.base_scraper_url + endpoint,
            headers=self.hpc_header(),
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
