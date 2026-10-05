from uuid import uuid4

from app.main import app

from app.db.database import SessionLocal
from app.models.agent import Agent
from app.models.incident import Incident
from app.models.incident_alert import IncidentAlert
from app.models.incident_timeline import IncidentTimelineEntry
from app.models.security_alert import SecurityAlert
from app.models.security_event import SecurityEvent
from app.models.webhook_delivery import WebhookDelivery

from app.services.security_alert_service import create_security_alert
from app.services.incident_correlation_service import correlate_security_alert
from app.services.incident_service import (
    add_incident_timeline_entry,
    create_incident,
    create_response_action,
    update_incident,
)
from app.services.webhook_service import create_webhook_endpoint


TEST_USER_ID = 4
TEST_AGENT_ID = 1


def test_phase15_event_to_alert_to_incident_to_timeline():
    db = SessionLocal()

    event = None
    alert = None
    incident = None

    try:
        agent = (
            db.query(Agent)
            .filter(
                Agent.id == TEST_AGENT_ID,
                Agent.owner_id == TEST_USER_ID,
            )
            .first()
        )

        assert agent is not None

        event = SecurityEvent(
            agent_id=agent.id,
            event_type="P15_INT_EVENT",
            action="TEST",
            decision="BLOCK",
            reason="Phase 15 integration event",
            event_metadata=None,
        )

        db.add(event)
        db.commit()
        db.refresh(event)

        alert = create_security_alert(
            db=db,
            security_event=event,
            alert_type="P15_INT_ALERT",
            severity="HIGH",
            title="Phase 15 integration alert",
            description="Event to alert integration test",
        )

        incident = correlate_security_alert(
            db=db,
            alert=alert,
        )

        assert incident is not None
        assert incident.agent_id == agent.id

        incident_alert = (
            db.query(IncidentAlert)
            .filter(
                IncidentAlert.incident_id == incident.id,
                IncidentAlert.alert_id == alert.id,
            )
            .first()
        )

        assert incident_alert is not None

        timeline_entry = add_incident_timeline_entry(
            db=db,
            incident_id=incident.id,
            entry_type="EVENT_DETECTED",
            description="Phase 15 integration event detected",
            created_by_user_id=TEST_USER_ID,
        )

        db.commit()

        assert timeline_entry.incident_id == incident.id
        assert timeline_entry.entry_type == "EVENT_DETECTED"

        stored_timeline = (
            db.query(IncidentTimelineEntry)
            .filter(
                IncidentTimelineEntry.id == timeline_entry.id,
            )
            .first()
        )

        assert stored_timeline is not None

    finally:
        if incident is not None:
            db.query(IncidentTimelineEntry).filter(
                IncidentTimelineEntry.incident_id == incident.id
            ).delete(synchronize_session=False)

            db.query(IncidentAlert).filter(
                IncidentAlert.incident_id == incident.id
            ).delete(synchronize_session=False)

            db.delete(incident)
            db.commit()

        if alert is not None:
            db.delete(alert)
            db.commit()

        if event is not None:
            db.delete(event)
            db.commit()

        db.close()


def test_phase15_incident_transition_creates_webhook_delivery():
    db = SessionLocal()

    incident = None
    endpoint = None

    try:
        incident = create_incident(
            db=db,
            agent_id=TEST_AGENT_ID,
            user_id=TEST_USER_ID,
            title="Phase 15 webhook integration incident",
            description="Testing incident transition integration",
            severity="HIGH",
        )

        assert incident is not None

        endpoint = create_webhook_endpoint(
            db=db,
            owner_id=TEST_USER_ID,
            name=f"Phase15-{uuid4().hex}",
            url="https://example.com/sentinelx-test",
            secret="integration-secret",
        )

        updated = update_incident(
            db=db,
            incident_id=incident.id,
            user_id=TEST_USER_ID,
            status="CONTAINED",
        )

        assert updated is not None
        assert updated.status == "CONTAINED"

        delivery = (
            db.query(WebhookDelivery)
            .filter(
                WebhookDelivery.endpoint_id == endpoint.id,
                WebhookDelivery.event_type == "INCIDENT_CONTAINED",
            )
            .first()
        )

        assert delivery is not None
        assert delivery.status == "PENDING"
        assert delivery.attempt_count == 0

    finally:
        if endpoint is not None:
            db.query(WebhookDelivery).filter(
                WebhookDelivery.endpoint_id == endpoint.id
            ).delete(synchronize_session=False)

            db.delete(endpoint)
            db.commit()

        if incident is not None:
            db.query(IncidentTimelineEntry).filter(
                IncidentTimelineEntry.incident_id == incident.id
            ).delete(synchronize_session=False)

            db.query(IncidentAlert).filter(
                IncidentAlert.incident_id == incident.id
            ).delete(synchronize_session=False)

            db.delete(incident)
            db.commit()

        db.close()


def test_phase15_response_action_is_authorized_and_audited():
    db = SessionLocal()

    incident = None
    action = None

    try:
        incident = create_incident(
            db=db,
            agent_id=TEST_AGENT_ID,
            user_id=TEST_USER_ID,
            title="Phase 15 response integration incident",
            description="Testing controlled response",
            severity="CRITICAL",
        )

        assert incident is not None

        action = create_response_action(
            db=db,
            incident_id=incident.id,
            user_id=TEST_USER_ID,
            action_type="SUSPEND_AGENT",
            agent_id=TEST_AGENT_ID,
            tool_id=None,
            api_key_id=None,
            reason="Integration test authorization",
            result="SUCCESS",
            details="Authorized by integration test",
        )

        assert action is not None
        assert action.incident_id == incident.id
        assert action.action_type == "SUSPEND_AGENT"
        assert action.authorized_by_user_id == TEST_USER_ID
        assert action.result == "SUCCESS"

        timeline_entry = add_incident_timeline_entry(
            db=db,
            incident_id=incident.id,
            entry_type="RESPONSE_ACTION",
            description="SUSPEND_AGENT executed",
            created_by_user_id=TEST_USER_ID,
        )

        db.commit()

        assert timeline_entry.incident_id == incident.id
        assert timeline_entry.entry_type == "RESPONSE_ACTION"

    finally:
        if incident is not None:
            db.query(IncidentTimelineEntry).filter(
                IncidentTimelineEntry.incident_id == incident.id
            ).delete(synchronize_session=False)

            db.query(IncidentAlert).filter(
                IncidentAlert.incident_id == incident.id
            ).delete(synchronize_session=False)

            if action is not None:
                db.delete(action)

            db.delete(incident)
            db.commit()

        db.close()


def test_phase15_incident_ownership_is_enforced():
    db = SessionLocal()

    incident = None

    try:
        incident = create_incident(
            db=db,
            agent_id=TEST_AGENT_ID,
            user_id=TEST_USER_ID,
            title="Phase 15 ownership integration incident",
            description="Testing ownership boundary",
            severity="MEDIUM",
        )

        assert incident is not None

        unauthorized_incident = (
            db.query(Incident)
            .join(Agent, Agent.id == Incident.agent_id)
            .filter(
                Incident.id == incident.id,
                Agent.owner_id == 999999,
            )
            .first()
        )

        assert unauthorized_incident is None

        unauthorized_action = create_response_action(
            db=db,
            incident_id=incident.id,
            user_id=999999,
            action_type="SUSPEND_AGENT",
            agent_id=TEST_AGENT_ID,
            tool_id=None,
            api_key_id=None,
            reason="Unauthorized integration test",
            result="SUCCESS",
            details=None,
        )

        assert unauthorized_action is None

    finally:
        if incident is not None:
            db.query(IncidentTimelineEntry).filter(
                IncidentTimelineEntry.incident_id == incident.id
            ).delete(synchronize_session=False)

            db.query(IncidentAlert).filter(
                IncidentAlert.incident_id == incident.id
            ).delete(synchronize_session=False)

            db.delete(incident)
            db.commit()

        db.close()
