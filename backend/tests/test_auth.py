
import pytest
from fastapi.testclient import TestClient
from app.core.security import hash_password, verify_password
from app.main import app
from app.api.dependencies import get_current_user
from app.db.database import get_db
from app.models.user import User


class FakeQuery:
    def __init__(self, users):
        self.users = users
        self.field = None
        self.value = None

    def filter(self, condition):
        self.field = condition.left.key
        self.value = condition.right.value
        return self

    def first(self):
        return next(
            (
                user
                for user in self.users
                if getattr(user, self.field) == self.value
            ),
            None,
        )


class FakeDB:
    def __init__(self, users=None):
        self.users = list(users or [])

    def query(self, model):
        assert model is User
        return FakeQuery(self.users)

    def add(self, user):
        user.id = max(
            (existing.id or 0 for existing in self.users),
            default=0,
        ) + 1
        self.users.append(user)

    def commit(self):
        pass

    def refresh(self, user):
        pass


@pytest.fixture
def auth_client():
    original_overrides = app.dependency_overrides.copy()
    db = FakeDB()

    app.dependency_overrides[get_db] = lambda: db

    try:
        with TestClient(app) as client:
            yield client, db
    finally:
        app.dependency_overrides.clear()
        app.dependency_overrides.update(original_overrides)


def make_user(
    user_id=1,
    username="testuser",
    email="test@example.com",
    password_hash="stored-hash",
    role="USER",
    is_active=True,
):
    return User(
        id=user_id,
        username=username,
        email=email,
        password_hash=password_hash,
        role=role,
        is_active=is_active,
    )


def test_register_creates_user_without_exposing_password_hash(
    auth_client, monkeypatch
):
    client, db = auth_client

    monkeypatch.setattr(
        "app.api.auth.hash_password",
        lambda password: "argon2-test-hash",
    )

    response = client.post(
        "/api/auth/register",
        json={
            "username": "newuser",
            "email": "new@example.com",
            "password": "StrongTestPassword123!",
        },
    )

    assert response.status_code == 201
    assert response.json()["username"] == "newuser"
    assert response.json()["email"] == "new@example.com"
    assert response.json()["role"] == "USER"
    assert response.json()["is_active"] is True
    assert "password_hash" not in response.json()

    assert len(db.users) == 1
    assert db.users[0].password_hash == "argon2-test-hash"


def test_register_rejects_duplicate_username(auth_client):
    client, db = auth_client
    db.users.append(make_user())

    response = client.post(
        "/api/auth/register",
        json={
            "username": "testuser",
            "email": "another@example.com",
            "password": "StrongTestPassword123!",
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Username already exists"


def test_register_rejects_duplicate_email(auth_client):
    client, db = auth_client
    db.users.append(make_user())

    response = client.post(
        "/api/auth/register",
        json={
            "username": "anotheruser",
            "email": "test@example.com",
            "password": "StrongTestPassword123!",
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Email already exists"


def test_login_returns_bearer_token(auth_client, monkeypatch):
    client, db = auth_client
    db.users.append(make_user())

    monkeypatch.setattr(
        "app.api.auth.verify_password",
        lambda plain, hashed: (
            plain == "correct-password" and hashed == "stored-hash"
        ),
    )

    captured = {}

    def fake_create_access_token(claims):
        captured.update(claims)
        return "test-access-token"

    monkeypatch.setattr(
        "app.api.auth.create_access_token",
        fake_create_access_token,
    )

    response = client.post(
        "/api/auth/login",
        json={
            "username": "testuser",
            "password": "correct-password",
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        "access_token": "test-access-token",
        "token_type": "bearer",
    }
    assert captured["sub"] == "1"
    assert captured["username"] == "testuser"
    assert captured["role"] == "USER"


@pytest.mark.parametrize(
    "username,password",
    [
        ("unknown-user", "wrong-password"),
        ("testuser", "wrong-password"),
    ],
)
def test_login_rejects_invalid_credentials(
    auth_client, monkeypatch, username, password
):
    client, db = auth_client
    db.users.append(make_user())

    monkeypatch.setattr(
        "app.api.auth.verify_password",
        lambda plain, hashed: False,
    )

    response = client.post(
        "/api/auth/login",
        json={"username": username, "password": password},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == (
        "Invalid username or password"
    )


def test_login_rejects_inactive_user(auth_client, monkeypatch):
    client, db = auth_client
    db.users.append(make_user(is_active=False))

    monkeypatch.setattr(
        "app.api.auth.verify_password",
        lambda plain, hashed: True,
    )

    response = client.post(
        "/api/auth/login",
        json={
            "username": "testuser",
            "password": "correct-password",
        },
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "User account is inactive"


def test_protected_route_rejects_invalid_token(
    auth_client, monkeypatch
):
    client, _ = auth_client

    monkeypatch.setattr(
        "app.api.dependencies.decode_access_token",
        lambda token: None,
    )

    response = client.get(
        "/api/protected",
        headers={"Authorization": "Bearer invalid-token"},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid or expired token"


def test_protected_route_rejects_token_without_username(
    auth_client, monkeypatch
):
    client, _ = auth_client

    monkeypatch.setattr(
        "app.api.dependencies.decode_access_token",
        lambda token: {"sub": "1", "role": "USER"},
    )

    response = client.get(
        "/api/protected",
        headers={"Authorization": "Bearer test-token"},
    )

    assert response.status_code == 401


def test_protected_route_rejects_missing_subject(
    auth_client, monkeypatch
):
    client, db = auth_client
    db.users.append(make_user())

    monkeypatch.setattr(
        "app.api.dependencies.decode_access_token",
        lambda token: {"username": "testuser", "role": "USER"},
    )

    response = client.get(
        "/api/protected",
        headers={"Authorization": "Bearer test-token"},
    )

    assert response.status_code == 401


def test_protected_route_rejects_subject_username_mismatch(
    auth_client, monkeypatch
):
    client, db = auth_client
    db.users.append(make_user(user_id=1, username="testuser"))

    monkeypatch.setattr(
        "app.api.dependencies.decode_access_token",
        lambda token: {
            "sub": "999",
            "username": "testuser",
            "role": "USER",
        },
    )

    response = client.get(
        "/api/protected",
        headers={"Authorization": "Bearer test-token"},
    )

    assert response.status_code == 401


def test_protected_route_rejects_inactive_user(
    auth_client, monkeypatch
):
    client, db = auth_client
    db.users.append(make_user(is_active=False))

    monkeypatch.setattr(
        "app.api.dependencies.decode_access_token",
        lambda token: {
            "sub": "1",
            "username": "testuser",
            "role": "USER",
        },
    )

    response = client.get(
        "/api/protected",
        headers={"Authorization": "Bearer test-token"},
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "User account is inactive"


def test_admin_route_uses_database_role_not_token_role(
    auth_client, monkeypatch
):
    client, db = auth_client
    db.users.append(make_user(role="USER"))

    monkeypatch.setattr(
        "app.api.dependencies.decode_access_token",
        lambda token: {
            "sub": "1",
            "username": "testuser",
            "role": "ADMIN",
        },
    )

    response = client.get(
        "/api/admin",
        headers={"Authorization": "Bearer test-token"},
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Insufficient permissions"

def test_password_hash_verifies_correct_password():
    password = "A-Temporary-Test-Password-42!"
    password_hash = hash_password(password)

    assert password_hash != password
    assert verify_password(password, password_hash)


def test_password_hash_rejects_wrong_password():
    password_hash = hash_password(
        "A-Temporary-Test-Password-42!"
    )

    assert not verify_password(
        "A-Different-Test-Password-42!",
        password_hash,
    )


def test_password_hashing_uses_unique_salts():
    password = "A-Temporary-Test-Password-42!"

    first_hash = hash_password(password)
    second_hash = hash_password(password)

    assert first_hash != second_hash
    assert verify_password(password, first_hash)
    assert verify_password(password, second_hash)
