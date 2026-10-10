from app.main import app  # noqa: F401

import json

from app.db.database import SessionLocal
from app.models.detection_rule import DetectionRule
from app.models.security_event import SecurityEvent
from app.services.detection_rule_service import (
    get_matching_detection_rules,
    rule_matches_event,
)


def create_event(
    event_type="TOOL_ACTION",
    action="BLOCK",
    decision="BLOCK",
    reason="TEST_REASON",
):
    db = SessionLocal()

    try:
        event = SecurityEvent(
            agent_id=1,
            policy_id=None,
            event_type=event_type,
            action=action,
            decision=decision,
            reason=reason,
            event_metadata=None,
        )

        db.add(event)
        db.commit()
        db.refresh(event)

        return event.id

    finally:
        db.close()


def cleanup_event(event_id):
    db = SessionLocal()

    try:
        event = (
            db.query(SecurityEvent)
            .filter(SecurityEvent.id == event_id)
            .first()
        )

        if event:
            db.delete(event)
            db.commit()

    finally:
        db.close()


def create_rule(
    conditions,
    threshold=1,
    window_seconds=0,
    enabled=True,
):
    db = SessionLocal()

    try:
        rule = DetectionRule(
            owner_id=None,
            name="Test Detection Rule",
            description="Detection rule service test",
            enabled=enabled,
            severity="HIGH",
            alert_type="TEST_ALERT",
            title="Test detection",
            conditions=json.dumps(conditions),
            threshold=threshold,
            window_seconds=window_seconds,
        )

        db.add(rule)
        db.commit()
        db.refresh(rule)

        return rule.id

    finally:
        db.close()


def cleanup_rule(rule_id):
    db = SessionLocal()

    try:
        rule = (
            db.query(DetectionRule)
            .filter(DetectionRule.id == rule_id)
            .first()
        )

        if rule:
            db.delete(rule)
            db.commit()

    finally:
        db.close()


def test_matching_rule_matches_event():
    event_id = create_event(
        event_type="TOOL_ACTION",
        decision="BLOCK",
        reason="TEST_REASON",
    )

    rule_id = create_rule(
        conditions={
            "event_type": "TOOL_ACTION",
            "decision": "BLOCK",
            "reason": "TEST_REASON",
        }
    )

    db = SessionLocal()

    try:
        event = db.query(SecurityEvent).filter(
            SecurityEvent.id == event_id
        ).first()

        rule = db.query(DetectionRule).filter(
            DetectionRule.id == rule_id
        ).first()

        assert rule_matches_event(
            db=db,
            security_event=event,
            rule=rule,
        ) is True

    finally:
        db.close()
        cleanup_event(event_id)
        cleanup_rule(rule_id)


def test_non_matching_rule_does_not_match_event():
    event_id = create_event(
        event_type="TOOL_ACTION",
        decision="ALLOW",
        reason="TEST_REASON",
    )

    rule_id = create_rule(
        conditions={
            "event_type": "TOOL_ACTION",
            "decision": "BLOCK",
        }
    )

    db = SessionLocal()

    try:
        event = db.query(SecurityEvent).filter(
            SecurityEvent.id == event_id
        ).first()

        rule = db.query(DetectionRule).filter(
            DetectionRule.id == rule_id
        ).first()

        assert rule_matches_event(
            db=db,
            security_event=event,
            rule=rule,
        ) is False

    finally:
        db.close()
        cleanup_event(event_id)
        cleanup_rule(rule_id)


def test_disabled_rule_does_not_match():
    event_id = create_event()

    rule_id = create_rule(
        conditions={
            "event_type": "TOOL_ACTION",
        },
        enabled=False,
    )

    db = SessionLocal()

    try:
        event = db.query(SecurityEvent).filter(
            SecurityEvent.id == event_id
        ).first()

        rule = db.query(DetectionRule).filter(
            DetectionRule.id == rule_id
        ).first()

        assert rule_matches_event(
            db=db,
            security_event=event,
            rule=rule,
        ) is False

    finally:
        db.close()
        cleanup_event(event_id)
        cleanup_rule(rule_id)


def test_threshold_requires_multiple_matching_events():
    first_event_id = create_event()
    second_event_id = create_event()

    rule_id = create_rule(
        conditions={
            "event_type": "TOOL_ACTION",
            "reason": "TEST_REASON",
        },
        threshold=2,
    )

    db = SessionLocal()

    try:
        second_event = db.query(SecurityEvent).filter(
            SecurityEvent.id == second_event_id
        ).first()

        rule = db.query(DetectionRule).filter(
            DetectionRule.id == rule_id
        ).first()

        assert rule_matches_event(
            db=db,
            security_event=second_event,
            rule=rule,
        ) is True

    finally:
        db.close()
        cleanup_event(first_event_id)
        cleanup_event(second_event_id)
        cleanup_rule(rule_id)


def test_threshold_not_reached_does_not_match():
    event_id = create_event()

    rule_id = create_rule(
        conditions={
            "event_type": "TOOL_ACTION",
            "reason": "TEST_REASON",
        },
        threshold=2,
    )

    db = SessionLocal()

    try:
        event = db.query(SecurityEvent).filter(
            SecurityEvent.id == event_id
        ).first()

        rule = db.query(DetectionRule).filter(
            DetectionRule.id == rule_id
        ).first()

        assert rule_matches_event(
            db=db,
            security_event=event,
            rule=rule,
        ) is False

    finally:
        db.close()
        cleanup_event(event_id)
        cleanup_rule(rule_id)


def test_unsupported_condition_field_does_not_match():
    event_id = create_event()

    rule_id = create_rule(
        conditions={
            "unknown_field": "something",
        }
    )

    db = SessionLocal()

    try:
        event = db.query(SecurityEvent).filter(
            SecurityEvent.id == event_id
        ).first()

        rule = db.query(DetectionRule).filter(
            DetectionRule.id == rule_id
        ).first()

        assert rule_matches_event(
            db=db,
            security_event=event,
            rule=rule,
        ) is False

    finally:
        db.close()
        cleanup_event(event_id)
        cleanup_rule(rule_id)


def test_matching_rules_include_global_enabled_rule():
    event_id = create_event()

    rule_id = create_rule(
        conditions={
            "event_type": "TOOL_ACTION",
        }
    )

    db = SessionLocal()

    try:
        event = db.query(SecurityEvent).filter(
            SecurityEvent.id == event_id
        ).first()

        matching_rules = get_matching_detection_rules(
            db=db,
            security_event=event,
        )

        assert any(
            rule.id == rule_id
            for rule in matching_rules
        )

    finally:
        db.close()
        cleanup_event(event_id)
        cleanup_rule(rule_id)
def test_malformed_conditions_never_match():
    event_id = create_event()
    rule_id = create_rule(
        conditions={"event_type": "TOOL_ACTION"}
    )

    db = SessionLocal()

    try:
        event = db.query(SecurityEvent).filter(
            SecurityEvent.id == event_id
        ).first()

        rule = db.query(DetectionRule).filter(
            DetectionRule.id == rule_id
        ).first()

        rule.conditions = '{"event_type":'
        db.commit()
        db.refresh(rule)

        assert rule_matches_event(
            db=db,
            security_event=event,
            rule=rule,
        ) is False

    finally:
        db.close()
        cleanup_event(event_id)
        cleanup_rule(rule_id)


def test_empty_conditions_never_match():
    event_id = create_event()
    rule_id = create_rule(conditions={})

    db = SessionLocal()

    try:
        event = db.query(SecurityEvent).filter(
            SecurityEvent.id == event_id
        ).first()

        rule = db.query(DetectionRule).filter(
            DetectionRule.id == rule_id
        ).first()

        assert rule_matches_event(
            db=db,
            security_event=event,
            rule=rule,
        ) is False

    finally:
        db.close()
        cleanup_event(event_id)
        cleanup_rule(rule_id)