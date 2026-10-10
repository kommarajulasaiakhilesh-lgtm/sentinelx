from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.models.security_event import SecurityEvent
from app.services.behavioral_baseline_configuration_service import (
    get_behavioral_baseline_configuration,
)


def _calculate_window_metrics(
    db: Session,
    agent_id: int,
    start_time: datetime,
    end_time: datetime,
    window_seconds: int,
) -> dict:
    """
    Calculate deterministic behavioral metrics for one time window.

    Metrics are derived directly from SecurityEvent records.
    """

    events = (
        db.query(SecurityEvent)
        .filter(
            SecurityEvent.agent_id == agent_id,
            SecurityEvent.created_at >= start_time,
            SecurityEvent.created_at < end_time,
        )
        .all()
    )

    total_events = len(events)

    tool_action_events = sum(
        1
        for event in events
        if event.event_type == "TOOL_ACTION"
    )

    blocked_events = sum(
        1
        for event in events
        if event.decision == "BLOCK"
    )

    if window_seconds > 0:
        activity_rate = total_events / window_seconds
        tool_action_rate = tool_action_events / window_seconds
        blocked_event_rate = blocked_events / window_seconds
    else:
        activity_rate = 0.0
        tool_action_rate = 0.0
        blocked_event_rate = 0.0

    return {
        "total_events": total_events,
        "tool_action_events": tool_action_events,
        "blocked_events": blocked_events,
        "activity_rate": activity_rate,
        "tool_action_rate": tool_action_rate,
        "blocked_event_rate": blocked_event_rate,
    }


def calculate_behavioral_baseline(
    db: Session,
    agent_id: int,
    owner_id: int | None = None,
    reference_time: datetime | None = None,
) -> dict:
    """
    Calculate the behavioral baseline and current observation metrics
    for an agent.

    The effective configuration is resolved through the DB-backed
    behavioral baseline configuration service.

    Time layout:

        baseline_start
              |
              v
        baseline_end
              |
              v
        observation_start
              |
              v
        reference_time

    The observation window is excluded from the historical baseline.
    """

    configuration = get_behavioral_baseline_configuration(
        db=db,
        owner_id=owner_id,
    )

    if configuration is None:
        raise ValueError(
            "No enabled behavioral baseline configuration is available"
        )

    if reference_time is None:
        reference_time = datetime.now(timezone.utc)

    if reference_time.tzinfo is None:
        reference_time = reference_time.replace(tzinfo=timezone.utc)

    observation_end = reference_time

    observation_start = (
        observation_end
        - timedelta(
            seconds=configuration.observation_window_seconds
        )
    )

    baseline_end = observation_start

    baseline_start = (
        baseline_end
        - timedelta(
            seconds=configuration.baseline_window_seconds
        )
    )

    baseline_metrics = _calculate_window_metrics(
        db=db,
        agent_id=agent_id,
        start_time=baseline_start,
        end_time=baseline_end,
        window_seconds=configuration.baseline_window_seconds,
    )

    observation_metrics = _calculate_window_metrics(
        db=db,
        agent_id=agent_id,
        start_time=observation_start,
        end_time=observation_end,
        window_seconds=configuration.observation_window_seconds,
    )

    sufficient_observations = (
        baseline_metrics["total_events"]
        >= configuration.minimum_observations
    )

    return {
        "agent_id": agent_id,
        "configuration_id": configuration.id,
        "configuration_name": configuration.name,
        "baseline": {
            "start_time": baseline_start,
            "end_time": baseline_end,
            **baseline_metrics,
        },
        "observation": {
            "start_time": observation_start,
            "end_time": observation_end,
            **observation_metrics,
        },
        "minimum_observations": configuration.minimum_observations,
        "sufficient_observations": sufficient_observations,
        "deviation_threshold_percent": (
            configuration.deviation_threshold_percent
        ),
    }