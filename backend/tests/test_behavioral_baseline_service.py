
from datetime import datetime, timedelta, timezone
from uuid import uuid4

from app.main import app  # noqa: F401
from app.db.database import SessionLocal
from app.models.agent import Agent
from app.models.security_event import SecurityEvent
from app.services.behavioral_baseline_service import (
    calculate_behavioral_baseline,
)


def create_test_agent(owner_id):
    """Create an isolated agent for a behavioral baseline test."""
    db = SessionLocal()

    try:
        agent = Agent(
            owner_id=owner_id,
            name=f"Baseline Test Agent {uuid4().hex[:8]}",
            description="Temporary agent for behavioral baseline tests",
        )
        db.add(agent)
        db.commit()
        db.refresh(agent)

        return agent.id
    finally:
        db.close()


def create_events(agent_id, events):
    """Create security events relative to the current time."""
    db = SessionLocal()
    event_ids = []

    try:
        for offset_seconds, event_type, decision in events:
            event = SecurityEvent(
                agent_id=agent_id,
                policy_id=None,
                event_type=event_type,
                action="EXECUTE",
                decision=decision,
                reason=None,
                event_metadata=None,
                created_at=(
                    datetime.now(timezone.utc)
                    - timedelta(seconds=offset_seconds)
                ),
            )
            db.add(event)
            db.flush()
            event_ids.append(event.id)

        db.commit()
        return event_ids
    finally:
        db.close()


def cleanup_test_data(agent_id, event_ids):
    """Delete only the events and agent created by this test."""
    db = SessionLocal()

    try:
        if event_ids:
            db.query(SecurityEvent).filter(
                SecurityEvent.id.in_(event_ids)
            ).delete(synchronize_session=False)

        if agent_id is not None:
            db.query(Agent).filter(
                Agent.id == agent_id
            ).delete(synchronize_session=False)

        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def test_calculate_behavioral_baseline_counts_events():
    agent_id = create_test_agent(owner_id=4)
    event_ids = []

    try:
        event_ids = create_events(
            agent_id,
            [
                (700, "TOOL_ACTION", "ALLOW"),
                (650, "TOOL_ACTION", "ALLOW"),
                (600, "TOOL_ACTION", "ALLOW"),
                (100, "TOOL_ACTION", "ALLOW"),
                (80, "TOOL_ACTION", "ALLOW"),
            ],
        )

        db = SessionLocal()

        try:
            reference_time = datetime.now(timezone.utc)

            result = calculate_behavioral_baseline(
                db=db,
                agent_id=agent_id,
                owner_id=4,
                reference_time=reference_time,
            )

            assert result["agent_id"] == agent_id
            assert result["baseline"]["total_events"] == 3
            assert result["observation"]["total_events"] == 2
        finally:
            db.close()
    finally:
        cleanup_test_data(agent_id, event_ids)


def test_calculate_behavioral_baseline_counts_tool_and_blocked_events():
    agent_id = create_test_agent(owner_id=5)
    event_ids = []

    try:
        event_ids = create_events(
            agent_id,
            [
                (700, "TOOL_ACTION", "BLOCK"),
                (650, "SECURITY_EVENT", "ALLOW"),
                (100, "TOOL_ACTION", "BLOCK"),
            ],
        )

        db = SessionLocal()

        try:
            reference_time = datetime.now(timezone.utc)

            result = calculate_behavioral_baseline(
                db=db,
                agent_id=agent_id,
                owner_id=5,
                reference_time=reference_time,
            )

            assert result["baseline"]["total_events"] == 2
            assert result["baseline"]["tool_action_events"] == 1
            assert result["baseline"]["blocked_events"] == 1

            assert result["observation"]["total_events"] == 1
            assert result["observation"]["tool_action_events"] == 1
            assert result["observation"]["blocked_events"] == 1
        finally:
            db.close()
    finally:
        cleanup_test_data(agent_id, event_ids)


def test_calculate_behavioral_baseline_calculates_rates():
    agent_id = create_test_agent(owner_id=6)
    event_ids = []

    try:
        event_ids = create_events(
            agent_id,
            [
                (700, "TOOL_ACTION", "ALLOW"),
                (650, "TOOL_ACTION", "ALLOW"),
                (600, "TOOL_ACTION", "ALLOW"),
                (550, "TOOL_ACTION", "ALLOW"),
                (100, "TOOL_ACTION", "ALLOW"),
                (80, "TOOL_ACTION", "ALLOW"),
            ],
        )

        db = SessionLocal()

        try:
            result = calculate_behavioral_baseline(
                db=db,
                agent_id=agent_id,
                owner_id=6,
                reference_time=datetime.now(timezone.utc),
            )

            assert result["baseline"]["activity_rate"] > 0
            assert result["baseline"]["tool_action_rate"] > 0
            assert result["observation"]["activity_rate"] > 0
            assert result["observation"]["tool_action_rate"] > 0
        finally:
            db.close()
    finally:
        cleanup_test_data(agent_id, event_ids)


def test_calculate_behavioral_baseline_reports_sufficient_observations():
    agent_id = create_test_agent(owner_id=7)
    event_ids = []

    try:
        event_ids = create_events(
            agent_id,
            [
                (offset, "TOOL_ACTION", "ALLOW")
                for offset in range(600, 1600, 50)
            ],
        )

        db = SessionLocal()

        try:
            result = calculate_behavioral_baseline(
                db=db,
                agent_id=agent_id,
                owner_id=7,
                reference_time=datetime.now(timezone.utc),
            )

            assert result["minimum_observations"] == 10
            assert result["baseline"]["total_events"] >= 10
            assert result["sufficient_observations"] is True
        finally:
            db.close()
    finally:
        cleanup_test_data(agent_id, event_ids)


def test_calculate_behavioral_baseline_rejects_missing_configuration():
    from app.models.behavioral_baseline_configuration import (
        BehavioralBaselineConfiguration,
    )

    db = SessionLocal()

    try:
        enabled_configurations = (
            db.query(BehavioralBaselineConfiguration)
            .filter(
                BehavioralBaselineConfiguration.enabled.is_(True)
            )
            .all()
        )

        original_states = [
            (configuration.id, configuration.enabled)
            for configuration in enabled_configurations
        ]

        try:
            for configuration in enabled_configurations:
                configuration.enabled = False

            db.commit()

            try:
                calculate_behavioral_baseline(
                    db=db,
                    agent_id=1,
                    owner_id=999999,
                    reference_time=datetime.now(timezone.utc),
                )
            except ValueError as exc:
                assert str(exc) == (
                    "No enabled behavioral baseline configuration is available"
                )
            else:
                raise AssertionError(
                    "Expected ValueError when no enabled configuration exists"
                )
        finally:
            for configuration_id, enabled in original_states:
                configuration = (
                    db.query(BehavioralBaselineConfiguration)
                    .filter(
                        BehavioralBaselineConfiguration.id
                        == configuration_id
                    )
                    .first()
                )

                if configuration is not None:
                    configuration.enabled = enabled

            db.commit()
    finally:
        db.close()
