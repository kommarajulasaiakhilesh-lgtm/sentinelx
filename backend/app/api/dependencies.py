from fastapi import Depends, HTTPException, Security
from fastapi.security import (
    HTTPAuthorizationCredentials,
    HTTPBearer,
    APIKeyHeader
)

from sqlalchemy.orm import Session

from app.db.database import get_db
from app.core.security import decode_access_token
from app.core.agent_api_key import verify_agent_api_key

from app.models.user import User
from app.models.agent import Agent
from app.models.agent_api_key import AgentAPIKey


# ============================================================
# USER JWT AUTHENTICATION
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
# ROLE-BASED AUTHORIZATION
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
    api_key: str | None = Security(
        agent_api_key_header
    ),
    db: Session = Depends(get_db)
):
    # No API key supplied
    if not api_key:
        raise HTTPException(
            status_code=401,
            detail="Agent API key is required"
        )

    # Get all active API keys
    api_keys = (
        db.query(AgentAPIKey)
        .filter(
            AgentAPIKey.is_active == True
        )
        .all()
    )

    # Compare supplied API key with stored Argon2 hashes
    for stored_key in api_keys:

        if verify_agent_api_key(
            api_key,
            stored_key.key_hash
        ):

            # Find the associated active agent
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

            return agent

    # No matching API key found
    raise HTTPException(
        status_code=401,
        detail="Invalid agent API key"
    )