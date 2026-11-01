"""Unit tests for the sliding-window rate limiter and auth enforcement.

Self-contained; run with --noconftest.
"""

import pytest
from fastapi.testclient import TestClient

from app.core.rate_limit import SlidingWindowRateLimiter
from app.main import app
from app.api.auth import login_rate_limit


def test_limiter_allows_up_to_limit_then_blocks():
    limiter = SlidingWindowRateLimiter(limit=3, window_seconds=60)
    now = 1000.0
    assert limiter.check("k", now)[0] is True
    assert limiter.check("k", now)[0] is True
    assert limiter.check("k", now)[0] is True
    allowed, retry_after = limiter.check("k", now)
    assert allowed is False
    assert retry_after > 0


def test_limiter_window_slides():
    limiter = SlidingWindowRateLimiter(limit=1, window_seconds=10)
    assert limiter.check("k", 100.0)[0] is True
    assert limiter.check("k", 105.0)[0] is False  # within window
    assert limiter.check("k", 111.0)[0] is True  # window passed


def test_limiter_keys_are_isolated():
    limiter = SlidingWindowRateLimiter(limit=1, window_seconds=60)
    assert limiter.check("a", 0.0)[0] is True
    assert limiter.check("b", 0.0)[0] is True
    assert limiter.check("a", 0.0)[0] is False


@pytest.fixture(autouse=True)
def _reset():
    login_rate_limit.limiter.reset()
    yield
    login_rate_limit.limiter.reset()


def test_login_endpoint_returns_429_when_flooded():
    client = TestClient(app)
    # The login limit is 10/min; the 11th attempt from the same client should
    # be rejected before credential checking.
    last_status = None
    for _ in range(12):
        resp = client.post(
            "/api/auth/login",
            json={"username": "nobody", "password": "whatever"},
        )
        last_status = resp.status_code
    assert last_status == 429
