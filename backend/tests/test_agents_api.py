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


def test_update_agent_rejects_invalid_status():
    setup_user_override()

    try:
        response = client.patch(
            "/api/agents/1/status",
            json={
                "status": "INVALID"
            }
        )

        assert response.status_code == 422

    finally:
        teardown_user_override()


def test_create_agent_api_key_handles_selector_failure(
    monkeypatch
):
    setup_user_override()

    try:
        monkeypatch.setattr(
            "app.api.agents.extract_key_selector",
            lambda raw_api_key: None
        )

        response = client.post(
            "/api/agents/1/api-keys"
        )

        assert response.status_code == 500
        assert response.json()["detail"] == (
            "Failed to generate agent API key"
        )

    finally:
        teardown_user_override()