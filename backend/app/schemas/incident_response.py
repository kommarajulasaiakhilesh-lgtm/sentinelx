from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, model_validator


IncidentActionType = Literal[
    "SUSPEND_AGENT",
    "DISABLE_TOOL",
    "ROTATE_AGENT_API_KEY",
]


class IncidentResponseActionCreate(BaseModel):
    action_type: IncidentActionType
    reason: str
    agent_id: int | None = None
    tool_id: int | None = None
    api_key_id: int | None = None

    @model_validator(mode="after")
    def validate_target(self):
        if not self.reason.strip():
            raise ValueError("Reason is required")

        if self.action_type == "DISABLE_TOOL" and self.tool_id is None:
            raise ValueError("tool_id is required for DISABLE_TOOL")

        if (
            self.action_type == "ROTATE_AGENT_API_KEY"
            and self.api_key_id is None
        ):
            raise ValueError(
                "api_key_id is required for ROTATE_AGENT_API_KEY"
            )

        if self.action_type == "SUSPEND_AGENT":
            if self.tool_id is not None or self.api_key_id is not None:
                raise ValueError(
                    "SUSPEND_AGENT does not accept tool_id or api_key_id"
                )

        return self


class IncidentResponseActionResponse(BaseModel):
    id: int
    incident_id: int
    action_type: str
    agent_id: int
    tool_id: int | None
    api_key_id: int | None
    authorized_by_user_id: int
    reason: str
    result: str
    details: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class IncidentResponseActionCreateResponse(
    IncidentResponseActionResponse
):
    api_key: str | None = None