import sys
from functools import lru_cache
from typing import Any, Dict, List, Optional
from typing_extensions import TypedDict

from pydantic import Field, root_validator
from pydantic.error_wrappers import ValidationError

from cluster_agent.datastore.interfaces.constants import BaseSettingsClass
from cluster_agent.utils.logging import logger


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
    ELASTICSEARCH_VERIFY_CERTS: bool = False
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

    class Config:

        env_file = ".env"
        env_prefix = "CLUSTER_AGENT_"


@lru_cache()
def init_settings() -> ElasticsearchSettings:
    try:
        return ElasticsearchSettings()
    except ValidationError as e:
        logger.error(e)
        sys.exit(1)


ELASTICSEARCH_SETTINGS = init_settings()
