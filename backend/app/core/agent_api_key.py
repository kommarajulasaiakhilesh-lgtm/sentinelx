import secrets

from passlib.context import CryptContext


pwd_context = CryptContext(
    schemes=["argon2"],
    deprecated="auto"
)


def generate_agent_api_key() -> str:
    """
    Generate an agent API key in the format:

    sx_<selector>_<secret>

    The selector uses hexadecimal characters only so
    it can never contain an underscore.
    """

    selector = secrets.token_hex(8)
    secret = secrets.token_urlsafe(32)

    return f"sx_{selector}_{secret}"


def extract_key_selector(api_key: str) -> str | None:
    """
    Extract the selector from an agent API key.
    """

    parts = api_key.split("_", 2)

    if len(parts) != 3:
        return None

    if parts[0] != "sx":
        return None

    if not parts[1]:
        return None

    return parts[1]


def hash_agent_api_key(api_key: str) -> str:
    """
    Hash the complete API key before storing it.
    """

    return pwd_context.hash(api_key)


def verify_agent_api_key(
    api_key: str,
    key_hash: str
) -> bool:
    """
    Verify a raw API key against its stored hash.
    """

    return pwd_context.verify(
        api_key,
        key_hash
    )