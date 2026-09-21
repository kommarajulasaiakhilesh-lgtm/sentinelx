from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user, get_current_agent
from app.db.database import get_db
from app.models.agent import Agent
from app.models.agent_api_key import AgentAPIKey
from app.models.user import User
from app.schemas.agent import AgentCreate, AgentResponse
from app.schemas.agent_api_key import (
    AgentAPIKeyCreateResponse,
    AgentAPIKeyResponse
)
from app.core.agent_api_key import (
    generate_agent_api_key,
    extract_key_selector,
    hash_agent_api_key
)

router = APIRouter(
    prefix="/api/agents",
    tags=["Agents"]
)


# ---------------------------------------------------------
# Create Agent
# ---------------------------------------------------------

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


# ---------------------------------------------------------
# Get My Agents
# ---------------------------------------------------------

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


# ---------------------------------------------------------
# Get Current Agent
# ---------------------------------------------------------

@router.get(
    "/me",
    response_model=AgentResponse
)
def get_current_agent_info(
    current_agent: Agent = Depends(get_current_agent)
):
    return current_agent


# ---------------------------------------------------------
# Get Agent By ID
# ---------------------------------------------------------

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


# ---------------------------------------------------------
# Create Agent API Key
# ---------------------------------------------------------

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
    # Verify that the authenticated user owns this agent
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

    # Generate raw API key
    raw_api_key = generate_agent_api_key()

    # Extract selector from raw API key
    key_selector = extract_key_selector(raw_api_key)

    if key_selector is None:
        raise HTTPException(
            status_code=500,
            detail="Failed to generate agent API key"
        )

    # Hash complete API key before storing it
    key_hash = hash_agent_api_key(raw_api_key)

    # Store only selector + hash
    api_key = AgentAPIKey(
        agent_id=agent.id,
        key_selector=key_selector,
        key_hash=key_hash
    )

    db.add(api_key)
    db.commit()
    db.refresh(api_key)

    # Return raw key ONLY during creation
    return {
        "id": api_key.id,
        "agent_id": api_key.agent_id,
        "api_key": raw_api_key,
        "created_at": api_key.created_at,
        "expires_at": api_key.expires_at,
        "is_active": api_key.is_active
    }


# ---------------------------------------------------------
# Get Agent API Keys
# ---------------------------------------------------------

@router.get(
    "/{agent_id}/api-keys",
    response_model=list[AgentAPIKeyResponse]
)
def get_agent_api_keys(
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

    api_keys = (
        db.query(AgentAPIKey)
        .filter(
            AgentAPIKey.agent_id == agent.id
        )
        .all()
    )

    return api_keys


# ---------------------------------------------------------
# Update Agent Status
# ---------------------------------------------------------

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