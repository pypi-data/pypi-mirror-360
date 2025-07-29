from typing import Dict, List, Any
from pydantic import BaseModel, Field


class AgentOutput(BaseModel):
    output: str | None = None
    intermediate_steps: List[Dict[str, Any]] | None = Field(default_factory=list)
    return_direct: bool = False
    with_llm_error: bool = False


class Memory(BaseModel):
    episodic: Dict[str, Any] | None = Field(default_factory=dict)
    declarative: Dict[str, Any] | None = Field(default_factory=dict)
    procedural: Dict[str, Any] | None = Field(default_factory=dict)


class MemoryPoint(BaseModel):
    content: str
    metadata: Dict[str, Any]


class MessageBase(BaseModel):
    text: str
    image: str | bytes | None = None


class Message(MessageBase):
    additional_fields: Dict[str, Any] | None = None


class SettingInput(BaseModel):
    name: str
    value: Dict[str, Any]
    category: str | None = None


class Why(BaseModel):
    input: str | None = None
    intermediate_steps: Dict[str, Any] | None = Field(default_factory=dict)
    memory: Memory = Field(default_factory=Memory)
    model_interactions: Dict[str, Any] | None = Field(default_factory=dict)
