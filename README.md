# SentinelX

## AI Agent Security Control Plane

SentinelX is a Python-based security control plane for monitoring, controlling, and enforcing security policies for AI agents.

The project focuses on protecting AI agents from unsafe actions, malicious inputs, excessive tool usage, and repeated security violations.

---

## Key Capabilities

- User authentication and authorization
- Agent identity and API-key authentication
- Agent lifecycle management
- Security policy management
- Prompt-injection detection
- Tool and action security
- Runtime tool-action rate limiting
- Repeated blocked-action detection
- Security event logging
- Security analytics and risk scoring
- Security alert generation
- Alert investigation and status management
- API-level validation and security hardening

---

## Architecture

```text
User
 │
 ▼
FastAPI API
 │
 ├── Authentication & Authorization
 │
 ├── Agent Security
 │
 ├── Policy Engine
 │
 ├── Tool & Action Security
 │
 ├── Runtime Guardrails
 │
 ├── Security Events
 │
 ├── Security Analytics
 │
 └── Security Alerts
 │
 ▼
PostgreSQL