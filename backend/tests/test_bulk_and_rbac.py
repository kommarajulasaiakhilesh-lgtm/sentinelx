"""Tests for pagination, RBAC gating, and bulk operations. Run --noconftest."""

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

import app.main  # noqa: F401
from app.main import app
from app.db.database import Base, get_db
from app.api.dependencies import get_current_user, require_role
from app.core.pagination import paginate
from app.models.user import User
from app.models.agent import Agent


# ---- unit: pagination ------------------------------------------------------

def test_paginate_splits_pages():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    db = Session(bind=engine)
    for i in range(25):
        db.add(User(username=f"u{i}", email=f"u{i}@x.test", password_hash="x", role="USER", is_active=True))
    db.commit()

    page = paginate(db.query(User), page=1, page_size=10)
    assert page.total == 25
    assert page.pages == 3
    assert len(page.items) == 10

    last = paginate(db.query(User), page=3, page_size=10)
    assert len(last.items) == 5
    db.close()
    engine.dispose()


# ---- unit: RBAC ------------------------------------------------------------

def test_require_role_blocks_non_admin():
    checker = require_role("ADMIN")
    admin = User(id=1, username="a", email="a@x.test", password_hash="x", role="ADMIN", is_active=True)
    operator = User(id=2, username="o", email="o@x.test", password_hash="x", role="USER", is_active=True)

    assert checker(current_user=admin) is admin
    with pytest.raises(HTTPException) as exc:
        checker(current_user=operator)
    assert exc.value.status_code == 403


# ---- integration: bulk + admin --------------------------------------------

@pytest.fixture()
def client_env():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    TestingSession = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    db = TestingSession()

    owner = User(id=1, username="owner", email="o@x.test", password_hash="x", role="ADMIN", is_active=True)
    other = User(id=2, username="other", email="x@x.test", password_hash="x", role="USER", is_active=True)
    db.add_all([owner, other])
    db.flush()
    db.add(Agent(id=1, owner_id=1, name="A1", status="ACTIVE"))
    db.add(Agent(id=2, owner_id=1, name="A2", status="ACTIVE"))
    db.add(Agent(id=3, owner_id=2, name="A3", status="ACTIVE"))  # not owner's
    db.commit()

    app.dependency_overrides[get_db] = lambda: db
    original = app.dependency_overrides.copy()
    try:
        with TestClient(app) as client:
            yield client, db, owner, other
    finally:
        app.dependency_overrides.clear()
        app.dependency_overrides.update({k: v for k, v in original.items() if k is not get_db})
        db.close()
        engine.dispose()


def _as(user):
    return lambda: user


def test_bulk_agent_status_owner_scoped(client_env):
    client, db, owner, other = client_env
    app.dependency_overrides[get_current_user] = _as(owner)

    resp = client.post(
        "/api/agents/bulk-status",
        json={"agent_ids": [1, 2, 3], "status": "SUSPENDED"},
    )
    assert resp.status_code == 200
    body = resp.json()
    # Only the two owned agents match; agent 3 belongs to another owner.
    assert body["matched"] == 2
    assert body["updated"] == 2
    assert db.get(Agent, 1).status == "SUSPENDED"
    assert db.get(Agent, 3).status == "ACTIVE"


def test_admin_stats_requires_admin(client_env):
    client, db, owner, other = client_env

    app.dependency_overrides[get_current_user] = _as(other)  # non-admin
    assert client.get("/api/admin/stats").status_code == 403

    app.dependency_overrides[get_current_user] = _as(owner)  # admin
    resp = client.get("/api/admin/stats")
    assert resp.status_code == 200
    assert resp.json()["agents"] == 3
