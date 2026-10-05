from app.main import app
from app.schemas.security_event import SecurityEventCreate
from app.services.security_event_service import create_security_event

from app.db.database import SessionLocal
from app.models.incident import Incident
from app.models.incident_alert import IncidentAlert
from app.models.security_alert import SecurityAlert
from app.models.security_event import SecurityEvent
from app.services.incident_correlation_service import (
    correlate_security_alert,
)


def create_test_alert(
    agent_id: int = 1,
    alert_type: str = "TOOL_RATE_LIMIT",
    severity: str = "HIGH"
):
    db = SessionLocal()

    try:
        event = SecurityEvent(
            agent_id=agent_id,
            event_type="TOOL_ACTION",
            action="BLOCK",
            decision="BLOCK",
            reason="Runtime tool action rate limit exceeded"
        )

        db.add(event)
        db.commit()
        db.refresh(event)

        alert = SecurityAlert(
            agent_id=agent_id,
            security_event_id=event.id,
            alert_type=alert_type,
            severity=severity,
            title=f"Test {alert_type}",
            description="Correlation test alert",
            status="OPEN"
        )

        db.add(alert)
        db.commit()
        db.refresh(alert)

        return alert.id, event.id

    finally:
        db.close()


def cleanup_alert(alert_id: int, event_id: int):
    db = SessionLocal()

    try:
        alert = (
            db.query(SecurityAlert)
            .filter(SecurityAlert.id == alert_id)
            .first()
        )

        if alert:
            incident_links = (
                db.query(IncidentAlert)
                .filter(IncidentAlert.alert_id == alert_id)
                .all()
            )

            for link in incident_links:
                db.delete(link)

            db.delete(alert)

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


def cleanup_incident(incident_id: int):
    db = SessionLocal()

    try:
        incident = (
            db.query(Incident)
            .filter(Incident.id == incident_id)
            .first()
        )

        if incident:
            db.delete(incident)
            db.commit()

    finally:
        db.close()


def test_first_alert_creates_incident():
    alert_id, event_id = create_test_alert()

    try:
        db = SessionLocal()

        try:
            alert = (
                db.query(SecurityAlert)
                .filter(SecurityAlert.id == alert_id)
                .first()
            )

            incident = correlate_security_alert(
                db=db,
                alert=alert
            )

            assert incident is not None
            assert incident.agent_id == alert.agent_id
            assert incident.severity == alert.severity
            assert incident.status == "OPEN"

            link = (
                db.query(IncidentAlert)
                .filter(
                    IncidentAlert.incident_id == incident.id,
                    IncidentAlert.alert_id == alert.id
                )
                .first()
            )

            assert link is not None

            incident_id = incident.id

        finally:
            db.close()

        cleanup_incident(incident_id)

    finally:
        cleanup_alert(alert_id, event_id)


def test_matching_alert_attaches_to_existing_incident():
    first_alert_id, first_event_id = create_test_alert()

    second_alert_id, second_event_id = create_test_alert()

    try:
        db = SessionLocal()

        try:
            first_alert = (
                db.query(SecurityAlert)
                .filter(SecurityAlert.id == first_alert_id)
                .first()
            )

            first_incident = correlate_security_alert(
                db=db,
                alert=first_alert
            )

            second_alert = (
                db.query(SecurityAlert)
                .filter(SecurityAlert.id == second_alert_id)
                .first()
            )

            second_incident = correlate_security_alert(
                db=db,
                alert=second_alert
            )

            assert second_incident.id == first_incident.id

            links = (
                db.query(IncidentAlert)
                .filter(
                    IncidentAlert.incident_id == first_incident.id
                )
                .all()
            )

            assert len(links) == 2

            incident_id = first_incident.id

        finally:
            db.close()

        cleanup_incident(incident_id)

    finally:
        cleanup_alert(first_alert_id, first_event_id)
        cleanup_alert(second_alert_id, second_event_id)


def test_different_alert_type_creates_separate_incident():
    first_alert_id, first_event_id = create_test_alert(
        alert_type="TOOL_RATE_LIMIT"
    )

    second_alert_id, second_event_id = create_test_alert(
        alert_type="REPEATED_BLOCKED_ACTIONS"
    )

    try:
        db = SessionLocal()

        try:
            first_alert = (
                db.query(SecurityAlert)
                .filter(SecurityAlert.id == first_alert_id)
                .first()
            )

            first_incident = correlate_security_alert(
                db=db,
                alert=first_alert
            )

            second_alert = (
                db.query(SecurityAlert)
                .filter(SecurityAlert.id == second_alert_id)
                .first()
            )

            second_incident = correlate_security_alert(
                db=db,
                alert=second_alert
            )

            assert second_incident.id != first_incident.id

            first_incident_id = first_incident.id
            second_incident_id = second_incident.id

        finally:
            db.close()

        cleanup_incident(first_incident_id)
        cleanup_incident(second_incident_id)

    finally:
        cleanup_alert(first_alert_id, first_event_id)
        cleanup_alert(second_alert_id, second_event_id)


def test_different_agent_creates_separate_incident():
    first_alert_id, first_event_id = create_test_alert(
        agent_id=1
    )

    second_alert_id, second_event_id = create_test_alert(
        agent_id=2
    )

    try:
        db = SessionLocal()

        try:
            first_alert = (
                db.query(SecurityAlert)
                .filter(SecurityAlert.id == first_alert_id)
                .first()
            )

            first_incident = correlate_security_alert(
                db=db,
                alert=first_alert
            )

            second_alert = (
                db.query(SecurityAlert)
                .filter(SecurityAlert.id == second_alert_id)
                .first()
            )

            second_incident = correlate_security_alert(
                db=db,
                alert=second_alert
            )

            assert second_incident.id != first_incident.id

            first_incident_id = first_incident.id
            second_incident_id = second_incident.id

        finally:
            db.close()

        cleanup_incident(first_incident_id)
        cleanup_incident(second_incident_id)

    finally:
        cleanup_alert(first_alert_id, first_event_id)
        cleanup_alert(second_alert_id, second_event_id)


def test_resolved_incident_is_not_reused():
    alert_id, event_id = create_test_alert()

    try:
        db = SessionLocal()

        try:
            alert = (
                db.query(SecurityAlert)
                .filter(SecurityAlert.id == alert_id)
                .first()
            )

            first_incident = correlate_security_alert(
                db=db,
                alert=alert
            )

            first_incident.status = "RESOLVED"
            db.commit()

            second_alert_id, second_event_id = create_test_alert()

            second_alert = (
                db.query(SecurityAlert)
                .filter(SecurityAlert.id == second_alert_id)
                .first()
            )

            second_incident = correlate_security_alert(
                db=db,
                alert=second_alert
            )

            assert second_incident.id != first_incident.id

            first_incident_id = first_incident.id
            second_incident_id = second_incident.id

        finally:
            db.close()

        cleanup_incident(first_incident_id)
        cleanup_incident(second_incident_id)
        cleanup_alert(second_alert_id, second_event_id)

    finally:
        cleanup_alert(alert_id, event_id)

def test_security_event_automatically_creates_alert_and_incident():
    db = SessionLocal()

    try:
        event_data = SecurityEventCreate(
            agent_id=1,
            event_type="TOOL_ACTION",
            action="READ",
            decision="BLOCK",
            reason="Runtime tool action rate limit exceeded",
            event_metadata=None
        )

        event = create_security_event(
            event_data=event_data,
            db=db
        )

        alert = (
            db.query(SecurityAlert)
            .filter(
                SecurityAlert.security_event_id == event.id,
                SecurityAlert.alert_type == "TOOL_RATE_LIMIT"
            )
            .first()
        )

        assert alert is not None

        incident_alert = (
            db.query(IncidentAlert)
            .filter(
                IncidentAlert.alert_id == alert.id
            )
            .first()
        )

        assert incident_alert is not None

        incident = (
            db.query(Incident)
            .filter(
                Incident.id == incident_alert.incident_id
            )
            .first()
        )

        assert incident is not None
        assert incident.agent_id == 1
        assert incident.severity == "HIGH"
        assert incident.status == "OPEN"

    finally:
        if "incident" in locals() and incident is not None:
            db.delete(incident)
            db.commit()

        if "alert" in locals() and alert is not None:
            db.delete(alert)
            db.commit()

        db.delete(event)
        db.commit()
        db.close()        