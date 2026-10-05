import hashlib
import hmac
import json

import pytest

from app.main import app
from app.db.database import SessionLocal
from app.models.webhook_endpoint import WebhookEndpoint
from app.services.webhook_service import (
    SUPPORTED_WEBHOOK_EVENTS,
    build_webhook_signature,
    create_webhook_delivery,
)

def create_test_webhook_endpoint():
    db = SessionLocal()

    try:
        endpoint = WebhookEndpoint(
            owner_id=4,
            name="Test Webhook",
            url="https://example.com/webhook",
            secret="test-secret",
            enabled=True,
        )

        db.add(endpoint)
        db.commit()
        db.refresh(endpoint)

        return endpoint.id

    finally:
        db.close()


def cleanup_webhook_endpoint(endpoint_id):
    db = SessionLocal()

    try:
        endpoint = (
            db.query(WebhookEndpoint)
            .filter(WebhookEndpoint.id == endpoint_id)
            .first()
        )

        if endpoint:
            db.delete(endpoint)
            db.commit()

    finally:
        db.close()


def test_supported_webhook_events():
    assert SUPPORTED_WEBHOOK_EVENTS == {
        "INCIDENT_CREATED",
        "INCIDENT_SEVERITY_CHANGED",
        "INCIDENT_CONTAINED",
        "INCIDENT_RESOLVED",
    }


def test_build_webhook_signature():
    secret = "test-secret"

    payload = {
        "incident_id": 123,
        "severity": "HIGH",
        "status": "OPEN",
    }

    expected_body = json.dumps(
        payload,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")

    expected_signature = hmac.new(
        secret.encode("utf-8"),
        expected_body,
        hashlib.sha256,
    ).hexdigest()

    assert build_webhook_signature(
        secret,
        payload,
    ) == expected_signature


def test_build_webhook_signature_changes_when_payload_changes():
    secret = "test-secret"

    payload_one = {
        "incident_id": 123,
        "severity": "HIGH",
    }

    payload_two = {
        "incident_id": 123,
        "severity": "CRITICAL",
    }

    signature_one = build_webhook_signature(
        secret,
        payload_one,
    )

    signature_two = build_webhook_signature(
        secret,
        payload_two,
    )

    assert signature_one != signature_two


def test_create_webhook_delivery_rejects_unsupported_event():
    endpoint_id = create_test_webhook_endpoint()

    db = SessionLocal()

    try:
        endpoint = (
            db.query(WebhookEndpoint)
            .filter(WebhookEndpoint.id == endpoint_id)
            .first()
        )

        with pytest.raises(
            ValueError,
            match="Unsupported webhook event type",
        ):
            create_webhook_delivery(
                db=db,
                endpoint=endpoint,
                event_type="UNSUPPORTED_EVENT",
                payload={"test": True},
            )

    finally:
        db.close()
        cleanup_webhook_endpoint(endpoint_id)