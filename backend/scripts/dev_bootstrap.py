"""Zero-install local development bootstrap for SentinelX.

Creates the full schema on the configured database (intended for the
SQLite local-dev URL, e.g. sqlite:///./sentinelx_dev.db) and seeds a
realistic set of synthetic data so every dashboard renders with authentic
backend records instead of empty states.

This script is additive and local-only. It never touches PostgreSQL
production/test databases and is safe to re-run (idempotent on the admin
account — if the admin already exists it exits without changes).

Run from the backend directory with the local .env in place:

    .venv/Scripts/python.exe scripts/dev_bootstrap.py
"""

from __future__ import annotations

import random
from datetime import datetime, timedelta, timezone

import app.main  # noqa: F401 - registers every SQLAlchemy model

from app.db.database import Base, SessionLocal, engine
from app.core.security import hash_password

from app.models.user import User
from app.models.agent import Agent
from app.models.tool import Tool
from app.models.policy import Policy
from app.models.security_event import SecurityEvent
from app.models.security_alert import SecurityAlert
from app.models.risk_scoring_configuration import RiskScoringConfiguration
from app.services.analytics_service import generate_agent_analytics


ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "SentinelX!2026"
ADMIN_EMAIL = "admin@sentinelx.local"

ANALYST_USERNAME = "analyst"
ANALYST_PASSWORD = "SentinelX!2026"
ANALYST_EMAIL = "analyst@sentinelx.local"


def _now() -> datetime:
    return datetime.now(timezone.utc)


def seed() -> None:
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        if db.query(User).filter(User.username == ADMIN_USERNAME).first():
            print("Bootstrap already applied (admin exists). Nothing to do.")
            return

        admin = User(
            username=ADMIN_USERNAME,
            email=ADMIN_EMAIL,
            password_hash=hash_password(ADMIN_PASSWORD),
            role="ADMIN",
            is_active=True,
        )
        analyst = User(
            username=ANALYST_USERNAME,
            email=ANALYST_EMAIL,
            password_hash=hash_password(ANALYST_PASSWORD),
            role="USER",
            is_active=True,
        )
        db.add_all([admin, analyst])
        db.flush()

        agent_specs = [
            ("Customer Support Copilot", "Handles tier-1 support conversations", "ACTIVE"),
            ("Finance Reconciliation Agent", "Automates invoice matching", "ACTIVE"),
            ("DevOps Assistant", "Runs infra queries and deploy checks", "ACTIVE"),
            ("Research Summarizer", "Summarizes internal documents", "SUSPENDED"),
            ("Sales Outreach Bot", "Drafts and sends prospect emails", "ACTIVE"),
        ]
        agents: list[Agent] = []
        for name, desc, status in agent_specs:
            a = Agent(
                owner_id=admin.id,
                name=name,
                description=desc,
                status=status,
            )
            db.add(a)
            agents.append(a)
        db.flush()

        tool_types = ["HTTP", "DATABASE", "SHELL", "EMAIL", "FILESYSTEM"]
        for a in agents:
            for i in range(random.randint(2, 4)):
                db.add(
                    Tool(
                        agent_id=a.id,
                        name=f"{a.name.split()[0].lower()}_tool_{i+1}",
                        description="Granted capability for this agent",
                        tool_type=random.choice(tool_types),
                        enabled=random.random() > 0.2,
                    )
                )

        policy_specs = [
            ("Prompt Injection Guard", "PROMPT_INJECTION", "BLOCK", 100),
            ("PII Egress Control", "DATA_LOSS_PREVENTION", "BLOCK", 90),
            ("Tool Allowlist", "TOOL_ACCESS", "ALLOW", 50),
            ("Rate Limit Policy", "RATE_LIMIT", "THROTTLE", 40),
        ]
        policies: list[Policy] = []
        for a in agents:
            for name, ptype, action, prio in random.sample(policy_specs, k=random.randint(2, 4)):
                p = Policy(
                    agent_id=a.id,
                    name=name,
                    description=f"{name} applied to {a.name}",
                    policy_type=ptype,
                    action=action,
                    priority=prio,
                    condition=None,
                    enabled=True,
                )
                db.add(p)
                policies.append(p)
        db.flush()

        decisions = ["ALLOW"] * 7 + ["BLOCK"] * 2 + ["SUSPICIOUS"] * 1
        event_types = [
            "TOOL_INVOCATION",
            "PROMPT_SUBMISSION",
            "DATA_ACCESS",
            "POLICY_EVALUATION",
            "CREDENTIAL_USE",
        ]
        reasons = {
            "BLOCK": "Matched prompt-injection signature",
            "SUSPICIOUS": "Anomalous tool-call frequency",
            "ALLOW": None,
        }

        events: list[SecurityEvent] = []
        for _ in range(140):
            a = random.choice(agents)
            decision = random.choice(decisions)
            created = _now() - timedelta(
                days=random.randint(0, 29),
                hours=random.randint(0, 23),
                minutes=random.randint(0, 59),
            )
            ev = SecurityEvent(
                agent_id=a.id,
                policy_id=None,
                event_type=random.choice(event_types),
                action=random.choice(["read", "write", "execute", "send"]),
                decision=decision,
                reason=reasons[decision],
                event_metadata=None,
                created_at=created,
            )
            db.add(ev)
            events.append(ev)
        db.flush()

        severities = ["LOW", "MEDIUM", "HIGH", "CRITICAL"]
        flagged = [e for e in events if e.decision in ("BLOCK", "SUSPICIOUS")]
        for e in random.sample(flagged, k=min(18, len(flagged))):
            sev = random.choices(severities, weights=[3, 4, 2, 1])[0]
            db.add(
                SecurityAlert(
                    agent_id=e.agent_id,
                    security_event_id=e.id,
                    alert_type=("PROMPT_INJECTION" if e.decision == "BLOCK" else "ANOMALY"),
                    severity=sev,
                    title=f"{sev.title()} severity {('block' if e.decision=='BLOCK' else 'anomaly')} detected",
                    description="Auto-generated from a flagged security event.",
                    status=random.choice(["OPEN", "OPEN", "ACKNOWLEDGED", "RESOLVED"]),
                    created_at=e.created_at,
                )
            )

        # Default (global) risk-scoring model so analytics can be computed.
        db.add(
            RiskScoringConfiguration(
                owner_id=None,
                name="Default Risk Model",
                enabled=True,
                blocked_event_weight=10,
                suspicious_event_weight=5,
                policy_violation_weight=8,
                score_cap=100,
                low_max=25,
                medium_max=50,
                high_max=75,
                critical_max=100,
            )
        )
        db.flush()

        # Generate authentic analytics rows from the seeded events.
        window_end = _now()
        window_start = window_end - timedelta(days=30)
        for a in agents:
            generate_agent_analytics(
                db=db,
                agent_id=a.id,
                period_start=window_start,
                period_end=window_end,
            )

        db.commit()
        print("Seed complete.")
        print(f"  users:   {db.query(User).count()}")
        print(f"  agents:  {db.query(Agent).count()}")
        print(f"  tools:   {db.query(Tool).count()}")
        print(f"  policies:{db.query(Policy).count()}")
        print(f"  events:  {db.query(SecurityEvent).count()}")
        print(f"  alerts:  {db.query(SecurityAlert).count()}")
        print(f"\nLogin: {ADMIN_USERNAME} / {ADMIN_PASSWORD}")
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed()
