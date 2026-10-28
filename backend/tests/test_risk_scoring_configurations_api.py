
import pytest
from fastapi.testclient import TestClient

from app.api.dependencies import get_current_user
from app.db.database import SessionLocal
from app.main import app
from app.models.risk_scoring_configuration import (
    RiskScoringConfiguration,
)
from app.models.user import User


client = TestClient(app)

TEST_USER_ID = 4
TEST_ADMIN_ID = 1
TEST_CONFIGURATION_NAME = "Phase 19 API Test Configuration"
OTHER_USER_CONFIGURATION_NAME = "Phase 19 Other User Isolation Test"

VALID_CONFIGURATION = {
    "name": TEST_CONFIGURATION_NAME,
    "enabled": True,
    "blocked_event_weight": 10,
    "suspicious_event_weight": 20,
    "policy_violation_weight": 15,
    "score_cap": 100,
    "low_max": 19,
    "medium_max": 49,
    "high_max": 79,
    "critical_max": 100,
}


def set_user_override(user_id: int) -> None:
    db = SessionLocal()

    try:
        user = db.query(User).filter(User.id == user_id).first()

        if user is None:
            raise RuntimeError(f"Test user {user_id} was not found")

        if not user.is_active:
            raise RuntimeError(f"Test user {user_id} is inactive")

        app.dependency_overrides[get_current_user] = lambda: user

    finally:
        db.close()


def clear_user_override() -> None:
    app.dependency_overrides.clear()


def cleanup_named_configuration(
    owner_id: int,
    configuration_name: str,
) -> None:
    db = SessionLocal()

    try:
        configurations = (
            db.query(RiskScoringConfiguration)
            .filter(
                RiskScoringConfiguration.owner_id == owner_id,
                RiskScoringConfiguration.name == configuration_name,
            )
            .all()
        )

        for configuration in configurations:
            db.delete(configuration)

        if configurations:
            db.commit()

    finally:
        db.close()


def cleanup_test_configuration() -> None:
    cleanup_named_configuration(
        TEST_USER_ID,
        TEST_CONFIGURATION_NAME,
    )


def find_user_without_personal_configuration(
    exclude_user_id: int,
) -> int | None:
    db = SessionLocal()

    try:
        users = (
            db.query(User)
            .filter(
                User.id != exclude_user_id,
                User.is_active.is_(True),
            )
            .all()
        )

        for user in users:
            existing_configuration = (
                db.query(RiskScoringConfiguration.id)
                .filter(
                    RiskScoringConfiguration.owner_id == user.id,
                )
                .first()
            )

            if existing_configuration is None:
                return user.id

        return None

    finally:
        db.close()


def test_risk_configuration_requires_authentication():
    clear_user_override()

    try:
        response = client.get(
            "/api/risk-configurations/effective"
        )

        assert response.status_code == 401

    finally:
        clear_user_override()


def test_regular_user_cannot_read_global_configuration():
    set_user_override(TEST_USER_ID)

    try:
        response = client.get(
            "/api/risk-configurations/global"
        )

        assert response.status_code == 403

    finally:
        clear_user_override()


def test_regular_user_cannot_update_global_configuration():
    set_user_override(TEST_USER_ID)

    try:
        response = client.put(
            "/api/risk-configurations/global",
            json=VALID_CONFIGURATION,
        )

        assert response.status_code == 403

    finally:
        clear_user_override()


def test_admin_can_read_global_configuration():
    set_user_override(TEST_ADMIN_ID)

    try:
        response = client.get(
            "/api/risk-configurations/global"
        )

        assert response.status_code == 200

        data = response.json()

        assert data["owner_id"] is None
        assert data["name"] == "Default Risk Scoring"
        assert data["score_cap"] == 100

    finally:
        clear_user_override()


def test_admin_can_update_global_configuration():
    set_user_override(TEST_ADMIN_ID)

    try:
        read_response = client.get(
            "/api/risk-configurations/global"
        )

        assert read_response.status_code == 200

        existing = read_response.json()

        payload = {
            field: existing[field]
            for field in VALID_CONFIGURATION
        }

        update_response = client.put(
            "/api/risk-configurations/global",
            json=payload,
        )

        assert update_response.status_code == 200

        updated = update_response.json()

        assert updated["owner_id"] is None
        assert updated["id"] == existing["id"]
        assert updated["name"] == existing["name"]
        assert updated["score_cap"] == existing["score_cap"]

    finally:
        clear_user_override()


def test_user_can_create_and_read_personal_configuration():
    cleanup_test_configuration()
    set_user_override(TEST_USER_ID)

    try:
        create_response = client.put(
            "/api/risk-configurations/mine",
            json=VALID_CONFIGURATION,
        )

        assert create_response.status_code == 200

        created = create_response.json()

        assert created["owner_id"] == TEST_USER_ID
        assert created["name"] == TEST_CONFIGURATION_NAME
        assert created["enabled"] is True
        assert created["score_cap"] == 100
        assert created["critical_max"] == 100

        read_response = client.get(
            "/api/risk-configurations/mine"
        )

        assert read_response.status_code == 200
        assert read_response.json()["id"] == created["id"]

        effective_response = client.get(
            "/api/risk-configurations/effective"
        )

        assert effective_response.status_code == 200
        assert effective_response.json()["id"] == created["id"]

    finally:
        clear_user_override()
        cleanup_test_configuration()


def test_user_cannot_read_or_overwrite_another_users_configuration():
    other_user_id = find_user_without_personal_configuration(
        exclude_user_id=TEST_USER_ID,
    )

    if other_user_id is None:
        pytest.skip(
            "No second active user without a personal configuration"
        )

    cleanup_test_configuration()
    cleanup_named_configuration(
        other_user_id,
        OTHER_USER_CONFIGURATION_NAME,
    )

    try:
        set_user_override(TEST_USER_ID)

        owner_response = client.put(
            "/api/risk-configurations/mine",
            json=VALID_CONFIGURATION,
        )

        assert owner_response.status_code == 200
        original_owner_configuration = owner_response.json()

        clear_user_override()
        set_user_override(other_user_id)

        other_read_response = client.get(
            "/api/risk-configurations/mine"
        )

        assert other_read_response.status_code == 404

        other_payload = {
            **VALID_CONFIGURATION,
            "name": OTHER_USER_CONFIGURATION_NAME,
            "blocked_event_weight": 3,
        }

        other_update_response = client.put(
            "/api/risk-configurations/mine",
            json=other_payload,
        )

        assert other_update_response.status_code == 200

        other_configuration = other_update_response.json()

        assert other_configuration["owner_id"] == other_user_id
        assert (
            other_configuration["name"]
            == OTHER_USER_CONFIGURATION_NAME
        )
        assert other_configuration["blocked_event_weight"] == 3

        db = SessionLocal()

        try:
            original = (
                db.query(RiskScoringConfiguration)
                .filter(
                    RiskScoringConfiguration.id
                    == original_owner_configuration["id"],
                )
                .first()
            )

            assert original is not None
            assert original.owner_id == TEST_USER_ID
            assert original.name == TEST_CONFIGURATION_NAME
            assert original.blocked_event_weight == 10

        finally:
            db.close()

    finally:
        clear_user_override()
        cleanup_test_configuration()
        cleanup_named_configuration(
            other_user_id,
            OTHER_USER_CONFIGURATION_NAME,
        )


def test_invalid_thresholds_are_rejected():
    cleanup_test_configuration()
    set_user_override(TEST_USER_ID)

    invalid_configuration = {
        **VALID_CONFIGURATION,
        "low_max": 50,
        "medium_max": 49,
    }

    try:
        response = client.put(
            "/api/risk-configurations/mine",
            json=invalid_configuration,
        )

        assert response.status_code == 422

    finally:
        clear_user_override()
        cleanup_test_configuration()
