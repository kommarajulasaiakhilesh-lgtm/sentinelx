from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.db.database import get_db
from app.models.agent import Agent
from app.models.user import User
from app.schemas.agent import AgentCreate, AgentResponse


router = APIRouter(
    prefix="/api/agents",
    tags=["Agents"]
)


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