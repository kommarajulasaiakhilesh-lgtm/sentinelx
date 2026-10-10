from datetime import datetime, timedelta, timezone
from uuid import uuid4

from app.models.agent import Agent
from app.services.analytics_service import generate_agent_analytics
from app.main import app  # noqa: F401
from app.db.database import SessionLocal
from app.models.security_analytics import SecurityAnalytics
from app.services.risk_scoring_service import calculate_risk_score


def test_risk_score_low():
    db = SessionLocal()

    try:
        score, level = calculate_risk_score(
            db=db,
            owner_id=None,
            blocked_events=0,
            suspicious_events=0,
            policy_violations=0
        )

        assert score == 0
        assert level == "LOW"

    finally:
        db.close()


def test_risk_score_medium():
    db = SessionLocal()

    try:
        score, level = calculate_risk_score(
            db=db,
            owner_id=None,
            blocked_events=1,
            suspicious_events=0,
            policy_violations=1
        )

        assert score == 25
        assert level == "MEDIUM"

    finally:
        db.close()


def test_risk_score_high():
    db = SessionLocal()

    try:
        score, level = calculate_risk_score(
            db=db,
            owner_id=None,
            blocked_events=5,
            suspicious_events=0,
            policy_violations=0
        )

        assert score == 50
        assert level == "HIGH"

    finally:
        db.close()


def test_risk_score_critical():
    db = SessionLocal()

    try:
        score, level = calculate_risk_score(
            db=db,
            owner_id=None,
            blocked_events=8,
            suspicious_events=0,
            policy_violations=0
        )

        assert score == 80
        assert level == "CRITICAL"

    finally:
        db.close()


def test_risk_score_capped_at_100():
    db = SessionLocal()

    try:
        score, level = calculate_risk_score(
            db=db,
            owner_id=None,
            blocked_events=20,
            suspicious_events=20,
            policy_violations=20
        )

        assert score == 100
        assert level == "CRITICAL"

    finally:
        db.close()


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

def test_generate_agent_analytics_with_no_events():
    db = SessionLocal()
    agent_id = None

    try:
        # Create an isolated agent with no security events.
        agent = Agent(
            owner_id=4,
            name=f"Zero Event Analytics Test {uuid4().hex[:8]}",
            description="Temporary agent for analytics regression test",
        )

        db.add(agent)
        db.commit()
        db.refresh(agent)
        agent_id = agent.id

        period_end = datetime.now(timezone.utc)
        period_start = period_end - timedelta(hours=1)

        analytics = generate_agent_analytics(
            db=db,
            agent_id=agent_id,
            period_start=period_start,
            period_end=period_end,
        )

        assert analytics.agent_id == agent_id
        assert analytics.total_events == 0
        assert analytics.allowed_events == 0
        assert analytics.blocked_events == 0
        assert analytics.suspicious_events == 0
        assert analytics.policy_violations == 0
        assert analytics.risk_score == 0
        assert analytics.risk_level == "LOW"

    finally:
        try:
            if agent_id is not None:
                # Delete analytics first because they reference the agent.
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
