import hashlib
import hmac
import json
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.webhook_delivery import WebhookDelivery
from app.models.webhook_endpoint import WebhookEndpoint


SUPPORTED_WEBHOOK_EVENTS = {
    "INCIDENT_CREATED",
    "INCIDENT_SEVERITY_CHANGED",
    "INCIDENT_CONTAINED",
    "INCIDENT_RESOLVED",
}


def get_owned_endpoint(
    db: Session,
    endpoint_id: int,
    owner_id: int
) -> WebhookEndpoint | None:
    return (
        db.query(WebhookEndpoint)
        .filter(
            WebhookEndpoint.id == endpoint_id,
            WebhookEndpoint.owner_id == owner_id
        )
        .first()
    )


def list_owned_endpoints(
    db: Session,
    owner_id: int
) -> list[WebhookEndpoint]:
    return (
        db.query(WebhookEndpoint)
        .filter(
            WebhookEndpoint.owner_id == owner_id
        )
        .order_by(WebhookEndpoint.created_at.desc())
        .all()
    )


def create_webhook_endpoint(
    db: Session,
    owner_id: int,
    name: str,
    url: str,
    secret: str | None
) -> WebhookEndpoint:

    endpoint = WebhookEndpoint(
        owner_id=owner_id,
        name=name,
        url=url,
        secret=secret,
        enabled=True
    )

    db.add(endpoint)
    db.commit()
    db.refresh(endpoint)

    return endpoint


def update_webhook_endpoint(
    db: Session,
    endpoint: WebhookEndpoint,
    name: str | None = None,
    url: str | None = None,
    secret: str | None = None,
    enabled: bool | None = None
) -> WebhookEndpoint:

    if name is not None:
        endpoint.name = name

    if url is not None:
        endpoint.url = url

    if secret is not None:
        endpoint.secret = secret

    if enabled is not None:
        endpoint.enabled = enabled

    db.commit()
    db.refresh(endpoint)

    return endpoint


def delete_webhook_endpoint(
    db: Session,
    endpoint: WebhookEndpoint
) -> None:

    db.delete(endpoint)
    db.commit()


def create_webhook_delivery(
    db: Session,
    endpoint: WebhookEndpoint,
    event_type: str,
    payload: dict
) -> WebhookDelivery:

    if event_type not in SUPPORTED_WEBHOOK_EVENTS:
        raise ValueError(
            f"Unsupported webhook event type: {event_type}"
        )

    delivery = WebhookDelivery(
        endpoint_id=endpoint.id,
        event_type=event_type,
        status="PENDING",
        attempt_count=0
    )

    db.add(delivery)
    db.commit()
    db.refresh(delivery)

    return delivery
def queue_webhook_event(
    db: Session,
    owner_id: int,
    event_type: str,
    payload: dict,
) -> list[WebhookDelivery]:

    if event_type not in SUPPORTED_WEBHOOK_EVENTS:
        raise ValueError(f"Unsupported webhook event type: {event_type}")

    endpoints = (
        db.query(WebhookEndpoint)
        .filter(
            WebhookEndpoint.owner_id == owner_id,
            WebhookEndpoint.enabled.is_(True),
        )
        .all()
    )

    deliveries = []

    for endpoint in endpoints:
        delivery = WebhookDelivery(
            endpoint_id=endpoint.id,
            event_type=event_type,
            status="PENDING",
            attempt_count=0,
        )
        db.add(delivery)
        deliveries.append(delivery)

    db.flush()

    return deliveries


def build_webhook_signature(
    secret: str,
    payload: dict
) -> str:

    body = json.dumps(
        payload,
        separators=(",", ":"),
        sort_keys=True
    ).encode("utf-8")

    return hmac.new(
        secret.encode("utf-8"),
        body,
        hashlib.sha256
    ).hexdigest()


def mark_delivery_success(
    db: Session,
    delivery: WebhookDelivery,
    response_status: int,
    response_body: str | None
) -> WebhookDelivery:

    delivery.status = "DELIVERED"
    delivery.attempt_count += 1
    delivery.response_status = response_status
    delivery.response_body = response_body
    delivery.delivered_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(delivery)

    return delivery


def mark_delivery_failure(
    db: Session,
    delivery: WebhookDelivery,
    response_status: int | None,
    response_body: str | None
) -> WebhookDelivery:

    delivery.status = "FAILED"
    delivery.attempt_count += 1
    delivery.response_status = response_status
    delivery.response_body = response_body

    db.commit()
    db.refresh(delivery)

    return delivery