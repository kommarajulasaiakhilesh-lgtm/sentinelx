from sqlalchemy.orm import Session

from app.models.security_event import SecurityEvent
from app.schemas.security_event import SecurityEventCreate


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

    return event