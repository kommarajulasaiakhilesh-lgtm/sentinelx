from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, HttpUrl


WebhookEventType = Literal[
    "INCIDENT_CREATED",
    "INCIDENT_SEVERITY_CHANGED",
    "INCIDENT_CONTAINED",
    "INCIDENT_RESOLVED",
]


class WebhookEndpointCreate(BaseModel):
    name: str
    url: HttpUrl
    secret: str | None = None


class WebhookEndpointUpdate(BaseModel):
    name: str | None = None
    url: HttpUrl | None = None
    secret: str | None = None
    enabled: bool | None = None


class WebhookEndpointResponse(BaseModel):
    id: int
    owner_id: int
    name: str
    url: str
    enabled: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class WebhookDeliveryResponse(BaseModel):
    id: int
    endpoint_id: int
    event_type: str
    status: str
    attempt_count: int
    response_status: int | None
    response_body: str | None
    created_at: datetime
    delivered_at: datetime | None

    model_config = ConfigDict(from_attributes=True)
    