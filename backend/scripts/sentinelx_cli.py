#!/usr/bin/env python
"""SentinelX operations CLI.

A small automation/tooling entry point over the platform's services — handy for
provisioning, status checks, and security testing from the shell or CI.

Usage (from the backend directory, with the local .env in place):

    PYTHONPATH=. python scripts/sentinelx_cli.py stats
    PYTHONPATH=. python scripts/sentinelx_cli.py agents
    PYTHONPATH=. python scripts/sentinelx_cli.py battery <agent_id>
    PYTHONPATH=. python scripts/sentinelx_cli.py sla
    PYTHONPATH=. python scripts/sentinelx_cli.py seed-demo
    PYTHONPATH=. python scripts/sentinelx_cli.py seed-owasp
"""

from __future__ import annotations

import argparse
import json
import sys

import app.main  # noqa: F401 - register models

from sqlalchemy import func

from app.db.database import SessionLocal
from app.models.agent import Agent
from app.models.security_event import SecurityEvent
from app.models.security_alert import SecurityAlert
from app.models.user import User


def _first_admin_id(db) -> int | None:
    admin = db.query(User).filter(User.role == "ADMIN").order_by(User.id).first()
    return admin.id if admin else None


def cmd_stats(_args) -> int:
    db = SessionLocal()
    try:
        print("SentinelX platform status")
        print(f"  agents:          {db.query(func.count(Agent.id)).scalar() or 0}")
        print(f"  active agents:   {db.query(func.count(Agent.id)).filter(Agent.status=='ACTIVE').scalar() or 0}")
        print(f"  security events: {db.query(func.count(SecurityEvent.id)).scalar() or 0}")
        print(f"  blocked events:  {db.query(func.count(SecurityEvent.id)).filter(SecurityEvent.decision=='BLOCK').scalar() or 0}")
        print(f"  open alerts:     {db.query(func.count(SecurityAlert.id)).filter(SecurityAlert.status.in_(['OPEN','ACKNOWLEDGED'])).scalar() or 0}")
    finally:
        db.close()
    return 0


def cmd_agents(_args) -> int:
    db = SessionLocal()
    try:
        for a in db.query(Agent).order_by(Agent.id).all():
            print(f"  #{a.id:<4} {a.status:<10} {a.name}")
    finally:
        db.close()
    return 0


def cmd_battery(args) -> int:
    from app.services.attack_battery_service import run_attack_battery

    db = SessionLocal()
    try:
        agent = db.get(Agent, args.agent_id)
        if agent is None:
            print(f"Agent {args.agent_id} not found", file=sys.stderr)
            return 1
        report = run_attack_battery(db, agent)
        s = report["summary"]
        print(f"Attack battery for agent #{agent.id} ({agent.name}):")
        print(f"  detection rate:  {s['detection_rate_percent']}%")
        print(f"  attacks caught:  {s['detected']}/{s['total_attacks']}")
        print(f"  false positives: {s['false_positives']}")
    finally:
        db.close()
    return 0


def cmd_sla(_args) -> int:
    from app.services.incident_sla_service import incident_sla_report

    db = SessionLocal()
    try:
        owner_id = _first_admin_id(db)
        if owner_id is None:
            print("No admin user found", file=sys.stderr)
            return 1
        report = incident_sla_report(db, owner_id)
        print(json.dumps(report["summary"], indent=2))
    finally:
        db.close()
    return 0


def cmd_seed_demo(_args) -> int:
    from scripts.dev_bootstrap import seed
    seed()
    return 0


def cmd_seed_owasp(_args) -> int:
    from scripts.seed_owasp_frameworks import seed
    seed()
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="sentinelx", description="SentinelX operations CLI")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("stats", help="Show platform status").set_defaults(func=cmd_stats)
    sub.add_parser("agents", help="List agents").set_defaults(func=cmd_agents)
    b = sub.add_parser("battery", help="Run the prompt-injection attack battery")
    b.add_argument("agent_id", type=int)
    b.set_defaults(func=cmd_battery)
    sub.add_parser("sla", help="Incident SLA summary").set_defaults(func=cmd_sla)
    sub.add_parser("seed-demo", help="Seed synthetic demo data").set_defaults(func=cmd_seed_demo)
    sub.add_parser("seed-owasp", help="Seed OWASP frameworks").set_defaults(func=cmd_seed_owasp)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
