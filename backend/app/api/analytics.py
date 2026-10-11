
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.db.database import get_db
from app.models.agent import Agent
from app.models.user import User
from app.schemas.analytics import SecurityMetricsResponse
from app.services.analytics_service import generate_agent_analytics
from app.services.security_metrics_service import calculate_security_metrics


router = APIRouter(
    prefix="/api/analytics",
    tags=["Analytics"],
)


def _get_accessible_agent(
    db: Session,
    agent_id: int,
    current_user: User,
) -> Agent:
    agent = (
        db.query(Agent)
        .filter(Agent.id == agent_id)
        .first()
    )

    if (
        agent is None
        or (
            current_user.role != "ADMIN"
            and agent.owner_id != current_user.id
        )
    ):
        raise HTTPException(
            status_code=404,
            detail="Analytics not found for this agent",
        )

    return agent


@router.get(
    "/agents/{agent_id}",
    response_model=SecurityMetricsResponse,
)
def get_agent_metrics(
    agent_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _get_accessible_agent(db, agent_id, current_user)

    metrics = calculate_security_metrics(db, agent_id)

    if metrics is None:
        raise HTTPException(
            status_code=404,
            detail="Analytics not found for this agent",
        )

    return metrics


@router.post(
    "/agents/{agent_id}/refresh",
    response_model=SecurityMetricsResponse,
)
def refresh_agent_metrics(
    agent_id: int,
    period_start: datetime,
    period_end: datetime,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _get_accessible_agent(db, agent_id, current_user)

    if period_start >= period_end:
        raise HTTPException(
            status_code=422,
            detail="period_start must be earlier than period_end",
        )

    generate_agent_analytics(
        db=db,
        agent_id=agent_id,
        period_start=period_start,
        period_end=period_end,
    )

    metrics = calculate_security_metrics(db, agent_id)

    if metrics is None:
        raise HTTPException(
            status_code=500,
            detail="Analytics refresh completed without a readable result",
        )

    return metrics
