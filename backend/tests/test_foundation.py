from fastapi.testclient import TestClient
from sqlalchemy.exc import SQLAlchemyError
from app.main import app
from app.db.database import engine
from sqlalchemy import text


client = TestClient(app)


def test_root():
    response = client.get("/")

    assert response.status_code == 200
    assert response.json()["message"] == "SentinelX is running"


def test_health():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_database_connection():
    with engine.connect() as connection:
        result = connection.execute(text("SELECT current_database()"))
        database_name = result.scalar()

    assert database_name == engine.url.database

def test_readiness_when_database_is_available():
    response = client.get("/ready")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ready",
        "database": "ready",
    }


def test_readiness_hides_database_errors(monkeypatch):
    def fail_connection():
        raise SQLAlchemyError("internal connection details")

    monkeypatch.setattr(
        "app.main.engine.connect",
        fail_connection,
    )

    response = client.get("/ready")

    assert response.status_code == 503
    assert response.json() == {
        "detail": "Database is not ready",
    }
    assert "internal connection details" not in response.text
