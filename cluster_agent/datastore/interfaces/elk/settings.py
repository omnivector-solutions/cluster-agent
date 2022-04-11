from typing import Any, Dict, List, Optional
from typing_extensions import TypedDict

from pydantic import Field, root_validator

from cluster_agent.datastore.interfaces.constants import BaseSettingsClass


class ElasticsearchConnection(TypedDict):
    hosts: List[str]
    verify_certs: bool


class ElasticsearchQuerySettings(TypedDict):
    number_of_shards: int
    number_of_replicas: int
    blocks: Dict[str, Any]


class ElasticsearchSettings(BaseSettingsClass):

    ELASTICSEARCH_CONNECTION_URL: Optional[str] = Field(
        None, description="Elasticsearch connection string"
    )
    ELASTICSEARCH_VERIFY_CERTS: bool = True
    ELASTICSEARCH_CONNECTION_PROPERTIES: Dict[str, Any] = None
    ELASTICSEARCH_QUERY_SETTINGS = ElasticsearchQuerySettings(
        number_of_shards=1, number_of_replicas=1, blocks=dict(read_only_allow_delete=None)
    )

    @root_validator
    def assemble_attrs_from_env(cls, values):

        # assemble Elasticsearch connection properties
        if values.get("ELASTICSEARCH_CONNECTION_URL"):
            values.update(
                ELASTICSEARCH_CONNECTION_PROPERTIES=ElasticsearchConnection(
                    hosts=[values.get("ELASTICSEARCH_CONNECTION_URL")],
                    verify_certs=values.get("ELASTICSEARCH_VERIFY_CERTS"),
                ),
                is_configured=True,
            )

        return values


ELASTICSEARCH_SETTINGS = ElasticsearchSettings()
