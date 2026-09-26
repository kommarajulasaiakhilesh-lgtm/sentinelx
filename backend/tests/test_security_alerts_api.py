from fastapi.testclient import TestClient

from app.main import app
from app.api.dependencies import get_current_user
from app.db.database import SessionLocal
from app.models.user import User
from app.models.security_alert import SecurityAlert
from app.models.security_event import SecurityEvent


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
    app.dependency_overrides[get_current_user] = lambda: user


def teardown_user_override():
    app.dependency_overrides.clear()


def create_test_alert():
    db = SessionLocal()

    try:
        event = SecurityEvent(
            agent_id=1,
            event_type="TOOL_ACTION",
            action="BLOCK",
            decision="BLOCK",
            reason="Runtime tool action rate limit exceeded"
        )

        db.add(event)
        db.commit()
        db.refresh(event)

        alert = SecurityAlert(
            agent_id=1,
            security_event_id=event.id,
            alert_type="TOOL_RATE_LIMIT",
            severity="HIGH",
            title="Test security alert",
            description="Test alert",
            status="OPEN"
        )

        db.add(alert)
        db.commit()
        db.refresh(alert)

        return alert.id, event.id

    finally:
        db.close()


def cleanup_test_alert(alert_id, event_id):
    db = SessionLocal()

    try:
        alert = (
            db.query(SecurityAlert)
            .filter(SecurityAlert.id == alert_id)
            .first()
        )

        if alert:
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


def test_list_security_alerts():
    setup_user_override()

    try:
        response = client.get(
            "/api/security-alerts"
        )

        assert response.status_code == 200

        data = response.json()

        assert "items" in data
        assert "page" in data
        assert "page_size" in data
        assert "total" in data
        assert "pages" in data

    finally:
        teardown_user_override()


def test_get_security_alert():
    alert_id, event_id = create_test_alert()

    setup_user_override()

    try:
        response = client.get(
            f"/api/security-alerts/{alert_id}"
        )

        assert response.status_code == 200

        data = response.json()

        assert data["id"] == alert_id
        assert data["agent_id"] == 1
        assert data["severity"] == "HIGH"
        assert data["status"] == "OPEN"

    finally:
        teardown_user_override()
        cleanup_test_alert(alert_id, event_id)


def test_filter_security_alerts_by_severity():
    alert_id, event_id = create_test_alert()

    setup_user_override()

    try:
        response = client.get(
            "/api/security-alerts?severity=HIGH"
        )

        assert response.status_code == 200

        data = response.json()

        for alert in data["items"]:
            assert alert["severity"] == "HIGH"

    finally:
        teardown_user_override()
        cleanup_test_alert(alert_id, event_id)


def test_update_security_alert_status():
    alert_id, event_id = create_test_alert()

    setup_user_override()

    try:
        response = client.patch(
            f"/api/security-alerts/{alert_id}/status"
            "?status=ACKNOWLEDGED"
        )

        assert response.status_code == 200

        data = response.json()

        assert data["status"] == "ACKNOWLEDGED"

    finally:
        teardown_user_override()
        cleanup_test_alert(alert_id, event_id)


def test_invalid_security_alert_status():
    alert_id, event_id = create_test_alert()

    setup_user_override()

    try:
        response = client.patch(
            f"/api/security-alerts/{alert_id}/status"
            "?status=INVALID"
        )

        assert response.status_code == 400

    finally:
        teardown_user_override()
        cleanup_test_alert(alert_id, event_id)


def test_resolve_security_alert():
    alert_id, event_id = create_test_alert()

    setup_user_override()

    try:
        response = client.patch(
            f"/api/security-alerts/{alert_id}/status"
            "?status=RESOLVED"
        )

        assert response.status_code == 200

        data = response.json()

        assert data["status"] == "RESOLVED"

    finally:
        teardown_user_override()
        cleanup_test_alert(alert_id, event_id)