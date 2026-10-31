"""Audit logging helper.

``record_audit`` appends a single governance event. It flushes within the
caller's transaction so the audit entry commits atomically with the action it
describes — if the action rolls back, so does its audit record.
"""

from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog
from app.models.user import User


def record_audit(
    db: Session,
    *,
    actor: User | None,
    action: str,
    resource_type: str,
    summary: str,
    resource_id: int | None = None,
    actor_username: str | None = None,
) -> AuditLog:
    entry = AuditLog(
        actor_user_id=actor.id if actor is not None else None,
        actor_username=(
            actor.username if actor is not None else (actor_username or "unknown")
        ),
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        summary=summary,
    )
    db.add(entry)
    db.flush()
    return entry
