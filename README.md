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

- API base: http://127.0.0.1:8000
- Interactive API documentation: http://127.0.0.1:8000/docs
- Health endpoint: http://127.0.0.1:8000/health

Keep this terminal open while developing.

### Run the webhook delivery worker

Start a separate terminal from the repository root after configuring the same
database environment variables:

```powershell
$env:PYTHONPATH = "$PWD\backend"
python -m app.webhook_worker
```

The worker sends due deliveries, applies persisted retry delays, and can also
process one batch with `python -m app.webhook_worker --once`.

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

Open http://localhost:3000.

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

## Security notes

- Never commit `.env`, `.env.local`, passwords, access tokens, database credentials, or production secrets.
- Use unique secrets and credentials for each environment.
- Keep dependencies updated through a deliberate, tested dependency-management process.
- Use HTTPS and appropriately restricted CORS origins in production.
- The webhook worker rejects local and non-public destinations, disables
  redirects, and checks DNS results before sending. DNS rebinding remains a
  residual risk because the HTTP client resolves the hostname again when it
  connects. Restrict worker egress at the network layer to approved public
  destinations and block private, loopback, link-local, and metadata ranges.
- Treat browser `localStorage` tokens as accessible to JavaScript; cross-site scripting can expose them.
- Do not treat compliance-control mappings as proof of certification or regulatory compliance.
- Review configuration, access controls, migrations, and test results before deployment.
