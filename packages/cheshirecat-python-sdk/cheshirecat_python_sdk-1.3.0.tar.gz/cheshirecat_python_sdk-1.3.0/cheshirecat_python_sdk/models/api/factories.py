from typing import Dict, List, Any
from pydantic import BaseModel


class FactoryObjectSettingOutput(BaseModel):
    name: str
    value: Dict[str, Any]
    scheme: Dict[str, Any] | None = None


class FactoryObjectSettingsOutput(BaseModel):
    settings: List[FactoryObjectSettingOutput]
    selected_configuration: str
