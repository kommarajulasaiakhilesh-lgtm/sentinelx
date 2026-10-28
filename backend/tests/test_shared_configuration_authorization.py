from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient

from app.api.dependencies import get_current_user
from app.db.database import get_db
from app.main import app


@pytest.mark.parametrize(
    ("path", "payload"),
    [
        ("/api/frameworks", {"name": "test", "version": "1"}),
        (
            "/api/frameworks/1/controls",
            {"control_id": "test", "title": "test"},
        ),
        (
            "/api/sentinelx-controls",
            {
                "control_id": "test",
                "name": "test",
                "implementation_status": "IMPLEMENTED",
            },
        ),
        (
            "/api/control-mappings",
            {
                "framework_control_id": 1,
                "sentinelx_control_id": 1,
                "mapping_status": "IMPLEMENTED",
            },
        ),
        (
            "/api/evidence",
            {
                "sentinelx_control_id": 1,
                "evidence_type": "DOCUMENT",
                "source": "test",
                "evidence_status": "AVAILABLE",
            },
        ),
    ],
)
def test_non_admin_cannot_write_shared_compliance_records(
    path, payload
):
    original_overrides = app.dependency_overrides.copy()
    app.dependency_overrides[get_current_user] = lambda: SimpleNamespace(
        id=42,
        role="USER",
    )
    app.dependency_overrides[get_db] = lambda: object()

    try:
        with TestClient(app) as client:
            response = client.post(path, json=payload)

        assert response.status_code == 403
        assert response.json()["detail"] == "Insufficient permissions"
    finally:
        app.dependency_overrides.clear()
        app.dependency_overrides.update(original_overrides)
