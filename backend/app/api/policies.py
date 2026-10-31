from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.db.database import get_db
from app.services.audit_service import record_audit
from app.models.agent import Agent
from app.models.policy import Policy
from app.models.user import User
from app.schemas.policy import (
    PolicyCreate,
    PolicyUpdate,
    PolicyResponse
)


router = APIRouter(
    prefix="/api/policies",
    tags=["Policies"]
)


# ============================================================
# CREATE POLICY
# ============================================================

@router.post(
    "/agent/{agent_id}",
    response_model=PolicyResponse,
    status_code=status.HTTP_201_CREATED
)
def create_policy(
    agent_id: int,
    policy_data: PolicyCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    agent = (
        db.query(Agent)
        .filter(
            Agent.id == agent_id,
            Agent.owner_id == current_user.id
        )
        .first()
    )

    if agent is None:
        raise HTTPException(
            status_code=404,
            detail="Agent not found"
        )

    policy = Policy (
    agent_id=agent.id,
    name=policy_data.name,
    description=policy_data.description,
    policy_type=policy_data.policy_type,
    action=policy_data.action,
    priority=policy_data.priority,
    condition=policy_data.condition,
     )

    db.add(policy)
    db.flush()

    record_audit(
        db,
        actor=current_user,
        action="POLICY_CREATED",
        resource_type="POLICY",
        resource_id=policy.id,
        summary=f"Created policy '{policy.name}' on agent '{agent.name}'",
    )

    db.commit()
    db.refresh(policy)

    return policy


# ============================================================
# GET POLICIES FOR AN AGENT
# ============================================================

@router.get(
    "/agent/{agent_id}",
    response_model=list[PolicyResponse]
)
def get_agent_policies(
    agent_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    agent = (
        db.query(Agent)
        .filter(
            Agent.id == agent_id,
            Agent.owner_id == current_user.id
        )
        .first()
    )

    if agent is None:
        raise HTTPException(
            status_code=404,
            detail="Agent not found"
        )

    policies = (
        db.query(Policy)
        .filter(
            Policy.agent_id == agent.id
        )
        .all()
    )

    return policies


# ============================================================
# UPDATE POLICY
# ============================================================

@router.patch(
    "/policy/{policy_id}",
    response_model=PolicyResponse
)
def update_policy(
    policy_id: int,
    policy_data: PolicyUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    policy = (
        db.query(Policy)
        .join(Agent)
        .filter(
            Policy.id == policy_id,
            Agent.owner_id == current_user.id
        )
        .first()
    )

    if policy is None:
        raise HTTPException(
            status_code=404,
            detail="Policy not found"
        )

    update_data = policy_data.model_dump(
        exclude_unset=True
    )

    for field, value in update_data.items():
        setattr(policy, field, value)

    changed_fields = ", ".join(sorted(update_data.keys())) or "no fields"

    record_audit(
        db,
        actor=current_user,
        action="POLICY_UPDATED",
        resource_type="POLICY",
        resource_id=policy.id,
        summary=f"Updated policy '{policy.name}' ({changed_fields})",
    )

    db.commit()
    db.refresh(policy)

    return policy


# ============================================================
# DELETE POLICY
# ============================================================

@router.delete(
    "/policy/{policy_id}"
)
def delete_policy(
    policy_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    policy = (
        db.query(Policy)
        .join(Agent)
        .filter(
            Policy.id == policy_id,
            Agent.owner_id == current_user.id
        )
        .first()
    )

    if policy is None:
        raise HTTPException(
            status_code=404,
            detail="Policy not found"
        )

    deleted_name = policy.name

    record_audit(
        db,
        actor=current_user,
        action="POLICY_DELETED",
        resource_type="POLICY",
        resource_id=policy_id,
        summary=f"Deleted policy '{deleted_name}'",
    )

    db.delete(policy)
    db.commit()

    return {
        "message": "Policy deleted successfully",
        "policy_id": policy_id
    }