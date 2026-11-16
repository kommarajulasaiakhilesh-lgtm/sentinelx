"""Prometheus metrics endpoint.

Exposes SentinelX platform state in Prometheus exposition format at /metrics
for scraping by Prometheus and visualization in Grafana. Values are computed
from the database on each scrape via a custom collector, so no per-request
instrumentation is required. The endpoint is unauthenticated by convention
(scraped inside the trust boundary); restrict it at the network layer in
production.
"""

from fastapi import APIRouter
from fastapi.responses import Response
from prometheus_client import CollectorRegistry, generate_latest, CONTENT_TYPE_LATEST
from prometheus_client.core import GaugeMetricFamily
from sqlalchemy import func

from app.db.database import SessionLocal
from app.models.agent import Agent
from app.models.security_event import SecurityEvent
from app.models.security_alert import SecurityAlert
from app.models.incident import Incident
from app.models.policy import Policy


router = APIRouter(tags=["Monitoring"])


class SentinelXCollector:
    """Collects live platform gauges from the database at scrape time."""

    def collect(self):
        db = SessionLocal()
        try:
            # Agents
            agents_total = db.query(func.count(Agent.id)).scalar() or 0
            agents_active = (
                db.query(func.count(Agent.id))
                .filter(Agent.status == "ACTIVE")
                .scalar()
                or 0
            )
            g = GaugeMetricFamily(
                "sentinelx_agents",
                "Registered agents by status",
                labels=["status"],
            )
            g.add_metric(["active"], agents_active)
            g.add_metric(["suspended"], agents_total - agents_active)
            yield g

            # Security events by decision
            ev = GaugeMetricFamily(
                "sentinelx_security_events_total",
                "Security events by enforcement decision",
                labels=["decision"],
            )
            rows = (
                db.query(SecurityEvent.decision, func.count(SecurityEvent.id))
                .group_by(SecurityEvent.decision)
                .all()
            )
            for decision, count in rows:
                ev.add_metric([decision or "UNKNOWN"], count)
            yield ev

            # Open alerts by severity
            al = GaugeMetricFamily(
                "sentinelx_open_alerts",
                "Open/acknowledged alerts by severity",
                labels=["severity"],
            )
            alert_rows = (
                db.query(SecurityAlert.severity, func.count(SecurityAlert.id))
                .filter(SecurityAlert.status.in_(["OPEN", "ACKNOWLEDGED"]))
                .group_by(SecurityAlert.severity)
                .all()
            )
            for severity, count in alert_rows:
                al.add_metric([severity or "UNKNOWN"], count)
            yield al

            # Incidents by status
            inc = GaugeMetricFamily(
                "sentinelx_incidents",
                "Incidents by status",
                labels=["status"],
            )
            inc_rows = (
                db.query(Incident.status, func.count(Incident.id))
                .group_by(Incident.status)
                .all()
            )
            for status, count in inc_rows:
                inc.add_metric([status or "UNKNOWN"], count)
            yield inc

            # Policies
            pol = GaugeMetricFamily(
                "sentinelx_policies_total",
                "Total configured policies",
            )
            pol.add_metric([], db.query(func.count(Policy.id)).scalar() or 0)
            yield pol
        finally:
            db.close()


@router.get("/metrics")
def metrics():
    registry = CollectorRegistry()
    registry.register(SentinelXCollector())
    return Response(
        content=generate_latest(registry),
        media_type=CONTENT_TYPE_LATEST,
    )
