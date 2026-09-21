from fastapi import FastAPI, Depends

from app.db.database import Base, engine
from app.models.user import User
from app.models.agent import Agent

from app.api.auth import router as auth_router
from app.api.agents import router as agents_router

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