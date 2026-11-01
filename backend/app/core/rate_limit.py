"""In-process sliding-window rate limiting.

Lightweight, dependency-free protection for sensitive endpoints (e.g.
authentication) against brute-force and abuse. State is per-process, which is
sufficient for a single-instance deployment; a multi-instance deployment would
move this to a shared store (Redis). Exposed as a FastAPI dependency factory.
"""

from __future__ import annotations

import threading
import time
from collections import defaultdict, deque

from fastapi import HTTPException, Request, status


class SlidingWindowRateLimiter:
    def __init__(self, limit: int, window_seconds: float) -> None:
        self.limit = limit
        self.window = window_seconds
        self._hits: dict[str, deque[float]] = defaultdict(deque)
        self._lock = threading.Lock()

    def check(self, key: str, now: float | None = None) -> tuple[bool, float]:
        """Register a hit for ``key``.

        Returns (allowed, retry_after_seconds). When not allowed, no hit is
        recorded and retry_after indicates when the oldest hit expires.
        """
        now = time.monotonic() if now is None else now
        with self._lock:
            bucket = self._hits[key]
            cutoff = now - self.window
            while bucket and bucket[0] <= cutoff:
                bucket.popleft()

            if len(bucket) >= self.limit:
                retry_after = self.window - (now - bucket[0])
                return False, max(0.0, retry_after)

            bucket.append(now)
            return True, 0.0

    def reset(self) -> None:
        with self._lock:
            self._hits.clear()


def _client_ip(request: Request) -> str:
    # X-Forwarded-For is set by trusted proxies (Render/Vercel); fall back to
    # the socket peer. Only the first hop is used for the key.
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


def rate_limit(limit: int, window_seconds: float, scope: str):
    """Build a FastAPI dependency that rate-limits by client IP within a scope."""
    limiter = SlidingWindowRateLimiter(limit, window_seconds)

    def dependency(request: Request) -> None:
        key = f"{scope}:{_client_ip(request)}"
        allowed, retry_after = limiter.check(key)
        if not allowed:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many requests. Please slow down and try again.",
                headers={"Retry-After": str(int(retry_after) + 1)},
            )

    # Expose the limiter so tests can reset or inspect it.
    dependency.limiter = limiter  # type: ignore[attr-defined]
    return dependency
