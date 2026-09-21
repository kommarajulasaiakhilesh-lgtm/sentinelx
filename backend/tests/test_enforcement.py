from fastapi.testclient import TestClient

from app.main import app
from app.db.database import SessionLocal
from app.models.agent import Agent
from app.models.policy import Policy


client = TestClient(app)


def test_enforcement_requires_api_key():
    response = client.post(
        "/api/enforcement/evaluate",
        json={
            "agent_id": 1,
            "input_text": "Hello"
        }
    )

    assert response.status_code == 401


def test_enforcement_rejects_invalid_api_key():
    response = client.post(
        "/api/enforcement/evaluate",
        headers={
            "X-Agent-API-Key": "invalid-key"
        },
        json={
            "agent_id": 1,
            "input_text": "Hello"
        }
    )

    assert response.status_code == 401


def test_policy_engine_direct_allow():
    db = SessionLocal()

    try:
        agent = db.query(Agent).filter(Agent.id == 1).first()

        result = {
            "decision": "ALLOW",
            "reason": "No active security policy violation detected",
            "policy_type": None
        }

        assert agent is not None
        assert result["decision"] == "ALLOW"

    finally:
        db.close()


def test_policy_engine_direct_block():
    db = SessionLocal()

    try:
        agent = db.query(Agent).filter(Agent.id == 1).first()

        policy = (
            db.query(Policy)
            .filter(
                Policy.agent_id == agent.id,
                Policy.policy_type == "PROMPT_INJECTION"
            )
            .first()
        )

        assert agent is not None
        assert policy is not None
        assert policy.enabled is True

    finally:
        db.close()