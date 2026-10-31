
# SentinelX — Demo Walkthrough

## 1. Overview

SentinelX is a standalone AI Agent Security Control Plane built with FastAPI, PostgreSQL, and Next.js.

This walkthrough presents a local demonstration of agent management, security controls, detection, incident investigation, risk intelligence, and compliance visibility.

**Demo environment:** Local development using a newly created, isolated demo database.

**Important:** Do not use production credentials or any existing database for this demonstration. Do not start the webhook delivery worker against production.

## 2. Demo objectives

Demonstrate how SentinelX brings together:

- AI agent registration and lifecycle management
- Security policies, tools, and guardrails
- Security events and detection rules
- Alerts and incident investigation
- Risk scoring and analytics
- Security testing and compliance-control mappings

## 3. Start the application

Follow the backend and frontend setup instructions in the root README.

Before creating demo data:

- Obtain explicit approval to create a separate demo database.
- Confirm the application is configured to connect exclusively to that database.
- Run the required migrations against that database.
- Use a dedicated demonstration account and synthetic data created through application APIs.

Never use `sentinelx_db`, the existing `sentinelx_test_db`, or any production database for this demonstration.

Verify the backend:

- `GET /` — application information
- `GET /health` — application liveness
- `GET /ready` — database readiness

Open the frontend in the browser and authenticate using the local demonstration account.

Use only demonstration credentials and synthetic data.

## 4. Demonstration sequence

### Step 1 — Agent management

**Frontend:** `/agents`

Demonstrate the agent management interface.

Explain:
- How agents are registered.
- How agent identity and lifecycle are managed.
- How agent API credentials support agent authentication.

Use a demonstration agent. Never display or share a real API key.

### Step 2 — Security policies and guardrails

**Frontend:** `/policies`, `/tools`, `/guardrails`

Demonstrate the security configuration surfaces.

Explain:
- Policy-based restrictions.
- Tool access management.
- Guardrail configuration and enforcement.

Use test configurations and explain the expected security outcome.

### Step 3 — Detection and security events

**Frontend:** `/detection-rules`, `/events`

Demonstrate detection-rule configuration and security-event visibility.

Explain how deterministic detection logic evaluates relevant security activity and how events support investigation.

Do not claim that every possible attack is detected.

### Step 4 — Alerts and incident investigation

**Frontend:** `/alerts`, `/incidents`

Show how security alerts and incidents support operational investigation.

Explain:
- Alert review and status management.
- Incident investigation and lifecycle management.
- How related security information supports triage.

Generate demonstration records through the application APIs.

### Step 5 — Risk intelligence and analytics

**Frontend:** `/risk-configurations`, `/analytics`

Explain how configurable risk scoring and detection intelligence contribute to security visibility.

Show the available analytics and risk-related information.

Do not present demonstration scores as independently validated real-world risk measurements.

### Step 6 — Security testing and compliance visibility

**Frontend:** `/security-tests`, `/compliance`

Demonstrate the security testing interface and framework/control mappings.

Explain that these mappings provide control visibility and do not establish certification or regulatory compliance.

## 5. Suggested presentation narrative

> AI agents introduce new operational capabilities, but they also create security risks involving identity, permissions, tool usage, unexpected behavior, and sensitive information.
>
> SentinelX provides a centralized control plane for managing agent security. It combines agent lifecycle management, policy enforcement, guardrails, detection rules, risk scoring, alerts, incident investigation, and compliance-control visibility.
>
> The goal is to make AI agent security observable and manageable through a unified platform.

## 6. Demo safety checklist

- [ ] Use a newly created, isolated demo database.
- [ ] Confirm the application connects only to that database.
- [ ] Use dedicated demonstration accounts and synthetic data.
- [ ] Never expose API keys, JWTs, or environment secrets.
- [ ] Do not use production credentials or existing databases.
- [ ] Do not activate the production webhook worker.
- [ ] Avoid sending webhooks to real external destinations.
- [ ] Clean up demonstration records when appropriate.

## 7. Known limitations and responsible claims

- Webhook destination validation is not a complete SSRF boundary; production worker activation remains restricted.
- Browser localStorage tokens are accessible to JavaScript.
- Compliance-control mappings are not proof of certification.
- Detection coverage is limited to implemented detection logic.
- Demonstration data and scores should not be represented as production security outcomes.

## 8. Portfolio presentation outline

A concise project presentation can follow this structure:

1. Problem: AI agent security and governance.
2. Solution: SentinelX security control plane.
3. Architecture: Next.js frontend, FastAPI backend, PostgreSQL database.
4. Security capabilities: identity, policies, guardrails, detection, and risk scoring.
5. Operations: alerts, incidents, analytics, and evidence.
6. Verification: automated tests, migrations, and CI.
7. Security considerations: threat model, residual risks, and deployment restrictions.
8. Future work: stronger webhook connection-time protections and independently verified network isolation.

## 9. Project links

- Source code: https://github.com/kommarajulasaiakhilesh-lgtm/sentinelx
- API documentation: available at `/docs` when the local backend is running.
- Security threat model: `docs/THREAT_MODEL.md`
