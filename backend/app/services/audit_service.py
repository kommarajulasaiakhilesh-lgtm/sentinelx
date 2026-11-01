"""Audit logging helper.

``record_audit`` appends a single governance event within the caller's
transaction; the caller is responsible for committing.

``record_audit_safely`` is a best-effort variant that commits the audit entry
on its own and never raises — call it *after* the primary action has been
committed so that an audit-logging problem (e.g. a missing table during a
rollout) can never fail or roll back the action it describes.
"""

import hashlib
import logging

from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog
from app.models.user import User


logger = logging.getLogger("sentinelx.audit")


def compute_entry_hash(
    actor_user_id: int | None,
    actor_username: str,
    action: str,
    resource_type: str,
    resource_id: int | None,
    summary: str,
) -> str:
    """SHA-256 over an audit entry's content fields (tamper-evidence)."""
    parts = [
        str(actor_user_id if actor_user_id is not None else ""),
        actor_username,
        action,
        resource_type,
        str(resource_id if resource_id is not None else ""),
        summary,
    ]
    joined = "\x1f".join(parts)  # unit-separator avoids delimiter collisions
    return hashlib.sha256(joined.encode("utf-8")).hexdigest()


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
    resolved_actor_id = actor.id if actor is not None else None
    resolved_username = (
        actor.username if actor is not None else (actor_username or "unknown")
    )
    entry = AuditLog(
        actor_user_id=resolved_actor_id,
        actor_username=resolved_username,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        summary=summary,
        entry_hash=compute_entry_hash(
            resolved_actor_id,
            resolved_username,
            action,
            resource_type,
            resource_id,
            summary,
        ),
    )
    db.add(entry)
    return entry


def record_audit_safely(
    db: Session,
    *,
    actor: User | None,
    action: str,
    resource_type: str,
    summary: str,
    resource_id: int | None = None,
    actor_username: str | None = None,
) -> bool:
    """Best-effort audit write that commits on its own and never raises.

    Returns True on success, False if the audit entry could not be written
    (the failure is logged). The caller's primary action must already be
    committed, so this cannot affect it.
    """
    try:
        record_audit(
            db,
            actor=actor,
            action=action,
            resource_type=resource_type,
            summary=summary,
            resource_id=resource_id,
            actor_username=actor_username,
        )
        db.commit()
        return True
    except Exception:
        try:
            db.rollback()
        except Exception:
            pass
        logger.warning(
            "audit_write_failed action=%s resource_type=%s",
            action,
            resource_type,
            exc_info=True,
        )
        return False
