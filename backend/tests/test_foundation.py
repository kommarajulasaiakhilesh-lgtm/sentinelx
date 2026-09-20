from fastapi.testclient import TestClient

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

    assert database_name == "sentinelx_db"