import logging
from time import perf_counter

from fastapi import Depends, FastAPI, HTTPException, Request
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.core.observability import get_request_id
from fastapi.middleware.cors import CORSMiddleware
from app.api.webhooks import router as webhooks_router
from app.models.sentinelx_control import SentinelXControl
from app.models.control_mapping import ControlMapping
from app.models.evidence import Evidence
from app.api.tools import router as tools_router
from app.api import analytics
from app.api.security_events import router as security_events_router
from app.api.security_alerts import router as security_alerts_router
from app.models.framework import Framework
from app.models.framework import FrameworkControl
from app.models.tool import Tool
from app.models.agent_api_key import AgentAPIKey
from app.models.user import User
from app.api.security_tests import router as security_tests_router
from app.models.agent import Agent
from app.models.policy import Policy
from app.models.security_event import SecurityEvent
from app.models.security_analytics import SecurityAnalytics
from app.models.security_alert import SecurityAlert
from app.models.incident import Incident
from app.models.incident_alert import IncidentAlert
from app.models.incident_timeline import IncidentTimelineEntry
from app.models.incident_response import IncidentResponseAction
from app.models.webhook_endpoint import WebhookEndpoint
from app.models.webhook_delivery import WebhookDelivery
from app.api.frameworks import router as frameworks_router
from app.db.database import Base, engine
from app.core.config import CORS_ORIGINS
from app.api.auth import router as auth_router
from app.api.agents import router as agents_router
from app.api.policies import router as policies_router
from app.api.evidence import router as evidence_router
from app.api.enforcement import router as enforcement_router
from app.api.control_mappings import router as control_mappings_router
from app.api.sentinelx_controls import router as sentinelx_controls_router
from app.api.compliance import router as compliance_router
from app.api.incidents import router as incidents_router
from app.api.detection_rules import router as detection_rules_router
from app.api.dependencies import (
    get_current_user,
    require_role
)
from app.api.risk_scoring_configurations import (
    router as risk_scoring_configurations_router,
)


app = FastAPI(
    title="SentinelX",
    description="AI Agent Security Control Plane",
    version="0.1.0"
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

request_logger = logging.getLogger("sentinelx.request")


@app.middleware("http")
async def request_observability(request: Request, call_next):
    request_id = get_request_id(
        request.headers.get("X-Request-ID")
    )
    request.state.request_id = request_id
    started_at = perf_counter()

    try:
        response = await call_next(request)
    except Exception:
        duration_ms = (perf_counter() - started_at) * 1000
        route = request.scope.get("route")
        route_template = getattr(route, "path", "<unmatched>")

        request_logger.error(
            "http_request_failed request_id=%s method=%s "
            "route=%s status_code=500 duration_ms=%.2f",
            request_id,
            request.method,
            route_template,
            duration_ms,
        )
        raise

    duration_ms = (perf_counter() - started_at) * 1000
    route = request.scope.get("route")
    route_template = getattr(route, "path", "<unmatched>")

    response.headers["X-Request-ID"] = request_id

    request_logger.info(
        "http_request request_id=%s method=%s "
        "route=%s status_code=%d duration_ms=%.2f",
        request_id,
        request.method,
        route_template,
        response.status_code,
        duration_ms,
    )

    return response



app.include_router(auth_router)
app.include_router(agents_router)
app.include_router(policies_router)
app.include_router(enforcement_router)
app.include_router(tools_router)
app.include_router(security_events_router)
app.include_router(security_alerts_router)
app.include_router(analytics.router)
app.include_router(frameworks_router)
app.include_router(evidence_router)
app.include_router(control_mappings_router)
app.include_router(sentinelx_controls_router)
app.include_router(compliance_router)
app.include_router(security_tests_router)
app.include_router(incidents_router)
app.include_router(webhooks_router)
app.include_router(detection_rules_router)
app.include_router(risk_scoring_configurations_router)


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

@app.get("/ready")
def readiness():
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
    except SQLAlchemyError:
        raise HTTPException(
            status_code=503,
            detail="Database is not ready",
        ) from None

    return {
        "status": "ready",
        "database": "ready",
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