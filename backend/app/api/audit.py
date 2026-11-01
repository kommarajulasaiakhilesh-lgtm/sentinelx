"""Audit log API.

Read-only access to the acting operator's governance evidence trail. Entries
are never mutable through the API.
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.db.database import get_db
from app.models.audit_log import AuditLog
from app.models.user import User
from app.services.audit_service import compute_entry_hash


router = APIRouter(prefix="/api/audit", tags=["Audit Log"])


@router.get("")
def list_audit_entries(
    action: str | None = Query(default=None),
    resource_type: str | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=500),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    query = db.query(AuditLog).filter(
        AuditLog.actor_user_id == current_user.id
    )

    if action:
        query = query.filter(AuditLog.action == action)
    if resource_type:
        query = query.filter(AuditLog.resource_type == resource_type)

    entries = query.order_by(AuditLog.created_at.desc()).limit(limit).all()

    # Distinct action types for client-side filtering.
    action_rows = (
        db.query(AuditLog.action)
        .filter(AuditLog.actor_user_id == current_user.id)
        .distinct()
        .all()
    )

    return {
        "count": len(entries),
        "available_actions": sorted(r[0] for r in action_rows),
        "entries": [_entry_dict(e) for e in entries],
    }


def _entry_dict(e: AuditLog) -> dict:
    return {
        "id": e.id,
        "actor_username": e.actor_username,
        "action": e.action,
        "resource_type": e.resource_type,
        "resource_id": e.resource_id,
        "summary": e.summary,
        "created_at": e.created_at.isoformat() if e.created_at else None,
    }


@router.get("/export")
def export_audit(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Full chronological export of the operator's audit trail (JSON)."""
    entries = (
        db.query(AuditLog)
        .filter(AuditLog.actor_user_id == current_user.id)
        .order_by(AuditLog.created_at.asc())
        .all()
    )
    return {"count": len(entries), "entries": [_entry_dict(e) for e in entries]}


@router.get("/integrity")
def verify_integrity(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Recompute each entry's content hash to detect tampering of rows.

    Detects modification of an entry's content fields. It does not by itself
    prove no rows were deleted; combine with off-site retention for that.
    """
    entries = (
        db.query(AuditLog)
        .filter(AuditLog.actor_user_id == current_user.id)
        .order_by(AuditLog.id.asc())
        .all()
    )

    verified = 0
    legacy = 0
    tampered: list[int] = []
    for e in entries:
        if not e.entry_hash:
            legacy += 1
            continue
        expected = compute_entry_hash(
            e.actor_user_id,
            e.actor_username,
            e.action,
            e.resource_type,
            e.resource_id,
            e.summary,
        )
        if expected == e.entry_hash:
            verified += 1
        else:
            tampered.append(e.id)

    return {
        "total": len(entries),
        "verified": verified,
        "legacy_unhashed": legacy,
        "tampered_ids": tampered,
        "ok": len(tampered) == 0,
    }
