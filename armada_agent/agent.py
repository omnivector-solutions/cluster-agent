from armada_agent.config import Config

from pprint import pprint
import json

import requests

class ScraperAgent:

    def __init__(self, stage="dev") -> None:

        self.config = Config(stage)

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

        if response.status_code == 401:

            raise requests.HTTPError("Authentication failed.")

        elif response.status_code == 200:

            partitions = response.json()

        else:

            raise requests.RequestException("Unknown error.")

        # get node data
        response = requests.get(
            self.config.base_scraper_url + node_endpoint,
            headers=self.hpc_header(),
            data={}
        )

        if response.status_code == 401:

            raise requests.HTTPError("Authentication failed.")

        elif response.status_code == 200:

            nodes = response.json()

        else:

            raise requests.RequestException("Unknown error.")

        responses = list()

        for partition in partitions["partitions"]:

            payload = {
                "partition": {
                    "name": partition["name"],
                    "status": "active"
                },
                "nodes": list(map(
                    lambda _node: {
                        "name": _node["name"],
                        "status": _node["state"]
                    },
                    filter(
                        lambda node: node["name"] in partition["nodes"],
                        nodes["nodes"]
                    )
                ))
            }

            # send data to api
            response = requests.post(
                self.config.base_api_url + "/partition/upsert",
                headers=self.armada_api_header(),
                data=json.dumps(payload)
            )

            responses.append(response)

        return responses

    def upsert_partition_record(self):

        endpoint = "/slurm/v0.0.36/partitions/"

        response = requests.get(
            self.config.base_scraper_url + endpoint,
            headers=self.hpc_header(),
            data={}
        )

        if response.status_code == 401:

            raise requests.HTTPError("Authentication failed.")

        elif response.status_code == 200:

            partitions = response.json()

        else:

            raise requests.RequestException("Unknown error.")

        if isinstance(partitions.get("partitions"), dict):

            payload = {
                "partitionInfo": next(iter(partitions.get("partitions").values()))
            }

            response = requests.put(
                self.config.base_api_url + "/partition",
                headers=self.armada_api_header(),
                data=json.dumps(payload)
            )
        
        elif isinstance(partitions.get("partitions"), list):

            for partition in partitions.get("partitions"):

                payload = {
                    "partitionInfo": [partition]
                }

                response = requests.put(
                    self.config.base_api_url + "/partition",
                    headers=self.armada_api_header(),
                    data=json.dumps(payload)
                )

    def upsert_node_record(self):

        endpoint = "/slurm/v0.0.36/nodes"

        response = requests.get(
            self.config.base_scraper_url + endpoint,
            headers=self.hpc_header(),
            data={}
        )

        if response.status_code == 401:

            raise requests.HTTPError("Authentication failed.")

        elif response.status_code == 200:

            nodes = response.json()

        else:

            raise requests.RequestException("Unknown error.")

        for node in nodes["nodes"]:

            response = requests.post(
                self.config.base_api_url + "/node/upsert",
                headers=self.armada_api_header(),
                data=json.dumps({
                    "name": node["name"],
                    "status": node["state"]
                })
            )

    def update_cluster_diagnostics(self, table_name):

        endpoint = "/slurm/v0.0.35/diag/"

        response = requests.get(
            self.config.base_scraper_url + endpoint,
            headers=self.hpc_header(),
            data={}
        )

        if response.status_code == 401:

            raise requests.HTTPError("Authentication failed.")

        elif response.status_code == 200:

            payload = {
                "diagnostics": [response.json()]
            }

        else:

            raise requests.RequestException("Unknown error.")

        pass

        response = requests.put(
            self.config.base_api_url + "/diag",
            headers=self.armada_api_header(),
            data=json.dumps(payload),
            params={
                "tableName": table_name
            }
        )

    def upsert_cluster_record(self):

        pass


if __name__ == "__main__":

    agent = ScraperAgent()

    pprint(agent.upsert_partition_and_node_records())