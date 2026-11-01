"""Policy version history and rollback.

``snapshot_policy`` records an immutable version of a policy. It is best-effort
and committed on its own, so a versioning problem (e.g. a missing table during
a rollout) never fails the policy operation it accompanies. Call it after the
policy change has been committed.
"""

from __future__ import annotations

import logging

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.policy import Policy
from app.models.policy_version import PolicyVersion
from app.models.user import User


logger = logging.getLogger("sentinelx.policy_version")

SNAPSHOT_FIELDS = (
    "name",
    "description",
    "policy_type",
    "action",
    "priority",
    "condition",
    "enabled",
)


def _next_version_number(db: Session, policy_id: int) -> int:
    current = (
        db.query(func.max(PolicyVersion.version_number))
        .filter(PolicyVersion.policy_id == policy_id)
        .scalar()
    )
    return (current or 0) + 1


def snapshot_policy(
    db: Session,
    policy: Policy,
    *,
    actor: User | None,
    change_note: str,
) -> None:
    """Best-effort: record the current state of ``policy`` as a new version."""
    try:
        version = PolicyVersion(
            policy_id=policy.id,
            version_number=_next_version_number(db, policy.id),
            name=policy.name,
            description=policy.description,
            policy_type=policy.policy_type,
            action=policy.action,
            priority=policy.priority,
            condition=policy.condition,
            enabled=policy.enabled,
            change_note=change_note,
            changed_by_user_id=actor.id if actor is not None else None,
        )
        db.add(version)
        db.commit()
    except Exception:
        try:
            db.rollback()
        except Exception:
            pass
        logger.warning("policy_snapshot_failed policy_id=%s", policy.id, exc_info=True)


def rollback_policy(
    db: Session,
    policy: Policy,
    version: PolicyVersion,
) -> None:
    """Apply a historical version's field values back onto ``policy``."""
    for field in SNAPSHOT_FIELDS:
        setattr(policy, field, getattr(version, field))
    db.commit()
    db.refresh(policy)
