from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.analytics import SecurityMetricsResponse
from app.services.security_metrics_service import calculate_security_metrics


router = APIRouter(
    prefix="/api/analytics",
    tags=["Analytics"]
)


@router.get(
    "/agents/{agent_id}",
    response_model=SecurityMetricsResponse
)
def get_agent_metrics(
    agent_id: int,
    db: Session = Depends(get_db)
):
    metrics = calculate_security_metrics(
        db,
        agent_id
    )

    if metrics is None:
        raise HTTPException(
            status_code=404,
            detail="Analytics not found for this agent"
        )

    return metrics