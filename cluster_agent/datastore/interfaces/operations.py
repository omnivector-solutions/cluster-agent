import inspect
import time
from string import Template
from textwrap import dedent

from elasticsearch_dsl import connections, Document
from elasticsearch.exceptions import RequestError

from cluster_agent.datastore import BaseDataStoreOps
from cluster_agent.datastore.interfaces.elk import documents
from cluster_agent.datastore.interfaces.elk.settings import ELASTICSEARCH_SETTINGS
from cluster_agent.identity.cluster_api import sync_backend_client as cluster_api_client
from cluster_agent.identity.slurmrestd import sync_backend_client as slurmrestd_client
from cluster_agent.settings import SETTINGS
from cluster_agent.utils.exception import SlurmrestdError, ClusterAPIError
from cluster_agent.utils.logging import logger


class ElkOps(BaseDataStoreOps):
    """
    Base Elasticsearch operations class.
    """

    def __init__(self) -> None:
        super().__init__(settings=ELASTICSEARCH_SETTINGS, database_type="Elasticsearch")


    def _create_all_elasticsearch_indexes(self):
        """
        Create all needed indexes, e.g. jobs, diagnostics, partitions and nodes.
        """

        for class_name, obj in inspect.getmembers(documents, inspect.isclass):
            if issubclass(obj, Document) and obj is not Document:
                try:
                    obj._index.create()
                except RequestError as e:
                    logger.info("Exception: {}".format(str(e)))


    def _connect(self):
        connections.create_connection(**ELASTICSEARCH_SETTINGS.ELASTICSEARCH_CONNECTION_PROPERTIES)
        self._create_all_elasticsearch_indexes()


    def _push_jobs(self):
        """
        Pull jobs data from slurmrestd and push to elasticsearch directly
        """

        # fetch cluster ID
        query = Template('query {cluster(clientId: "$client_id"){clusterId}}').substitute(
            client_id=SETTINGS.AUTH0_CLIENT_ID
        )
        r = cluster_api_client.post(
            "/cluster/graphql/query", json=dict(query=dedent(query), variables=dict())
        )
        ClusterAPIError.require_condition(
            r.status_code == 200,
            f"Cluster API returned {r.status_code} when calling {r.url}: {r.text}",
        )

        with ClusterAPIError.handle_errors(
            f"No cluster matches client_id={SETTINGS.AUTH0_CLIENT_ID}",
            raise_exc_class=ClusterAPIError,
        ):
            cluster_id = r.json().get("data").get("cluster")[0].get("clusterId")

        assert cluster_id is not None

        # fetch jobs data
        r = slurmrestd_client.get("/slurm/v0.0.36/jobs")
        SlurmrestdError.require_condition(
            r.status_code == 200,
            f"Slurmrestd returned {r.status_code} when calling {r.url}: {r.text}",
        )
        jobs = r.json()

        for job in jobs["jobs"]:

            documents.Jobs(
                _id="{cluster_id}-{job_id}".format(cluster_id=cluster_id, job_id=job.get("job_id")),
                timestamp=time.time(),
                cluster_id=cluster_id,
                **job,
            ).save(refresh=True)

        if len(jobs["jobs"]) == 0:
            logger.debug("**** No job from slurmrestd to push to Elasticsearch")
        else:
            logger.debug("**** Pushed all available jobs to Elasticsearch")


    def _push(self):
        logger.debug("**** Pushing jobs to Elasticsearch")
        self._push_jobs()
