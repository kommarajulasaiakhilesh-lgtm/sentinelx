
import hashlib
import hmac
from types import SimpleNamespace
from unittest.mock import MagicMock

import httpx
import pytest

from app import webhook_worker as worker


class FakeSession:
    def __init__(self, delivery, endpoint, claim_succeeds=True):
        self.delivery = delivery
        self.endpoint = endpoint
        self.claim_succeeds = claim_succeeds

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def get(self, model, record_id):
        if model is worker.WebhookDelivery:
            return self.delivery if self.delivery.id == record_id else None
        if model is worker.WebhookEndpoint:
            return (
                self.endpoint
                if self.endpoint and self.endpoint.id == record_id
                else None
            )
        return None

    def commit(self):
        pass

    def rollback(self):
        pass

    def execute(self, statement):
        if not self.claim_succeeds:
            return SimpleNamespace(rowcount=0)
        self.delivery.attempt_count += 1
        return SimpleNamespace(rowcount=1)


class FakeResponse:
    def __init__(self, status_code, body=b"response"):
        self.status_code = status_code
        self.body = body

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def iter_bytes(self, chunk_size=1024):
        for offset in range(0, len(self.body), chunk_size):
            yield self.body[offset : offset + chunk_size]


@pytest.fixture
def delivery_setup(monkeypatch):
    payload = {"z": 2, "a": 1}

    delivery = SimpleNamespace(
        id=101,
        endpoint_id=202,
        status="PENDING",
        payload=payload,
        event_type="INCIDENT_CREATED",
        attempt_count=0,
        last_attempt_at=None,
        next_attempt_at=None,
        locked_until=None,
        response_status=None,
        response_body=None,
        delivered_at=None,
        claim_token="claim-1",
    )

    endpoint = SimpleNamespace(
        id=202,
        url="https://hooks.example.com/events",
        secret="test-secret",
        enabled=True,
    )

    session = FakeSession(delivery, endpoint)
    monkeypatch.setattr(worker, "SessionLocal", lambda: session)

    finish = MagicMock()
    monkeypatch.setattr(worker, "finish_delivery", finish)

    return delivery, endpoint, finish


def test_canonical_payload_is_sorted_and_compact():
    result = worker.canonical_payload({"z": 2, "a": 1})

    assert result == b'{"a":1,"z":2}'


@pytest.mark.parametrize(
    "url",
    [
        "ftp://hooks.example.com/events",
        "http://localhost/callback",
        "http://127.0.0.1/callback",
        "http://192.168.1.10/callback",
        "http://user:password@example.com/callback",
    ],
)
def test_unsafe_destination_is_rejected(url):
    with pytest.raises(ValueError):
        worker.validate_destination(url)


def test_successful_delivery_sends_signed_canonical_bytes(
    monkeypatch, delivery_setup
):
    delivery, endpoint, finish = delivery_setup
    response = FakeResponse(204, b"ok")

    client = MagicMock()
    client.stream.return_value = response
    client_context = MagicMock()
    client_context.__enter__.return_value = client
    client_context.__exit__.return_value = False

    monkeypatch.setattr(worker.httpx, "Client", lambda **kwargs: client_context)
    monkeypatch.setattr(worker, "validate_destination", lambda url: None)

    worker.process_delivery(delivery.id, "claim-1")

    request = client.stream.call_args
    assert request.args == ("POST", endpoint.url)

    sent_body = request.kwargs["content"]
    expected_body = b'{"a":1,"z":2}'
    expected_signature = hmac.new(
        endpoint.secret.encode(),
        expected_body,
        hashlib.sha256,
    ).hexdigest()

    assert sent_body == expected_body
    assert request.kwargs["headers"]["X-SentinelX-Signature"] == (
        expected_signature
    )
    assert request.kwargs["headers"]["X-SentinelX-Event"] == (
        "INCIDENT_CREATED"
    )
    assert request.kwargs["headers"]["Content-Type"] == "application/json"
    assert client_context.__enter__.call_count == 1

    finish.assert_called_once_with(
        delivery.id,
        "claim-1",
        success=True,
        response_status=204,
        response_body="ok",
    )


@pytest.mark.parametrize("status_code", [408, 425, 429, 500, 503])
def test_transient_http_responses_are_retryable(
    monkeypatch, delivery_setup, status_code
):
    delivery, endpoint, finish = delivery_setup
    delivery.attempt_count = 1

    response = FakeResponse(status_code, b"temporary failure")
    client = MagicMock()
    client.stream.return_value = response

    client_context = MagicMock()
    client_context.__enter__.return_value = client
    client_context.__exit__.return_value = False

    monkeypatch.setattr(worker.httpx, "Client", lambda **kwargs: client_context)
    monkeypatch.setattr(worker, "validate_destination", lambda url: None)

    worker.process_delivery(delivery.id, "claim-1")

    finish.assert_called_once_with(
        delivery.id,
        "claim-1",
        success=False,
        retryable=True,
        response_status=status_code,
        response_body="temporary failure",
    )


@pytest.mark.parametrize("status_code", [400, 401, 403, 404])
def test_permanent_http_errors_are_not_retryable(
    monkeypatch, delivery_setup, status_code
):
    delivery, endpoint, finish = delivery_setup

    response = FakeResponse(status_code, b"permanent failure")
    client = MagicMock()
    client.stream.return_value = response

    client_context = MagicMock()
    client_context.__enter__.return_value = client
    client_context.__exit__.return_value = False

    monkeypatch.setattr(worker.httpx, "Client", lambda **kwargs: client_context)
    monkeypatch.setattr(worker, "validate_destination", lambda url: None)

    worker.process_delivery(delivery.id, "claim-1")

    finish.assert_called_once_with(
        delivery.id,
        "claim-1",
        success=False,
        retryable=False,
        response_status=status_code,
        response_body="permanent failure",
    )


def test_unsafe_destination_never_sends_http(
    monkeypatch, delivery_setup
):
    delivery, endpoint, finish = delivery_setup
    endpoint.url = "http://127.0.0.1/internal"

    client_factory = MagicMock()
    monkeypatch.setattr(worker.httpx, "Client", client_factory)

    worker.process_delivery(delivery.id, "claim-1")

    client_factory.assert_not_called()
    finish.assert_called_once()
    assert finish.call_args.args == (delivery.id, "claim-1")
    assert finish.call_args.kwargs["success"] is False
    assert "destination rejected" in (
        finish.call_args.kwargs["response_body"].lower()
    )


def test_stale_worker_does_not_start_attempt_or_send(monkeypatch, delivery_setup):
    delivery, endpoint, _ = delivery_setup
    delivery.attempt_count = 2
    session = FakeSession(delivery, endpoint, claim_succeeds=False)
    monkeypatch.setattr(worker, "SessionLocal", lambda: session)
    client_factory = MagicMock()
    monkeypatch.setattr(worker.httpx, "Client", client_factory)

    worker.process_delivery(delivery.id, "expired-claim")

    assert delivery.attempt_count == 2
    client_factory.assert_not_called()


def test_stale_worker_cannot_persist_an_outcome(monkeypatch):
    delivery = SimpleNamespace(
        id=101,
        claim_token="new-owner",
        status="PENDING",
    )
    session = FakeSession(delivery, None, claim_succeeds=False)
    monkeypatch.setattr(worker, "SessionLocal", lambda: session)

    worker.finish_delivery(101, "old-owner", success=True, response_status=204)

    assert delivery.status == "PENDING"
    assert delivery.claim_token == "new-owner"


def test_claim_tokens_are_unique_per_claim(monkeypatch):
    first = SimpleNamespace(
        id=1,
        locked_until=None,
        claim_token=None,
        attempt_count=0,
    )
    second = SimpleNamespace(
        id=2,
        locked_until=None,
        claim_token=None,
        attempt_count=0,
    )
    session = SimpleNamespace(
        scalars=lambda statement: SimpleNamespace(all=lambda: [first, second]),
        commit=lambda: None,
    )
    monkeypatch.setattr(worker, "SessionLocal", lambda: _SessionContext(session))

    claimed = worker.claim_batch(2)

    assert [delivery_id for delivery_id, _ in claimed] == [1, 2]
    assert len({token for _, token in claimed}) == 2
    assert first.claim_token == claimed[0][1]
    assert second.claim_token == claimed[1][1]


def test_claim_marks_crashed_final_attempt_as_failed(monkeypatch):
    exhausted = SimpleNamespace(
        id=3,
        locked_until=None,
        claim_token="expired",
        attempt_count=worker.MAX_ATTEMPTS,
        status="PENDING",
        next_attempt_at=None,
        response_body=None,
    )
    session = SimpleNamespace(
        scalars=lambda statement: SimpleNamespace(all=lambda: [exhausted]),
        commit=lambda: None,
    )
    monkeypatch.setattr(worker, "SessionLocal", lambda: _SessionContext(session))

    assert worker.claim_batch(1) == []
    assert exhausted.status == "FAILED"
    assert exhausted.claim_token is None
    assert exhausted.locked_until is None
    assert exhausted.response_body == "Maximum webhook attempts exceeded."


class _SessionContext:
    def __init__(self, session):
        self.session = session

    def __enter__(self):
        return self.session

    def __exit__(self, *args):
        return False


def test_disabled_endpoint_is_not_sent(
    monkeypatch, delivery_setup
):
    delivery, endpoint, finish = delivery_setup
    endpoint.enabled = False

    client_factory = MagicMock()
    monkeypatch.setattr(worker.httpx, "Client", client_factory)

    worker.process_delivery(delivery.id, "claim-1")

    client_factory.assert_not_called()
    assert delivery.status == "FAILED"
    assert delivery.attempt_count == 1
    assert delivery.locked_until is None

def test_finish_delivery_does_not_commit_when_lease_is_no_longer_valid(
    monkeypatch,
):
    session = SimpleNamespace(
        execute=MagicMock(return_value=SimpleNamespace(rowcount=0)),
        commit=MagicMock(),
        rollback=MagicMock(),
    )
    monkeypatch.setattr(
        worker,
        "SessionLocal",
        lambda: _SessionContext(session),
    )

    worker.finish_delivery(
        101,
        "old-claim",
        success=True,
        response_status=204,
    )

    statement = session.execute.call_args.args[0]
    conditions = str(statement.whereclause)

    assert "locked_until" in conditions
    assert "claim_token" in conditions
    session.rollback.assert_called_once()
    session.commit.assert_not_called()


def test_dns_resolution_rejects_mixed_public_and_private_addresses(monkeypatch):
    import socket

    public_result = (
        socket.AF_INET,
        socket.SOCK_STREAM,
        6,
        "",
        ("8.8.8.8", 443),
    )
    private_result = (
        socket.AF_INET,
        socket.SOCK_STREAM,
        6,
        "",
        ("10.0.0.5", 443),
    )

    monkeypatch.setattr(
        worker.socket,
        "getaddrinfo",
        lambda *args, **kwargs: [public_result, private_result],
    )

    with pytest.raises(ValueError, match="non-public"):
        worker.validate_destination("https://hooks.example.com/events")


def test_dns_resolution_failure_is_rejected(monkeypatch):
    import socket

    def fail_resolution(*args, **kwargs):
        raise socket.gaierror("simulated DNS failure")

    monkeypatch.setattr(worker.socket, "getaddrinfo", fail_resolution)

    with pytest.raises(ValueError, match="could not be safely resolved"):
        worker.validate_destination("https://hooks.example.com/events")


def test_empty_dns_resolution_is_rejected(monkeypatch):
    monkeypatch.setattr(
        worker.socket,
        "getaddrinfo",
        lambda *args, **kwargs: [],
    )

    with pytest.raises(ValueError, match="did not resolve"):
        worker.validate_destination("https://hooks.example.com/events")


@pytest.mark.parametrize(
    "url",
    [
        "http://[::1]/callback",
        "http://[fc00::1]/callback",
        "http://169.254.169.254/latest/meta-data/",
        "http://hooks.example.com:invalid/callback",
    ],
)
def test_special_ip_addresses_and_invalid_ports_are_rejected(url):
    with pytest.raises(ValueError):
        worker.validate_destination(url)
