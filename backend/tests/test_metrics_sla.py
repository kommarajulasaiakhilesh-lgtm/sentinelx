"""Tests for incident SLA tracking and the Prometheus metrics collector.

Run with --noconftest.
"""

from datetime import datetime, timedelta, timezone

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

import app.main  # noqa: F401

from app.db.database import Base
from app.models.agent import Agent
from app.models.incident import Incident
from app.models.security_event import SecurityEvent
from app.models.user import User
from app.services.incident_sla_service import incident_sla_report


@pytest.fixture()
def session():
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    Base.metadata.create_all(bind=engine)
    db = Session(bind=engine)
    db._engine_for_test = engine  # type: ignore[attr-defined]
    try:
        yield db
    finally:
        db.close()
        engine.dispose()


def _seed(db):
    db.add(User(id=1, username="u", email="u@x.test", password_hash="x", role="ADMIN", is_active=True))
    db.flush()
    db.add(Agent(id=1, owner_id=1, name="A", status="ACTIVE"))
    db.flush()


def test_sla_classifies_breach_and_within(session):
    _seed(session)
    now = datetime.now(timezone.utc)
    # CRITICAL target is 60 min. Open 10 min ago -> WITHIN; open 2h ago -> BREACHED.
    session.add(Incident(agent_id=1, title="fresh", severity="CRITICAL", status="OPEN",
                         created_at=now - timedelta(minutes=10)))
    session.add(Incident(agent_id=1, title="stale", severity="CRITICAL", status="OPEN",
                         created_at=now - timedelta(hours=2)))
    session.commit()

    report = incident_sla_report(session, owner_id=1)
    statuses = {r["title"]: r["sla_status"] for r in report["incidents"]}
    assert statuses["fresh"] == "WITHIN"
    assert statuses["stale"] == "BREACHED"
    assert report["summary"]["breached"] == 1
    assert report["summary"]["total"] == 2


def test_sla_resolved_incident_met(session):
    _seed(session)
    now = datetime.now(timezone.utc)
    inc = Incident(agent_id=1, title="done", severity="HIGH", status="RESOLVED",
                   created_at=now - timedelta(hours=2))
    session.add(inc)
    session.flush()
    inc.updated_at = inc.created_at + timedelta(minutes=30)
    session.commit()

    report = incident_sla_report(session, owner_id=1)
    assert report["incidents"][0]["sla_status"] == "MET"


def test_metrics_collector_emits_series(session, monkeypatch):
    import app.api.metrics as metrics_mod

    _seed(session)
    session.add(SecurityEvent(agent_id=1, event_type="X", action="read", decision="BLOCK"))
    session.add(SecurityEvent(agent_id=1, event_type="X", action="read", decision="ALLOW"))
    session.commit()

    TestingSession = sessionmaker(bind=session._engine_for_test)  # type: ignore[attr-defined]
    monkeypatch.setattr(metrics_mod, "SessionLocal", TestingSession)

    from prometheus_client import CollectorRegistry, generate_latest

    reg = CollectorRegistry()
    reg.register(metrics_mod.SentinelXCollector())
    output = generate_latest(reg).decode()

    assert "sentinelx_agents" in output
    assert "sentinelx_security_events_total" in output
    assert 'decision="BLOCK"' in output
