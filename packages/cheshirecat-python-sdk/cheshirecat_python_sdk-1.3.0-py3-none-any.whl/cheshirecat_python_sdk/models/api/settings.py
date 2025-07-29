from typing import Dict, List, Any
from pydantic import BaseModel


class SettingDeleteOutput(BaseModel):
    deleted: bool


class SettingOutput(BaseModel):
    name: str
    value: Dict[str, Any]
    category: str
    setting_id: str
    updated_at: int | str


class SettingOutputItem(BaseModel):
    setting: SettingOutput


class SettingsOutputCollection(BaseModel):
    settings: List[SettingOutput]
