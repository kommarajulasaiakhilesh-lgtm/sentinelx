
from datetime import datetime, timedelta, timezone
from unittest.mock import patch
from uuid import uuid4

from app.main import app  # noqa: F401
from app.db.database import SessionLocal
from app.models.agent import Agent
from app.models.behavioral_baseline_configuration import (
    BehavioralBaselineConfiguration,
)
from app.models.incident import Incident
from app.models.incident_alert import IncidentAlert
from app.models.security_alert import SecurityAlert
from app.models.security_event import SecurityEvent
from app.schemas.security_event import SecurityEventCreate
from app.services.security_event_service import create_security_event


def create_test_agent(db):
    agent = Agent(
        owner_id=7,
        name=f"Anomaly Integration Test {uuid4().hex[:8]}",
        description="Temporary agent for behavioral anomaly integration tests",
    )
    db.add(agent)
    db.commit()
    db.refresh(agent)
    return agent


def cleanup_test_records(
    db,
    agent_id=None,
    event_ids=None,
    alert_ids=None,
    incident_ids=None,
    configuration_ids=None,
):
    event_ids = event_ids or []
    alert_ids = alert_ids or []
    incident_ids = incident_ids or []
    configuration_ids = configuration_ids or []

    try:
        if incident_ids:
            db.query(IncidentAlert).filter(
                IncidentAlert.incident_id.in_(incident_ids)
            ).delete(synchronize_session=False)

        if alert_ids:
            db.query(IncidentAlert).filter(
                IncidentAlert.alert_id.in_(alert_ids)
            ).delete(synchronize_session=False)

        if incident_ids:
            db.query(Incident).filter(
                Incident.id.in_(incident_ids)
            ).delete(synchronize_session=False)

        if alert_ids:
            db.query(SecurityAlert).filter(
                SecurityAlert.id.in_(alert_ids)
            ).delete(synchronize_session=False)

        if event_ids:
            db.query(SecurityEvent).filter(
                SecurityEvent.id.in_(event_ids)
            ).delete(synchronize_session=False)

        if configuration_ids:
            db.query(BehavioralBaselineConfiguration).filter(
                BehavioralBaselineConfiguration.id.in_(
                    configuration_ids
                )
            ).delete(synchronize_session=False)

        if agent_id is not None:
            db.query(Agent).filter(
                Agent.id == agent_id
            ).delete(synchronize_session=False)

        db.commit()
    except Exception:
        db.rollback()
        raise


def test_event_ingestion_continues_when_baseline_configuration_is_missing():
    db = SessionLocal()
    agent = None
    event_ids = []
    configuration_states = []

    try:
        agent = create_test_agent(db)

        configurations = (
            db.query(BehavioralBaselineConfiguration)
            .filter(
                BehavioralBaselineConfiguration.owner_id
                == agent.owner_id,
                BehavioralBaselineConfiguration.enabled.is_(True),
            )
            .all()
        )

        configuration_states = [
            (configuration.id, configuration.enabled)
            for configuration in configurations
        ]

        try:
            for configuration in configurations:
                configuration.enabled = False
            db.commit()

            with (
                patch(
                    "app.services.security_event_service."
                    "detect_security_alert",
                    return_value=None,
                ),
                patch(
                    "app.services.security_event_service."
                    "correlate_security_alert",
                ),
                patch(
                    "app.services.security_alert_service."
                    "detect_behavioral_anomalies",
                    side_effect=ValueError(
                        "No enabled baseline configuration"
                    ),
                ),
            ):
                event = create_security_event(
                    event_data=SecurityEventCreate(
                        agent_id=agent.id,
                        event_type="INTEGRATION_TEST",
                        action="READ",
                        decision="ALLOW",
                        reason="Missing baseline configuration test",
                    ),
                    db=db,
                )

            event_ids.append(event.id)

            assert event.id is not None
            assert event.event_type == "INTEGRATION_TEST"

        finally:
            for configuration_id, enabled in configuration_states:
                configuration = (
                    db.query(BehavioralBaselineConfiguration)
                    .filter(
                        BehavioralBaselineConfiguration.id
                        == configuration_id
                    )
                    .first()
                )
                if configuration is not None:
                    configuration.enabled = enabled
            db.commit()

    finally:
        cleanup_test_records(
            db,
            agent_id=agent.id if agent else None,
            event_ids=event_ids,
        )
        db.close()


def test_behavioral_anomaly_alert_is_created_and_correlated():
    db = SessionLocal()
    agent = None
    event_ids = []
    alert_ids = []
    incident_ids = []

    try:
        agent = create_test_agent(db)
        reference_time = datetime.now(timezone.utc)

        anomaly_result = {
            "anomaly_detected": True,
            "baseline_window": {
                "start_time": reference_time - timedelta(seconds=3600),
                "end_time": reference_time - timedelta(seconds=300),
            },
            "observation_window": {
                "start_time": reference_time - timedelta(seconds=300),
                "end_time": reference_time,
            },
            "anomalies": [
                {
                    "metric": "activity_rate",
                    "baseline_rate": 0.001,
                    "observed_rate": 0.01,
                    "deviation_percent": 900.0,
                    "threshold_percent": 50,
                    "reason": "Observed activity exceeded the configured baseline",
                }
            ],
        }

        with (
            patch(
                "app.services.security_event_service."
                "detect_security_alert",
                return_value=None,
            ),
            patch(
                "app.services.security_alert_service."
                "detect_behavioral_anomalies",
                return_value=anomaly_result,
            ),
        ):
            event = create_security_event(
                event_data=SecurityEventCreate(
                    agent_id=agent.id,
                    event_type="OTHER",
                    action="READ",
                    decision="ALLOW",
                    reason="Behavioral anomaly integration test",
                ),
                db=db,
            )

        event_ids.append(event.id)

        alert = (
            db.query(SecurityAlert)
            .filter(
                SecurityAlert.security_event_id == event.id,
                SecurityAlert.alert_type == "BEHAVIORAL_ANOMALY",
            )
            .first()
        )

        assert alert is not None, (
            "Expected a BEHAVIORAL_ANOMALY alert for the test event"
        )
        alert_ids.append(alert.id)

        assert alert.severity == "HIGH"
        assert alert.title == "Behavioral Anomaly Detected"
        assert alert.description is not None
        assert "Metric: activity_rate" in alert.description
        assert "900.0%" in alert.description

        links = (
            db.query(IncidentAlert)
            .filter(IncidentAlert.alert_id == alert.id)
            .all()
        )

        assert links, "Expected the behavioral alert to be correlated"

        incident_ids.extend(
            link.incident_id for link in links
        )

        incidents = (
            db.query(Incident)
            .filter(Incident.id.in_(incident_ids))
            .all()
        )

        assert incidents, "Expected an incident for the anomaly alert"

    finally:
        cleanup_test_records(
            db,
            agent_id=agent.id if agent else None,
            event_ids=event_ids,
            alert_ids=alert_ids,
            incident_ids=incident_ids,
        )
        db.close()
