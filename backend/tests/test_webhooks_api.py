from fastapi.testclient import TestClient

from app.api.dependencies import get_current_user
from app.db.database import SessionLocal
from app.main import app
from app.models.user import User
from app.models.webhook_endpoint import WebhookEndpoint


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


def cleanup_webhooks():
    db = SessionLocal()

    try:
        db.query(WebhookEndpoint).filter(
            WebhookEndpoint.owner_id == 4
        ).delete(
            synchronize_session=False
        )

        db.commit()

    finally:
        db.close()


def test_create_webhook():
    setup_user_override()

    try:
        response = client.post(
            "/api/webhooks",
            json={
                "name": "Test Security Webhook",
                "url": "https://example.com/security",
                "secret": "test-secret",
            },
        )

        assert response.status_code == 201

        data = response.json()

        assert data["owner_id"] == 4
        assert data["name"] == "Test Security Webhook"
        assert data["url"] == "https://example.com/security"
        assert data["enabled"] is True

    finally:
        teardown_user_override()
        cleanup_webhooks()


def test_list_webhooks():
    setup_user_override()

    try:
        create_response = client.post(
            "/api/webhooks",
            json={
                "name": "List Test Webhook",
                "url": "https://example.com/list",
            },
        )

        assert create_response.status_code == 201

        response = client.get(
            "/api/webhooks"
        )

        assert response.status_code == 200

        data = response.json()

        assert isinstance(data, list)
        assert any(
            webhook["name"] == "List Test Webhook"
            for webhook in data
        )

    finally:
        teardown_user_override()
        cleanup_webhooks()


def test_get_webhook():
    setup_user_override()

    try:
        create_response = client.post(
            "/api/webhooks",
            json={
                "name": "Get Test Webhook",
                "url": "https://example.com/get",
            },
        )

        assert create_response.status_code == 201

        endpoint_id = create_response.json()["id"]

        response = client.get(
            f"/api/webhooks/{endpoint_id}"
        )

        assert response.status_code == 200
        assert response.json()["id"] == endpoint_id

    finally:
        teardown_user_override()
        cleanup_webhooks()


def test_get_missing_webhook_returns_404():
    setup_user_override()

    try:
        response = client.get(
            "/api/webhooks/999999999"
        )

        assert response.status_code == 404
        assert response.json()["detail"] == (
            "Webhook endpoint not found"
        )

    finally:
        teardown_user_override()


def test_update_webhook():
    setup_user_override()

    try:
        create_response = client.post(
            "/api/webhooks",
            json={
                "name": "Update Test Webhook",
                "url": "https://example.com/update",
            },
        )

        assert create_response.status_code == 201

        endpoint_id = create_response.json()["id"]

        response = client.patch(
            f"/api/webhooks/{endpoint_id}",
            json={
                "name": "Updated Webhook",
                "url": "https://example.com/updated",
                "enabled": False,
            },
        )

        assert response.status_code == 200

        data = response.json()

        assert data["name"] == "Updated Webhook"
        assert data["url"] == "https://example.com/updated"
        assert data["enabled"] is False

    finally:
        teardown_user_override()
        cleanup_webhooks()


def test_delete_webhook():
    setup_user_override()

    try:
        create_response = client.post(
            "/api/webhooks",
            json={
                "name": "Delete Test Webhook",
                "url": "https://example.com/delete",
            },
        )

        assert create_response.status_code == 201

        endpoint_id = create_response.json()["id"]

        response = client.delete(
            f"/api/webhooks/{endpoint_id}"
        )

        assert response.status_code == 204

        get_response = client.get(
            f"/api/webhooks/{endpoint_id}"
        )

        assert get_response.status_code == 404

    finally:
        teardown_user_override()
        cleanup_webhooks()


def test_webhook_requires_authentication():
    app.dependency_overrides.clear()

    response = client.get(
        "/api/webhooks"
    )

    assert response.status_code == 401