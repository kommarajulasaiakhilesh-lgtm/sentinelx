import secrets

from passlib.context import CryptContext


pwd_context = CryptContext(
    schemes=["argon2"],
    deprecated="auto"
)


def generate_agent_api_key() -> str:
    return secrets.token_urlsafe(32)


def hash_agent_api_key(api_key: str) -> str:
    return pwd_context.hash(api_key)


def verify_agent_api_key(
    api_key: str,
    key_hash: str
) -> bool:
    return pwd_context.verify(
        api_key,
        key_hash
    )