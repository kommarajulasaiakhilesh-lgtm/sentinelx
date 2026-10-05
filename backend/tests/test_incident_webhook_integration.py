from app.main import app

from app.db.database import SessionLocal
from app.models.agent import Agent
from app.models.incident import Incident
from app.models.webhook_delivery import WebhookDelivery
from app.models.webhook_endpoint import WebhookEndpoint
from app.services.incident_service import (
    create_incident,
    update_incident,
)


def create_test_webhook(
    name: str = "Incident Integration Webhook",
    enabled: bool = True,
):
    db = SessionLocal()

    try:
        endpoint = WebhookEndpoint(
            owner_id=4,
            name=name,
            url="https://example.com/security",
            secret="test-secret",
            enabled=enabled,
        )

        db.add(endpoint)
        db.commit()
        db.refresh(endpoint)

        return endpoint.id

    finally:
        db.close()


def cleanup_webhook(endpoint_id: int):
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


def get_deliveries(endpoint_id: int):
    db = SessionLocal()

    try:
        return (
            db.query(WebhookDelivery)
            .filter(
                WebhookDelivery.endpoint_id == endpoint_id
            )
            .order_by(WebhookDelivery.id.asc())
            .all()
        )

    finally:
        db.close()


def test_incident_created_queues_webhook():
    endpoint_id = create_test_webhook()

    try:
        db = SessionLocal()

        try:
            incident = create_incident(
                db=db,
                agent_id=1,
                user_id=4,
                title="Webhook Creation Test",
                description="Testing incident creation webhook",
                severity="HIGH",
            )

            assert incident is not None
            incident_id = incident.id

        finally:
            db.close()

        deliveries = get_deliveries(endpoint_id)

        assert len(deliveries) == 1
        assert deliveries[0].event_type == "INCIDENT_CREATED"
        assert deliveries[0].status == "PENDING"
        assert deliveries[0].attempt_count == 0

    finally:
        cleanup_incident(incident_id)
        cleanup_webhook(endpoint_id)


def test_severity_change_queues_webhook():
    endpoint_id = create_test_webhook()

    try:
        db = SessionLocal()

        try:
            incident = create_incident(
                db=db,
                agent_id=1,
                user_id=4,
                title="Severity Change Test",
                description="Testing severity webhook",
                severity="MEDIUM",
            )

            assert incident is not None
            incident_id = incident.id

            update_incident(
                db=db,
                incident_id=incident_id,
                user_id=4,
                severity="CRITICAL",
            )

        finally:
            db.close()

        deliveries = get_deliveries(endpoint_id)

        assert len(deliveries) == 2
        assert deliveries[0].event_type == "INCIDENT_CREATED"
        assert deliveries[1].event_type == "INCIDENT_SEVERITY_CHANGED"

    finally:
        cleanup_incident(incident_id)
        cleanup_webhook(endpoint_id)


def test_contained_status_queues_webhook():
    endpoint_id = create_test_webhook()

    try:
        db = SessionLocal()

        try:
            incident = create_incident(
                db=db,
                agent_id=1,
                user_id=4,
                title="Contained Test",
                description="Testing contained webhook",
                severity="HIGH",
            )

            assert incident is not None
            incident_id = incident.id

            update_incident(
                db=db,
                incident_id=incident_id,
                user_id=4,
                status="CONTAINED",
            )

        finally:
            db.close()

        deliveries = get_deliveries(endpoint_id)

        assert len(deliveries) == 2
        assert deliveries[0].event_type == "INCIDENT_CREATED"
        assert deliveries[1].event_type == "INCIDENT_CONTAINED"

    finally:
        cleanup_incident(incident_id)
        cleanup_webhook(endpoint_id)


def test_resolved_status_queues_webhook():
    endpoint_id = create_test_webhook()

    try:
        db = SessionLocal()

        try:
            incident = create_incident(
                db=db,
                agent_id=1,
                user_id=4,
                title="Resolved Test",
                description="Testing resolved webhook",
                severity="HIGH",
            )

            assert incident is not None
            incident_id = incident.id

            update_incident(
                db=db,
                incident_id=incident_id,
                user_id=4,
                status="RESOLVED",
            )

        finally:
            db.close()

        deliveries = get_deliveries(endpoint_id)

        assert len(deliveries) == 2
        assert deliveries[0].event_type == "INCIDENT_CREATED"
        assert deliveries[1].event_type == "INCIDENT_RESOLVED"

    finally:
        cleanup_incident(incident_id)
        cleanup_webhook(endpoint_id)


def test_unrelated_update_does_not_queue_webhook():
    endpoint_id = create_test_webhook()

    try:
        db = SessionLocal()

        try:
            incident = create_incident(
                db=db,
                agent_id=1,
                user_id=4,
                title="Unrelated Update Test",
                description="Testing unrelated update",
                severity="LOW",
            )

            assert incident is not None
            incident_id = incident.id

            update_incident(
                db=db,
                incident_id=incident_id,
                user_id=4,
                title="Updated Title",
                description="Updated description",
            )

        finally:
            db.close()

        deliveries = get_deliveries(endpoint_id)

        assert len(deliveries) == 1
        assert deliveries[0].event_type == "INCIDENT_CREATED"

    finally:
        cleanup_incident(incident_id)
        cleanup_webhook(endpoint_id)


def test_disabled_webhook_does_not_receive_delivery():
    endpoint_id = create_test_webhook(
        name="Disabled Incident Webhook",
        enabled=False,
    )

    try:
        db = SessionLocal()

        try:
            incident = create_incident(
                db=db,
                agent_id=1,
                user_id=4,
                title="Disabled Webhook Test",
                description="Testing disabled webhook",
                severity="HIGH",
            )

            assert incident is not None
            incident_id = incident.id

        finally:
            db.close()

        deliveries = get_deliveries(endpoint_id)

        assert len(deliveries) == 0

    finally:
        cleanup_incident(incident_id)
        cleanup_webhook(endpoint_id)


def test_multiple_enabled_webhooks_each_receive_delivery():
    first_endpoint_id = create_test_webhook(
        name="First Incident Webhook",
    )

    second_endpoint_id = create_test_webhook(
        name="Second Incident Webhook",
    )

    try:
        db = SessionLocal()

        try:
            incident = create_incident(
                db=db,
                agent_id=1,
                user_id=4,
                title="Multiple Webhook Test",
                description="Testing webhook fan-out",
                severity="CRITICAL",
            )

            assert incident is not None
            incident_id = incident.id

        finally:
            db.close()

        first_deliveries = get_deliveries(first_endpoint_id)
        second_deliveries = get_deliveries(second_endpoint_id)

        assert len(first_deliveries) == 1
        assert len(second_deliveries) == 1

        assert (
            first_deliveries[0].event_type
            == "INCIDENT_CREATED"
        )

        assert (
            second_deliveries[0].event_type
            == "INCIDENT_CREATED"
        )

    finally:
        cleanup_incident(incident_id)
        cleanup_webhook(first_endpoint_id)
        cleanup_webhook(second_endpoint_id)