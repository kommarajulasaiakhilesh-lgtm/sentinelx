
from fastapi.testclient import TestClient

from app.main import app
from app.api.dependencies import get_current_user
from app.db.database import SessionLocal
from app.models.user import User


client = TestClient(app)


def get_test_user():
    db = SessionLocal()

    try:
        user = (
            db.query(User)
            .filter(User.id == 4)
            .first()
        )

        return user

    finally:
        db.close()


def setup_user_override():
    user = get_test_user()

    app.dependency_overrides[get_current_user] = lambda: user


def teardown_user_override():
    app.dependency_overrides.clear()


def test_security_events_list():
    setup_user_override()

    try:
        response = client.get(
            "/api/security-events"
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


def test_security_events_filter_by_decision():
    setup_user_override()

    try:
        response = client.get(
            "/api/security-events?decision=BLOCK"
        )

        assert response.status_code == 200

        data = response.json()

        for event in data["items"]:
            assert event["decision"] == "BLOCK"

    finally:
        teardown_user_override()


def test_security_events_pagination():
    setup_user_override()

    try:
        response = client.get(
            "/api/security-events?page=1&page_size=2"
        )

        assert response.status_code == 200

        data = response.json()

        assert data["page"] == 1
        assert data["page_size"] == 2
        assert len(data["items"]) <= 2
        assert data["total"] >= len(data["items"])
        assert data["pages"] >= 1

    finally:
        teardown_user_override()


def test_security_events_filter_by_action():
    setup_user_override()

    try:
        response = client.get(
            "/api/security-events?action=WARN"
        )

        assert response.status_code == 200

        data = response.json()

        for event in data["items"]:
            assert event["action"] == "WARN"

    finally:
        teardown_user_override()


def test_security_events_combined_filters():
    setup_user_override()

    try:
        response = client.get(
            "/api/security-events"
            "?event_type=POLICY_CHECK"
            "&decision=ALLOW"
        )

        assert response.status_code == 200

        data = response.json()

        for event in data["items"]:
            assert event["event_type"] == "POLICY_CHECK"
            assert event["decision"] == "ALLOW"

    finally:
        teardown_user_override()


def test_security_events_only_show_owned_agents():
    setup_user_override()

    try:
        response = client.get(
            "/api/security-events"
        )

        assert response.status_code == 200

        data = response.json()

        for event in data["items"]:
            assert event["agent_id"] == 1

    finally:
        teardown_user_override()

