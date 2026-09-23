from datetime import datetime
from typing import Literal
from pydantic import BaseModel, ConfigDict
PolicyAction = Literal[
    "BLOCK",
    "ALLOW",
    "WARN"
]
class PolicyCreate(BaseModel):
    name: str
    description: str | None = None
    policy_type: str
    action: PolicyAction = "BLOCK"
    priority: int = 100
    condition: str | None = None
class PolicyUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    policy_type: str | None = None
    action: PolicyAction | None = None
    enabled: bool | None = None
    priority: int | None = None
    condition: str | None = None
class PolicyResponse(BaseModel):
    id: int
    agent_id: int
    name: str
    description: str | None
    policy_type: str
    action: PolicyAction
    enabled: bool
    created_at: datetime
    updated_at: datetime
    priority: int
    condition: str | None
    model_config = ConfigDict(
        from_attributes=True
    )
