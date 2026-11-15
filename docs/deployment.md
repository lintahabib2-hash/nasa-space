# Deployment notes and live URL verification

> Owner: Member 6 (Backend, Integration, QA & Deployment)

## What is deployed

Two ways, both free:

- **Frontend only on GitHub Pages** (default, below). No server; the app reads the bundled snapshot.
- **Full app: frontend on Vercel + backend API on Render** (see [Full deployment](#full-deployment-vercel--render-free)).
  The app reads live data from the API, falls back to the snapshot when it is unreachable, and sends saved check-ins to it.

### GitHub Pages (frontend only)

The **frontend only**, as static files (`frontend/dist`) on **GitHub Pages**. There is no server to keep running: the
dashboard uses its bundled simulated scenarios, and `frontend/public/data/*.json` is a snapshot of what the backend API
returns, exported by `backend/scripts/export_static_snapshot.py`. A service worker (`dist/sw.js`, generated at build time)
caches every file so the app opens with no connection after the first visit.

Why GitHub Pages: free, HTTPS (browsers only allow service workers on HTTPS), lives next to the code, and deploys from
the same workflow that runs the tests.

**Live URL:** `https://lintahabib2-hash.github.io/nasa-space/`  (confirm after the first deploy, then record it in `submission/links.md`)

## One-time setup (repo admin)

1. Repo **Settings -> Pages -> Build and deployment -> Source: GitHub Actions**.
2. Repo **Settings -> Branches -> Add rule for `main`**: require a pull request, require the status checks **backend** and
   **frontend** (from `ci.yml`), no force pushes.
3. Fill `.github/CODEOWNERS` with real usernames (replace each `@MEMBERn`, uncomment the lines).

## Full deployment: Vercel + Render (free)

The backend cannot run on Vercel: Vercel runs Python as short-lived serverless functions with a read-only disk
(only `/tmp`, wiped often and not shared between instances), so the SQLite check-in store would lose data. The API
runs on Render instead; the frontend stays on Vercel. Deploy the backend first, because each side needs the other's URL.

Who can do it: the repo owner connects the repo to Render and Vercel once (GitHub only lets the owner of a personal repo
install those apps) and invites teammates to the Render project and the Vercel team. A collaborator can also deploy from
a fork, or from the public repo URL (Render "Public Git Repository", `vercel` CLI), without auto-deploy.

### 1. Backend on Render

1. render.com -> sign up with GitHub -> **New -> Blueprint** -> pick this repo. `render.yaml` fills in everything.
   Without the Blueprint: **New -> Web Service** with these settings:

   | Field | Value |
   |---|---|
   | Root Directory | empty (repo root; the code imports `backend.app`) |
   | Runtime / Plan | Python 3 / Free |
   | Build Command | `pip install -r backend/requirements.txt` |
   | Start Command | `uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT` |
   | Health Check Path | `/api/health` |
   | Env vars | `PYTHON_VERSION=3.11.9`, `CREW_VITALS_SEED=1`, `CREW_VITALS_CORS=http://localhost:5173` (replaced in step 3) |

2. When it is live, check `https://<name>.onrender.com/api/health`, `/docs` and `/api/baseline/all?subject_id=X01_downward_drift`.

### 2. Frontend on Vercel

1. vercel.com -> sign up (Hobby) with GitHub -> **Add New -> Project** -> import this repo
   (if it is not listed: **Adjust GitHub App Permissions** and add it).
2. Leave Framework (Other), **Root Directory `./`** and the build settings as they are; `vercel.json` sets them.
   The build reads `shared/knowledge/`, so do not set the root to `frontend`.
3. **Environment Variables:** `VITE_API_BASE` = `https://<name>.onrender.com` (no trailing `/`). -> **Deploy**.

### 3. Connect them (CORS)

Render -> service -> **Environment**: `CREW_VITALS_CORS` = the Vercel URL, e.g. `https://crew-vitals.vercel.app`
(comma-separated for several origins). Save; Render redeploys.

### 4. Check it

- The Vercel site loads live data (not "saved snapshot").
- Saving a check-in shows **"Saved on this device and sent to the crew API."**; it is listed at `<render-url>/api/checkins`.
- DevTools -> Network -> Offline -> reload: the app still works, and check-ins say they will be sent later.

### Free-plan limits

- **Render free sleeps after about 15 minutes idle.** The next request wakes it (30-60 s). Meanwhile the app shows the
  snapshot (5 s API timeout) and keeps check-ins in its outbox; they are sent on the next save or the next visit to the
  check-in page. To keep it awake, point a free monitor (UptimeRobot, cron-job.org) at `/api/health` every 10 minutes
  (one service running all month fits Render's 750 free hours). Before a demo, open `/api/health` once.
- **Render free has no persistent disk.** Saved check-ins are lost on restart or redeploy; the simulated X01 scenarios
  reload on start. For durable storage: paid instance + Render Disk at `/var/data`, `CREW_VITALS_DB=/var/data/crew_vitals.sqlite3`.
- **`VITE_API_BASE` is baked in at build time.** After changing it in Vercel, redeploy (Deployments -> ... -> Redeploy).
- Pushes to `main` redeploy both automatically when the repo itself is connected (not from a fork or a public URL).

## How a release happens

1. A member's PR is reviewed and `CI` is green (`backend` + `frontend` jobs).
2. M6 merges into `main`.
3. `Deploy` runs: backend tests -> snapshot freshness check -> type check -> unit tests -> build -> browser tests -> publish.
4. `verify-live` then runs the offline and scenario browser tests **against the live URL**. If it is red, the deployed site is broken: fix forward or revert the merge.

## Run it locally

```bash
# Frontend only (works offline, uses bundled simulated data)
cd frontend && npm ci && npm run dev            # http://localhost:5173

# Backend API (optional): live API + SQLite persistence
pip install -r backend/requirements.txt
uvicorn backend.app.main:app --port 8000        # docs at http://127.0.0.1:8000/docs
# then point the frontend at it:  VITE_API_BASE=http://127.0.0.1:8000 npm run dev

# Production build and the offline test (what CI runs)
cd frontend && npm run build && npm run test:e2e
```

When the data or the analytics change, regenerate the snapshot and commit it (CI fails if it is stale):

```bash
python backend/scripts/export_static_snapshot.py
```

## Verify the live deployment (do this before submitting)

Automated, from any machine with Node:

```bash
cd frontend && npm ci && npx playwright install chromium
PLAYWRIGHT_BASE_URL=https://lintahabib2-hash.github.io/nasa-space/ npm run test:e2e
```

Manual: follow [offline-qa-checklist.md](offline-qa-checklist.md) in a fresh/incognito window and on a phone.

## Verification record (fill in)

| Date (UTC) | Commit | Live URL tested | Automated live test | Manual offline test (desktop) | Manual offline test (phone) | By |
|---|---|---|---|---|---|---|
| | | | | | | |

## Known behaviours and limits

- **First visit must be online** once so the worker can cache the app. The header badge says **Offline ready** when it is done.
- **Updates arrive on the next load.** Each build gets a new cache name (hash of all shipped files); the new worker installs, takes over, and deletes the old cache. Hard-reload once after a deploy to see it immediately.
- **Sub-path hosting works.** All asset URLs and the worker scope are relative, so `/<repo>/` is fine. (Tested by serving the build from `/nasa-space/`.)
- **Check-ins stay on the device** (localStorage plus an IndexedDB mirror). Clearing site data in the browser deletes them; use the History export.
- **Private/incognito windows** may discard storage when closed. The app still works; saved check-ins may not persist.
- **No live backend on Pages.** `VITE_API_BASE` is unset there, so the app reads the snapshot. For a live API use the Vercel + Render setup above.
- **Other hosts:** Netlify/Vercel also work. Build command `cd frontend && npm ci && npm run build`, publish directory `frontend/dist`.
- **Vercel:** `vercel.json` at the repo root already sets install, build and output, and keeps `sw.js` uncached. Import the repo with the **Root Directory left at the repository root** (the build reads `shared/knowledge/`). Set `VITE_API_BASE` only if a backend is deployed (see above).
- **Until Pages is enabled**, the Deploy workflow still runs every test and the build, then finishes green with a warning ("GitHub Pages is not enabled") instead of failing. Enable Pages and re-run it to publish.
