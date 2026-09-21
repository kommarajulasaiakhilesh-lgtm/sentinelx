from datetime import datetime, timezone

from fastapi import Depends, HTTPException, Security
from fastapi.security import (
    HTTPAuthorizationCredentials,
    HTTPBearer,
    APIKeyHeader
)
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.core.security import decode_access_token
from app.core.agent_api_key import (
    verify_agent_api_key,
    extract_key_selector
)

from app.models.user import User
from app.models.agent import Agent
from app.models.agent_api_key import AgentAPIKey


# ============================================================
# USER AUTHENTICATION
# ============================================================

security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    token = credentials.credentials

    payload = decode_access_token(token)

    if payload is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token"
        )

    username = payload.get("username")

    if username is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid token"
        )

    user = (
        db.query(User)
        .filter(User.username == username)
        .first()
    )

    if user is None:
        raise HTTPException(
            status_code=401,
            detail="User not found"
        )

    if not user.is_active:
        raise HTTPException(
            status_code=403,
            detail="User account is inactive"
        )

    return user


# ============================================================
# ROLE AUTHORIZATION
# ============================================================

def require_role(required_role: str):

    def role_checker(
        current_user: User = Depends(get_current_user)
    ):
        if current_user.role != required_role:
            raise HTTPException(
                status_code=403,
                detail="Insufficient permissions"
            )

        return current_user

    return role_checker


# ============================================================
# AGENT API KEY AUTHENTICATION
# ============================================================

agent_api_key_header = APIKeyHeader(
    name="X-Agent-API-Key",
    auto_error=False
)


def get_current_agent(
    api_key: str | None = Security(agent_api_key_header),
    db: Session = Depends(get_db)
):
    # --------------------------------------------------------
    # Check API key exists
    # --------------------------------------------------------

    if not api_key:
        raise HTTPException(
            status_code=401,
            detail="Agent API key is required"
        )

    # --------------------------------------------------------
    # Extract public key selector
    # --------------------------------------------------------

    key_selector = extract_key_selector(api_key)

    if key_selector is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid agent API key"
        )

    # --------------------------------------------------------
    # Find matching active API key
    # --------------------------------------------------------

    stored_key = (
        db.query(AgentAPIKey)
        .filter(
            AgentAPIKey.key_selector == key_selector,
            AgentAPIKey.is_active == True
        )
        .first()
    )

    if stored_key is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid agent API key"
        )

    # --------------------------------------------------------
    # Verify complete API key against Argon2 hash
    # --------------------------------------------------------

    if not verify_agent_api_key(
        api_key,
        stored_key.key_hash
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid agent API key"
        )

    # --------------------------------------------------------
    # Check API key expiration
    # --------------------------------------------------------

    now = datetime.now(timezone.utc)

    if (
        stored_key.expires_at is not None
        and stored_key.expires_at <= now
    ):
        raise HTTPException(
            status_code=401,
            detail="Agent API key has expired"
        )

    # --------------------------------------------------------
    # Find active agent
    # --------------------------------------------------------

    agent = (
        db.query(Agent)
        .filter(
            Agent.id == stored_key.agent_id,
            Agent.status == "ACTIVE"
        )
        .first()
    )

    if agent is None:
        raise HTTPException(
            status_code=401,
            detail="Agent is inactive or not found"
        )

    # --------------------------------------------------------
    # Authentication successful
    # --------------------------------------------------------

    return agent