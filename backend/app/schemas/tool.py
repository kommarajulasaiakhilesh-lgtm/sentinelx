from datetime import datetime

from pydantic import BaseModel


class ToolCreate(BaseModel):
    name: str
    description: str | None = None
    tool_type: str


class ToolResponse(BaseModel):
    id: int
    agent_id: int
    name: str
    description: str | None
    tool_type: str
    enabled: bool
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }