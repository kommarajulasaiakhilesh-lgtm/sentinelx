
from fastapi.testclient import TestClient

from app.api.dependencies import get_current_user
from app.db.database import SessionLocal
from app.main import app
from app.models.agent import Agent
from app.models.user import User


client = TestClient(app)


def get_user(user_id: int) -> User:
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if user is None:
            raise RuntimeError(f"Test user {user_id} was not found")
        return user
    finally:
        db.close()


def set_user_override(user: User) -> None:
    app.dependency_overrides[get_current_user] = lambda: user


def clear_overrides() -> None:
    app.dependency_overrides.clear()


def test_get_agent_analytics():
    db = SessionLocal()
    try:
        agent = db.query(Agent).filter(Agent.id == 1).first()
        if agent is None:
            raise RuntimeError("Expected test agent 1 was not found")
        owner_id = agent.owner_id
    finally:
        db.close()

    set_user_override(get_user(owner_id))
    try:
        response = client.get("/api/analytics/agents/1")

        assert response.status_code == 200
        data = response.json()

        assert data["agent_id"] == 1
        assert data["total_events"] == 13
        assert data["allowed_events"] == 6
        assert data["blocked_events"] == 1
        assert data["suspicious_events"] == 0
        assert data["policy_violations"] == 1
        assert data["risk_score"] == 25
        assert data["risk_level"] == "MEDIUM"
        assert data["block_rate"] == 7.69
        assert data["violation_rate"] == 7.69
        assert "period_start" in data
        assert "period_end" in data
    finally:
        clear_overrides()


def test_get_missing_agent_analytics():
    set_user_override(get_user(4))
    try:
        response = client.get("/api/analytics/agents/999999")

        assert response.status_code == 404
        assert response.json()["detail"] == (
            "Analytics not found for this agent"
        )
    finally:
        clear_overrides()


def test_agent_analytics_cannot_be_accessed_by_another_owner():
    db = SessionLocal()
    try:
        agent = db.query(Agent).filter(Agent.id == 1).first()
        if agent is None:
            raise RuntimeError("Expected test agent 1 was not found")

        other_user = (
            db.query(User)
            .filter(
    User.id != agent.owner_id,
    User.role == "USER",
                   )
            .first()
        )
        if other_user is None:
            raise RuntimeError("An alternate test user is required")

        other_user_id = other_user.id
    finally:
        db.close()

    set_user_override(get_user(other_user_id))
    try:
        response = client.get("/api/analytics/agents/1")
        assert response.status_code == 404
    finally:
        clear_overrides()

def create_refresh_test_agent() -> int:
    from uuid import uuid4

    db = SessionLocal()

    try:
        agent = Agent(
            owner_id=4,
            name=f"Analytics Refresh Test {uuid4().hex[:8]}",
            description="Temporary agent for analytics refresh API tests",
        )
        db.add(agent)
        db.commit()
        db.refresh(agent)
        return agent.id
    finally:
        db.close()


def cleanup_refresh_test_agent(agent_id: int) -> None:
    from app.models.security_analytics import SecurityAnalytics

    db = SessionLocal()

    try:
        db.query(SecurityAnalytics).filter(
            SecurityAnalytics.agent_id == agent_id
        ).delete(synchronize_session=False)

        db.query(Agent).filter(
            Agent.id == agent_id
        ).delete(synchronize_session=False)

        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def test_refresh_agent_analytics_with_no_events():
    from datetime import datetime, timedelta, timezone

    agent_id = create_refresh_test_agent()
    period_end = datetime.now(timezone.utc)
    period_start = period_end - timedelta(hours=1)

    set_user_override(get_user(4))

    try:
        response = client.post(
            f"/api/analytics/agents/{agent_id}/refresh",
            params={
                "period_start": period_start.isoformat(),
                "period_end": period_end.isoformat(),
            },
        )

        assert response.status_code == 200

        data = response.json()
        assert data["agent_id"] == agent_id
        assert data["total_events"] == 0
        assert data["allowed_events"] == 0
        assert data["blocked_events"] == 0
        assert data["suspicious_events"] == 0
        assert data["policy_violations"] == 0
        assert data["risk_score"] == 0
        assert data["risk_level"] == "LOW"
        assert data["block_rate"] == 0
        assert data["violation_rate"] == 0

        # The existing GET endpoint must read the refreshed metrics.
        get_response = client.get(
            f"/api/analytics/agents/{agent_id}"
        )

        assert get_response.status_code == 200
        assert get_response.json()["risk_level"] == "LOW"

    finally:
        clear_overrides()
        cleanup_refresh_test_agent(agent_id)


def test_refresh_agent_analytics_requires_authentication():
    clear_overrides()

    response = client.post(
        "/api/analytics/agents/1/refresh",
        params={
            "period_start": "2026-10-10T00:00:00+00:00",
            "period_end": "2026-10-11T00:00:00+00:00",
        },
    )

    assert response.status_code == 401


def test_refresh_agent_analytics_denies_another_owner():
    agent_id = create_refresh_test_agent()

    set_user_override(get_user(3))

    try:
        response = client.post(
            f"/api/analytics/agents/{agent_id}/refresh",
            params={
                "period_start": "2026-10-10T00:00:00+00:00",
                "period_end": "2026-10-11T00:00:00+00:00",
            },
        )

        assert response.status_code == 404

    finally:
        clear_overrides()
        cleanup_refresh_test_agent(agent_id)


def test_refresh_agent_analytics_rejects_invalid_period():
    from datetime import datetime, timezone

    agent_id = create_refresh_test_agent()
    same_time = datetime.now(timezone.utc).isoformat()

    set_user_override(get_user(4))

    try:
        response = client.post(
            f"/api/analytics/agents/{agent_id}/refresh",
            params={
                "period_start": same_time,
                "period_end": same_time,
            },
        )

        assert response.status_code == 422
        assert response.json()["detail"] == (
            "period_start must be earlier than period_end"
        )

    finally:
        clear_overrides()
        cleanup_refresh_test_agent(agent_id)
