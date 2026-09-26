from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.db.database import get_db
from app.models.agent import Agent
from app.models.security_alert import SecurityAlert
from app.models.user import User
from app.schemas.security_alert import (
    SecurityAlertResponse,
    SecurityAlertListResponse
)


router = APIRouter(
    prefix="/api/security-alerts",
    tags=["Security Alerts"]
)


def get_owned_alert(
    alert_id: int,
    current_user: User,
    db: Session
):
    alert = (
        db.query(SecurityAlert)
        .join(Agent)
        .filter(
            SecurityAlert.id == alert_id,
            Agent.owner_id == current_user.id
        )
        .first()
    )

    if not alert:
        raise HTTPException(
            status_code=404,
            detail="Security alert not found"
        )

    return alert


@router.get(
    "",
    response_model=SecurityAlertListResponse
)
def list_security_alerts(
    status: str | None = None,
    severity: str | None = None,
    alert_type: str | None = None,
    agent_id: int | None = None,
    page: int = 1,
    page_size: int = 10,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if page < 1:
        page = 1

    if page_size < 1:
        page_size = 10

    if page_size > 100:
        page_size = 100

    query = (
        db.query(SecurityAlert)
        .join(Agent)
        .filter(
            Agent.owner_id == current_user.id
        )
    )

    if status:
        query = query.filter(
            SecurityAlert.status == status
        )

    if severity:
        query = query.filter(
            SecurityAlert.severity == severity
        )

    if alert_type:
        query = query.filter(
            SecurityAlert.alert_type == alert_type
        )

    if agent_id:
        query = query.filter(
            SecurityAlert.agent_id == agent_id
        )

    total = query.count()

    alerts = (
        query
        .order_by(SecurityAlert.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    pages = max(
        1,
        (total + page_size - 1) // page_size
    )

    return SecurityAlertListResponse(
        items=alerts,
        page=page,
        page_size=page_size,
        total=total,
        pages=pages
    )


@router.get(
    "/{alert_id}",
    response_model=SecurityAlertResponse
)
def get_security_alert(
    alert_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return get_owned_alert(
        alert_id=alert_id,
        current_user=current_user,
        db=db
    )
@router.patch(
    "/{alert_id}/status",
    response_model=SecurityAlertResponse
)
def update_security_alert_status(
    alert_id: int,
    status: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    allowed_statuses = {
        "OPEN",
        "ACKNOWLEDGED",
        "RESOLVED"
    }

    if status not in allowed_statuses:
        raise HTTPException(
            status_code=400,
            detail="Invalid alert status"
        )

    alert = get_owned_alert(
        alert_id=alert_id,
        current_user=current_user,
        db=db
    )

    if alert.status == "RESOLVED":
        raise HTTPException(
            status_code=400,
            detail="Resolved alert cannot be updated"
        )

    alert.status = status

    db.commit()
    db.refresh(alert)

    return alert