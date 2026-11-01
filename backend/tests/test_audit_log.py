"""Unit tests for the audit logging service.

Self-contained (isolated in-memory SQLite), independent of the Postgres CI
fixtures. Run with: pytest tests/test_audit_log.py --noconftest -q
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

import app.main  # noqa: F401 - register all models

from app.db.database import Base
from app.models.audit_log import AuditLog
from app.models.user import User
from app.services.audit_service import record_audit


@pytest.fixture()
def session():
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}
    )
    Base.metadata.create_all(bind=engine)
    db = Session(bind=engine)
    try:
        yield db
    finally:
        db.close()
        engine.dispose()


def _user(db, uid=1, name="admin"):
    u = User(
        id=uid,
        username=name,
        email=f"{name}@example.test",
        password_hash="x",
        role="ADMIN",
        is_active=True,
    )
    db.add(u)
    db.flush()
    return u


def test_record_audit_persists_entry(session):
    user = _user(session)

    entry = record_audit(
        session,
        actor=user,
        action="AGENT_CREATED",
        resource_type="AGENT",
        resource_id=42,
        summary="Registered agent 'X'",
    )
    session.commit()

    assert entry.id is not None
    stored = session.get(AuditLog, entry.id)
    assert stored.actor_user_id == user.id
    assert stored.actor_username == "admin"
    assert stored.action == "AGENT_CREATED"
    assert stored.resource_id == 42
    assert stored.created_at is not None


def test_record_audit_without_actor_uses_fallback(session):
    entry = record_audit(
        session,
        actor=None,
        action="USER_LOGIN",
        resource_type="USER",
        summary="anonymous attempt",
        actor_username="ghost",
    )
    session.commit()

    assert entry.actor_user_id is None
    assert entry.actor_username == "ghost"


def test_entries_are_owner_scoped_by_actor(session):
    owner = _user(session, uid=1, name="owner")
    other = _user(session, uid=2, name="other")

    record_audit(
        session,
        actor=owner,
        action="POLICY_CREATED",
        resource_type="POLICY",
        summary="owner policy",
    )
    record_audit(
        session,
        actor=other,
        action="POLICY_CREATED",
        resource_type="POLICY",
        summary="other policy",
    )
    session.commit()

    owner_entries = (
        session.query(AuditLog)
        .filter(AuditLog.actor_user_id == owner.id)
        .all()
    )
    assert len(owner_entries) == 1
    assert owner_entries[0].summary == "owner policy"


def test_record_audit_sets_entry_hash(session):
    from app.services.audit_service import compute_entry_hash

    user = _user(session)
    entry = record_audit(
        session,
        actor=user,
        action="AGENT_CREATED",
        resource_type="AGENT",
        resource_id=7,
        summary="Registered agent 'X'",
    )
    session.commit()

    assert entry.entry_hash is not None
    assert entry.entry_hash == compute_entry_hash(
        user.id, "admin", "AGENT_CREATED", "AGENT", 7, "Registered agent 'X'"
    )


def test_tampering_changes_recomputed_hash(session):
    from app.services.audit_service import compute_entry_hash

    user = _user(session)
    entry = record_audit(
        session,
        actor=user,
        action="POLICY_DELETED",
        resource_type="POLICY",
        resource_id=3,
        summary="Deleted policy 'A'",
    )
    session.commit()
    original = entry.entry_hash

    # Simulate tampering with the stored summary.
    entry.summary = "Deleted policy 'B'"
    recomputed = compute_entry_hash(
        entry.actor_user_id,
        entry.actor_username,
        entry.action,
        entry.resource_type,
        entry.resource_id,
        entry.summary,
    )
    assert recomputed != original
