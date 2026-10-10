import json
from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.models.agent import Agent
from app.models.detection_rule import DetectionRule
from app.models.security_event import SecurityEvent


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


def _parse_conditions(
    conditions: str | None,
) -> dict | None:
    """Return valid stored conditions, or None if invalid."""

    if not conditions:
        return None

    try:
        parsed = json.loads(conditions)
    except (TypeError, json.JSONDecodeError):
        return None

    if not isinstance(parsed, dict) or not parsed:
        return None

    for field_name, expected_value in parsed.items():
        if field_name not in SUPPORTED_EVENT_FIELDS:
            return None

        values = (
            expected_value
            if isinstance(expected_value, list)
            else [expected_value]
        )

        if not values:
            return None

        if field_name in STRING_EVENT_FIELDS:
            if not all(
                isinstance(value, str)
                for value in values
            ):
                return None

        elif field_name in INTEGER_EVENT_FIELDS:
            if not all(
                isinstance(value, int)
                and not isinstance(value, bool)
                for value in values
            ):
                return None

    return parsed


def _condition_matches(
    security_event: SecurityEvent,
    conditions: dict,
) -> bool:
    """Check one event against a validated condition set."""

    for field_name, expected_value in conditions.items():
        if field_name not in SUPPORTED_EVENT_FIELDS:
            return False

        actual_value = getattr(
            security_event,
            field_name,
            None,
        )

        if isinstance(expected_value, list):
            if actual_value not in expected_value:
                return False
        elif actual_value != expected_value:
            return False

    return True


def _count_matching_events(
    db: Session,
    security_event: SecurityEvent,
    rule: DetectionRule,
    conditions: dict,
) -> int:
    """Count matching events in SQL instead of loading all rows."""

    reference_time = security_event.created_at

    if reference_time is None:
        return 0

    if reference_time.tzinfo is None:
        reference_time = reference_time.replace(
            tzinfo=timezone.utc
        )

    query = db.query(SecurityEvent).filter(
        SecurityEvent.agent_id == security_event.agent_id,
        SecurityEvent.created_at <= reference_time,
    )

    if rule.window_seconds > 0:
        window_start = reference_time - timedelta(
            seconds=rule.window_seconds
        )

        query = query.filter(
            SecurityEvent.created_at >= window_start
        )

    for field_name, expected_value in conditions.items():
        column = getattr(SecurityEvent, field_name)

        if isinstance(expected_value, list):
            query = query.filter(
                column.in_(expected_value)
            )
        else:
            query = query.filter(
                column == expected_value
            )

    return query.count()


def rule_matches_event(
    db: Session,
    security_event: SecurityEvent | None,
    rule: DetectionRule | None,
) -> bool:
    if security_event is None or rule is None:
        return False

    if not rule.enabled:
        return False

    if rule.threshold < 1 or rule.window_seconds < 0:
        return False

    conditions = _parse_conditions(rule.conditions)

    # Invalid, malformed, or empty conditions never match.
    if conditions is None:
        return False

    if not _condition_matches(security_event, conditions):
        return False

    matching_event_count = _count_matching_events(
        db=db,
        security_event=security_event,
        rule=rule,
        conditions=conditions,
    )

    return matching_event_count >= rule.threshold


def get_matching_detection_rules(
    db: Session,
    security_event: SecurityEvent | None,
) -> list[DetectionRule]:
    if security_event is None:
        return []

    agent = (
        db.query(Agent.id, Agent.owner_id)
        .filter(Agent.id == security_event.agent_id)
        .first()
    )

    if agent is None:
        return []

    owner_id = agent.owner_id

    query = db.query(DetectionRule).filter(
        DetectionRule.enabled.is_(True)
    )

    if owner_id is None:
        query = query.filter(
            DetectionRule.owner_id.is_(None)
        )
    else:
        query = query.filter(
            (DetectionRule.owner_id.is_(None))
            | (DetectionRule.owner_id == owner_id)
        )

    rules = query.order_by(
        DetectionRule.id.asc()
    ).all()

    return [
        rule
        for rule in rules
        if rule_matches_event(
            db=db,
            security_event=security_event,
            rule=rule,
        )
    ]