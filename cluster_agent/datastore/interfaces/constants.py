from pydantic import BaseSettings


class BaseSettingsClass(BaseSettings):

    is_configured = False

    class Config:

        env_file = ".env"
        env_prefix = "CLUSTER_AGENT_"
