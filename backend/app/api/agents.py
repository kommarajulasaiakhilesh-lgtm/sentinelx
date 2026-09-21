from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session

from app.api.dependencies import (
    get_current_user,
    get_current_agent
)

from app.db.database import get_db

from app.models.agent import Agent
from app.models.user import User
from app.models.agent_api_key import AgentAPIKey

from app.schemas.agent import (
    AgentCreate,
    AgentResponse
)

from app.schemas.agent_api_key import (
    AgentAPIKeyCreateResponse
)

from app.core.agent_api_key import (
    generate_agent_api_key,
    hash_agent_api_key
)


router = APIRouter(
    prefix="/api/agents",
    tags=["Agents"]
)


# ============================================================
# CREATE AGENT
# ============================================================

@router.post(
    "",
    response_model=AgentResponse,
    status_code=status.HTTP_201_CREATED
)
def create_agent(
    agent_data: AgentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    agent = Agent(
        owner_id=current_user.id,
        name=agent_data.name,
        description=agent_data.description
    )

    db.add(agent)
    db.commit()
    db.refresh(agent)

    return agent


# ============================================================
# GET MY AGENTS
# ============================================================

@router.get(
    "/my-agents",
    response_model=list[AgentResponse]
)
def get_my_agents(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    agents = (
        db.query(Agent)
        .filter(
            Agent.owner_id == current_user.id
        )
        .all()
    )

    return agents


# ============================================================
# GET SPECIFIC AGENT
# ============================================================
@router.get("/me")
def get_agent_profile(
    current_agent: Agent = Depends(get_current_agent)
):
    return {
        "message": "Agent authentication successful",
        "agent_id": current_agent.id,
        "name": current_agent.name,
        "owner_id": current_agent.owner_id,
        "status": current_agent.status
    }
@router.patch(
    "/{agent_id}/status"
)
def update_agent_status(
    agent_id: int,
    status_data: dict,
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

    new_status = status_data.get("status")

    allowed_statuses = [
        "ACTIVE",
        "SUSPENDED"
    ]

    if new_status not in allowed_statuses:
        raise HTTPException(
            status_code=400,
            detail="Invalid agent status"
        )

    agent.status = new_status

    db.commit()
    db.refresh(agent)

    return {
        "message": "Agent status updated successfully",
        "agent_id": agent.id,
        "status": agent.status
    }
@router.get(
    "/{agent_id}",
    response_model=AgentResponse
)
def get_agent(
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

    return agent


# ============================================================
# CREATE AGENT API KEY
# ============================================================

@router.post(
    "/{agent_id}/api-keys",
    response_model=AgentAPIKeyCreateResponse,
    status_code=status.HTTP_201_CREATED
)
def create_agent_api_key(
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

    raw_api_key = generate_agent_api_key()

    key_hash = hash_agent_api_key(
        raw_api_key
    )

    api_key = AgentAPIKey(
        agent_id=agent.id,
        key_hash=key_hash
    )

    db.add(api_key)
    db.commit()
    db.refresh(api_key)

    return {
        "id": api_key.id,
        "agent_id": api_key.agent_id,
        "api_key": raw_api_key,
        "created_at": api_key.created_at,
        "expires_at": api_key.expires_at,
        "is_active": api_key.is_active
    }


# ============================================================
# AGENT AUTHENTICATION TEST
# ============================================================

