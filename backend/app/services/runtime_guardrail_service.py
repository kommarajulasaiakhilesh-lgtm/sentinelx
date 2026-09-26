from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.models.security_event import SecurityEvent


MAX_TOOL_ACTIONS = 10
TIME_WINDOW_SECONDS = 60


def is_tool_action_rate_limited(
    db: Session,
    agent_id: int
) -> bool:

    window_start = (
        datetime.now(timezone.utc)
        - timedelta(seconds=TIME_WINDOW_SECONDS)
    )

    recent_tool_actions = (
        db.query(SecurityEvent)
        .filter(
            SecurityEvent.agent_id == agent_id,
            SecurityEvent.event_type == "TOOL_ACTION",
            SecurityEvent.created_at >= window_start
        )
        .count()
    )

    return recent_tool_actions >= MAX_TOOL_ACTIONS
MAX_BLOCKED_ACTIONS = 5
BLOCKED_ACTION_WINDOW_SECONDS = 60


def has_repeated_blocked_actions(
    db: Session,
    agent_id: int
) -> bool:

    window_start = (
        datetime.now(timezone.utc)
        - timedelta(seconds=BLOCKED_ACTION_WINDOW_SECONDS)
    )

    blocked_actions = (
        db.query(SecurityEvent)
        .filter(
            SecurityEvent.agent_id == agent_id,
            SecurityEvent.event_type == "TOOL_ACTION",
            SecurityEvent.decision == "BLOCK",
            SecurityEvent.created_at >= window_start
        )
        .count()
    )

    return blocked_actions >= MAX_BLOCKED_ACTIONS