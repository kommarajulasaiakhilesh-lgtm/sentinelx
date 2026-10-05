from fastapi.testclient import TestClient

from app.main import app
from app.api.dependencies import get_current_user
from app.db.database import SessionLocal
from app.models.incident import Incident
from app.models.incident_timeline import IncidentTimelineEntry
from app.models.user import User


client = TestClient(app)


def get_test_user(user_id: int = 4):
    db = SessionLocal()
    try:
        return (
            db.query(User)
            .filter(User.id == user_id)
            .first()
        )
    finally:
        db.close()


def setup_user_override(user_id: int = 4):
    user = get_test_user(user_id)

    if user is None:
        raise RuntimeError(f"Test user with id={user_id} was not found")

    app.dependency_overrides[get_current_user] = lambda: user


def teardown_user_override():
    app.dependency_overrides.clear()


def cleanup_incident(incident_id):
    db = SessionLocal()
    try:
        entries = (
            db.query(IncidentTimelineEntry)
            .filter(IncidentTimelineEntry.incident_id == incident_id)
            .all()
        )

        for entry in entries:
            db.delete(entry)

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


def test_create_incident_timeline_entry():
    setup_user_override()
    incident_id = None

    try:
        db = SessionLocal()
        incident = Incident(
            agent_id=1,
            title="Timeline Test Incident",
            description="incident for timeline test",
            severity="HIGH",
            status="OPEN"
        )
        db.add(incident)
        db.commit()
        db.refresh(incident)
        incident_id = incident.id
        db.close()

        response = client.post(
            f"/api/incidents/{incident_id}/timeline",
            json={
                "entry_type": "OPERATOR_NOTE",
                "description": "Operator added investigation note"
            }
        )

        assert response.status_code == 201

        data = response.json()
        assert data["incident_id"] == incident_id
        assert data["entry_type"] == "OPERATOR_NOTE"
        assert data["description"] == "Operator added investigation note"
        assert data["created_by_user_id"] == 4

    finally:
        if incident_id is not None:
            cleanup_incident(incident_id)
        teardown_user_override()


def test_get_incident_timeline():
    setup_user_override()
    incident_id = None

    try:
        db = SessionLocal()
        incident = Incident(
            agent_id=1,
            title="Timeline Retrieval",
            description="incident for retrieval test",
            severity="MEDIUM",
            status="OPEN"
        )
        db.add(incident)
        db.commit()
        db.refresh(incident)
        incident_id = incident.id

        entry = IncidentTimelineEntry(
            incident_id=incident.id,
            entry_type="EVENT_DETECTED",
            description="Security event detected",
            created_by_user_id=None
        )
        db.add(entry)
        db.commit()
        db.refresh(entry)
        db.close()

        response = client.get(
            f"/api/incidents/{incident_id}/timeline"
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
        assert any(item["entry_type"] == "EVENT_DETECTED" for item in data)

    finally:
        if incident_id is not None:
            cleanup_incident(incident_id)
        teardown_user_override()


def test_incident_timeline_ownership_isolation():
    setup_user_override(user_id=4)
    other_user = get_test_user(user_id=5)
    incident_id = None

    if other_user is None:
        teardown_user_override()
        return

    try:
        db = SessionLocal()
        other_agent = (
            db.query(Incident)
            .filter(Incident.agent_id == 2)
            .first()
        )

        if other_agent is None:
            other_agent = Incident(
                agent_id=2,
                title="Other user incident",
                description="should be inaccessible",
                severity="HIGH",
                status="OPEN"
            )
            db.add(other_agent)
            db.commit()
            db.refresh(other_agent)

        incident_id = other_agent.id

        db.add(IncidentTimelineEntry(
            incident_id=incident_id,
            entry_type="OPERATOR_NOTE",
            description="Should not be visible",
            created_by_user_id=other_user.id
        ))
        db.commit()
        db.close()

        response = client.get(
            f"/api/incidents/{incident_id}/timeline"
        )

        assert response.status_code == 404
        assert response.json()["detail"] == "Incident not found"

    finally:
        if incident_id is not None:
            cleanup_incident(incident_id)
        teardown_user_override()
