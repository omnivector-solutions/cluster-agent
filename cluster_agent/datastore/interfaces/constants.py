from pydantic import BaseModel


class BaseSettingsClass(BaseModel):

    is_configured = False

    class Config:

        env_file = ".env"
        env_prefix = "CLUSTER_AGENT_"