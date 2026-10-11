
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
