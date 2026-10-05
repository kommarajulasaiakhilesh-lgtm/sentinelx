from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.models.agent import Agent
from app.models.incident import Incident
from app.models.incident_alert import IncidentAlert
from app.models.security_alert import SecurityAlert
from app.services.event_stream_service import (
    security_event_stream,
    serialize_incident,
)


CORRELATION_WINDOW_SECONDS = 300

CORRELATABLE_INCIDENT_STATUSES = {
    "OPEN",
    "INVESTIGATING",
}


def find_correlatable_incident(
    db: Session,
    alert: SecurityAlert
) -> Incident | None:

    window_start = (
        datetime.now(timezone.utc)
        - timedelta(seconds=CORRELATION_WINDOW_SECONDS)
    )

    return (
        db.query(Incident)
        .filter(
            Incident.agent_id == alert.agent_id,
            Incident.severity == alert.severity,
            Incident.created_at >= window_start,
            Incident.status.in_(CORRELATABLE_INCIDENT_STATUSES)
        )
        .join(
            IncidentAlert,
            IncidentAlert.incident_id == Incident.id
        )
        .join(
            SecurityAlert,
            SecurityAlert.id == IncidentAlert.alert_id
        )
        .filter(
            SecurityAlert.alert_type == alert.alert_type
        )
        .order_by(
            Incident.created_at.desc()
        )
        .first()
    )


def create_correlated_incident(
    db: Session,
    alert: SecurityAlert
) -> Incident:

    incident = Incident(
        agent_id=alert.agent_id,
        title=alert.title,
        description=alert.description,
        severity=alert.severity,
        status="OPEN"
    )

    db.add(incident)
    db.flush()

    return incident


def attach_alert_to_incident(
    db: Session,
    incident: Incident,
    alert: SecurityAlert
) -> IncidentAlert:

    existing_link = (
        db.query(IncidentAlert)
        .filter(
            IncidentAlert.incident_id == incident.id,
            IncidentAlert.alert_id == alert.id
        )
        .first()
    )

    if existing_link:
        return existing_link

    incident_alert = IncidentAlert(
        incident_id=incident.id,
        alert_id=alert.id
    )

    db.add(incident_alert)
    db.flush()

    return incident_alert


def correlate_security_alert(
    db: Session,
    alert: SecurityAlert
) -> Incident:

    incident = find_correlatable_incident(
        db=db,
        alert=alert
    )

    incident_created = incident is None

    if incident_created:
        incident = create_correlated_incident(
            db=db,
            alert=alert
        )

    attach_alert_to_incident(
        db=db,
        incident=incident,
        alert=alert
    )

    db.commit()
    db.refresh(incident)

    if incident_created:
        agent_owner_id = (
            db.query(Agent)
            .filter(Agent.id == incident.agent_id)
            .first()
            .owner_id
        )

        security_event_stream.publish(
            user_id=agent_owner_id,
            event_type="INCIDENT_CREATED",
            data=serialize_incident(incident)
        )

    return incident