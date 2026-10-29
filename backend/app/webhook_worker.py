
from __future__ import annotations

import argparse
import hashlib
import hmac
import ipaddress
import json
import logging
import socket
import threading
import time
from uuid import uuid4
from datetime import datetime, timedelta, timezone
from urllib.parse import urlsplit

import httpx
from sqlalchemy import or_, select, update
from sqlalchemy.orm import Session

from app.db.database import SessionLocal

# Register application models and their ORM relationships.
from app.models.user import User  # noqa: F401
from app.models.agent import Agent  # noqa: F401
from app.models.webhook_delivery import WebhookDelivery
from app.models.webhook_endpoint import WebhookEndpoint
# Register all application models so SQLAlchemy can resolve relationships.
import app.main  # noqa: F401
logger = logging.getLogger("sentinelx.webhook_worker")

MAX_ATTEMPTS = 5
BATCH_SIZE = 20
MAX_BATCH_SIZE = 100
LEASE_SECONDS = 60
REQUEST_TIMEOUT_SECONDS = 10
MAX_RESPONSE_BODY_BYTES = 4096
BASE_RETRY_SECONDS = 5
MAX_RETRY_SECONDS = 300

RETRYABLE_STATUSES = {408, 425, 429}
LEASE_RENEW_INTERVAL_SECONDS = LEASE_SECONDS / 3


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def canonical_payload(payload: object) -> bytes:
    """Serialize exactly the same way as the webhook signing helper."""
    return json.dumps(
        payload,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")


def validate_destination(url: str) -> None:
    """Reject non-HTTP destinations and hostnames resolving to unsafe IPs.

    DNS is checked before the HTTP request. This alone cannot completely
    prevent DNS rebinding; enforce outbound network restrictions as well.
    """
    parsed = urlsplit(url)

    if parsed.scheme.lower() not in {"http", "https"}:
        raise ValueError("Only HTTP and HTTPS webhook URLs are allowed.")

    if not parsed.hostname or parsed.username is not None or parsed.password is not None:
        raise ValueError("Webhook URL has an invalid or credential-bearing authority.")

    host = parsed.hostname.rstrip(".").lower()

    if (
        host == "localhost"
        or host.endswith(".localhost")
        or host.endswith(".local")
        or host.endswith(".internal")
    ):
        raise ValueError("Local webhook destinations are not allowed.")

    try:
        literal_ip = ipaddress.ip_address(host)
    except ValueError:
        literal_ip = None

    if literal_ip is not None:
        if not literal_ip.is_global:
            raise ValueError("Webhook destination IP is not globally routable.")
        return

    try:
        results = socket.getaddrinfo(
            host,
            parsed.port or (443 if parsed.scheme.lower() == "https" else 80),
            type=socket.SOCK_STREAM,
        )
    except (OSError, socket.gaierror) as exc:
        raise ValueError("Webhook hostname could not be safely resolved.") from exc

    if not results:
        raise ValueError("Webhook hostname did not resolve.")

    for result in results:
        address = result[4][0].split("%", 1)[0]
        try:
            ip = ipaddress.ip_address(address)
        except ValueError as exc:
            raise ValueError("Webhook hostname resolved to an invalid address.") from exc

        if not ip.is_global:
            raise ValueError("Webhook hostname resolves to a non-public IP address.")


def claim_batch(batch_size: int) -> list[tuple[int, str]]:
    """Claim due deliveries in a short transaction using SKIP LOCKED."""
    now = utcnow()
    claimed: list[tuple[int, str]] = []

    with SessionLocal() as db:
        statement = (
            select(WebhookDelivery)
            .where(
                WebhookDelivery.status == "PENDING",
                or_(
                    WebhookDelivery.next_attempt_at.is_(None),
                    WebhookDelivery.next_attempt_at <= now,
                ),
                or_(
                    WebhookDelivery.locked_until.is_(None),
                    WebhookDelivery.locked_until <= now,
                ),
            )
            .order_by(WebhookDelivery.created_at, WebhookDelivery.id)
            .limit(max(1, min(batch_size, MAX_BATCH_SIZE)))
            .with_for_update(skip_locked=True)
        )

        deliveries = db.scalars(statement).all()

        for delivery in deliveries:
            if delivery.attempt_count >= MAX_ATTEMPTS:
                # A worker may crash after starting the final allowed
                # attempt. Recover the expired lease as a terminal failure.
                delivery.status = "FAILED"
                delivery.next_attempt_at = None
                delivery.locked_until = None
                delivery.claim_token = None
                delivery.response_body = "Maximum webhook attempts exceeded."
                continue

            token = str(uuid4())
            delivery.locked_until = now + timedelta(seconds=LEASE_SECONDS)
            delivery.claim_token = token
            claimed.append((delivery.id, token))

        db.commit()

    return claimed


def read_bounded_response(response: httpx.Response) -> str:
    """Read at most the configured number of response-body bytes."""
    chunks: list[bytes] = []
    remaining = MAX_RESPONSE_BODY_BYTES

    for chunk in response.iter_bytes(chunk_size=1024):
        if not chunk:
            continue

        kept = chunk[:remaining]
        chunks.append(kept)
        remaining -= len(kept)

        if remaining <= 0:
            break

    return b"".join(chunks).decode("utf-8", errors="replace")


def renew_lease(delivery_id: int, claim_token: str) -> bool:
    """Extend only a still-valid lease owned by this worker."""
    now = utcnow()
    with SessionLocal() as db:
        result = db.execute(
            update(WebhookDelivery)
            .where(
                WebhookDelivery.id == delivery_id,
                WebhookDelivery.status == "PENDING",
                WebhookDelivery.claim_token == claim_token,
                WebhookDelivery.locked_until > now,
            )
            .values(locked_until=now + timedelta(seconds=LEASE_SECONDS))
        )
        if result.rowcount != 1:
            db.rollback()
            return False
        db.commit()
        return True


class LeaseRenewer:
    """Renew a claim while network I/O is active; stop on ownership loss."""

    def __init__(self, delivery_id: int, claim_token: str):
        self.delivery_id = delivery_id
        self.claim_token = claim_token
        self.stop_event = threading.Event()
        self.lost_event = threading.Event()
        self.thread = threading.Thread(target=self._run, daemon=True)

    def _run(self) -> None:
        while not self.stop_event.wait(LEASE_RENEW_INTERVAL_SECONDS):
            try:
                if not renew_lease(self.delivery_id, self.claim_token):
                    self.lost_event.set()
                    return
            except Exception:
                logger.exception("Could not renew webhook delivery lease")
                self.lost_event.set()
                return

    def __enter__(self):
        self.thread.start()
        return self

    def __exit__(self, *args):
        self.stop_event.set()
        self.thread.join(timeout=LEASE_RENEW_INTERVAL_SECONDS + 1)
        return False


def finish_delivery(
    delivery_id: int,
    claim_token: str,
    *,
    success: bool,
    retryable: bool = False,
    response_status: int | None = None,
    response_body: str | None = None,
) -> None:
    """Persist an outcome after the HTTP request, in its own short transaction."""
    with SessionLocal() as db:
        now = utcnow()
        values = {
            "response_status": response_status,
            "response_body": (
                response_body[:MAX_RESPONSE_BODY_BYTES]
                if response_body is not None
                else None
            ),
            "locked_until": None,
            "claim_token": None,
        }

        if success:
            values.update(status="DELIVERED", delivered_at=now, next_attempt_at=None)
        elif retryable:
            delivery = db.get(WebhookDelivery, delivery_id)
            if delivery is None or delivery.claim_token != claim_token:
                return
            if delivery.attempt_count >= MAX_ATTEMPTS:
                values.update(status="FAILED", next_attempt_at=None)
            else:
                attempt_count = delivery.attempt_count
                delay = min(
                    BASE_RETRY_SECONDS * (2 ** max(0, attempt_count - 1)),
                    MAX_RETRY_SECONDS,
                )
                values.update(
                    status="PENDING",
                    next_attempt_at=now + timedelta(seconds=delay),
                )
        else:
            values.update(status="FAILED", next_attempt_at=None)

        result = db.execute(
            update(WebhookDelivery)
            .where(
                WebhookDelivery.id == delivery_id,
                WebhookDelivery.status == "PENDING",
                WebhookDelivery.claim_token == claim_token,
                WebhookDelivery.locked_until > now,
            )
            .values(**values)
        )
        if result.rowcount != 1:
            db.rollback()
            return
        db.commit()


def process_delivery(delivery_id: int, claim_token: str) -> None:
    """Record an attempt, close the DB transaction, then perform HTTP."""
    with SessionLocal() as db:
        # The claim token is rotated on every lease acquisition. Claim and
        # attempt start are conditional so an expired worker cannot proceed.
        now = utcnow()
        result = db.execute(
            update(WebhookDelivery)
            .where(
                WebhookDelivery.id == delivery_id,
                WebhookDelivery.status == "PENDING",
                WebhookDelivery.claim_token == claim_token,
                WebhookDelivery.locked_until > now,
                WebhookDelivery.attempt_count < MAX_ATTEMPTS,
            )
            .values(
                attempt_count=WebhookDelivery.attempt_count + 1,
                last_attempt_at=now,
            )
        )
        if result.rowcount != 1:
            db.rollback()
            return

        delivery = db.get(WebhookDelivery, delivery_id)
        if delivery is None:
            db.rollback()
            return

        endpoint = db.get(WebhookEndpoint, delivery.endpoint_id)

        # Count an attempt when this worker starts processing the delivery.
        if endpoint is None or not endpoint.enabled:
            delivery.status = "FAILED"
            delivery.next_attempt_at = None
            delivery.locked_until = None
            delivery.claim_token = None
            delivery.response_body = "Webhook endpoint is missing or disabled."
            db.commit()
            return

        payload = delivery.payload
        url = endpoint.url
        secret = endpoint.secret
        event_type = delivery.event_type
        attempt_count = delivery.attempt_count

        # Do not hold a database transaction open during network activity.
        db.commit()

    if payload is None:
        finish_delivery(
            delivery_id,
            claim_token,
            success=False,
            response_body="Delivery payload is missing.",
        )
        return

    try:
        validate_destination(url)
    except ValueError as exc:
        finish_delivery(
            delivery_id,
            claim_token,
            success=False,
            response_body=f"Webhook destination rejected: {exc}",
        )
        return

    # DNS validation can take long enough for the claim to expire.
    # Renew the lease synchronously before starting the outbound request.
    try:
        if not renew_lease(delivery_id, claim_token):
            logger.warning(
                "Webhook delivery %s lost its lease before HTTP request",
                delivery_id,
            )
            return
    except Exception:
        logger.exception(
            "Could not confirm webhook delivery %s lease before HTTP request",
            delivery_id,
        )
        raise

    body = canonical_payload(payload)
    headers = {
        "Content-Type": "application/json",
        "X-SentinelX-Event": event_type,
    }

    if secret is not None:
        signature = hmac.new(
            secret.encode("utf-8"),
            body,
            hashlib.sha256,
        ).hexdigest()
        headers["X-SentinelX-Signature"] = signature

    try:
        timeout = httpx.Timeout(
            REQUEST_TIMEOUT_SECONDS,
            connect=3.0,
        )

        # Disable redirects so a trusted destination cannot redirect the
        # worker to a private or otherwise unsafe destination.
        with LeaseRenewer(delivery_id, claim_token) as lease_renewer:
            with httpx.Client(
                timeout=timeout,
                follow_redirects=False,
                trust_env=False,
            ) as client:
                with client.stream(
                    "POST",
                    url,
                    content=body,
                    headers=headers,
                ) as response:
                    status_code = response.status_code
                    response_body = read_bounded_response(response)
        if lease_renewer.lost_event.is_set():
            logger.warning(
                "Webhook delivery %s lost its lease during HTTP request; "
                "discarding the result",
                delivery_id,
            )
            return

        if 200 <= status_code < 300:
            finish_delivery(
                delivery_id,
                claim_token,
                success=True,
                response_status=status_code,
                response_body=response_body,
            )
        else:
            transient = (
                status_code in RETRYABLE_STATUSES
                or 500 <= status_code <= 599
            )
            finish_delivery(
                delivery_id,
                claim_token,
                success=False,
                retryable=transient and attempt_count < MAX_ATTEMPTS,
                response_status=status_code,
                response_body=response_body,
            )

    except httpx.RequestError as exc:
        logger.warning(
            "Webhook delivery %s encountered a network error: %s",
            delivery_id,
            type(exc).__name__,
        )
        finish_delivery(
            delivery_id,
            claim_token,
            success=False,
            retryable=attempt_count < MAX_ATTEMPTS,
            response_body=f"Network error: {type(exc).__name__}",
        )


def run_worker_once(batch_size: int = BATCH_SIZE) -> int:
    delivery_ids = claim_batch(batch_size)

    for delivery_id, claim_token in delivery_ids:
        try:
            process_delivery(delivery_id, claim_token)
        except Exception:
            # An unexpected failure leaves the lease to expire, allowing
            # another worker to recover the delivery.
            logger.exception("Unexpected error processing delivery %s", delivery_id)

    return len(delivery_ids)


def main() -> None:
    parser = argparse.ArgumentParser(description="SentinelX webhook delivery worker")
    parser.add_argument(
        "--once",
        action="store_true",
        help="Process one batch and exit.",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=BATCH_SIZE,
        help=f"Maximum deliveries per batch (1-{MAX_BATCH_SIZE}).",
    )
    parser.add_argument(
        "--poll-interval",
        type=float,
        default=2.0,
        help="Seconds to wait when no deliveries are available.",
    )
    args = parser.parse_args()

    if not 1 <= args.batch_size <= MAX_BATCH_SIZE:
        parser.error(f"--batch-size must be between 1 and {MAX_BATCH_SIZE}.")
    if args.poll_interval <= 0:
        parser.error("--poll-interval must be positive.")

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    logger.info("SentinelX webhook worker started")

    while True:
        try:
            processed = run_worker_once(args.batch_size)
            if args.once:
                logger.info("Worker processed %s claimed deliveries", processed)
                return
            if processed == 0:
                time.sleep(args.poll_interval)
        except KeyboardInterrupt:
            logger.info("SentinelX webhook worker stopped")
            return
        except Exception:
            logger.exception("Webhook worker batch failed")
            if args.once:
                raise
            time.sleep(args.poll_interval)


if __name__ == "__main__":
    main()
