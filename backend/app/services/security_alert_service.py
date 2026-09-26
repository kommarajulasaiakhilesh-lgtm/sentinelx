
from sqlalchemy.orm import Session

from app.models.security_alert import SecurityAlert
from app.models.security_event import SecurityEvent


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
