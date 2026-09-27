from datetime import datetime

from typing import Literal

from pydantic import BaseModel, ConfigDict


class AgentCreate(BaseModel):
    name: str
    description: str | None = None

class AgentStatusUpdate(BaseModel):
    status: Literal["ACTIVE", "SUSPENDED"]


class AgentResponse(BaseModel):
    id: int
    owner_id: int
    name: str
    description: str | None
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)