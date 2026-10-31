"""Unit tests for the Agent Security Posture scoring service.

Self-contained: builds an isolated in-memory SQLite database and its own
Session, so it does not depend on the shared Postgres CI fixtures and can run
anywhere. Verifies the deterministic scoring rules in
``agent_posture_service``.
"""

from datetime import datetime, timezone

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

import app.main  # noqa: F401 - register all models on Base

from app.db.database import Base
from app.models.agent import Agent
from app.models.policy import Policy
from app.models.tool import Tool
from app.models.security_event import SecurityEvent
from app.models.security_alert import SecurityAlert
from app.models.user import User
from app.services.agent_posture_service import (
    evaluate_agent_posture,
    evaluate_fleet_posture,
)


@pytest.fixture()
def session():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
    )
    Base.metadata.create_all(bind=engine)
    db = Session(bind=engine)
    try:
        yield db
    finally:
        db.close()
        engine.dispose()


def _make_owner(db: Session, owner_id: int = 1) -> User:
    user = User(
        id=owner_id,
        username=f"owner_{owner_id}",
        email=f"owner_{owner_id}@example.test",
        password_hash="x",
        role="ADMIN",
        is_active=True,
    )
    db.add(user)
    db.flush()
    return user


def test_well_governed_agent_scores_high(session):
    _make_owner(session)
    agent = Agent(id=1, owner_id=1, name="Hardened", status="ACTIVE")
    session.add(agent)
    session.flush()
    session.add(
        Policy(
            agent_id=1,
            name="PI Guard",
            policy_type="PROMPT_INJECTION",
            action="BLOCK",
            priority=100,
            enabled=True,
        )
    )
    session.add(Tool(agent_id=1, name="http", tool_type="HTTP", enabled=True))
    session.commit()

    report = evaluate_agent_posture(session, agent)

    assert report["score"] == 100
    assert report["grade"] == "A"
    assert report["level"] == "STRONG"
    assert report["findings"] == []


def test_ungoverned_agent_is_penalized(session):
    _make_owner(session)
    agent = Agent(id=1, owner_id=1, name="Exposed", status="ACTIVE")
    session.add(agent)
    session.flush()
    # No policies, but a high-risk SHELL tool enabled.
    session.add(Tool(agent_id=1, name="shell", tool_type="SHELL", enabled=True))
    session.commit()

    report = evaluate_agent_posture(session, agent)

    codes = {f["code"] for f in report["findings"]}
    assert "NO_POLICY_COVERAGE" in codes
    assert "UNGOVERNED_RISKY_TOOLS" in codes
    # 100 - 30 (no policy) - 20 (ungoverned risky tools) = 50
    assert report["score"] == 50
    assert report["level"] == "WEAK"


def test_recent_activity_and_alerts_reduce_score(session):
    _make_owner(session)
    agent = Agent(id=1, owner_id=1, name="NoisyAgent", status="SUSPENDED")
    session.add(agent)
    session.flush()
    session.add(
        Policy(
            agent_id=1,
            name="PI Guard",
            policy_type="PROMPT_INJECTION",
            action="BLOCK",
            priority=100,
            enabled=True,
        )
    )
    now = datetime.now(timezone.utc)
    for _ in range(2):
        session.add(
            SecurityEvent(
                agent_id=1,
                event_type="PROMPT_SUBMISSION",
                action="read",
                decision="BLOCK",
                created_at=now,
            )
        )
    session.add(
        SecurityAlert(
            agent_id=1,
            alert_type="PROMPT_INJECTION",
            severity="HIGH",
            title="t",
            status="OPEN",
            created_at=now,
        )
    )
    session.commit()

    report = evaluate_agent_posture(session, agent)

    codes = {f["code"] for f in report["findings"]}
    assert "AGENT_SUSPENDED" in codes
    assert "RECENT_BLOCKS" in codes
    assert "OPEN_ALERTS" in codes
    # 100 - 10 (suspended) - 6 (2 blocks * 3) - 3 (1 open alert * 3) = 81
    assert report["score"] == 81


def test_fleet_posture_aggregates(session):
    _make_owner(session)
    strong = Agent(id=1, owner_id=1, name="Strong", status="ACTIVE")
    weak = Agent(id=2, owner_id=1, name="Weak", status="ACTIVE")
    session.add_all([strong, weak])
    session.flush()
    session.add(
        Policy(
            agent_id=1,
            name="PI",
            policy_type="PROMPT_INJECTION",
            action="BLOCK",
            priority=1,
            enabled=True,
        )
    )
    session.commit()

    fleet = evaluate_fleet_posture(session, owner_id=1)

    assert fleet["agent_count"] == 2
    assert 0 <= fleet["average_score"] <= 100
    # Weakest agent (no policy) should sort first.
    assert fleet["weakest_agents"][0]["agent_name"] == "Weak"
