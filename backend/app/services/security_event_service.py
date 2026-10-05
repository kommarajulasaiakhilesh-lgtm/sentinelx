

from sqlalchemy.orm import Session

from app.models.security_event import SecurityEvent
from app.schemas.security_event import SecurityEventCreate
from app.services.event_stream_service import (
    security_event_stream,
    serialize_security_event,
)
from app.services.incident_correlation_service import (
    correlate_security_alert
)
from app.services.security_alert_service import detect_security_alert


def create_security_event(
    event_data: SecurityEventCreate,
    db: Session
) -> SecurityEvent:

    event = SecurityEvent(
        agent_id=event_data.agent_id,
        policy_id=event_data.policy_id,
        event_type=event_data.event_type,
        action=event_data.action,
        decision=event_data.decision,
        reason=event_data.reason,
        event_metadata=event_data.event_metadata
    )

    db.add(event)
    db.commit()
    db.refresh(event)

    alert = detect_security_alert(
        db=db,
        security_event=event
    )

    if alert is not None:
        correlate_security_alert(
            db=db,
            alert=alert
        )

    agent_owner_id = (
        db.query(SecurityEvent)
        .join(SecurityEvent.agent)
        .filter(
            SecurityEvent.id == event.id
        )
        .first()
        .agent.owner_id
    )

    security_event_stream.publish(
    user_id=agent_owner_id,
    event_type="SECURITY_EVENT",
    data=serialize_security_event(event)
)

    return event