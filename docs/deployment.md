# Deployment notes and live URL verification

> Owner: Member 6 (Backend, Integration, QA & Deployment)

## What is deployed

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
- **No live backend on Pages.** `VITE_API_BASE` is unset in production, so the app reads the snapshot. The API is for local development and for the integration tests.
- **Other hosts:** Netlify/Vercel also work. Build command `cd frontend && npm ci && npm run build`, publish directory `frontend/dist`.
- **Vercel:** `vercel.json` at the repo root already sets install, build and output, and keeps `sw.js` uncached. Import the repo in Vercel with the **Root Directory left at the repository root** (the build reads `shared/knowledge/`), and deploy. No other settings are needed.
- **Until Pages is enabled**, the Deploy workflow still runs every test and the build, then finishes green with a warning ("GitHub Pages is not enabled") instead of failing. Enable Pages and re-run it to publish.
