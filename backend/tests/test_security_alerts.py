from fastapi.testclient import TestClient

from app.services.security_alert_service import detect_security_alerts
from app.models.detection_rule import DetectionRule

from app.main import app
from app.db.database import SessionLocal
from app.models.security_event import SecurityEvent
from app.models.security_alert import SecurityAlert
from app.services.security_alert_service import detect_security_alert


client = TestClient(app)


def create_test_event(
    event_type,
    decision,
    reason
):
    db = SessionLocal()

    try:
        event = SecurityEvent(
            agent_id=1,
            policy_id=None,
            event_type=event_type,
            action="BLOCK",
            decision=decision,
            reason=reason,
            event_metadata=None
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
        alert = (
            db.query(SecurityAlert)
            .filter(
                SecurityAlert.security_event_id == event_id
            )
            .first()
        )

        if alert:
            db.delete(alert)

        event = (
            db.query(SecurityEvent)
            .filter(
                SecurityEvent.id == event_id
            )
            .first()
        )

        if event:
            db.delete(event)

        db.commit()

    finally:
        db.close()


def test_rate_limit_event_creates_alert():
    event_id = create_test_event(
        event_type="TOOL_ACTION",
        decision="BLOCK",
        reason="Runtime tool action rate limit exceeded"
    )

    db = SessionLocal()

    try:
        event = (
            db.query(SecurityEvent)
            .filter(
                SecurityEvent.id == event_id
            )
            .first()
        )

        alert = detect_security_alert(
            db=db,
            security_event=event
        )

        assert alert is not None
        assert alert.alert_type == "TOOL_RATE_LIMIT"
        assert alert.severity == "HIGH"
        assert alert.status == "OPEN"
        assert alert.security_event_id == event_id

    finally:
        db.close()
        cleanup_event(event_id)


def test_repeated_blocked_event_creates_alert():
    event_id = create_test_event(
        event_type="TOOL_ACTION",
        decision="BLOCK",
        reason="Repeated blocked tool actions detected"
    )

    db = SessionLocal()

    try:
        event = (
            db.query(SecurityEvent)
            .filter(
                SecurityEvent.id == event_id
            )
            .first()
        )

        alert = detect_security_alert(
            db=db,
            security_event=event
        )

        assert alert is not None
        assert alert.alert_type == "REPEATED_BLOCKED_ACTIONS"
        assert alert.severity == "HIGH"
        assert alert.status == "OPEN"
        assert alert.security_event_id == event_id

    finally:
        db.close()
        cleanup_event(event_id)


def test_normal_event_does_not_create_alert():
    event_id = create_test_event(
        event_type="TOOL_ACTION",
        decision="ALLOW",
        reason="Tool action allowed"
    )

    db = SessionLocal()

    try:
        event = (
            db.query(SecurityEvent)
            .filter(
                SecurityEvent.id == event_id
            )
            .first()
        )

        alert = detect_security_alert(
            db=db,
            security_event=event
        )

        assert alert is None

        alert_count = (
            db.query(SecurityAlert)
            .filter(
                SecurityAlert.security_event_id == event_id
            )
            .count()
        )

        assert alert_count == 0

    finally:
        db.close()
        cleanup_event(event_id)


def test_duplicate_alert_is_not_created():
    event_id = create_test_event(
        event_type="TOOL_ACTION",
        decision="BLOCK",
        reason="Runtime tool action rate limit exceeded"
    )

    db = SessionLocal()

    try:
        event = (
            db.query(SecurityEvent)
            .filter(
                SecurityEvent.id == event_id
            )
            .first()
        )

        first_alert = detect_security_alert(
            db=db,
            security_event=event
        )

        second_alert = detect_security_alert(
            db=db,
            security_event=event
        )

        assert first_alert is not None
        assert second_alert is not None

        assert first_alert.id == second_alert.id

        alert_count = (
            db.query(SecurityAlert)
            .filter(
                SecurityAlert.security_event_id == event_id
            )
            .count()
        )

        assert alert_count == 1

    finally:
        db.close()
        cleanup_event(event_id)

def test_multiple_matching_rules_create_distinct_alert_types():
    event_id = create_test_event(
        event_type="TOOL_ACTION",
        decision="BLOCK",
        reason="MULTI_RULE_PHASE17_TEST",
    )
    rule_ids = []

    try:
        db = SessionLocal()

        try:
            for index, alert_type in enumerate(
                ["PHASE17_ALERT_A", "PHASE17_ALERT_B"]
            ):
                rule = DetectionRule(
                    owner_id=None,
                    name=f"Phase 17 Multi Rule {index}",
                    description="Multiple matching rule regression test",
                    enabled=True,
                    severity="HIGH",
                    alert_type=alert_type,
                    title=f"Phase 17 alert {index}",
                    conditions=(
                        '{"event_type":"TOOL_ACTION",'
                        '"decision":"BLOCK",'
                        '"reason":"MULTI_RULE_PHASE17_TEST"}'
                    ),
                    threshold=1,
                    window_seconds=0,
                )
                db.add(rule)

            db.commit()

            rules = (
                db.query(DetectionRule)
                .filter(
                    DetectionRule.alert_type.in_(
                        ["PHASE17_ALERT_A", "PHASE17_ALERT_B"]
                    ),
                    DetectionRule.name.like("Phase 17 Multi Rule %"),
                )
                .all()
            )
            rule_ids = [rule.id for rule in rules]

            event = (
                db.query(SecurityEvent)
                .filter(SecurityEvent.id == event_id)
                .first()
            )

            alerts = detect_security_alerts(
                db=db,
                security_event=event,
            )

            phase17_alerts = [
                alert
                for alert in alerts
                if alert.alert_type in {
                    "PHASE17_ALERT_A",
                    "PHASE17_ALERT_B",
                }
            ]

            assert {
                alert.alert_type for alert in phase17_alerts
            } == {
                "PHASE17_ALERT_A",
                "PHASE17_ALERT_B",
            }

        finally:
            db.close()

    finally:
        cleanup_event(event_id)

        db = SessionLocal()
        try:
            if rule_ids:
                (
                    db.query(DetectionRule)
                    .filter(DetectionRule.id.in_(rule_ids))
                    .delete(synchronize_session=False)
                )
                db.commit()
        finally:
            db.close()


def test_multiple_rules_with_same_alert_type_create_one_alert():
    event_id = create_test_event(
        event_type="TOOL_ACTION",
        decision="BLOCK",
        reason="SAME_TYPE_PHASE17_TEST",
    )
    rule_ids = []

    try:
        db = SessionLocal()

        try:
            for index in range(2):
                rule = DetectionRule(
                    owner_id=None,
                    name=f"Phase 17 Same Type {index}",
                    description="Duplicate alert type regression test",
                    enabled=True,
                    severity="HIGH",
                    alert_type="PHASE17_SHARED_ALERT",
                    title=f"Shared alert {index}",
                    conditions=(
                        '{"event_type":"TOOL_ACTION",'
                        '"decision":"BLOCK",'
                        '"reason":"SAME_TYPE_PHASE17_TEST"}'
                    ),
                    threshold=1,
                    window_seconds=0,
                )
                db.add(rule)

            db.commit()

            rules = (
                db.query(DetectionRule)
                .filter(
                    DetectionRule.alert_type == "PHASE17_SHARED_ALERT",
                    DetectionRule.name.like("Phase 17 Same Type %"),
                )
                .all()
            )
            rule_ids = [rule.id for rule in rules]

            event = (
                db.query(SecurityEvent)
                .filter(SecurityEvent.id == event_id)
                .first()
            )

            alerts = detect_security_alerts(
                db=db,
                security_event=event,
            )

            matching_alerts = [
                alert
                for alert in alerts
                if alert.alert_type == "PHASE17_SHARED_ALERT"
            ]

            assert len(matching_alerts) == 1

            alert_count = (
                db.query(SecurityAlert)
                .filter(
                    SecurityAlert.security_event_id == event_id,
                    SecurityAlert.alert_type == "PHASE17_SHARED_ALERT",
                )
                .count()
            )
            assert alert_count == 1

        finally:
            db.close()

    finally:
        cleanup_event(event_id)

        db = SessionLocal()
        try:
            if rule_ids:
                (
                    db.query(DetectionRule)
                    .filter(DetectionRule.id.in_(rule_ids))
                    .delete(synchronize_session=False)
                )
                db.commit()
        finally:
            db.close()
