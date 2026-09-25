from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.db.database import get_db
from app.models.agent import Agent
from app.models.tool import Tool
from app.models.user import User
from app.schemas.tool import ToolCreate, ToolResponse


router = APIRouter(
    prefix="/api/agents",
    tags=["Tools"]
)


@router.post(
    "/{agent_id}/tools",
    response_model=ToolResponse,
    status_code=status.HTTP_201_CREATED
)
def create_tool(
    agent_id: int,
    tool_data: ToolCreate,
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

    tool = Tool(
        agent_id=agent.id,
        name=tool_data.name,
        description=tool_data.description,
        tool_type=tool_data.tool_type
    )

    db.add(tool)
    db.commit()
    db.refresh(tool)

    return tool


@router.get(
    "/{agent_id}/tools",
    response_model=list[ToolResponse]
)
def get_agent_tools(
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

    tools = (
        db.query(Tool)
        .filter(
            Tool.agent_id == agent.id
        )
        .all()
    )

    return tools