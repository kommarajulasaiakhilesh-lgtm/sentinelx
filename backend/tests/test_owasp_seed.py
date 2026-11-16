"""Tests for the OWASP framework seed. Run with --noconftest."""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

import app.main  # noqa: F401

from app.db.database import Base
from app.models.framework import Framework, FrameworkControl
from app.models.sentinelx_control import SentinelXControl
from app.models.control_mapping import ControlMapping
from scripts.seed_owasp_frameworks import (
    OWASP_LLM,
    OWASP_AGENTIC,
    _get_or_create_sx_controls,
    _seed_framework,
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


def _run(db):
    sx = _get_or_create_sx_controls(db)
    _seed_framework(db, OWASP_LLM, sx)
    _seed_framework(db, OWASP_AGENTIC, sx)
    db.commit()


def test_seed_creates_frameworks_and_mappings(session):
    _run(session)

    assert session.query(Framework).count() == 2
    # 10 LLM + 15 agentic framework controls.
    assert session.query(FrameworkControl).count() == 25
    assert session.query(SentinelXControl).count() == 10

    # Only mapped (non-gap) controls produce ControlMapping rows.
    mapped_llm = sum(1 for c in OWASP_LLM["controls"] if c[2] is not None)
    mapped_ag = sum(1 for c in OWASP_AGENTIC["controls"] if c[2] is not None)
    assert session.query(ControlMapping).count() == mapped_llm + mapped_ag

    llm = session.query(Framework).filter(Framework.name == OWASP_LLM["name"]).first()
    assert llm.version == "2025"


def test_seed_is_idempotent(session):
    _run(session)
    first = (
        session.query(Framework).count(),
        session.query(FrameworkControl).count(),
        session.query(ControlMapping).count(),
    )
    _run(session)  # run again
    second = (
        session.query(Framework).count(),
        session.query(FrameworkControl).count(),
        session.query(ControlMapping).count(),
    )
    assert first == second
