# SentinelX — Portfolio & Technical Overview

> **AI Agent Security Control Plane** — a standalone platform to register, govern,
> monitor, and investigate AI agents: identities, policies, tools, guardrails,
> detection, risk, alerts, incidents, analytics, and compliance visibility.

- **Live app:** https://sentinelx-rho.vercel.app
- **API:** https://sentinelx-x7vp.onrender.com (`/health`, `/docs`)
- **Demo login:** `admin` / `SentinelX!2026` (change after first use)

---

## 1. Elevator pitch

As organizations deploy LLM-based agents, they need the same controls they
already have for human and service identities: who can do what, with which
tools, under which policies — plus detection, auditing, and incident response
when something goes wrong. **SentinelX is a security control plane for AI
agents.** It lets a security team register agents, attach runtime policies and
guardrails, govern tool access, evaluate prompt-injection defenses, score each
agent's security posture, and keep a tamper-evident audit trail — all behind a
clean operator console.

## 2. Architecture

```
┌────────────────┐     HTTPS     ┌─────────────────┐     psycopg     ┌──────────────┐
│  Next.js (FE)  │ ───────────▶ │  FastAPI (BE)   │ ─────────────▶ │  PostgreSQL  │
│  Vercel        │   JWT auth    │  Render         │   SQLAlchemy    │  Supabase    │
└────────────────┘               └─────────────────┘                 └──────────────┘
      │                                  │
      │ TanStack Query                   │ policy engine · detection rules · risk
      │ Recharts · Motion                │ scoring · posture · audit · webhooks(off)
```

- **Frontend** — Next.js 16 (App Router) + React 19 + TypeScript + Tailwind v4,
  TanStack Query for data, Recharts for charts, Motion for animation. Light and
  dark themes.
- **Backend** — FastAPI + SQLAlchemy 2 + Pydantic 2. JWT auth (Argon2 password
  hashing), per-owner authorization, Alembic migrations.
- **Database** — PostgreSQL (Supabase in production). No PG-specific column
  types, so a zero-install SQLite path exists for local development.
- **Deployment** — Frontend on Vercel, backend on Render, DB on Supabase. CI on
  GitHub Actions (backend tests on isolated Postgres, frontend lint/type/build).

## 3. Tech stack

| Layer | Choice | Why |
|---|---|---|
| API | FastAPI | Typed, async-capable, auto OpenAPI docs |
| ORM | SQLAlchemy 2 (typed) | Mature, explicit, DB-portable |
| Auth | JWT + Argon2 | Stateless sessions; memory-hard hashing |
| Migrations | Alembic | Versioned, reviewable schema changes |
| Frontend | Next.js + React 19 | App Router, SSR, modern DX |
| Data fetching | TanStack Query | Caching, invalidation, mutations |
| Styling | Tailwind v4 | Token-driven theming, light + dark |
| Charts | Recharts | Declarative, composable |
| Tests | Pytest + ESLint + tsc | Backend units, type + lint gates |

## 4. Feature catalog

**Identity & access**
- Agent registration and lifecycle (active / suspended), bulk status changes.
- Agent API-key lifecycle: generation (shown once), expiry, last-used tracking,
  revocation — all audited.
- RBAC: operator vs admin; admin-only system endpoints via `require_role`.

**Policy & enforcement**
- Policy management (prompt-injection, DLP, tool-access, rate limiting).
- A runtime policy engine that evaluates requests and returns ALLOW/BLOCK/WARN.
- **Policy versioning + rollback** — every change snapshots an immutable version.

**Detection & intelligence**
- Detection rules, risk scoring, behavioral baselines, anomaly detection.
- **Agent Security Posture** scoring — a configuration-centric score per agent
  (policy coverage, risky tools, status, recent blocks, open alerts).
- **Prompt-injection attack battery** — a reproducible library of direct,
  evasion, and benign inputs scored against an agent's live enforcement
  (detection rate, false positives). Honest about evasion gaps.

**Operations**
- Security events (searchable/sortable table + CSV export), alerts, incident
  correlation and response.
- Analytics and dashboards built from authentic backend data.

**Governance**
- **Audit log** — append-only, with per-row SHA-256 content hashes and a
  `/integrity` verification endpoint; CSV export.
- Compliance control mappings (NIST AI RMF, ISO/IEC 42001, HIPAA) with coverage
  reporting and CSV export — presented as *mappings*, not certification.

**Console UX**
- Command palette (⌘K), light/dark themes, toasts, confirmation modals,
  skeleton loaders, agent detail pages, notification and profile menus.

## 5. Security model & key decisions

- **Authorization is at the API layer.** Every query is scoped by `owner_id`
  (or a join to the owner's agents). This is the real tenant boundary; the DB
  connection uses a service role, so database-level RLS is not relied upon and
  is not claimed.
- **Secrets never round-trip.** Passwords and API keys are hashed (Argon2);
  plaintext API keys are shown exactly once at creation and never stored.
- **Audit is resilient and tamper-evident.** Audit writes are best-effort and
  committed separately from the action they describe, so an audit problem can
  never fail a login or other primary action. Each row carries a content hash
  for integrity verification.
- **SSRF defense-in-depth.** Outbound webhook destinations are validated against
  loopback/private/link-local/CGNAT/ULA/multicast/reserved and cloud-metadata
  ranges (IPv4, IPv6, IPv4-mapped), with redirects and env proxies disabled.
  A residual DNS-rebinding window remains, so the production webhook worker
  stays **disabled** pending network-level egress controls — documented, not
  hand-waved.
- **Rate limiting** protects authentication endpoints against brute force.
- **Honest claims.** The platform never asserts certification, full
  prompt-injection immunity, or guaranteed detection — it measures and reports.

## 6. Testing strategy

- **Backend:** 130+ tests. A large Postgres-backed suite (run in CI against an
  isolated `sentinelx_phase27_test_db`) plus self-contained unit suites
  (SSRF, rate limiting, posture, audit integrity, policy versioning, attack
  battery, bulk ops/RBAC) that use in-memory SQLite and run anywhere.
- **Frontend:** TypeScript type-check, ESLint, and a production Next.js build
  all gate every PR.
- **CI:** GitHub Actions runs `alembic upgrade head`, seeds, backend tests, and
  the frontend checks on every push; Vercel builds the frontend.

## 7. Demo script (5–10 minutes)

1. **Sign in** at the live URL (`admin` / `SentinelX!2026`). Point out the
   JWT-protected console and the light/dark toggle (⌘K opens the command palette).
2. **Command Center** — fleet counts, enforcement-decision donut, 14-day event
   volume, alerts-by-severity. All from live data.
3. **Agents → open an agent** — show its posture score, policies, tools, and the
   **API-key** panel (generate a key → "shown once").
4. **Run the attack battery** on that agent — walk through the detection rate and
   the *missed* evasion payloads; emphasize the honest framing.
5. **Agent Posture** page — fleet posture, weakest agents, and findings.
6. **Policies → Version history** on a policy — show change history and roll back.
7. **Audit Log** — click **Verify integrity**, then **Export CSV**.
8. **Bulk ops** — select a couple of agents and bulk-suspend/activate.
9. **Compliance** — framework coverage and **Export report**.

## 8. Likely interview questions & answers

**Q: How do you isolate one operator's data from another's?**
A: At the API layer — every list/detail query filters by `owner_id` or joins
through the owner's agents, and this is covered by tests (e.g. bulk ops only
touch owned rows, admin endpoints 403 for non-admins). The DB connection uses a
service role, so I don't rely on Postgres RLS and I don't claim DB-level
isolation; if the DB were ever exposed directly to clients, RLS policies would
be required and designed around the same owner boundary.

**Q: Why is the webhook worker disabled?**
A: The destination validator blocks private/metadata/loopback IPs across v4/v6
and disables redirects and env proxies, but DNS rebinding leaves a small
time-of-check/time-of-use window between validation and the client's own
connection. Closing it properly needs network-level egress controls in the
host. Rather than ship a documentation warning as if it were a control, the
worker stays off until that's in place.

**Q: How do you keep auditing from breaking the app?**
A: Audit writes are best-effort and committed *after* the primary action, in
their own transaction. A missing table or failed write logs a warning but never
rolls back or 500s the action it describes. I learned this the hard way when a
missing `audit_logs` table in production 500'd login — which is exactly why the
write is now non-fatal, and why each entry carries a verifiable content hash.

**Q: Isn't a prompt-injection "detection rate" misleading?**
A: It would be if I claimed it as coverage. The attack battery is a fixed,
reproducible set with *direct* payloads (should be caught) and *evasion*
payloads (obfuscated, usually missed by naive matching) plus benign controls.
The result surfaces the gap honestly — it's a measurement and regression signal,
not a guarantee.

**Q: How would you scale this?**
A: Move rate limiting and caching to Redis; run webhook delivery and analytics
rollups on a worker queue; stream the security-event firehose through Kafka;
add OpenSearch for event/log search and Grafana/Prometheus/OTel for
observability; containerize and run on Kubernetes with Terraform IaC; and add
SSO (OIDC/SAML) with fine-grained authz (OPA/Cedar) for enterprise access.

## 9. Known limitations & future work

- Webhook worker disabled pending egress controls (see above).
- RLS intentionally not enabled; authorization is enforced in the API.
- Compliance features are control *mappings* and visibility, not certification.
- Free-tier hosting spins down when idle (first request after idle is slow).
- Future: dark-mode is shipped; next would be E2E (Playwright), SAST (CodeQL),
  dependency scanning, error tracking (Sentry), containerization, and a
  detection-rule tuning workbench.
