# SentinelX — Local Development (Zero-Install)

This guide runs SentinelX end-to-end on a machine **without PostgreSQL or
Docker**, using a local SQLite database. PostgreSQL remains the production
default (see `backend/.env.example`); SQLite is a local-dev convenience only.

> The models use no PostgreSQL-specific column types, so SQLite is a faithful
> local stand-in. The only code change supporting this is an additive
> `check_same_thread` connect-arg in `backend/app/db/database.py` (PostgreSQL
> deployments are unaffected).

## 1. Backend

```bash
cd backend
python -m venv .venv
./.venv/Scripts/python.exe -m pip install -r requirements.txt
```

The local `backend/.env` is already configured with:

- `DATABASE_URL=sqlite:///./sentinelx_dev.db`
- a generated `SECRET_KEY`
- `CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000`

Create the schema and seed realistic synthetic data (idempotent):

```bash
cd backend
PYTHONPATH=. ./.venv/Scripts/python.exe scripts/dev_bootstrap.py
```

This seeds an admin login, 5 agents, tools, policies, 140 security events,
alerts, a default risk-scoring model, and derived analytics.

Run the API:

```bash
cd backend
PYTHONPATH=. ./.venv/Scripts/python.exe -m uvicorn app.main:app --reload --port 8000
```

- API docs: http://127.0.0.1:8000/docs
- Health: http://127.0.0.1:8000/health

## 2. Frontend

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:3000 and sign in:

- **Username:** `admin`
- **Password:** `SentinelX!2026`

(A second non-admin account `analyst` / `SentinelX!2026` is also seeded.)

## 3. Verification

```bash
# backend posture tests (self-contained, no external DB)
cd backend
PYTHONPATH=. ./.venv/Scripts/python.exe -m pytest tests/test_agent_posture.py --noconftest -q

# frontend
cd frontend
npx tsc --noEmit
npm run lint
npm run build
```

## What changed from the upstream checkpoint

- **Light professional theme** across the app (new token system in
  `globals.css`, converted components, Framer Motion page transitions and
  interactions).
- **Agent Security Posture** moat feature: `backend/app/services/
  agent_posture_service.py`, `backend/app/api/agent_posture.py`,
  `frontend/src/app/posture/page.tsx`, plus tests.
- **Audit Log / governance evidence** moat feature: `backend/app/models/
  audit_log.py`, `backend/app/services/audit_service.py`,
  `backend/app/api/audit.py`, audit hooks on agent/policy/auth endpoints,
  Alembic migration `a1b2c3d4e5f6_add_audit_logs.py`, and
  `frontend/src/app/audit/page.tsx`, plus tests.
- **Zero-install local dev**: `scripts/dev_bootstrap.py` + SQLite support.

Run the new tests here with:

```bash
cd backend
PYTHONPATH=. ./.venv/Scripts/python.exe -m pytest tests/test_agent_posture.py tests/test_audit_log.py --noconftest -q
```

The full existing backend test suite (264 tests) still targets an isolated
PostgreSQL database (`sentinelx_phase27_test_db`) and is unchanged.
