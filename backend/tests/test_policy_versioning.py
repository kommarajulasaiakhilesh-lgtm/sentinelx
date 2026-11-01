"""Tests for policy version history + rollback. Run with --noconftest."""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

import app.main  # noqa: F401 - register models

from app.db.database import Base
from app.models.agent import Agent
from app.models.policy import Policy
from app.models.policy_version import PolicyVersion
from app.models.user import User
from app.services.policy_version_service import (
    rollback_policy,
    snapshot_policy,
)


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


def _seed_policy(db: Session) -> tuple[User, Policy]:
    user = User(id=1, username="u", email="u@x.test", password_hash="x", role="ADMIN", is_active=True)
    db.add(user)
    db.flush()
    agent = Agent(id=1, owner_id=1, name="A", status="ACTIVE")
    db.add(agent)
    db.flush()
    policy = Policy(
        agent_id=1,
        name="PI Guard",
        policy_type="PROMPT_INJECTION",
        action="BLOCK",
        priority=100,
        enabled=True,
    )
    db.add(policy)
    db.commit()
    db.refresh(policy)
    return user, policy


def test_snapshots_increment_version(session):
    user, policy = _seed_policy(session)
    snapshot_policy(session, policy, actor=user, change_note="created")
    policy.priority = 50
    session.commit()
    snapshot_policy(session, policy, actor=user, change_note="updated (priority)")

    versions = (
        session.query(PolicyVersion)
        .filter(PolicyVersion.policy_id == policy.id)
        .order_by(PolicyVersion.version_number)
        .all()
    )
    assert [v.version_number for v in versions] == [1, 2]
    assert versions[0].priority == 100
    assert versions[1].priority == 50
    assert versions[1].change_note == "updated (priority)"


def test_rollback_restores_fields(session):
    user, policy = _seed_policy(session)
    snapshot_policy(session, policy, actor=user, change_note="created")  # v1: BLOCK/100

    policy.action = "ALLOW"
    policy.priority = 10
    session.commit()
    snapshot_policy(session, policy, actor=user, change_note="updated")  # v2: ALLOW/10

    v1 = (
        session.query(PolicyVersion)
        .filter(PolicyVersion.policy_id == policy.id, PolicyVersion.version_number == 1)
        .first()
    )
    rollback_policy(session, policy, v1)

    assert policy.action == "BLOCK"
    assert policy.priority == 100


def test_snapshot_is_best_effort(session):
    """A snapshot failure must not raise (degrades gracefully)."""
    user, policy = _seed_policy(session)
    # Drop the versions table to simulate a missing table mid-rollout.
    PolicyVersion.__table__.drop(bind=session.get_bind())
    snapshot_policy(session, policy, actor=user, change_note="created")
    # Policy row is still intact and usable.
    assert session.get(Policy, policy.id) is not None
