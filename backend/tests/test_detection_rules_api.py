from fastapi.testclient import TestClient

from app.main import app
from app.api.dependencies import get_current_user
from app.db.database import SessionLocal
from app.models.user import User
from app.models.detection_rule import DetectionRule


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


def cleanup_rule(rule_id):
    db = SessionLocal()

    try:
        rule = (
            db.query(DetectionRule)
            .filter(DetectionRule.id == rule_id)
            .first()
        )

        if rule:
            db.delete(rule)
            db.commit()

    finally:
        db.close()


def test_create_detection_rule():
    setup_user_override()

    rule_id = None

    try:
        response = client.post(
            "/api/detection-rules",
            json={
                "name": "Blocked Tool Activity",
                "description": (
                    "Detect repeated blocked tool activity"
                ),
                "enabled": True,
                "severity": "HIGH",
                "alert_type": "REPEATED_BLOCKED_ACTIONS",
                "title": "Repeated blocked tool actions",
                "conditions": {
                    "event_type": "TOOL_ACTION",
                    "decision": "BLOCK"
                },
                "threshold": 5,
                "window_seconds": 60
            }
        )

        assert response.status_code == 201

        data = response.json()

        assert data["owner_id"] == 4
        assert data["name"] == "Blocked Tool Activity"
        assert data["enabled"] is True
        assert data["severity"] == "HIGH"
        assert data["alert_type"] == (
            "REPEATED_BLOCKED_ACTIONS"
        )
        assert data["title"] == (
            "Repeated blocked tool actions"
        )
        assert data["threshold"] == 5
        assert data["window_seconds"] == 60

        assert data["conditions"] is not None

        rule_id = data["id"]

    finally:
        if rule_id is not None:
            cleanup_rule(rule_id)

        teardown_user_override()


def test_list_detection_rules():
    setup_user_override()

    rule_id = None

    try:
        db = SessionLocal()

        rule = DetectionRule(
            owner_id=4,
            name="List Test Rule",
            description="Rule for list API test",
            enabled=True,
            severity="MEDIUM",
            alert_type="LIST_TEST",
            title="List test detection",
            conditions='{"event_type": "TEST"}',
            threshold=2,
            window_seconds=30
        )

        db.add(rule)
        db.commit()
        db.refresh(rule)

        rule_id = rule.id

        db.close()

        response = client.get(
            "/api/detection-rules"
        )

        assert response.status_code == 200

        data = response.json()

        rule_ids = [
            item["id"]
            for item in data
        ]

        assert rule_id in rule_ids

    finally:
        if rule_id is not None:
            cleanup_rule(rule_id)

        teardown_user_override()


def test_get_detection_rule():
    setup_user_override()

    rule_id = None

    try:
        db = SessionLocal()

        rule = DetectionRule(
            owner_id=4,
            name="Get Test Rule",
            description="Rule for detail API test",
            enabled=True,
            severity="HIGH",
            alert_type="GET_TEST",
            title="Get test detection",
            conditions='{"decision": "BLOCK"}',
            threshold=3,
            window_seconds=45
        )

        db.add(rule)
        db.commit()
        db.refresh(rule)

        rule_id = rule.id

        db.close()

        response = client.get(
            f"/api/detection-rules/{rule_id}"
        )

        assert response.status_code == 200

        data = response.json()

        assert data["id"] == rule_id
        assert data["owner_id"] == 4
        assert data["name"] == "Get Test Rule"
        assert data["severity"] == "HIGH"
        assert data["threshold"] == 3
        assert data["window_seconds"] == 45

    finally:
        if rule_id is not None:
            cleanup_rule(rule_id)

        teardown_user_override()


def test_update_detection_rule():
    setup_user_override()

    rule_id = None

    try:
        db = SessionLocal()

        rule = DetectionRule(
            owner_id=4,
            name="Update Test Rule",
            description="Original description",
            enabled=True,
            severity="MEDIUM",
            alert_type="UPDATE_TEST",
            title="Original detection",
            conditions='{"decision": "BLOCK"}',
            threshold=2,
            window_seconds=30
        )

        db.add(rule)
        db.commit()
        db.refresh(rule)

        rule_id = rule.id

        db.close()

        response = client.patch(
            f"/api/detection-rules/{rule_id}",
            json={
                "name": "Updated Detection Rule",
                "description": "Updated description",
                "enabled": False,
                "severity": "CRITICAL",
                "title": "Updated detection",
                "conditions": {
                    "event_type": "TOOL_ACTION",
                    "decision": "BLOCK"
                },
                "threshold": 10,
                "window_seconds": 120
            }
        )

        assert response.status_code == 200

        data = response.json()

        assert data["id"] == rule_id
        assert data["name"] == "Updated Detection Rule"
        assert data["description"] == (
            "Updated description"
        )
        assert data["enabled"] is False
        assert data["severity"] == "CRITICAL"
        assert data["title"] == "Updated detection"
        assert data["threshold"] == 10
        assert data["window_seconds"] == 120
        assert data["conditions"] is not None

    finally:
        if rule_id is not None:
            cleanup_rule(rule_id)

        teardown_user_override()


def test_delete_detection_rule():
    setup_user_override()

    rule_id = None

    try:
        db = SessionLocal()

        rule = DetectionRule(
            owner_id=4,
            name="Delete Test Rule",
            description="Rule for delete API test",
            enabled=True,
            severity="LOW",
            alert_type="DELETE_TEST",
            title="Delete test detection",
            conditions=None,
            threshold=1,
            window_seconds=0
        )

        db.add(rule)
        db.commit()
        db.refresh(rule)

        rule_id = rule.id

        db.close()

        response = client.delete(
            f"/api/detection-rules/{rule_id}"
        )

        assert response.status_code == 200

        data = response.json()

        assert data["rule_id"] == rule_id

        db = SessionLocal()

        deleted_rule = (
            db.query(DetectionRule)
            .filter(DetectionRule.id == rule_id)
            .first()
        )

        db.close()

        assert deleted_rule is None

        rule_id = None

    finally:
        if rule_id is not None:
            cleanup_rule(rule_id)

        teardown_user_override()


def test_get_nonexistent_detection_rule():
    setup_user_override()

    try:
        response = client.get(
            "/api/detection-rules/999999999"
        )

        assert response.status_code == 404
        assert response.json()["detail"] == (
            "Detection rule not found"
        )

    finally:
        teardown_user_override()


def test_detection_rule_cannot_be_accessed_by_another_owner():
    setup_user_override()

    rule_id = None

    try:
        db = SessionLocal()

        other_user = (
            db.query(User)
            .filter(User.id != 4)
            .first()
        )

        if other_user is None:
            db.close()
            return

        rule = DetectionRule(
            owner_id=other_user.id,
            name="Other Owner Rule",
            description="Ownership isolation test",
            enabled=True,
            severity="HIGH",
            alert_type="OWNER_TEST",
            title="Owner isolation test",
            conditions=None,
            threshold=1,
            window_seconds=0
        )

        db.add(rule)
        db.commit()
        db.refresh(rule)

        rule_id = rule.id

        db.close()

        response = client.get(
            f"/api/detection-rules/{rule_id}"
        )

        assert response.status_code == 404

    finally:
        if rule_id is not None:
            cleanup_rule(rule_id)

        teardown_user_override()