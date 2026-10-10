from datetime import datetime
from typing import Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    model_validator,
)


DetectionSeverity = Literal[
    "LOW",
    "MEDIUM",
    "HIGH",
    "CRITICAL",
]

ConditionValue = (
    str | int | bool | list[str] | list[int]
)

SUPPORTED_EVENT_FIELDS = {
    "event_type",
    "action",
    "decision",
    "reason",
    "agent_id",
    "policy_id",
}

STRING_EVENT_FIELDS = {
    "event_type",
    "action",
    "decision",
    "reason",
}

INTEGER_EVENT_FIELDS = {
    "agent_id",
    "policy_id",
}


def validate_conditions(
    conditions: dict[str, ConditionValue] | None,
) -> None:
    if conditions is None:
        return

    if not conditions:
        raise ValueError(
            "Conditions must contain at least one field."
        )

    for field_name, expected_value in conditions.items():
        if field_name not in SUPPORTED_EVENT_FIELDS:
            raise ValueError(
                f"Unsupported condition field: {field_name}"
            )

        values = (
            expected_value
            if isinstance(expected_value, list)
            else [expected_value]
        )

        if not values:
            raise ValueError(
                f"Condition '{field_name}' cannot use an empty list."
            )

        if field_name in STRING_EVENT_FIELDS:
            if not all(
                isinstance(value, str)
                for value in values
            ):
                raise ValueError(
                    f"Condition '{field_name}' requires string values."
                )

        elif field_name in INTEGER_EVENT_FIELDS:
            if not all(
                isinstance(value, int)
                and not isinstance(value, bool)
                for value in values
            ):
                raise ValueError(
                    f"Condition '{field_name}' requires integer values."
                )


class DetectionRuleCreate(BaseModel):
    name: str = Field(min_length=1, max_length=150)
    description: str | None = None
    enabled: bool = True
    severity: DetectionSeverity
    alert_type: str = Field(min_length=1, max_length=100)
    title: str = Field(min_length=1, max_length=200)

    conditions: dict[str, ConditionValue] | None = None

    threshold: int = Field(default=1, ge=1, le=1_000_000)
    window_seconds: int = Field(
        default=0,
        ge=0,
        le=31_536_000,
    )

    @model_validator(mode="after")
    def validate_rule_conditions(self):
        validate_conditions(self.conditions)
        return self


class DetectionRuleUpdate(BaseModel):
    name: str | None = Field(
        default=None,
        min_length=1,
        max_length=150,
    )
    description: str | None = None
    enabled: bool | None = None
    severity: DetectionSeverity | None = None
    alert_type: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
    )
    title: str | None = Field(
        default=None,
        min_length=1,
        max_length=200,
    )

    conditions: dict[str, ConditionValue] | None = None

    threshold: int | None = Field(
        default=None,
        ge=1,
        le=1_000_000,
    )
    window_seconds: int | None = Field(
        default=None,
        ge=0,
        le=31_536_000,
    )

    @model_validator(mode="after")
    def validate_rule_conditions(self):
        if "conditions" in self.model_fields_set:
            validate_conditions(self.conditions)
        return self


class DetectionRuleResponse(BaseModel):
    id: int
    owner_id: int | None
    name: str
    description: str | None
    enabled: bool
    severity: DetectionSeverity
    alert_type: str
    title: str
    conditions: str | None
    threshold: int
    window_seconds: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)