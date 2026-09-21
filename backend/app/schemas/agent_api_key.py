from datetime import datetime

from pydantic import BaseModel, ConfigDict


class AgentAPIKeyResponse(BaseModel):
    id: int
    agent_id: int
    created_at: datetime
    expires_at: datetime | None
    is_active: bool

    model_config = ConfigDict(from_attributes=True)


class AgentAPIKeyCreateResponse(BaseModel):
    id: int
    agent_id: int
    api_key: str
    created_at: datetime
    expires_at: datetime | None
    is_active: bool