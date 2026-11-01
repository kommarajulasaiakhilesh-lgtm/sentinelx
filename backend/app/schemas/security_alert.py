from datetime import datetime

from typing import Literal

from pydantic import BaseModel, ConfigDict


class BulkAlertStatusUpdate(BaseModel):
    alert_ids: list[int]
    status: Literal["OPEN", "ACKNOWLEDGED", "RESOLVED"]


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