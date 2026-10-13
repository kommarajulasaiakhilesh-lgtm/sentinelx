# SentinelX Frontend

The SentinelX frontend is a Next.js application built with React, TypeScript, and Tailwind CSS. It provides the web interface for the SentinelX AI Agent Security Control Plane.

For the complete project overview and backend setup, see the [root README](../README.md).

## Prerequisites

- Node.js compatible with the installed Next.js version
- npm
- A running SentinelX backend

## Setup

### 1. Install dependencies

From the `frontend` directory:

```powershell
npm ci
```

### 2. Configure the backend URL

Create `.env.local` in the `frontend` directory:

```dotenv
NEXT_PUBLIC_API_URL=http://127.0.0.1:8000
```

Set this variable to the appropriate backend URL for your environment. Restart the development server after changing it.

### 3. Start the development server

```powershell
npm run dev
```

Open http://localhost:3000.

## Available commands

Run these commands from the `frontend` directory.

| Command | Purpose |
|---|---|
| `npm run dev` | Start the development server |
| `npm run lint` | Run ESLint |
| `npx tsc --noEmit` | Check TypeScript types |
| `npm run build` | Create a production build |
| `npm run start` | Serve a production build |

Run `npm run build` before using `npm run start`.

## Configuration and security

- Keep `.env.local` out of version control.
- Variables prefixed with `NEXT_PUBLIC_` can be exposed to browser code. Do not put passwords, private API keys, or other secrets in them.
- Authentication tokens stored in browser `localStorage` can be accessed by JavaScript. Cross-site scripting can expose these tokens.
- Use HTTPS and an appropriately configured backend URL in production.

## Troubleshooting

**The frontend cannot reach the backend**
- Confirm the backend is running.
- Check `NEXT_PUBLIC_API_URL` in `.env.local`.
- Verify that the backend CORS configuration permits the frontend origin.
- Restart the frontend development server after changing environment variables.

**Dependency installation fails**
- Confirm Node.js and npm are installed.
- Run `npm ci` from the `frontend` directory.
- Check the terminal output for dependency or network errors.

**Lint, type checking, or build fails**
- Read the first relevant error in the terminal.
- Resolve the underlying issue before deploying.
