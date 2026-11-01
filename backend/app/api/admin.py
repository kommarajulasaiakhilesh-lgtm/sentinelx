"""Administrative API.

Endpoints here are gated to the ADMIN role via require_role, demonstrating
role-based access control distinct from the per-owner authorization used
everywhere else.
"""

from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.api.dependencies import require_role
from app.db.database import get_db
from app.models.user import User
from app.models.agent import Agent
from app.models.security_event import SecurityEvent
from app.models.security_alert import SecurityAlert


router = APIRouter(prefix="/api/admin", tags=["Administration"])


@router.get("/stats")
def admin_stats(
    _admin: User = Depends(require_role("ADMIN")),
    db: Session = Depends(get_db),
):
    """System-wide counts. ADMIN only (403 for non-admins)."""
    return {
        "users": db.query(func.count(User.id)).scalar() or 0,
        "active_users": db.query(func.count(User.id)).filter(User.is_active.is_(True)).scalar() or 0,
        "agents": db.query(func.count(Agent.id)).scalar() or 0,
        "suspended_agents": db.query(func.count(Agent.id)).filter(Agent.status == "SUSPENDED").scalar() or 0,
        "security_events": db.query(func.count(SecurityEvent.id)).scalar() or 0,
        "open_alerts": db.query(func.count(SecurityAlert.id)).filter(SecurityAlert.status.in_(["OPEN", "ACKNOWLEDGED"])).scalar() or 0,
    }
