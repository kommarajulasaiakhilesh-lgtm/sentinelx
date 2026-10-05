from datetime import datetime

from pydantic import BaseModel, ConfigDict


class IncidentTimelineCreate(BaseModel):
    entry_type: str
    description: str


class IncidentTimelineResponse(BaseModel):
    id: int
    incident_id: int
    entry_type: str
    description: str
    created_by_user_id: int | None
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )