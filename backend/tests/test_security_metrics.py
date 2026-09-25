from app.db.database import SessionLocal
from app.models.user import User
from app.models.agent import Agent
from app.models.policy import Policy
from app.models.agent_api_key import AgentAPIKey
from app.models.security_event import SecurityEvent
from app.models.security_analytics import SecurityAnalytics
from app.services.security_metrics_service import calculate_security_metrics


def test_security_metrics_for_existing_agent():
    db = SessionLocal()

    try:
        metrics = calculate_security_metrics(
            db,
            1
        )

        assert metrics is not None
        assert metrics["agent_id"] == 1
        assert metrics["total_events"] == 13
        assert metrics["allowed_events"] == 6
        assert metrics["blocked_events"] == 1
        assert metrics["suspicious_events"] == 0
        assert metrics["policy_violations"] == 1
        assert metrics["risk_score"] == 25
        assert metrics["risk_level"] == "MEDIUM"
        assert metrics["block_rate"] == 7.69
        assert metrics["violation_rate"] == 7.69
        assert metrics["period_start"] is not None
        assert metrics["period_end"] is not None

    finally:
        db.close()


def test_security_metrics_for_missing_agent():
    db = SessionLocal()

    try:
        metrics = calculate_security_metrics(
            db,
            999999
        )

        assert metrics is None

    finally:
        db.close()