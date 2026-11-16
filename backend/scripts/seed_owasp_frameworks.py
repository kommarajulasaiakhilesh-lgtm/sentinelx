"""Seed OWASP LLM Top 10 (2025) and OWASP Agentic AI Threats frameworks.

Creates the SentinelX internal controls these map to, the two OWASP
frameworks and their framework controls, and honest control mappings — marking
items SentinelX does not address as gaps rather than overclaiming coverage.

Idempotent: safe to re-run. Run from the backend directory:

    PYTHONPATH=. .venv/Scripts/python.exe scripts/seed_owasp_frameworks.py
"""

from __future__ import annotations

import app.main  # noqa: F401 - register models

from app.db.database import SessionLocal
from app.models.framework import Framework, FrameworkControl
from app.models.sentinelx_control import SentinelXControl
from app.models.control_mapping import ControlMapping


# ---------------------------------------------------------------------------
# SentinelX internal controls that the OWASP items map onto.
# (control_id, name, category)
# ---------------------------------------------------------------------------
SENTINELX_CONTROLS = [
    ("SX-ENF-01", "Runtime Policy Enforcement", "Enforcement"),
    ("SX-PI-01", "Prompt-Injection Guardrails", "Guardrails"),
    ("SX-DLP-01", "Sensitive-Data / PII Egress Controls", "Guardrails"),
    ("SX-TOOL-01", "Tool Access Governance & Least Privilege", "Access Control"),
    ("SX-IDENT-01", "Agent Identity & API-Key Lifecycle", "Identity"),
    ("SX-RATE-01", "Rate Limiting & Consumption Controls", "Enforcement"),
    ("SX-AUDIT-01", "Tamper-Evident Audit Logging", "Governance"),
    ("SX-POSTURE-01", "Agent Security Posture Scoring", "Intelligence"),
    ("SX-DETECT-01", "Detection Rules & Anomaly Monitoring", "Detection"),
    ("SX-TEST-01", "Adversarial Security Testing (Attack Battery)", "Testing"),
]

# ---------------------------------------------------------------------------
# OWASP Top 10 for LLM Applications (2025).
# control_id, title, mapped SentinelX control_id (or None = gap), status, rationale
# status in IMPLEMENTED | PARTIALLY_IMPLEMENTED | GAP_IDENTIFIED
# ---------------------------------------------------------------------------
OWASP_LLM = {
    "name": "OWASP Top 10 for LLM Applications",
    "version": "2025",
    "description": (
        "OWASP GenAI Security Project Top 10 risks for LLM applications (2025). "
        "Mappings reflect SentinelX coverage; items outside the platform's scope "
        "are marked as gaps."
    ),
    "controls": [
        ("LLM01", "Prompt Injection", "SX-PI-01", "IMPLEMENTED",
         "Prompt-injection policies + enforcement engine; the attack battery measures detection."),
        ("LLM02", "Sensitive Information Disclosure", "SX-DLP-01", "PARTIALLY_IMPLEMENTED",
         "PII/DLP policies exist; semantic output inspection is not yet implemented."),
        ("LLM03", "Supply Chain", None, "GAP_IDENTIFIED",
         "Model/dependency supply-chain assurance is out of the platform's current scope."),
        ("LLM04", "Data and Model Poisoning", None, "GAP_IDENTIFIED",
         "Training-data and model poisoning defenses are out of scope."),
        ("LLM05", "Improper Output Handling", "SX-ENF-01", "PARTIALLY_IMPLEMENTED",
         "Runtime guardrails evaluate outputs; downstream output encoding is the caller's duty."),
        ("LLM06", "Excessive Agency", "SX-TOOL-01", "IMPLEMENTED",
         "Tool allowlists + posture scoring flag excessive permissions and risky tools."),
        ("LLM07", "System Prompt Leakage", "SX-PI-01", "PARTIALLY_IMPLEMENTED",
         "Detection patterns catch reveal/show-system-prompt attempts; not exhaustive."),
        ("LLM08", "Vector and Embedding Weaknesses", None, "GAP_IDENTIFIED",
         "RAG / vector-store security is out of the platform's current scope."),
        ("LLM09", "Misinformation", "SX-DETECT-01", "PARTIALLY_IMPLEMENTED",
         "Detection rules and anomaly monitoring; no factuality verification."),
        ("LLM10", "Unbounded Consumption", "SX-RATE-01", "IMPLEMENTED",
         "Rate-limit policies and consumption monitoring constrain runaway usage."),
    ],
}

# ---------------------------------------------------------------------------
# OWASP Agentic AI - Threats and Mitigations (15 threats).
# ---------------------------------------------------------------------------
OWASP_AGENTIC = {
    "name": "OWASP Agentic AI Threats",
    "version": "2025",
    "description": (
        "OWASP GenAI Security Project 'Agentic AI - Threats and Mitigations' "
        "taxonomy. Mappings reflect SentinelX coverage; multi-agent and memory "
        "threats outside the platform's scope are marked as gaps."
    ),
    "controls": [
        ("T1", "Memory Poisoning", None, "GAP_IDENTIFIED",
         "Agent memory/context integrity is out of scope."),
        ("T2", "Tool Misuse", "SX-TOOL-01", "PARTIALLY_IMPLEMENTED",
         "Tool allowlists and tool-action policies govern access; runtime intent checks are limited."),
        ("T3", "Privilege Compromise", "SX-POSTURE-01", "PARTIALLY_IMPLEMENTED",
         "Posture scoring flags excessive permissions; no automatic privilege revocation."),
        ("T4", "Resource Overload", "SX-RATE-01", "IMPLEMENTED",
         "Rate limiting and consumption controls bound resource use."),
        ("T5", "Cascading Hallucination Attacks", None, "GAP_IDENTIFIED",
         "Cross-step hallucination containment is out of scope."),
        ("T6", "Intent Breaking & Goal Manipulation", "SX-PI-01", "PARTIALLY_IMPLEMENTED",
         "Prompt-injection guardrails address some goal-manipulation vectors."),
        ("T7", "Misaligned & Deceptive Behaviors", "SX-DETECT-01", "PARTIALLY_IMPLEMENTED",
         "Detection rules and behavioral anomaly monitoring surface abnormal behavior."),
        ("T8", "Repudiation & Untraceability", "SX-AUDIT-01", "IMPLEMENTED",
         "Tamper-evident audit log with per-row hashing and integrity verification."),
        ("T9", "Identity Spoofing & Impersonation", "SX-IDENT-01", "IMPLEMENTED",
         "Per-agent hashed API keys with lifecycle, revocation, and last-use tracking."),
        ("T10", "Overwhelming Human-in-the-Loop", None, "GAP_IDENTIFIED",
         "HITL fatigue / approval-flow protections are out of scope."),
        ("T11", "Unexpected RCE and Code Attacks", "SX-TOOL-01", "PARTIALLY_IMPLEMENTED",
         "High-risk tools (shell/filesystem) are governed and flagged; no sandbox enforcement."),
        ("T12", "Agent Communication Poisoning", None, "GAP_IDENTIFIED",
         "Inter-agent message integrity is out of scope."),
        ("T13", "Rogue Agents in Multi-Agent Systems", "SX-POSTURE-01", "PARTIALLY_IMPLEMENTED",
         "Per-agent posture and detection help, but multi-agent coordination is out of scope."),
        ("T14", "Human Attacks on Multi-Agent Systems", None, "GAP_IDENTIFIED",
         "Multi-agent attack-surface protections are out of scope."),
        ("T15", "Human Manipulation", "SX-PI-01", "PARTIALLY_IMPLEMENTED",
         "Injection guardrails address some manipulation vectors delivered via prompts."),
    ],
}


def _get_or_create_sx_controls(db) -> dict[str, SentinelXControl]:
    result = {}
    for control_id, name, category in SENTINELX_CONTROLS:
        existing = (
            db.query(SentinelXControl)
            .filter(SentinelXControl.control_id == control_id)
            .first()
        )
        if existing is None:
            existing = SentinelXControl(
                control_id=control_id,
                name=name,
                category=category,
                implementation_status="IMPLEMENTED",
                enabled=True,
            )
            db.add(existing)
            db.flush()
        result[control_id] = existing
    return result


def _seed_framework(db, spec: dict, sx: dict[str, SentinelXControl]) -> None:
    framework = (
        db.query(Framework).filter(Framework.name == spec["name"]).first()
    )
    if framework is None:
        framework = Framework(
            name=spec["name"],
            version=spec["version"],
            description=spec["description"],
            enabled=True,
        )
        db.add(framework)
        db.flush()

    for control_id, title, sx_id, status, rationale in spec["controls"]:
        fc = (
            db.query(FrameworkControl)
            .filter(
                FrameworkControl.framework_id == framework.id,
                FrameworkControl.control_id == control_id,
            )
            .first()
        )
        if fc is None:
            fc = FrameworkControl(
                framework_id=framework.id,
                control_id=control_id,
                title=title,
                description=rationale,
                category=spec["name"],
                reference=spec["name"],
                enabled=True,
            )
            db.add(fc)
            db.flush()

        if sx_id is None:
            continue  # intentional gap: no mapping

        exists = (
            db.query(ControlMapping)
            .filter(
                ControlMapping.framework_control_id == fc.id,
                ControlMapping.sentinelx_control_id == sx[sx_id].id,
            )
            .first()
        )
        if exists is None:
            db.add(
                ControlMapping(
                    framework_control_id=fc.id,
                    sentinelx_control_id=sx[sx_id].id,
                    mapping_status=status,
                    rationale=rationale,
                )
            )


def seed() -> None:
    db = SessionLocal()
    try:
        sx = _get_or_create_sx_controls(db)
        _seed_framework(db, OWASP_LLM, sx)
        _seed_framework(db, OWASP_AGENTIC, sx)
        db.commit()
        print("Seeded OWASP LLM Top 10 (2025) and OWASP Agentic AI Threats.")
        print(f"  sentinelx_controls: {db.query(SentinelXControl).count()}")
        print(f"  frameworks:         {db.query(Framework).count()}")
        print(f"  framework_controls: {db.query(FrameworkControl).count()}")
        print(f"  control_mappings:   {db.query(ControlMapping).count()}")
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed()
