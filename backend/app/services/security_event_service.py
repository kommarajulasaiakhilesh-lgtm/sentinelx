
from sqlalchemy.orm import Session

from app.models.security_event import SecurityEvent
from app.schemas.security_event import SecurityEventCreate
from app.services.event_stream_service import (
    security_event_stream,
    serialize_security_event,
)
from app.services.incident_correlation_service import (
    correlate_security_alert,
)
from app.services.security_alert_service import (
    detect_behavioral_anomaly_alert,
    detect_security_alert,
)


def create_security_event(
    event_data: SecurityEventCreate,
    db: Session,
) -> SecurityEvent:
    event = SecurityEvent(
        agent_id=event_data.agent_id,
        policy_id=event_data.policy_id,
        event_type=event_data.event_type,
        action=event_data.action,
        decision=event_data.decision,
        reason=event_data.reason,
        event_metadata=event_data.event_metadata,
    )

    db.add(event)
    db.commit()
    db.refresh(event)

    # 1. Run existing deterministic detection rules.
    rule_alert = detect_security_alert(
        db=db,
        security_event=event,
    )

    if rule_alert is not None:
        correlate_security_alert(
            db=db,
            alert=rule_alert,
        )

    # 2. Run behavioral anomaly detection using the configured
    # database-backed baseline and observation windows.
    anomaly_alert = detect_behavioral_anomaly_alert(
        db=db,
        security_event=event,
    )

    if anomaly_alert is not None:
        correlate_security_alert(
            db=db,
            alert=anomaly_alert,
        )

    # 3. Preserve the existing event-stream publication.
    event_record = (
        db.query(SecurityEvent)
        .join(SecurityEvent.agent)
        .filter(SecurityEvent.id == event.id)
        .first()
    )

    if event_record is not None:
        security_event_stream.publish(
            user_id=event_record.agent.owner_id,
            event_type="SECURITY_EVENT",
            data=serialize_security_event(event),
        )

    return event
