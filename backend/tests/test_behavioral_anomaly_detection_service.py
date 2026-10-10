
from datetime import datetime, timedelta, timezone

from app.db.database import SessionLocal
from app.main import app  # noqa: F401
from app.models.behavioral_baseline_configuration import (
    BehavioralBaselineConfiguration,
)
from app.models.security_event import SecurityEvent
from app.services.behavioral_anomaly_detection_service import (
    _compare_metric,
    detect_behavioral_anomalies,
)


def test_normal_activity_does_not_trigger_anomaly():
    result = _compare_metric("activity_rate", 0.01, 0.012, 50)

    assert result["is_anomaly"] is False
    assert abs(result["deviation_percent"] - 20.0) < 0.0001


def test_increased_activity_triggers_anomaly():
    result = _compare_metric("activity_rate", 0.01, 0.02, 50)

    assert result["is_anomaly"] is True
    assert abs(result["deviation_percent"] - 100.0) < 0.0001
    assert result["reason"] is not None


def test_new_activity_with_zero_baseline_triggers_anomaly():
    result = _compare_metric("blocked_event_rate", 0.0, 0.01, 50)

    assert result["is_anomaly"] is True
    assert result["deviation_percent"] is None


def test_zero_activity_with_zero_baseline_is_not_anomaly():
    result = _compare_metric("blocked_event_rate", 0.0, 0.0, 50)

    assert result["is_anomaly"] is False
    assert result["deviation_percent"] == 0.0


def test_activity_at_threshold_does_not_trigger_anomaly():
    result = _compare_metric("activity_rate", 0.01, 0.015, 50)

    assert result["is_anomaly"] is False
    assert abs(result["deviation_percent"] - 50.0) < 0.0001


def test_activity_above_threshold_triggers_anomaly():
    result = _compare_metric("activity_rate", 0.01, 0.0151, 50)

    assert result["is_anomaly"] is True
    assert result["deviation_percent"] > 50.0


def create_test_configuration(db):
    configuration = BehavioralBaselineConfiguration(
        owner_id=7,
        name="Anomaly Detection Integration Test",
        enabled=True,
        baseline_window_seconds=3600,
        observation_window_seconds=300,
        minimum_observations=10,
        deviation_threshold_percent=50,
    )
    db.add(configuration)
    db.commit()
    db.refresh(configuration)
    return configuration


def create_test_events(db, reference_time, offsets):
    events = [
        SecurityEvent(
            agent_id=4,
            event_type="OTHER",
            action="TEST",
            decision="ALLOW",
            reason="Behavioral anomaly integration test",
            created_at=reference_time - timedelta(seconds=offset),
        )
        for offset in offsets
    ]
    db.add_all(events)
    db.commit()
    return [event.id for event in events]


def cleanup_test_data(db, event_ids, configuration_id):
    try:
        if event_ids:
            db.query(SecurityEvent).filter(
                SecurityEvent.id.in_(event_ids)
            ).delete(synchronize_session=False)

        if configuration_id is not None:
            db.query(BehavioralBaselineConfiguration).filter(
                BehavioralBaselineConfiguration.id == configuration_id
            ).delete(synchronize_session=False)

        db.commit()
    except Exception:
        db.rollback()
        raise


def test_database_detection_does_not_flag_normal_activity():
    db = SessionLocal()
    event_ids = []
    configuration_id = None

    try:
        configuration = create_test_configuration(db)
        configuration_id = configuration.id
        reference_time = datetime.now(timezone.utc)

        event_ids = create_test_events(
            db,
            reference_time,
            [400 + index * 100 for index in range(10)] + [30],
        )

        result = detect_behavioral_anomalies(
            db=db,
            agent_id=4,
            owner_id=7,
            reference_time=reference_time,
        )

        assert result["sufficient_observations"] is True
        assert result["anomaly_detected"] is False
        assert result["anomalies"] == []
    finally:
        cleanup_test_data(db, event_ids, configuration_id)
        db.close()


def test_database_detection_reports_increased_activity():
    db = SessionLocal()
    event_ids = []
    configuration_id = None

    try:
        configuration = create_test_configuration(db)
        configuration_id = configuration.id
        reference_time = datetime.now(timezone.utc)

        event_ids = create_test_events(
            db,
            reference_time,
            [400 + index * 100 for index in range(10)]
            + [10, 20, 30],
        )

        result = detect_behavioral_anomalies(
            db=db,
            agent_id=4,
            owner_id=7,
            reference_time=reference_time,
        )

        assert result["sufficient_observations"] is True
        assert result["anomaly_detected"] is True

        activity_anomaly = next(
            item
            for item in result["anomalies"]
            if item["metric"] == "activity_rate"
        )

        assert activity_anomaly["baseline_rate"] > 0
        assert activity_anomaly["observed_rate"] > (
            activity_anomaly["baseline_rate"]
        )
        assert activity_anomaly["deviation_percent"] > 50
        assert activity_anomaly["reason"] is not None
    finally:
        cleanup_test_data(db, event_ids, configuration_id)
        db.close()


def test_database_detection_suppresses_anomalies_with_insufficient_history():
    db = SessionLocal()
    event_ids = []
    configuration_id = None

    try:
        configuration = create_test_configuration(db)
        configuration_id = configuration.id
        reference_time = datetime.now(timezone.utc)

        event_ids = create_test_events(
            db,
            reference_time,
            [500, 700, 10, 20, 30],
        )

        result = detect_behavioral_anomalies(
            db=db,
            agent_id=4,
            owner_id=7,
            reference_time=reference_time,
        )

        assert result["sufficient_observations"] is False
        assert result["anomaly_detected"] is False
        assert result["anomalies"] == []
        assert all(
            comparison["is_anomaly"] is False
            for comparison in result["comparisons"]
        )
    finally:
        cleanup_test_data(db, event_ids, configuration_id)
        db.close()
