from sqlalchemy.orm import Session
from app.services.webhook_service import queue_webhook_event
from app.core.agent_api_key import (
    extract_key_selector,
    generate_agent_api_key,
    hash_agent_api_key,
)
from app.models.agent import Agent
from app.models.agent_api_key import AgentAPIKey
from app.models.incident import Incident
from app.models.incident_alert import IncidentAlert
from app.models.incident_response import IncidentResponseAction
from app.models.incident_timeline import IncidentTimelineEntry
from app.models.security_alert import SecurityAlert
from app.models.tool import Tool


def get_owned_agent(
    db: Session,
    agent_id: int,
    user_id: int,
) -> Agent | None:
    return (
        db.query(Agent)
        .filter(
            Agent.id == agent_id,
            Agent.owner_id == user_id,
        )
        .first()
    )


def create_incident(
    db: Session,
    agent_id: int,
    user_id: int,
    title: str,
    description: str | None,
    severity: str,
) -> Incident | None:
    agent = get_owned_agent(
        db=db,
        agent_id=agent_id,
        user_id=user_id,
    )

    if agent is None:
        return None

    incident = Incident(
        agent_id=agent.id,
        title=title,
        description=description,
        severity=severity,
        status="OPEN",
    )

    db.add(incident)
    db.flush()

    queue_webhook_event(
        db=db,
        owner_id=agent.owner_id,
        event_type="INCIDENT_CREATED",
        payload={
            "incident_id": incident.id,
            "agent_id": incident.agent_id,
            "title": incident.title,
            "description": incident.description,
            "severity": incident.severity,
            "status": incident.status,
        },
    )

    db.commit()
    db.refresh(incident)

    return incident


def get_incident(
    db: Session,
    incident_id: int,
    user_id: int,
) -> Incident | None:
    return (
        db.query(Incident)
        .join(Agent, Agent.id == Incident.agent_id)
        .filter(
            Incident.id == incident_id,
            Agent.owner_id == user_id,
        )
        .first()
    )


def list_incidents(
    db: Session,
    user_id: int,
    page: int = 1,
    page_size: int = 10,
) -> tuple[list[Incident], int]:
    query = (
        db.query(Incident)
        .join(Agent, Agent.id == Incident.agent_id)
        .filter(Agent.owner_id == user_id)
    )

    total = query.count()

    incidents = (
        query.order_by(Incident.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    return incidents, total


def update_incident(
    db: Session,
    incident_id: int,
    user_id: int,
    title: str | None = None,
    description: str | None = None,
    severity: str | None = None,
    status: str | None = None,
) -> Incident | None:
    incident = get_incident(
        db=db,
        incident_id=incident_id,
        user_id=user_id,
    )

    if incident is None:
        return None

    previous_severity = incident.severity
    previous_status = incident.status

    if title is not None:
        incident.title = title

    if description is not None:
        incident.description = description

    if severity is not None:
        incident.severity = severity

    if status is not None:
        incident.status = status

    db.flush()

    if (
        severity is not None
        and severity != previous_severity
    ):
        queue_webhook_event(
            db=db,
            owner_id=incident.agent.owner_id,
            event_type="INCIDENT_SEVERITY_CHANGED",
            payload={
                "incident_id": incident.id,
                "agent_id": incident.agent_id,
                "title": incident.title,
                "severity": incident.severity,
                "previous_severity": previous_severity,
                "status": incident.status,
            },
        )

    if (
        status is not None
        and status != previous_status
        and status == "CONTAINED"
    ):
        queue_webhook_event(
            db=db,
            owner_id=incident.agent.owner_id,
            event_type="INCIDENT_CONTAINED",
            payload={
                "incident_id": incident.id,
                "agent_id": incident.agent_id,
                "title": incident.title,
                "severity": incident.severity,
                "status": incident.status,
            },
        )

    if (
        status is not None
        and status != previous_status
        and status == "RESOLVED"
    ):
        queue_webhook_event(
            db=db,
            owner_id=incident.agent.owner_id,
            event_type="INCIDENT_RESOLVED",
            payload={
                "incident_id": incident.id,
                "agent_id": incident.agent_id,
                "title": incident.title,
                "severity": incident.severity,
                "status": incident.status,
            },
        )

    db.commit()
    db.refresh(incident)

    return incident


def get_incident_alerts(
    db: Session,
    incident_id: int,
    user_id: int,
) -> list[SecurityAlert] | None:
    incident = get_incident(
        db=db,
        incident_id=incident_id,
        user_id=user_id,
    )

    if incident is None:
        return None

    return (
        db.query(SecurityAlert)
        .join(
            IncidentAlert,
            IncidentAlert.alert_id == SecurityAlert.id,
        )
        .filter(
            IncidentAlert.incident_id == incident_id,
        )
        .order_by(SecurityAlert.created_at.desc())
        .all()
    )


def get_incident_timeline(
    db: Session,
    incident_id: int,
    user_id: int,
) -> list[IncidentTimelineEntry] | None:
    incident = get_incident(
        db=db,
        incident_id=incident_id,
        user_id=user_id,
    )

    if incident is None:
        return None

    return (
        db.query(IncidentTimelineEntry)
        .filter(
            IncidentTimelineEntry.incident_id == incident_id,
        )
        .order_by(IncidentTimelineEntry.created_at.asc())
        .all()
    )


def add_incident_timeline_entry(
    db: Session,
    incident_id: int,
    entry_type: str,
    description: str,
    created_by_user_id: int | None = None,
) -> IncidentTimelineEntry:
    entry = IncidentTimelineEntry(
        incident_id=incident_id,
        entry_type=entry_type,
        description=description,
        created_by_user_id=created_by_user_id,
    )

    db.add(entry)
    db.flush()

    return entry


def create_incident_timeline_entry(
    db: Session,
    incident_id: int,
    entry_type: str,
    description: str,
    created_by_user_id: int | None = None,
) -> IncidentTimelineEntry | None:
    incident = get_incident(
        db=db,
        incident_id=incident_id,
        user_id=created_by_user_id,
    )

    if incident is None:
        return None

    entry = add_incident_timeline_entry(
        db=db,
        incident_id=incident_id,
        entry_type=entry_type,
        description=description,
        created_by_user_id=created_by_user_id,
    )

    db.commit()
    db.refresh(entry)

    return entry


def get_incident_response_actions(
    db: Session,
    incident_id: int,
    user_id: int,
) -> list[IncidentResponseAction] | None:
    incident = get_incident(
        db=db,
        incident_id=incident_id,
        user_id=user_id,
    )

    if incident is None:
        return None

    return (
        db.query(IncidentResponseAction)
        .filter(
            IncidentResponseAction.incident_id == incident_id,
        )
        .order_by(IncidentResponseAction.created_at.desc())
        .all()
    )


def get_owned_tool(
    db: Session,
    incident_id: int,
    user_id: int,
    tool_id: int,
) -> Tool | None:
    incident = get_incident(
        db=db,
        incident_id=incident_id,
        user_id=user_id,
    )

    if incident is None:
        return None

    return (
        db.query(Tool)
        .filter(
            Tool.id == tool_id,
            Tool.agent_id == incident.agent_id,
        )
        .first()
    )


def get_owned_api_key(
    db: Session,
    incident_id: int,
    user_id: int,
    api_key_id: int,
) -> AgentAPIKey | None:
    incident = get_incident(
        db=db,
        incident_id=incident_id,
        user_id=user_id,
    )

    if incident is None:
        return None

    return (
        db.query(AgentAPIKey)
        .filter(
            AgentAPIKey.id == api_key_id,
            AgentAPIKey.agent_id == incident.agent_id,
        )
        .first()
    )


def validate_incident_action_target(
    db: Session,
    incident_id: int,
    user_id: int,
    agent_id: int | None = None,
    tool_id: int | None = None,
    api_key_id: int | None = None,
) -> tuple[
    Incident | None,
    Agent | None,
    Tool | None,
    AgentAPIKey | None,
]:
    incident = get_incident(
        db=db,
        incident_id=incident_id,
        user_id=user_id,
    )

    if incident is None:
        return None, None, None, None

    agent = get_owned_agent(
        db=db,
        agent_id=incident.agent_id,
        user_id=user_id,
    )

    if agent is None:
        return None, None, None, None

    if agent_id is not None and agent_id != agent.id:
        return None, None, None, None

    tool = None

    if tool_id is not None:
        tool = get_owned_tool(
            db=db,
            incident_id=incident_id,
            user_id=user_id,
            tool_id=tool_id,
        )

        if tool is None:
            return None, None, None, None

    api_key = None

    if api_key_id is not None:
        api_key = get_owned_api_key(
            db=db,
            incident_id=incident_id,
            user_id=user_id,
            api_key_id=api_key_id,
        )

        if api_key is None:
            return None, None, None, None

    return incident, agent, tool, api_key


def rotate_agent_api_key_for_incident(
    db: Session,
    incident_id: int,
    user_id: int,
    api_key_id: int,
) -> tuple[AgentAPIKey | None, str | None]:
    (
        incident,
        agent,
        _,
        old_api_key,
    ) = validate_incident_action_target(
        db=db,
        incident_id=incident_id,
        user_id=user_id,
        api_key_id=api_key_id,
    )

    if (
        incident is None
        or agent is None
        or old_api_key is None
    ):
        return None, None

    new_raw_key = generate_agent_api_key()

    selector = extract_key_selector(new_raw_key)

    if selector is None:
        return None, None

    new_api_key = AgentAPIKey(
        agent_id=agent.id,
        key_selector=selector,
        key_hash=hash_agent_api_key(new_raw_key),
        expires_at=old_api_key.expires_at,
        is_active=True,
    )

    old_api_key.is_active = False

    db.add(new_api_key)
    db.flush()

    return new_api_key, new_raw_key


def create_response_action(
    db: Session,
    incident_id: int,
    user_id: int,
    action_type: str,
    agent_id: int,
    tool_id: int | None,
    api_key_id: int | None,
    reason: str,
    result: str,
    details: str | None,
) -> IncidentResponseAction | None:
    incident = get_incident(
        db=db,
        incident_id=incident_id,
        user_id=user_id,
    )

    if incident is None:
        return None

    action = IncidentResponseAction(
        incident_id=incident_id,
        action_type=action_type,
        agent_id=agent_id,
        tool_id=tool_id,
        api_key_id=api_key_id,
        authorized_by_user_id=user_id,
        reason=reason,
        result=result,
        details=details,
    )

    db.add(action)
    db.flush()

    return action


def create_failed_response_action(
    db: Session,
    incident_id: int,
    user_id: int,
    action_type: str,
    agent_id: int,
    tool_id: int | None,
    api_key_id: int | None,
    reason: str,
    details: str | None,
) -> IncidentResponseAction | None:
    return create_response_action(
        db=db,
        incident_id=incident_id,
        user_id=user_id,
        action_type=action_type,
        agent_id=agent_id,
        tool_id=tool_id,
        api_key_id=api_key_id,
        reason=reason,
        result="FAILED",
        details=details,
    )