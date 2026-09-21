from datetime import datetime

from pydantic import BaseModel, ConfigDict


class PolicyCreate(BaseModel):
    name: str
    description: str | None = None
    policy_type: str


class PolicyUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    policy_type: str | None = None
    enabled: bool | None = None


class PolicyResponse(BaseModel):
    id: int
    agent_id: int
    name: str
    description: str | None
    policy_type: str
    enabled: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )