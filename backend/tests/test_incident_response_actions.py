from fastapi.testclient import TestClient

from app.main import app
from app.api.dependencies import get_current_user
from app.db.database import SessionLocal
from app.models.user import User
from app.models.agent import Agent
from app.models.agent_api_key import AgentAPIKey
from app.models.incident import Incident
from app.models.incident_alert import IncidentAlert
from app.models.incident_response import IncidentResponseAction
from app.models.incident_timeline import IncidentTimelineEntry
from app.models.security_alert import SecurityAlert
from app.models.security_event import SecurityEvent
from app.models.tool import Tool


client = TestClient(app)


def get_test_user():
    db = SessionLocal()

    try:
        return (
            db.query(User)
            .filter(User.id == 4)
            .first()
        )
    finally:
        db.close()


def setup_user_override():
    user = get_test_user()

    if user is None:
        raise RuntimeError(
            "Test user with id=4 was not found"
        )

    app.dependency_overrides[get_current_user] = lambda: user


def teardown_user_override():
    app.dependency_overrides.clear()


def create_incident(agent_id=1):
    db = SessionLocal()

    try:
        incident = Incident(
            agent_id=agent_id,
            title="Response Action Test Incident",
            description="Incident used for response action testing",
            severity="HIGH",
            status="OPEN",
        )

        db.add(incident)
        db.commit()
        db.refresh(incident)

        return incident.id
    finally:
        db.close()


def cleanup_incident(incident_id):
    db = SessionLocal()

    try:
        incident = (
            db.query(Incident)
            .filter(Incident.id == incident_id)
            .first()
        )

        if incident:
            db.delete(incident)
            db.commit()
    finally:
        db.close()


def cleanup_tool(tool_id):
    db = SessionLocal()

    try:
        tool = (
            db.query(Tool)
            .filter(Tool.id == tool_id)
            .first()
        )

        if tool:
            db.delete(tool)
            db.commit()
    finally:
        db.close()


def cleanup_api_key(api_key_id):
    db = SessionLocal()

    try:
        api_key = (
            db.query(AgentAPIKey)
            .filter(AgentAPIKey.id == api_key_id)
            .first()
        )

        if api_key:
            db.delete(api_key)
            db.commit()
    finally:
        db.close()


def test_suspend_agent_response_action():
    setup_user_override()

    incident_id = None

    try:
        incident_id = create_incident(agent_id=1)

        response = client.post(
            f"/api/incidents/{incident_id}/actions",
            json={
                "action_type": "SUSPEND_AGENT",
                "agent_id": 1,
                "reason": "Contain compromised agent",
            },
        )

        assert response.status_code == 201

        data = response.json()

        assert data["action_type"] == "SUSPEND_AGENT"
        assert data["agent_id"] == 1
        assert data["result"] == "SUCCESS"
        assert data["reason"] == "Contain compromised agent"
        assert data["tool_id"] is None
        assert data["api_key_id"] is None

        db = SessionLocal()

        try:
            agent = (
                db.query(Agent)
                .filter(Agent.id == 1)
                .first()
            )

            assert agent is not None
            assert agent.status == "SUSPENDED"

            timeline = (
                db.query(IncidentTimelineEntry)
                .filter(
                    IncidentTimelineEntry.incident_id
                    == incident_id
                )
                .order_by(
                    IncidentTimelineEntry.created_at.asc()
                )
                .all()
            )

            entry_types = [
                entry.entry_type
                for entry in timeline
            ]

            assert "AGENT_SUSPENDED" in entry_types
            assert "RESPONSE_ACTION" in entry_types

        finally:
            db.close()

    finally:
        if incident_id is not None:
            cleanup_incident(incident_id)

        teardown_user_override()


def test_disable_tool_response_action():
    setup_user_override()

    incident_id = None
    tool_id = None

    try:
        db = SessionLocal()

        tool = Tool(
            agent_id=1,
            name="Response Test Tool",
            description="Tool used for response action testing",
            tool_type="file",
            enabled=True,
        )

        db.add(tool)
        db.commit()
        db.refresh(tool)

        tool_id = tool.id

        db.close()

        incident_id = create_incident(agent_id=1)

        response = client.post(
            f"/api/incidents/{incident_id}/actions",
            json={
                "action_type": "DISABLE_TOOL",
                "agent_id": 1,
                "tool_id": tool_id,
                "reason": "Disable compromised tool",
            },
        )

        assert response.status_code == 201

        data = response.json()

        assert data["action_type"] == "DISABLE_TOOL"
        assert data["agent_id"] == 1
        assert data["tool_id"] == tool_id
        assert data["api_key_id"] is None
        assert data["result"] == "SUCCESS"

        db = SessionLocal()

        try:
            tool = (
                db.query(Tool)
                .filter(Tool.id == tool_id)
                .first()
            )

            assert tool is not None
            assert tool.enabled is False

            timeline = (
                db.query(IncidentTimelineEntry)
                .filter(
                    IncidentTimelineEntry.incident_id
                    == incident_id
                )
                .all()
            )

            entry_types = [
                entry.entry_type
                for entry in timeline
            ]

            assert "TOOL_DISABLED" in entry_types
            assert "RESPONSE_ACTION" in entry_types

        finally:
            db.close()

    finally:
        if incident_id is not None:
            cleanup_incident(incident_id)

        if tool_id is not None:
            cleanup_tool(tool_id)

        teardown_user_override()


def test_rotate_agent_api_key_response_action():
    setup_user_override()

    incident_id = None
    old_key_id = None
    new_key_id = None

    try:
        db = SessionLocal()

        old_key = AgentAPIKey(
            agent_id=1,
            key_selector="responseold",
            key_hash="response-old-hash",
            is_active=True,
        )

        db.add(old_key)
        db.commit()
        db.refresh(old_key)

        old_key_id = old_key.id

        db.close()

        incident_id = create_incident(agent_id=1)

        response = client.post(
            f"/api/incidents/{incident_id}/actions",
            json={
                "action_type": "ROTATE_AGENT_API_KEY",
                "agent_id": 1,
                "api_key_id": old_key_id,
                "reason": "Rotate potentially compromised credential",
            },
        )

        assert response.status_code == 201

        data = response.json()

        assert data["action_type"] == "ROTATE_AGENT_API_KEY"
        assert data["agent_id"] == 1
        assert data["api_key_id"] != old_key_id
        assert data["result"] == "SUCCESS"

        assert data["api_key"] is not None
        assert data["api_key"].startswith("sx_")

        new_key_id = data["api_key_id"]

        db = SessionLocal()

        try:
            old_key = (
                db.query(AgentAPIKey)
                .filter(
                    AgentAPIKey.id == old_key_id
                )
                .first()
            )

            assert old_key is not None
            assert old_key.is_active is False

            new_key = (
                db.query(AgentAPIKey)
                .filter(
                    AgentAPIKey.id == new_key_id,
                    AgentAPIKey.agent_id == 1,
                )
                .first()
            )

            assert new_key is not None
            assert new_key.is_active is True

            timeline = (
                db.query(IncidentTimelineEntry)
                .filter(
                    IncidentTimelineEntry.incident_id
                    == incident_id
                )
                .all()
            )

            entry_types = [
                entry.entry_type
                for entry in timeline
            ]

            assert "API_KEY_ROTATED" in entry_types
            assert "RESPONSE_ACTION" in entry_types

        finally:
            db.close()

    finally:
        if incident_id is not None:
            cleanup_incident(incident_id)

        if new_key_id is not None:
            cleanup_api_key(new_key_id)

        if old_key_id is not None:
            cleanup_api_key(old_key_id)

        teardown_user_override()


def test_cross_user_incident_is_rejected():
    setup_user_override()

    incident_id = None

    try:
        db = SessionLocal()

        other_agent = (
            db.query(Agent)
            .filter(Agent.owner_id != 4)
            .first()
        )

        db.close()

        if other_agent is None:
            return

        incident_db = SessionLocal()

        incident = Incident(
            agent_id=other_agent.id,
            title="Cross User Incident",
            description="Incident owned by another user",
            severity="HIGH",
            status="OPEN",
        )

        incident_db.add(incident)
        incident_db.commit()
        incident_db.refresh(incident)

        incident_id = incident.id

        incident_db.close()

        response = client.post(
            f"/api/incidents/{incident_id}/actions",
            json={
                "action_type": "SUSPEND_AGENT",
                "agent_id": other_agent.id,
                "reason": "Unauthorized suspension attempt",
            },
        )

        assert response.status_code == 404
        assert response.json()["detail"] == "Incident not found"

    finally:
        if incident_id is not None:
            db = SessionLocal()

            try:
                incident = (
                    db.query(Incident)
                    .filter(
                        Incident.id == incident_id
                    )
                    .first()
                )

                if incident:
                    db.delete(incident)
                    db.commit()
            finally:
                db.close()

        teardown_user_override()


def test_cross_agent_tool_is_rejected():
    setup_user_override()

    incident_id = None
    tool_id = None

    try:
        db = SessionLocal()

        other_agent = (
            db.query(Agent)
            .filter(Agent.owner_id == 4)
            .filter(Agent.id != 1)
            .first()
        )

        if other_agent is None:
            db.close()
            return

        tool = Tool(
            agent_id=other_agent.id,
            name="Other Agent Tool",
            description="Tool belonging to another agent",
            tool_type="file",
            enabled=True,
        )

        db.add(tool)
        db.commit()
        db.refresh(tool)

        tool_id = tool.id

        db.close()

        incident_id = create_incident(agent_id=1)

        response = client.post(
            f"/api/incidents/{incident_id}/actions",
            json={
                "action_type": "DISABLE_TOOL",
                "agent_id": 1,
                "tool_id": tool_id,
                "reason": "Unauthorized tool disable attempt",
            },
        )

        assert response.status_code == 400
        assert response.json()["detail"] == "Invalid tool target"

        db = SessionLocal()

        try:
            tool = (
                db.query(Tool)
                .filter(Tool.id == tool_id)
                .first()
            )

            assert tool is not None
            assert tool.enabled is True

        finally:
            db.close()

    finally:
        if incident_id is not None:
            cleanup_incident(incident_id)

        if tool_id is not None:
            cleanup_tool(tool_id)

        teardown_user_override()


def test_cross_agent_api_key_is_rejected():
    setup_user_override()

    incident_id = None
    api_key_id = None

    try:
        db = SessionLocal()

        other_agent = (
            db.query(Agent)
            .filter(Agent.owner_id == 4)
            .filter(Agent.id != 1)
            .first()
        )

        if other_agent is None:
            db.close()
            return

        other_key = AgentAPIKey(
            agent_id=other_agent.id,
            key_selector="crossagentkey",
            key_hash="cross-agent-hash",
            is_active=True,
        )

        db.add(other_key)
        db.commit()
        db.refresh(other_key)

        api_key_id = other_key.id

        db.close()

        incident_id = create_incident(agent_id=1)

        response = client.post(
            f"/api/incidents/{incident_id}/actions",
            json={
                "action_type": "ROTATE_AGENT_API_KEY",
                "agent_id": 1,
                "api_key_id": api_key_id,
                "reason": "Unauthorized key rotation attempt",
            },
        )

        assert response.status_code == 400
        assert response.json()["detail"] == "Invalid API key target"

        db = SessionLocal()

        try:
            other_key = (
                db.query(AgentAPIKey)
                .filter(
                    AgentAPIKey.id == api_key_id
                )
                .first()
            )

            assert other_key is not None
            assert other_key.is_active is True

        finally:
            db.close()

    finally:
        if incident_id is not None:
            cleanup_incident(incident_id)

        if api_key_id is not None:
            cleanup_api_key(api_key_id)

        teardown_user_override()


def test_invalid_action_target_is_rejected_safely():
    setup_user_override()

    incident_id = None

    try:
        incident_id = create_incident(agent_id=1)

        response = client.post(
            f"/api/incidents/{incident_id}/actions",
            json={
                "action_type": "DISABLE_TOOL",
                "agent_id": 1,
                "tool_id": 999999999,
                "reason": "Invalid target test",
            },
        )

        assert response.status_code == 400
        assert response.json()["detail"] == "Invalid tool target"

    finally:
        if incident_id is not None:
            cleanup_incident(incident_id)

        teardown_user_override()


def test_response_actions_are_recorded():
    setup_user_override()

    incident_id = None

    try:
        incident_id = create_incident(agent_id=1)

        response = client.post(
            f"/api/incidents/{incident_id}/actions",
            json={
                "action_type": "SUSPEND_AGENT",
                "agent_id": 1,
                "reason": "Audit recording test",
            },
        )

        assert response.status_code == 201

        db = SessionLocal()

        try:
            action = (
                db.query(IncidentResponseAction)
                .filter(
                    IncidentResponseAction.incident_id
                    == incident_id
                )
                .first()
            )

            assert action is not None
            assert action.action_type == "SUSPEND_AGENT"
            assert action.agent_id == 1
            assert action.authorized_by_user_id == 4
            assert action.reason == "Audit recording test"
            assert action.result == "SUCCESS"

        finally:
            db.close()

    finally:
        if incident_id is not None:
            cleanup_incident(incident_id)

        teardown_user_override()


def test_raw_api_key_is_not_stored_in_response_action():
    setup_user_override()

    incident_id = None
    old_key_id = None
    new_key_id = None

    try:
        db = SessionLocal()

        old_key = AgentAPIKey(
            agent_id=1,
            key_selector="secretold",
            key_hash="secret-old-hash",
            is_active=True,
        )

        db.add(old_key)
        db.commit()
        db.refresh(old_key)

        old_key_id = old_key.id

        db.close()

        incident_id = create_incident(agent_id=1)

        response = client.post(
            f"/api/incidents/{incident_id}/actions",
            json={
                "action_type": "ROTATE_AGENT_API_KEY",
                "agent_id": 1,
                "api_key_id": old_key_id,
                "reason": "Secret exposure test",
            },
        )

        assert response.status_code == 201

        data = response.json()

        raw_api_key = data["api_key"]

        assert raw_api_key is not None
        assert raw_api_key.startswith("sx_")

        new_key_id = data["api_key_id"]

        db = SessionLocal()

        try:
            action = (
                db.query(IncidentResponseAction)
                .filter(
                    IncidentResponseAction.incident_id
                    == incident_id
                )
                .first()
            )

            assert action is not None

            assert raw_api_key not in (
                action.reason or ""
            )

            assert raw_api_key not in (
                action.details or ""
            )

        finally:
            db.close()

    finally:
        if incident_id is not None:
            cleanup_incident(incident_id)

        if new_key_id is not None:
            cleanup_api_key(new_key_id)

        if old_key_id is not None:
            cleanup_api_key(old_key_id)

        teardown_user_override()


def test_get_incident_response_actions():
    setup_user_override()

    incident_id = None

    try:
        incident_id = create_incident(agent_id=1)

        create_response = client.post(
            f"/api/incidents/{incident_id}/actions",
            json={
                "action_type": "SUSPEND_AGENT",
                "agent_id": 1,
                "reason": "Verify action listing",
            },
        )

        assert create_response.status_code == 201

        response = client.get(
            f"/api/incidents/{incident_id}/actions"
        )

        assert response.status_code == 200

        actions = response.json()

        assert len(actions) == 1
        assert actions[0]["action_type"] == "SUSPEND_AGENT"
        assert actions[0]["result"] == "SUCCESS"

    finally:
        if incident_id is not None:
            cleanup_incident(incident_id)

        teardown_user_override()