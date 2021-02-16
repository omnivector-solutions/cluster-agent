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

    def update_partition(self):

        endpoint = "/slurm/v0.0.35/partitions/"

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
                    "partitionInfo": partition
                }

                response = requests.put(
                    self.config.base_api_url + "/partition",
                    headers=self.armada_api_header(),
                    data=json.dumps(payload)
                )

    def update_node(self):

        endpoint = "/slurm/v0.0.35/nodes/"

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

        if isinstance(nodes.get("nodes"), dict):

            payload = {
                "nodeInfo": next(iter(nodes.get("nodes").values()))
            }

            response = requests.put(
                self.config.base_api_url + "/node",
                headers=self.armada_api_header(),
                data=json.dumps(payload)
            )
        
        elif isinstance(nodes.get("nodes"), list):

            for partition in nodes.get("nodes"):

                payload = {
                    "nodeInfo": partition
                }

                response = requests.put(
                    self.config.base_api_url + "/node",
                    headers=self.armada_api_header(),
                    data=json.dumps(payload)
                )

    def create_cluster_record(self):

        ## TODO:
        # check route which aggregates cluster data

        pass

    def update_cluster_record(self):

        ## TODO:
        # check whether status column must be in DynamoDB table

        pass


if __name__ == "__main__":

    agent = ScraperAgent()

    pprint(agent.update_node())