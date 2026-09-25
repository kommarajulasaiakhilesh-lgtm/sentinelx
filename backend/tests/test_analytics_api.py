from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_get_agent_analytics():
    response = client.get(
        "/api/analytics/agents/1"
    )

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


def test_get_missing_agent_analytics():
    response = client.get(
        "/api/analytics/agents/999999"
    )

    assert response.status_code == 404

    data = response.json()

    assert data["detail"] == (
        "Analytics not found for this agent"
    )