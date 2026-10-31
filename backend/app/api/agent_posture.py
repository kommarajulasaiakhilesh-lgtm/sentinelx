"""Agent Security Posture API.

Read-only endpoints exposing configuration-centric posture scores for the
authenticated operator's agents. Ownership is enforced on every lookup.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.db.database import get_db
from app.models.agent import Agent
from app.models.user import User
from app.services.agent_posture_service import (
    evaluate_agent_posture,
    evaluate_fleet_posture,
)


router = APIRouter(
    prefix="/api/posture",
    tags=["Agent Security Posture"],
)


@router.get("")
def get_fleet_posture(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Posture summary and per-agent breakdown for the operator's fleet."""
    return evaluate_fleet_posture(db, current_user.id)


@router.get("/agents/{agent_id}")
def get_agent_posture(
    agent_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Posture report for a single owned agent."""
    agent = (
        db.query(Agent)
        .filter(Agent.id == agent_id, Agent.owner_id == current_user.id)
        .first()
    )

    if agent is None:
        raise HTTPException(status_code=404, detail="Agent not found")

    return evaluate_agent_posture(db, agent)
