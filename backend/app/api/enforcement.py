from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_agent
from app.db.database import get_db
from app.models.agent import Agent
from app.schemas.enforcement import (
    EnforcementRequest,
    EnforcementResponse
)
from app.services.policy_engine import evaluate_policy


router = APIRouter(
    prefix="/api/enforcement",
    tags=["Enforcement"]
)


@router.post(
    "/evaluate",
    response_model=EnforcementResponse
)
def evaluate_request(
    request: EnforcementRequest,
    current_agent: Agent = Depends(get_current_agent),
    db: Session = Depends(get_db)
):

    if request.agent_id != current_agent.id:
        raise HTTPException(
            status_code=403,
            detail="Agent ID does not match authenticated agent"
        )

    result = evaluate_policy(
        agent=current_agent,
        input_text=request.input_text,
        db=db
    )

    return {
        "agent_id": current_agent.id,
        "decision": result["decision"],
        "reason": result["reason"],
        "policy_type": result["policy_type"]
    }