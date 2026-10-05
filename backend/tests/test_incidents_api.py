from fastapi.testclient import TestClient

from app.main import app
from app.api.dependencies import get_current_user
from app.db.database import SessionLocal
from app.models.user import User
from app.models.agent import Agent
from app.models.incident import Incident


client = TestClient(app)


def get_test_user():
    db = SessionLocal()
    try:
        return (
            db.query(User)
            .filter(User.id == 4)
            .first()
        )
    finally:
        db.close()


def setup_user_override():
    user = get_test_user()

    if user is None:
        raise RuntimeError("Test user with id=4 was not found")

    app.dependency_overrides[get_current_user] = lambda: user


def teardown_user_override():
    app.dependency_overrides.clear()


def cleanup_incident(incident_id):
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


def test_create_incident():
    setup_user_override()

    incident_id = None

    try:
        response = client.post(
            "/api/incidents",
            json={
                "agent_id": 1,
                "title": "Test Incident",
                "description": "Test incident created by API test",
                "severity": "HIGH"
            }
        )

        assert response.status_code == 201

        data = response.json()

        assert data["agent_id"] == 1
        assert data["title"] == "Test Incident"
        assert data["description"] == "Test incident created by API test"
        assert data["severity"] == "HIGH"
        assert data["status"] == "OPEN"

        incident_id = data["id"]

    finally:
        if incident_id is not None:
            cleanup_incident(incident_id)

        teardown_user_override()


def test_list_incidents():
    setup_user_override()

    incident_id = None

    try:
        db = SessionLocal()

        incident = Incident(
            agent_id=1,
            title="List Test Incident",
            description="Incident for list API test",
            severity="MEDIUM",
            status="OPEN"
        )

        db.add(incident)
        db.commit()
        db.refresh(incident)

        incident_id = incident.id

        db.close()

        response = client.get(
            "/api/incidents"
        )

        assert response.status_code == 200

        data = response.json()

        assert "items" in data
        assert "page" in data
        assert "page_size" in data
        assert "total" in data
        assert "pages" in data

        assert data["page"] == 1
        assert data["page_size"] == 10
        assert data["total"] >= 1

        incident_ids = [
            item["id"]
            for item in data["items"]
        ]

        assert incident_id in incident_ids

    finally:
        if incident_id is not None:
            cleanup_incident(incident_id)

        teardown_user_override()


def test_get_incident():
    setup_user_override()

    incident_id = None

    try:
        db = SessionLocal()

        incident = Incident(
            agent_id=1,
            title="Get Test Incident",
            description="Incident for detail API test",
            severity="HIGH",
            status="OPEN"
        )

        db.add(incident)
        db.commit()
        db.refresh(incident)

        incident_id = incident.id

        db.close()

        response = client.get(
            f"/api/incidents/{incident_id}"
        )

        assert response.status_code == 200

        data = response.json()

        assert data["id"] == incident_id
        assert data["agent_id"] == 1
        assert data["title"] == "Get Test Incident"
        assert data["severity"] == "HIGH"
        assert data["status"] == "OPEN"

    finally:
        if incident_id is not None:
            cleanup_incident(incident_id)

        teardown_user_override()


def test_update_incident():
    setup_user_override()

    incident_id = None

    try:
        db = SessionLocal()

        incident = Incident(
            agent_id=1,
            title="Update Test Incident",
            description="Original description",
            severity="MEDIUM",
            status="OPEN"
        )

        db.add(incident)
        db.commit()
        db.refresh(incident)

        incident_id = incident.id

        db.close()

        response = client.patch(
            f"/api/incidents/{incident_id}",
            json={
                "title": "Updated Incident",
                "description": "Updated description",
                "severity": "CRITICAL",
                "status": "INVESTIGATING"
            }
        )

        assert response.status_code == 200

        data = response.json()

        assert data["id"] == incident_id
        assert data["title"] == "Updated Incident"
        assert data["description"] == "Updated description"
        assert data["severity"] == "CRITICAL"
        assert data["status"] == "INVESTIGATING"

    finally:
        if incident_id is not None:
            cleanup_incident(incident_id)

        teardown_user_override()


def test_create_incident_for_unowned_agent():
    setup_user_override()

    try:
        db = SessionLocal()

        other_agent = (
            db.query(Agent)
            .filter(
                Agent.owner_id != 4
            )
            .first()
        )

        db.close()

        if other_agent is None:
            return

        response = client.post(
            "/api/incidents",
            json={
                "agent_id": other_agent.id,
                "title": "Unauthorized Incident",
                "description": "Should not be created",
                "severity": "HIGH"
            }
        )

        assert response.status_code == 404

    finally:
        teardown_user_override()


def test_get_nonexistent_incident():
    setup_user_override()

    try:
        response = client.get(
            "/api/incidents/999999999"
        )

        assert response.status_code == 404
        assert response.json()["detail"] == "Incident not found"

    finally:
        teardown_user_override()