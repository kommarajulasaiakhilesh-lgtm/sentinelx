
from fastapi.testclient import TestClient

from app.api.dependencies import get_current_user
from app.db.database import SessionLocal
from app.main import app
from app.models.agent import Agent
from app.models.security_test import SecurityTestScenario
from app.models.user import User


client = TestClient(app)


def clear_overrides():
    app.dependency_overrides.clear()


def set_user_override(user_id: int):
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if user is None:
            raise RuntimeError(f"Test user {user_id} was not found")
    finally:
        db.close()

    app.dependency_overrides[get_current_user] = lambda: user


def get_scenario_and_owner():
    db = SessionLocal()
    try:
        scenario = (
            db.query(SecurityTestScenario)
            .order_by(SecurityTestScenario.id.asc())
            .first()
        )
        if scenario is None:
            raise RuntimeError("At least one security test scenario is required")
        return scenario.id, scenario.owner_id
    finally:
        db.close()


def test_security_test_scenarios_require_authentication():
    clear_overrides()
    response = client.get("/api/security-tests/scenarios")
    assert response.status_code in (401, 403)


def test_scenario_owner_can_view_scenario():
    scenario_id, owner_id = get_scenario_and_owner()
    set_user_override(owner_id)
    try:
        response = client.get(
            f"/api/security-tests/scenarios/{scenario_id}"
        )
        assert response.status_code == 200
        assert response.json()["owner_id"] == owner_id
    finally:
        clear_overrides()


def test_other_user_cannot_view_scenario():
    scenario_id, owner_id = get_scenario_and_owner()

    db = SessionLocal()
    try:
        other_user = (
            db.query(User)
            .filter(
                User.id != owner_id,
                User.role == "USER",
                User.is_active.is_(True),
            )
            .first()
        )
        if other_user is None:
            raise RuntimeError("An alternate active USER is required")
        other_user_id = other_user.id
    finally:
        db.close()

    set_user_override(other_user_id)
    try:
        response = client.get(
            f"/api/security-tests/scenarios/{scenario_id}"
        )
        assert response.status_code == 404
    finally:
        clear_overrides()


def test_admin_can_view_existing_scenario():
    scenario_id, _ = get_scenario_and_owner()

    db = SessionLocal()
    try:
        admin = (
            db.query(User)
            .filter(User.role == "ADMIN", User.is_active.is_(True))
            .first()
        )
        if admin is None:
            raise RuntimeError("An active ADMIN is required")
        admin_id = admin.id
    finally:
        db.close()

    set_user_override(admin_id)
    try:
        response = client.get(
            f"/api/security-tests/scenarios/{scenario_id}"
        )
        assert response.status_code == 200
    finally:
        clear_overrides()


def test_scenario_creation_requires_agent_id():
    _, owner_id = get_scenario_and_owner()
    set_user_override(owner_id)
    try:
        response = client.post(
            "/api/security-tests/scenarios",
            json={
                "name": "Missing Agent Test",
                "category": "PROMPT_INJECTION",
                "expected_decision": "BLOCK",
            },
        )
        assert response.status_code == 422
    finally:
        clear_overrides()


def test_scenario_creation_rejects_unknown_category():
    db = SessionLocal()
    try:
        agent = db.query(Agent).first()
        if agent is None:
            raise RuntimeError("An agent is required for this test")
        owner_id = agent.owner_id
        agent_id = agent.id
    finally:
        db.close()

    set_user_override(owner_id)
    try:
        response = client.post(
            "/api/security-tests/scenarios",
            json={
                "name": "Invalid Category Test",
                "category": "UNKNOWN_ATTACK",
                "agent_id": agent_id,
                "expected_decision": "BLOCK",
            },
        )
        assert response.status_code == 422
    finally:
        clear_overrides()


def test_scenario_creation_rejects_invalid_expected_decision():
    db = SessionLocal()
    try:
        agent = db.query(Agent).first()
        if agent is None:
            raise RuntimeError("An agent is required for this test")
        owner_id = agent.owner_id
        agent_id = agent.id
    finally:
        db.close()

    set_user_override(owner_id)
    try:
        response = client.post(
            "/api/security-tests/scenarios",
            json={
                "name": "Invalid Decision Test",
                "category": "PROMPT_INJECTION",
                "agent_id": agent_id,
                "expected_decision": "IGNORE",
            },
        )
        assert response.status_code == 422
    finally:
        clear_overrides()


def test_scenario_creation_assigns_owner_and_can_be_cleaned_up():
    db = SessionLocal()
    try:
        agent = db.query(Agent).first()
        if agent is None:
            raise RuntimeError("An agent is required for this test")
        owner_id = agent.owner_id
        agent_id = agent.id
    finally:
        db.close()

    set_user_override(owner_id)
    scenario_id = None
    try:
        response = client.post(
            "/api/security-tests/scenarios",
            json={
                "name": "Phase 18 Ownership Test",
                "category": "PROMPT_INJECTION",
                "attack_input": "test input",
                "agent_id": agent_id,
                "expected_decision": "BLOCK",
                "enabled": True,
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["owner_id"] == owner_id
        assert data["agent_id"] == agent_id
        scenario_id = data["id"]
    finally:
        clear_overrides()
        if scenario_id is not None:
            db = SessionLocal()
            try:
                scenario = (
                    db.query(SecurityTestScenario)
                    .filter(SecurityTestScenario.id == scenario_id)
                    .first()
                )
                if scenario is not None:
                    db.delete(scenario)
                    db.commit()
            finally:
                db.close()
