"""Incident SLA tracking.

Applies response/resolution time targets per severity and classifies each
incident as WITHIN / AT_RISK / BREACHED. Read-only and computed on demand from
the incident's timestamps and status.
"""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.agent import Agent
from app.models.incident import Incident


# Resolution SLA targets per severity, in minutes.
SLA_TARGET_MINUTES: dict[str, int] = {
    "CRITICAL": 60,
    "HIGH": 240,
    "MEDIUM": 1440,
    "LOW": 4320,
}
DEFAULT_TARGET_MINUTES = 1440

CLOSED_STATUSES = {"RESOLVED", "CLOSED"}
AT_RISK_FRACTION = 0.75


def _aware(dt: datetime | None) -> datetime | None:
    if dt is None:
        return None
    return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)


def _evaluate(incident: Incident, now: datetime) -> dict:
    severity = (incident.severity or "MEDIUM").upper()
    target = SLA_TARGET_MINUTES.get(severity, DEFAULT_TARGET_MINUTES)

    created = _aware(incident.created_at) or now
    is_closed = (incident.status or "").upper() in CLOSED_STATUSES

    if is_closed:
        closed_at = _aware(incident.updated_at) or now
        elapsed = (closed_at - created).total_seconds() / 60.0
        breached = elapsed > target
        sla_status = "BREACHED" if breached else "MET"
    else:
        elapsed = (now - created).total_seconds() / 60.0
        if elapsed > target:
            sla_status = "BREACHED"
        elif elapsed > target * AT_RISK_FRACTION:
            sla_status = "AT_RISK"
        else:
            sla_status = "WITHIN"
        breached = sla_status == "BREACHED"

    return {
        "incident_id": incident.id,
        "title": incident.title,
        "severity": severity,
        "status": incident.status,
        "target_minutes": target,
        "elapsed_minutes": round(elapsed),
        "sla_status": sla_status,
        "breached": breached,
    }


def incident_sla_report(db: Session, owner_id: int) -> dict:
    now = datetime.now(timezone.utc)
    incidents = (
        db.query(Incident)
        .join(Agent, Incident.agent_id == Agent.id)
        .filter(Agent.owner_id == owner_id)
        .order_by(Incident.created_at.desc())
        .all()
    )

    rows = [_evaluate(i, now) for i in incidents]
    summary = {
        "total": len(rows),
        "breached": sum(1 for r in rows if r["sla_status"] == "BREACHED"),
        "at_risk": sum(1 for r in rows if r["sla_status"] == "AT_RISK"),
        "within": sum(1 for r in rows if r["sla_status"] in ("WITHIN", "MET")),
    }
    return {"summary": summary, "targets_minutes": SLA_TARGET_MINUTES, "incidents": rows}
