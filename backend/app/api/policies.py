from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.db.database import get_db
from app.services.audit_service import record_audit_safely
from app.services.policy_version_service import snapshot_policy, rollback_policy
from app.models.agent import Agent
from app.models.policy import Policy
from app.models.policy_version import PolicyVersion
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
    db.commit()
    db.refresh(policy)

    snapshot_policy(db, policy, actor=current_user, change_note="created")

    record_audit_safely(
        db,
        actor=current_user,
        action="POLICY_CREATED",
        resource_type="POLICY",
        resource_id=policy.id,
        summary=f"Created policy '{policy.name}' on agent '{agent.name}'",
    )

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

    db.commit()
    db.refresh(policy)

    snapshot_policy(
        db, policy, actor=current_user, change_note=f"updated ({changed_fields})"
    )

    record_audit_safely(
        db,
        actor=current_user,
        action="POLICY_UPDATED",
        resource_type="POLICY",
        resource_id=policy.id,
        summary=f"Updated policy '{policy.name}' ({changed_fields})",
    )

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

    # Remove version history first to satisfy the foreign key.
    db.query(PolicyVersion).filter(
        PolicyVersion.policy_id == policy.id
    ).delete(synchronize_session=False)

    db.delete(policy)
    db.commit()

    record_audit_safely(
        db,
        actor=current_user,
        action="POLICY_DELETED",
        resource_type="POLICY",
        resource_id=policy_id,
        summary=f"Deleted policy '{deleted_name}'",
    )

    return {
        "message": "Policy deleted successfully",
        "policy_id": policy_id
    }


# ============================================================
# POLICY VERSION HISTORY
# ============================================================

def _owned_policy(db: Session, policy_id: int, user: User) -> Policy:
    policy = (
        db.query(Policy)
        .join(Agent)
        .filter(Policy.id == policy_id, Agent.owner_id == user.id)
        .first()
    )
    if policy is None:
        raise HTTPException(status_code=404, detail="Policy not found")
    return policy


def _version_dict(v: PolicyVersion) -> dict:
    return {
        "id": v.id,
        "version_number": v.version_number,
        "name": v.name,
        "description": v.description,
        "policy_type": v.policy_type,
        "action": v.action,
        "priority": v.priority,
        "condition": v.condition,
        "enabled": v.enabled,
        "change_note": v.change_note,
        "changed_by_user_id": v.changed_by_user_id,
        "created_at": v.created_at.isoformat() if v.created_at else None,
    }


@router.get("/policy/{policy_id}/versions")
def get_policy_versions(
    policy_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _owned_policy(db, policy_id, current_user)
    versions = (
        db.query(PolicyVersion)
        .filter(PolicyVersion.policy_id == policy_id)
        .order_by(PolicyVersion.version_number.desc())
        .all()
    )
    return {"count": len(versions), "versions": [_version_dict(v) for v in versions]}


@router.post(
    "/policy/{policy_id}/rollback/{version_number}",
    response_model=PolicyResponse,
)
def rollback_policy_version(
    policy_id: int,
    version_number: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    policy = _owned_policy(db, policy_id, current_user)
    version = (
        db.query(PolicyVersion)
        .filter(
            PolicyVersion.policy_id == policy_id,
            PolicyVersion.version_number == version_number,
        )
        .first()
    )
    if version is None:
        raise HTTPException(status_code=404, detail="Policy version not found")

    rollback_policy(db, policy, version)
    snapshot_policy(
        db,
        policy,
        actor=current_user,
        change_note=f"rolled back to v{version_number}",
    )
    record_audit_safely(
        db,
        actor=current_user,
        action="POLICY_ROLLED_BACK",
        resource_type="POLICY",
        resource_id=policy.id,
        summary=f"Rolled policy '{policy.name}' back to version {version_number}",
    )

    return policy