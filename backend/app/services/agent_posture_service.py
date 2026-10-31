"""Agent Security Posture scoring.

Produces a configuration-centric security posture score for an agent by
evaluating its *current standing* — policy coverage, risky tool exposure,
operational status, recent blocked/suspicious activity, and open alerts.

This is deliberately distinct from the runtime risk-scoring engine
(``risk_scoring_service``), which scores individual events/decisions. Posture
answers "how well is this agent governed right now?" rather than "how risky
was this request?". It is read-only and computes entirely from existing data,
so it requires no new tables or migrations.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.agent import Agent
from app.models.policy import Policy
from app.models.tool import Tool
from app.models.security_event import SecurityEvent
from app.models.security_alert import SecurityAlert


# Tool types considered high-impact if left ungoverned.
HIGH_RISK_TOOL_TYPES = {"SHELL", "FILESYSTEM", "DATABASE"}

# Recent activity window used for event-based posture signals.
RECENT_WINDOW_DAYS = 30

# Open alert statuses that still demand operator attention.
OPEN_ALERT_STATUSES = {"OPEN", "ACKNOWLEDGED"}


def _grade(score: int) -> str:
    if score >= 90:
        return "A"
    if score >= 80:
        return "B"
    if score >= 70:
        return "C"
    if score >= 55:
        return "D"
    return "F"


def _level(score: int) -> str:
    if score >= 85:
        return "STRONG"
    if score >= 70:
        return "MODERATE"
    if score >= 50:
        return "WEAK"
    return "CRITICAL"


def evaluate_agent_posture(db: Session, agent: Agent) -> dict:
    """Return a posture report dict for a single (already-authorized) agent."""

    now = datetime.now(timezone.utc)
    window_start = now - timedelta(days=RECENT_WINDOW_DAYS)

    enabled_policies = (
        db.query(Policy)
        .filter(Policy.agent_id == agent.id, Policy.enabled.is_(True))
        .all()
    )
    policy_types = {p.policy_type for p in enabled_policies}

    enabled_tools = (
        db.query(Tool)
        .filter(Tool.agent_id == agent.id, Tool.enabled.is_(True))
        .all()
    )
    risky_tools = [t for t in enabled_tools if t.tool_type in HIGH_RISK_TOOL_TYPES]

    recent_blocked = (
        db.query(func.count(SecurityEvent.id))
        .filter(
            SecurityEvent.agent_id == agent.id,
            SecurityEvent.decision == "BLOCK",
            SecurityEvent.created_at >= window_start,
        )
        .scalar()
        or 0
    )
    recent_suspicious = (
        db.query(func.count(SecurityEvent.id))
        .filter(
            SecurityEvent.agent_id == agent.id,
            SecurityEvent.decision == "SUSPICIOUS",
            SecurityEvent.created_at >= window_start,
        )
        .scalar()
        or 0
    )
    open_alerts = (
        db.query(func.count(SecurityAlert.id))
        .filter(
            SecurityAlert.agent_id == agent.id,
            SecurityAlert.status.in_(OPEN_ALERT_STATUSES),
        )
        .scalar()
        or 0
    )

    score = 100
    findings: list[dict] = []

    # 1. Policy coverage — an agent with no enabled policies is ungoverned.
    if not enabled_policies:
        score -= 30
        findings.append(
            {
                "code": "NO_POLICY_COVERAGE",
                "severity": "HIGH",
                "title": "No enabled policies",
                "detail": "This agent has no active policies enforcing its behavior.",
            }
        )
    elif "PROMPT_INJECTION" not in policy_types:
        score -= 10
        findings.append(
            {
                "code": "NO_PROMPT_INJECTION_POLICY",
                "severity": "MEDIUM",
                "title": "No prompt-injection policy",
                "detail": "No enabled policy guards against prompt-injection attempts.",
            }
        )

    # 2. Risky tools without governing policies.
    if risky_tools and not enabled_policies:
        score -= 20
        findings.append(
            {
                "code": "UNGOVERNED_RISKY_TOOLS",
                "severity": "HIGH",
                "title": "Ungoverned high-risk tools",
                "detail": (
                    f"{len(risky_tools)} high-risk tool(s) are enabled without "
                    "any policy coverage."
                ),
            }
        )
    elif risky_tools:
        score -= 5
        findings.append(
            {
                "code": "RISKY_TOOLS_PRESENT",
                "severity": "LOW",
                "title": "High-risk tools enabled",
                "detail": (
                    f"{len(risky_tools)} high-risk tool(s) enabled; confirm they are "
                    "required and policy-scoped."
                ),
            }
        )

    # 3. Operational status.
    if agent.status and agent.status.upper() == "SUSPENDED":
        score -= 10
        findings.append(
            {
                "code": "AGENT_SUSPENDED",
                "severity": "MEDIUM",
                "title": "Agent suspended",
                "detail": "Agent is suspended and may indicate an unresolved concern.",
            }
        )

    # 4. Recent blocked / suspicious activity.
    if recent_blocked > 0:
        penalty = min(15, recent_blocked * 3)
        score -= penalty
        findings.append(
            {
                "code": "RECENT_BLOCKS",
                "severity": "MEDIUM",
                "title": "Recent blocked activity",
                "detail": f"{recent_blocked} blocked decision(s) in the last {RECENT_WINDOW_DAYS} days.",
            }
        )
    if recent_suspicious > 0:
        penalty = min(10, recent_suspicious * 2)
        score -= penalty
        findings.append(
            {
                "code": "RECENT_SUSPICIOUS",
                "severity": "MEDIUM",
                "title": "Recent suspicious activity",
                "detail": f"{recent_suspicious} suspicious decision(s) in the last {RECENT_WINDOW_DAYS} days.",
            }
        )

    # 5. Open alerts.
    if open_alerts > 0:
        penalty = min(15, open_alerts * 3)
        score -= penalty
        findings.append(
            {
                "code": "OPEN_ALERTS",
                "severity": "HIGH" if open_alerts >= 3 else "MEDIUM",
                "title": "Unresolved alerts",
                "detail": f"{open_alerts} open or acknowledged alert(s) awaiting resolution.",
            }
        )

    score = max(0, min(100, score))

    return {
        "agent_id": agent.id,
        "agent_name": agent.name,
        "status": agent.status,
        "score": score,
        "grade": _grade(score),
        "level": _level(score),
        "signals": {
            "enabled_policies": len(enabled_policies),
            "policy_types": sorted(policy_types),
            "enabled_tools": len(enabled_tools),
            "risky_tools": len(risky_tools),
            "recent_blocked_events": int(recent_blocked),
            "recent_suspicious_events": int(recent_suspicious),
            "open_alerts": int(open_alerts),
        },
        "findings": findings,
        "evaluated_at": now.isoformat(),
    }


def evaluate_fleet_posture(db: Session, owner_id: int) -> dict:
    """Evaluate posture across every agent owned by ``owner_id``."""

    agents = db.query(Agent).filter(Agent.owner_id == owner_id).all()
    reports = [evaluate_agent_posture(db, agent) for agent in agents]

    if reports:
        average = round(sum(r["score"] for r in reports) / len(reports))
    else:
        average = 0

    distribution: dict[str, int] = {}
    for report in reports:
        distribution[report["level"]] = distribution.get(report["level"], 0) + 1

    return {
        "owner_id": owner_id,
        "agent_count": len(reports),
        "average_score": average,
        "average_grade": _grade(average),
        "level_distribution": distribution,
        "weakest_agents": sorted(reports, key=lambda r: r["score"])[:5],
        "agents": reports,
    }
