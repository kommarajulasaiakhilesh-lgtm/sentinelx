
from datetime import datetime, timezone
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.security_alert import SecurityAlert
from app.models.security_event import SecurityEvent
from app.services.behavioral_anomaly_detection_service import (
    detect_behavioral_anomalies,
)
from app.services.detection_rule_service import (
    get_matching_detection_rules,
)
from app.services.event_stream_service import (
    security_event_stream,
    serialize_security_alert,
)



def create_security_alert(
    db: Session,
    security_event: SecurityEvent,
    alert_type: str,
    severity: str,
    title: str,
    description: str | None = None,
) -> SecurityAlert:
    existing_alert = (
        db.query(SecurityAlert)
        .filter(
            SecurityAlert.security_event_id == security_event.id,
            SecurityAlert.alert_type == alert_type,
        )
        .first()
    )

    if existing_alert is not None:
        return existing_alert

    alert = SecurityAlert(
        agent_id=security_event.agent_id,
        security_event_id=security_event.id,
        alert_type=alert_type,
        severity=severity,
        title=title,
        description=description,
        status="OPEN",
    )

    db.add(alert)

    try:
        db.commit()
        db.refresh(alert)
    except IntegrityError:
        db.rollback()

        # Another request may have inserted the same event/type pair.
        existing_alert = (
            db.query(SecurityAlert)
            .filter(
                SecurityAlert.security_event_id == security_event.id,
                SecurityAlert.alert_type == alert_type,
            )
            .first()
        )

        if existing_alert is not None:
            return existing_alert

        # The integrity error was unrelated to duplicate alert creation.
        raise

    event_record = (
        db.query(SecurityEvent)
        .join(SecurityEvent.agent)
        .filter(SecurityEvent.id == security_event.id)
        .first()
    )

    if event_record is not None:
        security_event_stream.publish(
            user_id=event_record.agent.owner_id,
            event_type="ALERT_CREATED",
            data=serialize_security_alert(alert),
        )

    return alert



def detect_security_alerts(
    db: Session,
    security_event: SecurityEvent,
) -> list[SecurityAlert]:
    """Create alerts for every distinct matching alert type."""

    matching_rules = get_matching_detection_rules(
        db=db,
        security_event=security_event,
    )

    alerts_by_type: dict[str, SecurityAlert] = {}

    for rule in matching_rules:
        # Alert deduplication is based on event ID and alert type.
        # Process each alert type once, even if several rules match.
        if rule.alert_type in alerts_by_type:
            continue

        alert = create_security_alert(
            db=db,
            security_event=security_event,
            alert_type=rule.alert_type,
            severity=rule.severity,
            title=rule.title,
            description=rule.description,
        )

        alerts_by_type[rule.alert_type] = alert

    return list(alerts_by_type.values())


def detect_security_alert(
    db: Session,
    security_event: SecurityEvent,
) -> SecurityAlert | None:
    """Compatibility wrapper returning the first matching alert."""

    alerts = detect_security_alerts(
        db=db,
        security_event=security_event,
    )

    return alerts[0] if alerts else None


def detect_behavioral_anomaly_alert(
    db: Session,
    security_event: SecurityEvent,
) -> SecurityAlert | None:
    """
    Detect behavioral anomalies and create one active alert per agent.

    Behavioral thresholds and time windows come from the database-backed
    behavioral baseline configuration.
    """

    event_record = (
        db.query(SecurityEvent)
        .join(SecurityEvent.agent)
        .filter(SecurityEvent.id == security_event.id)
        .first()
    )

    if event_record is None:
        return None

    owner_id = event_record.agent.owner_id

    try:
        result = detect_behavioral_anomalies(
            db=db,
            agent_id=security_event.agent_id,
            owner_id=owner_id,
            reference_time=datetime.now(timezone.utc),
        )
    except ValueError:
        # Missing enabled configuration must not block event ingestion.
        return None

    anomalies = result.get("anomalies", [])

    if not result.get("anomaly_detected") or not anomalies:
        return None

    existing_active_alert = (
        db.query(SecurityAlert)
        .filter(
            SecurityAlert.agent_id == security_event.agent_id,
            SecurityAlert.alert_type == "BEHAVIORAL_ANOMALY",
            SecurityAlert.status.in_(["OPEN", "ACKNOWLEDGED"]),
        )
        .order_by(SecurityAlert.id.asc())
        .first()
    )

    if existing_active_alert is not None:
        return existing_active_alert

    evidence_lines = [
        "Behavioral anomaly detected from configured historical baseline.",
        f"Agent ID: {security_event.agent_id}",
        f"Baseline window: "
        f"{result['baseline_window']['start_time'].isoformat()} to "
        f"{result['baseline_window']['end_time'].isoformat()}",
        f"Observation window: "
        f"{result['observation_window']['start_time'].isoformat()} to "
        f"{result['observation_window']['end_time'].isoformat()}",
    ]

    for anomaly in anomalies:
        evidence_lines.append(
            f"Metric: {anomaly['metric']}; "
            f"baseline rate: {anomaly['baseline_rate']}; "
            f"observed rate: {anomaly['observed_rate']}; "
            f"deviation: {anomaly['deviation_percent']}%; "
            f"configured threshold: {anomaly['threshold_percent']}%; "
            f"reason: {anomaly['reason']}"
        )

    return create_security_alert(
        db=db,
        security_event=security_event,
        alert_type="BEHAVIORAL_ANOMALY",
        severity="HIGH",
        title="Behavioral Anomaly Detected",
        description="\n".join(evidence_lines),
    )
