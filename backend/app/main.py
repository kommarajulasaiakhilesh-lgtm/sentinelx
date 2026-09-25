from fastapi import FastAPI, Depends

from app.api import analytics
from app.api.security_events import router as security_events_router

from app.models.agent_api_key import AgentAPIKey
from app.db.database import Base, engine
from app.models.user import User
from app.models.agent import Agent
from app.models.policy import Policy
from app.models.security_event import SecurityEvent
from app.models.security_analytics import SecurityAnalytics

from app.api.auth import router as auth_router
from app.api.agents import router as agents_router
from app.api.policies import router as policies_router
from app.api.enforcement import router as enforcement_router

from app.api.dependencies import (
    get_current_user,
    require_role
)


Base.metadata.create_all(
    bind=engine
)


app = FastAPI(
    title="SentinelX",
    description="AI Agent Security Control Plane",
    version="0.1.0"
)


app.include_router(
    auth_router
)

app.include_router(
    agents_router
)

app.include_router(
    policies_router
)

app.include_router(
    enforcement_router
)

app.include_router(
    security_events_router
)

app.include_router(
    analytics.router
)


@app.get("/")
def root():
    return {
        "message": "SentinelX is running",
        "version": "0.1.0"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }


@app.get("/api/protected")
def protected_route(
    current_user: User = Depends(
        get_current_user
    )
):
    return {
        "message": "Access granted",
        "username": current_user.username,
        "role": current_user.role
    }


@app.get("/api/admin")
def admin_route(
    current_user: User = Depends(
        require_role("ADMIN")
    )
):
    return {
        "message": "Admin access granted",
        "username": current_user.username,
        "role": current_user.role
    }