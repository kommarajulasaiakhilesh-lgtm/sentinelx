from sqlalchemy.orm import Session

from app.models.security_alert import SecurityAlert
from app.models.security_event import SecurityEvent
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
    description: str | None = None
) -> SecurityAlert:

    existing_alert = (
        db.query(SecurityAlert)
        .filter(
            SecurityAlert.security_event_id == security_event.id,
            SecurityAlert.alert_type == alert_type
        )
        .first()
    )

    if existing_alert:
        return existing_alert

    alert = SecurityAlert(
        agent_id=security_event.agent_id,
        security_event_id=security_event.id,
        alert_type=alert_type,
        severity=severity,
        title=title,
        description=description,
        status="OPEN"
    )

    db.add(alert)
    db.commit()
    db.refresh(alert)

    agent_owner_id = (
        db.query(SecurityEvent)
        .join(SecurityEvent.agent)
        .filter(SecurityEvent.id == security_event.id)
        .first()
        .agent.owner_id
    )

    security_event_stream.publish(
        user_id=agent_owner_id,
        event_type="ALERT_CREATED",
        data=serialize_security_alert(alert)
    )

    return alert


def detect_security_alert(
    db: Session,
    security_event: SecurityEvent
) -> SecurityAlert | None:

    if (
        security_event.event_type == "TOOL_ACTION"
        and security_event.decision == "BLOCK"
        and security_event.reason == "Runtime tool action rate limit exceeded"
    ):
        return create_security_alert(
            db=db,
            security_event=security_event,
            alert_type="TOOL_RATE_LIMIT",
            severity="HIGH",
            title="Tool action rate limit exceeded",
            description=(
                "The agent exceeded the configured runtime "
                "tool action rate limit."
            )
        )

    if (
        security_event.event_type == "TOOL_ACTION"
        and security_event.decision == "BLOCK"
        and security_event.reason == "Repeated blocked tool actions detected"
    ):
        return create_security_alert(
            db=db,
            security_event=security_event,
            alert_type="REPEATED_BLOCKED_ACTIONS",
            severity="HIGH",
            title="Repeated blocked tool actions detected",
            description=(
                "The agent generated multiple blocked tool actions "
                "within the configured runtime window."
            )
        )

    return None