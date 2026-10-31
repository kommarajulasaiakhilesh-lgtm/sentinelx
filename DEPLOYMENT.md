# SentinelX — Production Deployment

Topology: **Frontend → Vercel · Backend → Render · Database → Supabase (Postgres)**.

The frontend already auto-deploys to Vercel from `main`. This guide deploys
the FastAPI backend and connects the three together. The repo ships a Render
blueprint (`render.yaml`) so the backend is a guided, few-click deploy.

---

## 1. Database — Supabase

1. Create a project at https://supabase.com (free tier is fine).
2. Project → **Connect** → **Connection string** → **Session pooler**
   (port `5432`, host like `aws-0-<region>.pooler.supabase.com`).
   > Use the **pooler** host, not the direct `db.<ref>.supabase.co` host —
   > the direct host is IPv6-only and Render can't reach it on the free tier.
3. Copy the URI and substitute your DB password. It looks like:
   `postgresql://postgres.<ref>:<password>@aws-0-<region>.pooler.supabase.com:5432/postgres`
   Keep this secret — you'll paste it into Render as `DATABASE_URL`.

## 2. Backend — Render

1. Push is already done; `render.yaml` is at the repo root.
2. Render Dashboard → **New** → **Blueprint** → select
   `kommarajulasaiakhilesh-lgtm/sentinelx`. Render reads `render.yaml` and
   proposes the `sentinelx-api` web service.
3. Set the two secret env vars (marked `sync:false`):
   - `DATABASE_URL` → the Supabase pooler URI from step 1.
   - `CORS_ORIGINS` → your Vercel production URL
     (e.g. `https://sentinelx-<hash>.vercel.app`), comma-separated if several.
   `SECRET_KEY` is auto-generated; `SQL_ECHO=false` and `PYTHON_VERSION` are
   preset.
4. **Create**. On deploy, `preDeployCommand` runs `alembic upgrade head`
   against Supabase (creates all tables, including `audit_logs`), then the
   service starts with `uvicorn app.main:app --host 0.0.0.0 --port $PORT`.
5. Note the service URL, e.g. `https://sentinelx-api.onrender.com`.
   Verify: open `https://sentinelx-api.onrender.com/health` → `{"status":"healthy"}`.

### Optional — seed demo data in prod
To populate a portfolio demo (admin login + synthetic agents/events/alerts),
open the Render **Shell** for the service and run:

```bash
python scripts/dev_bootstrap.py
```

It is idempotent and seeds `admin` / `SentinelX!2026` plus synthetic data.
Change the admin password afterward (or edit the seed) before sharing widely.

## 3. Connect the frontend — Vercel

1. Vercel → the `sentinelx` project → **Settings** → **Environment Variables**.
2. Add `NEXT_PUBLIC_API_URL` = your Render URL
   (e.g. `https://sentinelx-api.onrender.com`) for the **Production** env.
3. **Redeploy** the frontend (Deployments → ⋯ → Redeploy) so the new env var
   is baked in.
4. Make sure the backend's `CORS_ORIGINS` (step 2.3) includes the exact Vercel
   production domain, or browser calls will be blocked by CORS.

## 4. Verify end-to-end

- `GET https://<render-url>/health` → healthy.
- Open the Vercel production site → sign in with the seeded admin → dashboards
  load real data from the Render backend.

---

## Notes & limitations

- **Free-tier spin-down**: Render free web services sleep after ~15 min idle;
  the first request after idle takes ~30–60s to wake. Supabase free projects
  also pause after a week of inactivity.
- **Webhook worker stays disabled** in production until the SSRF protections
  in the threat model are implemented and independently verified.
- **No secrets in the repo**: `DATABASE_URL`, `SECRET_KEY`, and `CORS_ORIGINS`
  live only in the Render/Vercel dashboards. `backend/.env` is gitignored.
- The migration chain is PostgreSQL-only (some migrations use `ALTER CONSTRAINT`).
  Local SQLite dev uses `create_all` instead — see `LOCAL_DEV.md`.
