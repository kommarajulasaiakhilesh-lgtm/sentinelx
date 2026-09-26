from datetime import datetime

from pydantic import BaseModel, ConfigDict


class SecurityAlertResponse(BaseModel):
    id: int
    agent_id: int
    security_event_id: int | None
    alert_type: str
    severity: str
    title: str
    description: str | None
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )


class SecurityAlertListResponse(BaseModel):
    items: list[SecurityAlertResponse]
    page: int
    page_size: int
    total: int
    pages: int