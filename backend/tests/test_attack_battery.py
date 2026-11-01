"""Tests for the prompt-injection attack battery. Run with --noconftest."""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

import app.main  # noqa: F401

from app.db.database import Base
from app.models.agent import Agent
from app.models.policy import Policy
from app.models.user import User
from app.services.attack_battery_service import run_attack_battery, ATTACK_LIBRARY


@pytest.fixture()
def session():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    db = Session(bind=engine)
    try:
        yield db
    finally:
        db.close()
        engine.dispose()


def _agent(db, with_policy: bool):
    db.add(User(id=1, username="u", email="u@x.test", password_hash="x", role="ADMIN", is_active=True))
    db.flush()
    agent = Agent(id=1, owner_id=1, name="A", status="ACTIVE")
    db.add(agent)
    db.flush()
    if with_policy:
        db.add(Policy(
            agent_id=1, name="PI Guard", policy_type="PROMPT_INJECTION",
            action="BLOCK", priority=100, condition=None, enabled=True,
        ))
    db.commit()
    return agent


def test_battery_detects_direct_attacks_with_policy(session):
    agent = _agent(session, with_policy=True)
    report = run_attack_battery(session, agent)

    s = report["summary"]
    assert s["total_cases"] == len(ATTACK_LIBRARY)
    assert s["detected"] >= 1              # baseline patterns catch DIRECT attacks
    assert s["false_positives"] == 0       # benign inputs are never flagged
    assert 0 <= s["detection_rate_percent"] <= 100

    direct = [r for r in report["results"] if r["category"] == "DIRECT"]
    assert all(r["verdict"] == "DETECTED" for r in direct)

    benign = [r for r in report["results"] if r["category"] == "BENIGN"]
    assert all(r["verdict"] == "ALLOWED" for r in benign)


def test_battery_without_policy_detects_nothing(session):
    agent = _agent(session, with_policy=False)
    report = run_attack_battery(session, agent)

    # No policy -> everything is allowed, including attacks (0% detection).
    assert report["summary"]["detected"] == 0
    assert report["summary"]["detection_rate_percent"] == 0
    assert report["summary"]["false_positives"] == 0
