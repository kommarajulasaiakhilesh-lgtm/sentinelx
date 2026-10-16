
import logging
import re

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_request_id_is_generated_when_missing():
    response = client.get("/health")

    request_id = response.headers.get("X-Request-ID")

    assert response.status_code == 200
    assert request_id is not None
    assert re.fullmatch(r"[0-9a-f]{32}", request_id)


def test_valid_request_id_is_preserved():
    expected_request_id = "phase22-test.request_01"

    response = client.get(
        "/health",
        headers={"X-Request-ID": expected_request_id},
    )

    assert response.status_code == 200
    assert response.headers["X-Request-ID"] == expected_request_id


def test_invalid_request_id_is_replaced():
    invalid_request_id = "invalid request id with spaces"

    response = client.get(
        "/health",
        headers={"X-Request-ID": invalid_request_id},
    )

    actual_request_id = response.headers["X-Request-ID"]

    assert response.status_code == 200
    assert actual_request_id != invalid_request_id
    assert re.fullmatch(r"[0-9a-f]{32}", actual_request_id)


def test_request_logs_exclude_query_parameters(caplog):
    caplog.set_level(
        logging.INFO,
        logger="sentinelx.request",
    )

    sensitive_query_value = "do-not-log-this-value"

    response = client.get(
        f"/health?token={sensitive_query_value}",
        headers={"X-Request-ID": "safe-log-test-01"},
    )

    assert response.status_code == 200
    assert response.headers["X-Request-ID"] == "safe-log-test-01"

    matching_records = [
        record
        for record in caplog.records
        if record.name == "sentinelx.request"
    ]

    assert matching_records
    assert any(
        "request_id=safe-log-test-01" in record.getMessage()
        and "method=GET" in record.getMessage()
        and "route=/health" in record.getMessage()
        and "status_code=200" in record.getMessage()
        for record in matching_records
    )

    all_request_logs = "\n".join(
        record.getMessage()
        for record in matching_records
    )

    assert sensitive_query_value not in all_request_logs
    assert "token=" not in all_request_logs
