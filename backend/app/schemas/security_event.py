
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class SecurityEventCreate(BaseModel):
    agent_id: int
    policy_id: int | None = None
    event_type: str
    action: str
    decision: str
    reason: str | None = None
    event_metadata: str | None = None


class SecurityEventResponse(BaseModel):
    id: int
    agent_id: int
    policy_id: int | None
    event_type: str
    action: str
    decision: str
    reason: str | None
    event_metadata: str | None
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )


class SecurityEventListResponse(BaseModel):
    items: list[SecurityEventResponse]
    page: int
    page_size: int
    total: int
    pages: int

