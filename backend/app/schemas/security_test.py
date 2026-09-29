from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class SecurityTestScenarioBase(BaseModel):
    name: str
    category: str
    description: Optional[str] = None
    attack_input: Optional[str] = None

    agent_id: Optional[int] = None
    tool_name: Optional[str] = None
    action: Optional[str] = None
    resource: Optional[str] = None

    expected_decision: str
    enabled: bool = True


class SecurityTestScenarioCreate(SecurityTestScenarioBase):
    pass


class SecurityTestScenarioResponse(SecurityTestScenarioBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class SecurityTestRunResponse(BaseModel):
    id: int
    scenario_id: int
    actual_decision: Optional[str] = None
    expected_decision: str
    result: str
    details: Optional[str] = None
    executed_at: datetime

    model_config = ConfigDict(from_attributes=True)