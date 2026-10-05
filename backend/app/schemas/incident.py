from datetime import datetime

from typing import Literal

from pydantic import BaseModel, ConfigDict


class IncidentCreate(BaseModel):
    agent_id: int
    title: str
    description: str | None = None
    severity: Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"]


class IncidentUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    severity: Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"] | None = None
    status: Literal[
        "OPEN",
        "INVESTIGATING",
        "CONTAINED",
        "RESOLVED",
    ] | None = None


class IncidentResponse(BaseModel):
    id: int
    agent_id: int
    title: str
    description: str | None
    severity: str
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )


class IncidentListResponse(BaseModel):
    items: list[IncidentResponse]
    page: int
    page_size: int
    total: int
    pages: int