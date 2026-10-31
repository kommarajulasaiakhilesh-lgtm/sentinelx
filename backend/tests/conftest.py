"""Shared fixtures for the isolated SentinelX test database."""

import pytest

import app.main  # noqa: F401 - register all SQLAlchemy models
from app.main import app

from app.db.database import SessionLocal, engine
from app.models.agent import Agent
from app.models.behavioral_baseline_configuration import (
    BehavioralBaselineConfiguration,
)
from app.models.policy import Policy
from app.models.security_analytics import SecurityAnalytics
from app.models.security_test import SecurityTestScenario
from app.models.user import User


EXPECTED_DATABASE = "sentinelx_phase27_test_db"


@pytest.fixture(autouse=True)
def preserve_fastapi_dependency_overrides():
    """Prevent one test's dependency cleanup from affecting other tests."""
    original_overrides = app.dependency_overrides.copy()
    try:
        yield
    finally:
        app.dependency_overrides.clear()
        app.dependency_overrides.update(original_overrides)


@pytest.fixture(scope="session", autouse=True)
def verify_isolated_test_database_baseline():
    """Verify existing synthetic fixtures without modifying database records."""

    if engine.url.database != EXPECTED_DATABASE:
        raise RuntimeError(
            "Refusing to run tests: unexpected database. "
            f"Expected {EXPECTED_DATABASE!r}, got {engine.url.database!r}."
        )

    db = SessionLocal()

    try:
        for user_id in range(1, 8):
            user = db.get(User, user_id)
            expected_role = "ADMIN" if user_id == 1 else "USER"

            if (
                user is None
                or user.username != f"ci_user_{user_id}"
                or user.email != f"ci_user_{user_id}@example.test"
                or user.role != expected_role
                or not user.is_active
            ):
                raise RuntimeError(
                    f"Required synthetic test user {user_id} is missing "
                    "or does not match the expected identity."
                )

        agent_specs = {
            1: (4, "CI Test Agent"),
            2: (5, "CI Test Agent 2"),
            4: (7, "CI Behavioral Test Agent"),
        }

        for agent_id, (owner_id, name) in agent_specs.items():
            agent = db.get(Agent, agent_id)

            if (
                agent is None
                or agent.owner_id != owner_id
                or agent.name != name
                or agent.status != "ACTIVE"
            ):
                raise RuntimeError(
                    f"Required synthetic test agent {agent_id} is missing "
                    "or does not match its expected identity and state."
                )

        baseline = (
            db.query(BehavioralBaselineConfiguration)
            .filter(
                BehavioralBaselineConfiguration.owner_id.is_(None),
                BehavioralBaselineConfiguration.name
                == "CI Default Behavioral Baseline",
            )
            .one_or_none()
        )

        expected_baseline = {
            "enabled": True,
            "baseline_window_seconds": 3600,
            "observation_window_seconds": 300,
            "minimum_observations": 10,
            "deviation_threshold_percent": 50,
        }

        if baseline is None or any(
            getattr(baseline, field) != value
            for field, value in expected_baseline.items()
        ):
            raise RuntimeError(
                "Required synthetic behavioral baseline is missing "
                "or does not match expected values."
            )

        policy = (
            db.query(Policy)
            .filter(
                Policy.agent_id == 1,
                Policy.name == "CI Prompt Injection Protection",
            )
            .one_or_none()
        )

        expected_policy = {
            "policy_type": "PROMPT_INJECTION",
            "action": "BLOCK",
            "priority": 100,
            "condition": None,
            "enabled": True,
        }

        if policy is None or any(
            getattr(policy, field) != value
            for field, value in expected_policy.items()
        ):
            raise RuntimeError(
                "Required synthetic prompt-injection policy is missing "
                "or does not match expected values."
            )

        scenario = (
            db.query(SecurityTestScenario)
            .filter(
                SecurityTestScenario.name == "CI Prompt Injection Scenario"
            )
            .one_or_none()
        )

        if (
            scenario is None
            or scenario.owner_id != 4
            or scenario.agent_id != 1
            or scenario.category != "PROMPT_INJECTION"
            or scenario.expected_decision != "BLOCK"
            or not scenario.enabled
        ):
            raise RuntimeError(
                "Required synthetic security-test scenario is missing "
                "or does not match expected values."
            )

        expected_metrics = {
            "total_events": 13,
            "allowed_events": 6,
            "blocked_events": 1,
            "suspicious_events": 0,
            "policy_violations": 1,
            "risk_score": 25,
            "risk_level": "MEDIUM",
        }

        analytics_rows = (
            db.query(SecurityAnalytics)
            .filter(SecurityAnalytics.agent_id == 1)
            .all()
        )

        if len(analytics_rows) != 1 or any(
            getattr(analytics_rows[0], field) != value
            for field, value in expected_metrics.items()
        ):
            raise RuntimeError(
                "Expected exactly one matching synthetic analytics record "
                "for agent 1; refusing to modify existing data."
            )

        print(
            "\nSentinelX isolated test database verified: "
            "users 1-7; agents 1, 2, 4; policy; scenario; "
            "behavioral baseline; analytics. No fixture records modified."
        )

    finally:
        db.close()