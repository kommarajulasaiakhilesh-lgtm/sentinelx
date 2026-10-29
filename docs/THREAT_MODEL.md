# SentinelX Security Threat Model

## 1. Purpose and Scope

SentinelX is a standalone AI Agent Security Control Plane built with
FastAPI, SQLAlchemy, PostgreSQL, and a Next.js frontend.

This document records the principal assets, trust boundaries, threats,
existing defensive controls, and residual risks considered during
Phase 26: Security Hardening and Threat Modeling.

SentinelX is independent of CIMP. No CIMP integration is in scope.

This document is an engineering threat assessment, not a penetration-test
report, compliance certification, or guarantee that every deployment is secure.

## 2. Security Objectives

- Protect user accounts, authentication credentials, and agent API keys.
- Enforce authentication and authorization at protected API boundaries.
- Preserve the integrity of security events, alerts, policies, and incidents.
- Prevent unsafe outbound webhook destinations and unauthorized delivery outcomes.
- Maintain reliable webhook processing when workers or database operations fail.
- Protect sensitive information from unintended disclosure through logs or APIs.
- Make security failures observable and support operational recovery.

## 3. Assets

| Asset | Security concern |
| --- | --- |
| User credentials and access tokens | Account compromise and unauthorized API access |
| Agent API keys | Agent impersonation and unauthorized operations |
| PostgreSQL records | Unauthorized disclosure, modification, or deletion |
| Security events and alerts | Tampering, loss, duplication, or misleading detection |
| Policies and risk configurations | Unauthorized changes to security enforcement |
| Webhook endpoints and payloads | SSRF, data disclosure, and unauthorized outbound requests |
| Webhook delivery state and claim tokens | Stale-worker writes and incorrect delivery outcomes |
| Application secrets and database credentials | Account takeover and infrastructure compromise |
| Logs and operational metrics | Sensitive-data exposure and delayed incident detection |

## 4. Trust Boundaries

1. Browser to frontend: user-controlled input and browser-side state cross
   into the application.
2. Frontend to backend API: requests must not be trusted solely because
   they originate from the frontend.
3. Backend to PostgreSQL: application queries and transactions operate on
   persistent security-sensitive state.
4. Agent to backend API: agent-supplied credentials and event data require
   appropriate validation and authorization.
5. Webhook worker to configured destinations: outbound requests cross from
   the trusted application environment to potentially untrusted networks.
6. Worker instances to shared delivery records: multiple workers may race
   to claim, renew, or finish the same delivery.
7. Deployment environment to application: environment variables, network
   policies, database permissions, and process supervision affect security.

## 5. Threat Scenarios and Controls

### T1. Unauthorized API access

Threat:
An unauthenticated or insufficiently privileged caller accesses protected
data or performs a security-sensitive operation.

Controls:
- JWT-based authentication and password hashing are part of the application.
- Authentication and authorization boundaries have dedicated backend tests.
- Protected operations should enforce authorization on the server, not
  rely on frontend visibility.

Verification:
- Review authentication and authorization tests and protected route
  dependencies during the final Phase 26 review.
- Confirm denial behavior for unauthenticated and unauthorized callers.

Residual risk:
Incorrect authorization on an individual route or a compromised user
credential can still expose permitted application operations.

### T2. Agent API-key compromise

Threat:
A leaked or stolen agent API key is used to impersonate an agent.

Controls:
- The codebase includes agent API-key handling and associated access controls.
- Key selectors, expiry, and active-state checks should be verified against
  the current implementation and tests.
- Secrets must not be written to logs or exposed in API responses.

Verification:
Confirm that invalid, expired, inactive, and unauthorized keys are rejected
and that stored key material is handled safely.

Residual risk:
A valid compromised key may remain usable until it expires or is revoked.

### T3. Unsafe webhook destination and SSRF

Threat:
An attacker influences a webhook destination to reach loopback, private,
link-local, cloud metadata, or another sensitive internal service.

Controls:
- Destination validation rejects unsafe destinations and invalid cases.
- DNS resolution rejects unsafe, mixed public/private, and empty results.
- Redirect following is disabled.
- Environment proxy configuration is not trusted by the HTTP client.
- The worker uses bounded request timeouts and response-body handling.
- Destination validation is defense in depth, not a substitute for network
  egress restrictions.

Verification:
The webhook worker test suite includes unsafe destination, DNS failure,
mixed-address, and no-request-on-invalid-destination tests.

Residual risk:
DNS rebinding and differences between validation-time and connection-time
resolution remain possible. Application checks alone do not prove that
production outbound traffic cannot reach internal services.

Required deployment control:
Isolate the worker from internal networks and enforce outbound network rules
that block loopback, private, link-local, and cloud metadata destinations
for IPv4 and IPv6. Verify the actual hosting environment and its enforcement.

### T4. Stale webhook worker and competing claims

Threat:
A slow or crashed worker loses its lease while another worker claims the
same delivery. The stale worker might otherwise send a request or overwrite
the newer worker's result.

Controls:
- Claims use row locking with SKIP LOCKED and per-claim tokens.
- Lease renewal and outcome persistence use conditional checks.
- A lease is confirmed after destination validation and before HTTP setup.
- A lost lease prevents the worker from initiating the HTTP request at that
  confirmation point.
- Database failures are propagated or handled so recovery can occur after
  lease expiry.

Verification:
Regression tests cover stale workers, unique claim tokens, lease renewal,
lease loss, and database failures.

Residual risk:
A lease can still be lost after the final confirmation and while a network
request is already in progress. A lease cannot guarantee exactly-once
delivery to an external receiver.

### T5. Duplicate webhook delivery

Threat:
A receiver processes a webhook more than once after retries, worker crashes,
timeouts, or uncertain network outcomes.

Controls:
- Delivery attempts and outcomes are tracked.
- Retry behavior uses bounded backoff and attempt limits.
- Redirects, request timeouts, and response-body processing are bounded.

Residual risk:
Webhook delivery is at-least-once, not exactly-once. Receivers should use a
stable event or delivery identifier for idempotent processing where duplicate
effects would be harmful.

### T6. Database or worker failure

Threat:
A transaction fails, a worker exits unexpectedly, or delivery processing
cannot persist its outcome.

Controls:
- Database commit failures are tested in webhook claim and outcome paths.
- Unexpected delivery errors are logged and do not prevent the worker loop
  from attempting subsequent deliveries.
- Lease expiry provides a recovery path for abandoned claims.
- The worker is intended to run as a separately supervised process.

Verification:
Confirm backend tests and operational deployment configuration before release.

Residual risk:
Recovery depends on database availability, correct lease handling, worker
supervision, and operational monitoring.

### T7. Sensitive information exposure

Threat:
Tokens, API keys, webhook payloads, or database credentials are exposed
through logs, responses, browser storage, or configuration.

Controls:
- Production configuration must use appropriate secret management.
- Logs should avoid credentials, tokens, and unnecessary sensitive payloads.
- Database access should be restricted.
- The frontend's token-storage approach must be reviewed for its XSS
  implications.

Residual risk:
Browser-accessible token storage can expose tokens if malicious script
executes in the application's origin. Review the current frontend
implementation and its content-security and XSS protections.

### T8. Denial of service and resource exhaustion

Threat:
High request volume, repeated failed deliveries, or oversized responses
consume application, worker, or database resources.

Controls:
- Webhook requests have timeouts and response-size limits.
- Delivery attempts and retry delays are bounded.
- Existing application guardrails and rate controls should be reviewed
  against the relevant API entry points.

Residual risk:
Application-level limits do not replace infrastructure-level rate limiting,
resource limits, queue monitoring, and capacity planning.

## 6. Operational Requirements

Before production deployment:

- Enforce outbound network restrictions for the webhook worker.
- Run the worker under process supervision with restart and failure alerts.
- Restrict database network access and database privileges.
- Store secrets outside source control and rotate exposed credentials.
- Monitor worker failures, delivery retries, exhausted attempts, and
  readiness failures.
- Keep `/health` as a liveness signal and `/ready` as a database-readiness
  signal; neither endpoint proves overall security.
- Verify HTTPS at the public entry point and the deployment's actual TLS setup.
- Define retention and access controls for security events and logs.
- Verify dependency updates and security-relevant configuration before release.

## 7. Verification Status

The Phase 26 development checkpoint recorded:

- Webhook lease-confirmation hardening committed as `511a547`.
- Focused webhook worker tests: 37 passed.
- Backend suite: 264 passed, with 4 warnings.
- `git diff --check` passed before that commit.
- The commit was pushed to `origin/main`.

These results describe the recorded checkpoint; they do not establish that
the current working environment has been re-tested after this document is added.

Not established by these results alone:

- Production outbound network isolation is enforced.
- DNS rebinding is impossible.
- Real PostgreSQL multi-worker concurrency has been exhaustively tested.
- External webhook receivers are idempotent.
- A complete penetration test has been performed.

## 8. Residual Risk and Sign-off

The highest-priority deployment risk is outbound network access from the
webhook worker. It must be addressed with actual network-level restrictions,
not merely application validation or documentation.

Other residual risks include duplicate external delivery, compromised valid
credentials, frontend XSS exposure, and failures in deployment monitoring.

Phase 26 should be considered complete only after the threat-model review,
relevant regression tests, final diff review, and the project's required
verification checks have passed. Deployment-only controls must be explicitly
recorded as verified or outstanding; they must not be assumed to exist.
