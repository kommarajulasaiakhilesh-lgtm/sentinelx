
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class RiskScoringConfigurationUpdate(BaseModel):
    name: str = Field(min_length=1, max_length=150)
    enabled: bool = True

    blocked_event_weight: int = Field(ge=0)
    suspicious_event_weight: int = Field(ge=0)
    policy_violation_weight: int = Field(ge=0)

    score_cap: int = Field(ge=1)
    low_max: int = Field(ge=0)
    medium_max: int = Field(ge=1)
    high_max: int = Field(ge=2)
    critical_max: int = Field(ge=3)

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Configuration name cannot be blank")
        return value

    @model_validator(mode="after")
    def validate_thresholds(self):
        if not (
            0 <= self.low_max
            < self.medium_max
            < self.high_max
            < self.critical_max
        ):
            raise ValueError(
                "Thresholds must satisfy "
                "0 <= low_max < medium_max < high_max < critical_max"
            )

        if self.critical_max != self.score_cap:
            raise ValueError(
                "critical_max must equal score_cap"
            )

        return self


class RiskScoringConfigurationResponse(BaseModel):
    id: int
    owner_id: int | None
    name: str
    enabled: bool

    blocked_event_weight: int
    suspicious_event_weight: int
    policy_violation_weight: int

    score_cap: int
    low_max: int
    medium_max: int
    high_max: int
    critical_max: int

    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
