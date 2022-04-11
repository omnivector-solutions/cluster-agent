from pydantic import BaseModel


class BaseSettingsClass(BaseModel):

    is_configured = False
