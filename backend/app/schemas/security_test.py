
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


SUPPORTED_CATEGORIES = {
    "PROMPT_INJECTION",
    "UNAUTHORIZED_TOOL",
    "POLICY_BYPASS",
    "RATE_LIMIT",
    "REPEATED_BLOCK",
    "SUSPICIOUS_ACTION",
}

VALID_DECISIONS = {"ALLOW", "BLOCK", "WARN"}


class SecurityTestScenarioBase(BaseModel):
    name: str = Field(min_length=1, max_length=150)
    category: str
    description: Optional[str] = None
    attack_input: Optional[str] = None
    agent_id: int = Field(gt=0)
    tool_name: Optional[str] = Field(default=None, max_length=100)
    action: Optional[str] = Field(default=None, max_length=100)
    resource: Optional[str] = Field(default=None, max_length=255)
    expected_decision: str
    enabled: bool = True

    @field_validator("category")
    @classmethod
    def validate_category(cls, value: str) -> str:
        normalized = value.strip().upper()
        if normalized not in SUPPORTED_CATEGORIES:
            raise ValueError(
                f"Unsupported category. Allowed categories: "
                f"{', '.join(sorted(SUPPORTED_CATEGORIES))}"
            )
        return normalized

    @field_validator("expected_decision")
    @classmethod
    def validate_expected_decision(cls, value: str) -> str:
        normalized = value.strip().upper()
        if normalized not in VALID_DECISIONS:
            raise ValueError(
                "expected_decision must be ALLOW, BLOCK, or WARN"
            )
        return normalized


class SecurityTestScenarioCreate(SecurityTestScenarioBase):
    pass


class SecurityTestScenarioResponse(SecurityTestScenarioBase):
    id: int
    owner_id: int
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
