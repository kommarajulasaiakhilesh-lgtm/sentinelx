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
        "entries": [
            {
                "id": e.id,
                "actor_username": e.actor_username,
                "action": e.action,
                "resource_type": e.resource_type,
                "resource_id": e.resource_id,
                "summary": e.summary,
                "created_at": e.created_at.isoformat() if e.created_at else None,
            }
            for e in entries
        ],
    }
