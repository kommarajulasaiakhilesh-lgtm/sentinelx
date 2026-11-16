# SentinelX Monitoring (Prometheus + Grafana)

SentinelX exposes live platform metrics in Prometheus exposition format at
`GET /metrics` (no Docker required to run the stack — native binaries work).

## Metrics exposed

| Metric | Labels | Meaning |
|---|---|---|
| `sentinelx_agents` | `status` | Agents by status (active/suspended) |
| `sentinelx_security_events_total` | `decision` | Security events by enforcement decision |
| `sentinelx_open_alerts` | `severity` | Open/acknowledged alerts by severity |
| `sentinelx_incidents` | `status` | Incidents by status |
| `sentinelx_policies_total` | — | Total configured policies |

## Run it (native, no Docker)

1. Start the backend (exposes `/metrics`):
   ```bash
   cd backend
   PYTHONPATH=. .venv/Scripts/python.exe -m uvicorn app.main:app --port 8000
   ```
2. Start Prometheus pointed at this repo's scrape config:
   ```bash
   prometheus --config.file=monitoring/prometheus.yml
   ```
   Prometheus UI: http://localhost:9090 — try the query `sentinelx_agents`.
3. Start Grafana, add the Prometheus data source (http://localhost:9090), then
   **Dashboards → Import** and upload `monitoring/grafana-dashboard.json`.

In production, point `monitoring/prometheus.yml` at the deployed backend host
and restrict `/metrics` at the network layer (it is unauthenticated by
convention for in-cluster scraping).

## CLI

`scripts/sentinelx_cli.py` is a small operations/automation entry point:

```bash
cd backend
PYTHONPATH=. .venv/Scripts/python.exe scripts/sentinelx_cli.py stats
PYTHONPATH=. .venv/Scripts/python.exe scripts/sentinelx_cli.py battery 1
PYTHONPATH=. .venv/Scripts/python.exe scripts/sentinelx_cli.py sla
```
