# SentinelX

## AI Agent Security Control Plane

SentinelX is a standalone security control plane for monitoring AI agents, enforcing security policies, detecting suspicious behavior, and supporting security investigations.

The project combines a Python/FastAPI backend, PostgreSQL persistence, and a Next.js/TypeScript frontend.

## Key capabilities

- User registration, authentication, and role-based authorization
- Agent lifecycle management and agent API-key authentication
- Security policy and tool-action controls
- Runtime guardrails and repeated blocked-action detection
- Security event collection and analytics
- Detection rules, behavioral anomaly detection, and risk scoring
- Security alerts and incident investigation
- Security testing and compliance-control mappings
- Webhook integrations and security operations dashboards

## Architecture

```text
Next.js / React / TypeScript
            |
            | HTTP API
            v
      FastAPI Backend
            |
    +-------+--------+
    |       |        |
   Auth  Security  Detection,
   & RBAC Controls Risk & Alerts
            |
            v
        PostgreSQL
```

## Technology stack

**Backend**
- Python
- FastAPI
- SQLAlchemy
- PostgreSQL with psycopg 3
- Pydantic
- JWT authentication
- Argon2 password hashing
- Alembic database migrations
- Pytest and HTTPX

**Frontend**
- Next.js
- React
- TypeScript
- Tailwind CSS
- shadcn/ui components
- TanStack Query
- Recharts
- Motion

## Repository structure

```text
sentinelx/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── core/
│   │   ├── db/
│   │   ├── models/
│   │   ├── schemas/
│   │   └── services/
│   ├── alembic/
│   ├── tests/
│   ├── requirements.txt
│   ├── alembic.ini
│   └── pytest.ini
├── frontend/
│   ├── src/
│   ├── public/
│   ├── package.json
│   ├── package-lock.json
│   └── .env.example
└── README.md
```

## Prerequisites

Install the following before starting development:

- Python 3.14, matching the project's development environment
- PostgreSQL
- Node.js and npm
- Git

The commands below use PowerShell on Windows.

## Backend setup

### 1. Create and activate a virtual environment

Run from the repository root:

```powershell
py -3.14 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

If the virtual environment already exists, activate it instead of recreating it.

### 2. Install dependencies

```powershell
python -m pip install -r backend\requirements.txt
```

### 3. Configure environment variables

Create a `.env` file in the **repository root**, next to this README. The backend configuration loads environment variables from this location when running the documented commands from the repository root.

Configure the following values for your local PostgreSQL instance:

```dotenv
DATABASE_URL=postgresql://YOUR_DB_USER:YOUR_DB_PASSWORD@localhost:5432/sentinelx_db
SECRET_KEY=REPLACE_WITH_A_RANDOM_SECRET_OF_AT_LEAST_32_CHARACTERS
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
SQL_ECHO=false
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

Replace the example database credentials and secret with your own values. Generate a unique, strong secret for `SECRET_KEY`; never reuse a production secret in development.

Create the PostgreSQL database `sentinelx_db` if it does not already exist.

The committed `backend/.env.example` is a deployment-oriented template with placeholders. Do not use those placeholders as working credentials.

### 4. Apply database migrations

From the repository root:

```powershell
$env:PYTHONPATH = "$PWD\backend"
python -m alembic -c backend\alembic.ini upgrade head
```

### 5. Start the backend

```powershell
$env:PYTHONPATH = "$PWD\backend"
python -m uvicorn app.main:app --app-dir backend --reload
```

The API should be available at:

- API base: [http://127.0.0.1:8000](http://127.0.0.1:8000)
- Interactive API documentation: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- Health endpoint: [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)

Keep this terminal open while developing.

### Run the webhook delivery worker

Start a separate terminal from the repository root after configuring the same database environment variables:

```powershell
$env:PYTHONPATH = "$PWD\backend"
python -m app.webhook_worker
```

The worker sends due deliveries, applies persisted retry delays, and can also process one batch with `python -m app.webhook_worker --once`.

## Frontend setup

Open a second PowerShell terminal from the repository root.

### 1. Configure the API URL

Create `frontend/.env.local` with:

```dotenv
NEXT_PUBLIC_API_URL=http://127.0.0.1:8000
```

The frontend uses this variable to locate the backend. Restart the development server after changing environment variables.

### 2. Install dependencies and start the frontend

```powershell
cd frontend
npm ci
npm run dev
```

Open [http://localhost:3000](http://localhost:3000).

## Authentication

The backend provides these authentication endpoints:

- `POST /api/auth/register`
- `POST /api/auth/login`

Protected API routes use bearer-token authentication. Obtain a token through login and send it in the HTTP `Authorization` header:

```text
Authorization: Bearer YOUR_ACCESS_TOKEN
```

The backend validates the token and checks the user's identity and account status against the database. Authorization decisions should use the current database user rather than trusting token role claims alone.

## Testing and verification

Run these commands from the repository root unless a step explicitly changes directories.

### Backend tests

With the virtual environment activated:

```powershell
$env:PYTHONPATH = "$PWD\backend"
python -m pytest backend\tests -q
```

### Frontend lint

```powershell
cd frontend
npm run lint
```

### Frontend TypeScript check

```powershell
npx tsc --noEmit
```

### Frontend production build

```powershell
npm run build
```

### Database migration status

From the repository root:

```powershell
$env:PYTHONPATH = "$PWD\backend"
python -m alembic -c backend\alembic.ini current
python -m alembic -c backend\alembic.ini heads
```

Review migration status before deploying changes.

## Production operations

### Application startup

Run SentinelX as a managed application process in production. Do not use the development server's `--reload` option. Configure the deployment platform or reverse proxy to terminate HTTPS and forward requests to the ASGI application.

Example command from the repository root:

```powershell
$env:PYTHONPATH = "$PWD\backend"
python -m uvicorn app.main:app --app-dir backend --host 0.0.0.0 --port 8000
```

Use the deployment platform's process manager, restart policy, resource limits, and secret-management facilities. Do not commit production environment files or credentials.

### Production configuration

Before deployment, verify that:

- `DATABASE_URL` points to the intended production database and is available to the application process.
- `SECRET_KEY` is a strong, unique secret of at least 32 characters and is supplied through the deployment's secret store.
- `ALGORITHM` is set to `HS256`.
- `ACCESS_TOKEN_EXPIRE_MINUTES` is a positive value appropriate for the deployment.
- `CORS_ORIGINS` contains only the exact frontend origins that need access.
- `SQL_ECHO` is `false` in production.
- HTTPS is enforced at the public entry point, and database access is restricted to trusted services.

Keep application and worker configuration consistent where they share database and security settings. Never print secrets into deployment logs.

### Database migrations

Apply database migrations as a controlled deployment step before routing traffic to a new application version. From the repository root, run:

```powershell
$env:PYTHONPATH = "$PWD\backend"
python -m alembic -c backend\alembic.ini upgrade head
python -m alembic -c backend\alembic.ini current
python -m alembic -c backend\alembic.ini heads
```

Confirm the database is at the expected migration head. Review migration changes before applying them to production, and take appropriate backups according to your database recovery plan. Changes that do not alter the schema do not require a new migration.

### Liveness and readiness probes

- **`GET /health` — liveness:** confirms that the application responds. It does not verify database connectivity.
- **`GET /ready` — readiness:** checks database connectivity with a lightweight query. It returns HTTP `200` when ready and HTTP `503` when the database check fails.

Configure the deployment platform to use `/health` for liveness and `/ready` for readiness when it supports separate probes. A readiness failure should prevent the instance from receiving traffic until it recovers.

### Request IDs and request logs

SentinelX accepts a valid `X-Request-ID` request header or generates an ID when the supplied value is missing or invalid. Accepted IDs contain 1–128 ASCII letters, digits, periods, underscores, or hyphens. The response includes the resulting `X-Request-ID` header.

The `sentinelx.request` logger records request metadata, including the request ID, HTTP method, route template, status code, and duration. It is designed to avoid logging query strings, request bodies, cookies, and authorization headers.

Use the request ID to correlate an HTTP request with its application log entry. Treat client-supplied request IDs as untrusted correlation values, not as authentication or authorization evidence. Configure log retention and access according to your operational and privacy requirements.

### Webhook delivery worker

Run the webhook delivery worker as a separate managed process, rather than relying on the API process to keep it running. From the repository root, start it in a separate terminal or service:

```powershell
$env:PYTHONPATH = "$PWD\backend"
python -m app.webhook_worker
```

For a controlled one-time processing run, use:

```powershell
python -m app.webhook_worker --once
```

Provide the worker with the required environment configuration and database access. Configure process supervision and restart behavior, monitor worker logs and delivery outcomes, and restrict outbound network access to the destinations the worker needs. Keep the worker's network controls in place even when destination validation is enabled.

### Operational troubleshooting checklist

1. **Application not responding:** check process health, startup logs, deployment configuration, and the `/health` endpoint.
2. **Instance not ready:** check `/ready`, database availability, credentials, network access, and migration status. Do not expose database credentials or internal exception details in diagnostic output.
3. **Investigating a request:** capture its `X-Request-ID` and search the application logs for the same ID.
4. **Webhook deliveries delayed or failing:** inspect worker logs, delivery status, database connectivity, destination reachability, and outbound network restrictions.
5. **Deployment or migration problems:** inspect the deployed application version and Alembic current/head status, then follow the deployment's rollback and database recovery procedures.

## Security notes

- Never commit `.env`, `.env.local`, passwords, access tokens, database credentials, or production secrets.
- Use unique secrets and credentials for each environment.
- Keep dependencies updated through a deliberate, tested dependency-management process.
- Use HTTPS and appropriately restricted CORS origins in production.
- Webhook destination validation is defense in depth, not a complete SSRF boundary. The worker rejects local and non-public destinations, disables redirects and environment-derived proxies, and checks DNS results before sending. DNS rebinding remains possible because the HTTP client performs its own hostname resolution when connecting. Before production use, isolate the worker from internal networks and enforce outbound network rules that block loopback, private, link-local, and cloud metadata destinations, including IPv4 and IPv6. Verify those controls in the actual hosting environment; application validation and documentation alone do not enforce network isolation.
- Treat browser `localStorage` tokens as accessible to JavaScript; cross-site scripting can expose them.
- Do not treat compliance-control mappings as proof of certification or regulatory compliance.
- Review configuration, access controls, migrations, and test results before deployment.
