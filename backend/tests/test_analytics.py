from datetime import datetime, timedelta, timezone

from app.models.user import User
from app.models.agent import Agent
from app.models.policy import Policy
from app.models.agent_api_key import AgentAPIKey
from app.models.security_event import SecurityEvent
from app.models.security_analytics import SecurityAnalytics
from app.services.risk_scoring_service import calculate_risk_score


def test_risk_score_low():
    score, level = calculate_risk_score(
        blocked_events=0,
        suspicious_events=0,
        policy_violations=0
    )

    assert score == 0
    assert level == "LOW"


def test_risk_score_medium():
    score, level = calculate_risk_score(
        blocked_events=1,
        suspicious_events=0,
        policy_violations=1
    )

    assert score == 25
    assert level == "MEDIUM"


def test_risk_score_high():
    score, level = calculate_risk_score(
        blocked_events=5,
        suspicious_events=0,
        policy_violations=0
    )

    assert score == 50
    assert level == "HIGH"


def test_risk_score_critical():
    score, level = calculate_risk_score(
        blocked_events=8,
        suspicious_events=0,
        policy_violations=0
    )

    assert score == 80
    assert level == "CRITICAL"


def test_risk_score_capped_at_100():
    score, level = calculate_risk_score(
        blocked_events=20,
        suspicious_events=20,
        policy_violations=20
    )

    assert score == 100
    assert level == "CRITICAL"


def test_security_analytics_model_fields():
    now = datetime.now(timezone.utc)

    analytics = SecurityAnalytics(
        agent_id=1,
        period_start=now - timedelta(days=1),
        period_end=now,
        total_events=13,
        allowed_events=6,
        blocked_events=1,
        suspicious_events=0,
        policy_violations=1,
        risk_score=25,
        risk_level="MEDIUM"
    )

    assert analytics.total_events == 13
    assert analytics.allowed_events == 6
    assert analytics.blocked_events == 1
    assert analytics.suspicious_events == 0
    assert analytics.policy_violations == 1
    assert analytics.risk_score == 25
    assert analytics.risk_level == "MEDIUM"