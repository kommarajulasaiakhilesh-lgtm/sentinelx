from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.db.database import get_db
from app.models.agent import Agent
from app.models.user import User
from app.schemas.incident import (
    IncidentCreate,
    IncidentListResponse,
    IncidentResponse,
    IncidentUpdate,
)
from app.schemas.incident_response import (
    IncidentResponseActionCreate,
    IncidentResponseActionCreateResponse,
    IncidentResponseActionResponse,
)
from app.schemas.incident_timeline import (
    IncidentTimelineCreate,
    IncidentTimelineResponse,
)
from app.services.incident_service import (
    add_incident_timeline_entry,
    create_failed_response_action,
    create_incident,
    create_incident_timeline_entry,
    create_response_action,
    get_incident,
    get_incident_response_actions,
    get_owned_api_key,
    get_owned_tool,
    get_incident_timeline,
    list_incidents,
    rotate_agent_api_key_for_incident,
    update_incident,
)

router = APIRouter(
    prefix="/api/incidents",
    tags=["Incidents"],
)


@router.post("", response_model=IncidentResponse, status_code=201)
def create_incident_endpoint(
    incident_data: IncidentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    incident = create_incident(
        db=db,
        agent_id=incident_data.agent_id,
        user_id=current_user.id,
        title=incident_data.title,
        description=incident_data.description,
        severity=incident_data.severity,
    )

    if incident is None:
        raise HTTPException(
            status_code=404,
            detail="Agent not found",
        )

    return incident


@router.get("", response_model=IncidentListResponse)
def list_incidents_endpoint(
    page: int = 1,
    page_size: int = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if page < 1 or page_size < 1 or page_size > 100:
        raise HTTPException(
            status_code=400,
            detail="Invalid pagination parameters",
        )

    incidents, total = list_incidents(
        db=db,
        user_id=current_user.id,
        page=page,
        page_size=page_size,
    )

    pages = (total + page_size - 1) // page_size

    return IncidentListResponse(
        items=incidents,
        total=total,
        page=page,
        page_size=page_size,
        pages=pages,
    )


@router.get(
    "/{incident_id}",
    response_model=IncidentResponse,
)
def get_incident_endpoint(
    incident_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    incident = get_incident(
        db=db,
        incident_id=incident_id,
        user_id=current_user.id,
    )

    if incident is None:
        raise HTTPException(
            status_code=404,
            detail="Incident not found",
        )

    return incident


@router.patch(
    "/{incident_id}",
    response_model=IncidentResponse,
)
def update_incident_endpoint(
    incident_id: int,
    incident_data: IncidentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    incident = update_incident(
        db=db,
        incident_id=incident_id,
        user_id=current_user.id,
        title=incident_data.title,
        description=incident_data.description,
        severity=incident_data.severity,
        status=incident_data.status,
    )

    if incident is None:
        raise HTTPException(
            status_code=404,
            detail="Incident not found",
        )

    return incident


@router.get(
    "/{incident_id}/timeline",
    response_model=list[IncidentTimelineResponse],
)
def list_incident_timeline_endpoint(
    incident_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    timeline = get_incident_timeline(
        db=db,
        incident_id=incident_id,
        user_id=current_user.id,
    )

    if timeline is None:
        raise HTTPException(
            status_code=404,
            detail="Incident not found",
        )

    return timeline


@router.post(
    "/{incident_id}/timeline",
    response_model=IncidentTimelineResponse,
    status_code=201,
)
def create_incident_timeline_endpoint(
    incident_id: int,
    timeline_data: IncidentTimelineCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    entry = create_incident_timeline_entry(
        db=db,
        incident_id=incident_id,
        entry_type=timeline_data.entry_type,
        description=timeline_data.description,
        created_by_user_id=current_user.id,
    )

    if entry is None:
        raise HTTPException(
            status_code=404,
            detail="Incident not found",
        )

    return entry


@router.get(
    "/{incident_id}/actions",
    response_model=list[IncidentResponseActionResponse],
)
def list_incident_actions_endpoint(
    incident_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    actions = get_incident_response_actions(
        db=db,
        incident_id=incident_id,
        user_id=current_user.id,
    )

    if actions is None:
        raise HTTPException(
            status_code=404,
            detail="Incident not found",
        )

    return actions


@router.post(
    "/{incident_id}/actions",
    response_model=IncidentResponseActionCreateResponse,
    status_code=201,
)
def create_incident_action_endpoint(
    incident_id: int,
    action_data: IncidentResponseActionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    incident = get_incident(
        db=db,
        incident_id=incident_id,
        user_id=current_user.id,
    )

    if incident is None:
        raise HTTPException(
            status_code=404,
            detail="Incident not found",
        )

    agent = (
        db.query(Agent)
        .filter(
            Agent.id == incident.agent_id,
            Agent.owner_id == current_user.id,
        )
        .first()
    )

    if agent is None:
        raise HTTPException(
            status_code=404,
            detail="Incident not found",
        )

    if (
        action_data.agent_id is not None
        and action_data.agent_id != agent.id
    ):
        raise HTTPException(
            status_code=400,
            detail="Invalid agent target",
        )

    if action_data.action_type == "SUSPEND_AGENT":
        agent.status = "SUSPENDED"

        action = create_response_action(
            db=db,
            incident_id=incident_id,
            user_id=current_user.id,
            action_type="SUSPEND_AGENT",
            agent_id=agent.id,
            tool_id=None,
            api_key_id=None,
            reason=action_data.reason,
            result="SUCCESS",
            details=f"Agent {agent.id} suspended",
        )

        if action is None:
            db.rollback()
            raise HTTPException(
                status_code=500,
                detail="Failed to record response action",
            )

        add_incident_timeline_entry(
            db=db,
            incident_id=incident_id,
            entry_type="AGENT_SUSPENDED",
            description=f"Agent {agent.id} suspended",
            created_by_user_id=current_user.id,
        )

        add_incident_timeline_entry(
            db=db,
            incident_id=incident_id,
            entry_type="RESPONSE_ACTION",
            description="Response action SUSPEND_AGENT executed successfully",
            created_by_user_id=current_user.id,
        )

        db.commit()
        db.refresh(action)

        return IncidentResponseActionCreateResponse.model_validate(action)

    if action_data.action_type == "DISABLE_TOOL":
        tool = get_owned_tool(
            db=db,
            incident_id=incident_id,
            user_id=current_user.id,
            tool_id=action_data.tool_id,
        )

        if tool is None:
            raise HTTPException(
                status_code=400,
                detail="Invalid tool target",
            )

        tool.enabled = False

        action = create_response_action(
            db=db,
            incident_id=incident_id,
            user_id=current_user.id,
            action_type="DISABLE_TOOL",
            agent_id=agent.id,
            tool_id=tool.id,
            api_key_id=None,
            reason=action_data.reason,
            result="SUCCESS",
            details=f"Tool {tool.id} disabled",
        )

        if action is None:
            db.rollback()
            raise HTTPException(
                status_code=500,
                detail="Failed to record response action",
            )

        add_incident_timeline_entry(
            db=db,
            incident_id=incident_id,
            entry_type="TOOL_DISABLED",
            description=f"Tool {tool.id} disabled",
            created_by_user_id=current_user.id,
        )

        add_incident_timeline_entry(
            db=db,
            incident_id=incident_id,
            entry_type="RESPONSE_ACTION",
            description="Response action DISABLE_TOOL executed successfully",
            created_by_user_id=current_user.id,
        )

        db.commit()
        db.refresh(action)

        return IncidentResponseActionCreateResponse.model_validate(action)

    if action_data.action_type == "ROTATE_AGENT_API_KEY":
        old_api_key = get_owned_api_key(
            db=db,
            incident_id=incident_id,
            user_id=current_user.id,
            api_key_id=action_data.api_key_id,
        )

        if old_api_key is None:
            raise HTTPException(
                status_code=400,
                detail="Invalid API key target",
            )

        new_api_key, raw_api_key = rotate_agent_api_key_for_incident(
            db=db,
            incident_id=incident_id,
            user_id=current_user.id,
            api_key_id=action_data.api_key_id,
        )

        if new_api_key is None or raw_api_key is None:
            db.rollback()

            raise HTTPException(
                status_code=500,
                detail="API key rotation failed",
            )

        action = create_response_action(
            db=db,
            incident_id=incident_id,
            user_id=current_user.id,
            action_type="ROTATE_AGENT_API_KEY",
            agent_id=agent.id,
            tool_id=None,
            api_key_id=new_api_key.id,
            reason=action_data.reason,
            result="SUCCESS",
            details="Agent API key rotated successfully",
        )

        if action is None:
            db.rollback()

            raise HTTPException(
                status_code=500,
                detail="Failed to record response action",
            )

        add_incident_timeline_entry(
            db=db,
            incident_id=incident_id,
            entry_type="API_KEY_ROTATED",
            description="Agent API key rotated successfully",
            created_by_user_id=current_user.id,
        )

        add_incident_timeline_entry(
            db=db,
            incident_id=incident_id,
            entry_type="RESPONSE_ACTION",
            description="Response action ROTATE_AGENT_API_KEY executed successfully",
            created_by_user_id=current_user.id,
        )

        db.commit()
        db.refresh(action)

        return IncidentResponseActionCreateResponse(
            id=action.id,
            incident_id=action.incident_id,
            action_type=action.action_type,
            agent_id=action.agent_id,
            tool_id=action.tool_id,
            api_key_id=action.api_key_id,
            authorized_by_user_id=action.authorized_by_user_id,
            reason=action.reason,
            result=action.result,
            details=action.details,
            created_at=action.created_at,
            api_key=raw_api_key,
        )

    raise HTTPException(
        status_code=400,
        detail="Unsupported action type",
    )