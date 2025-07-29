from typing import Dict, Any
from pydantic import BaseModel


class PropertySettingsOutput(BaseModel):
    default: Any
    title: str
    type: str
    extra: Dict[str, Any] | None = None


class PluginSchemaSettings(BaseModel):
    title: str
    type: str
    properties: Dict[str, PropertySettingsOutput]


class PluginSettingsOutput(BaseModel):
    name: str
    value: Dict[str, Any]
    scheme: PluginSchemaSettings | None = None
