# AI assistance and third-party code citations

> Owner: Member 6 (Backend, Integration, QA & Deployment) maintains this file; every member adds their own rows.
> Honest disclosure matters more than a short list. If an AI tool helped, say what it did and how a person checked it.

## AI assistance log

| Area | Tool | What it did | How it was checked by a person | Checked by |
|---|---|---|---|---|
| Member 6: backend API, SQLite persistence, Pydantic contracts, JSON schemas, snapshot exporter (`backend/app/{api,contracts,storage}/`, `backend/app/services.py`, `backend/scripts/export_static_snapshot.py`, `shared/schemas/`) | Claude (Anthropic) | Drafted the code and its tests from the task plan and the existing module interfaces | 146 automated backend tests including integration, provenance, no-cross-join and snapshot-equals-API; run in CI | _name_ |
| Member 6: service worker, offline badge, API client with snapshot fallback, IndexedDB mirror, build plugin (`frontend/src/{sw,services,types}/`, `frontend/vite.config.ts`) | Claude (Anthropic) | Drafted the code and its tests | 75 unit tests; Playwright test with the network disabled; run against the live URL after deploy | _name_ |
| Member 6: CI, deploy workflows, docs (`.github/workflows/`, `docs/{deployment,offline-qa-checklist,data-contract,thresholds,licensing-notes}.md`, `submission/`) | Claude (Anthropic) | Drafted the text and workflow files | Thresholds page is test-checked against the code; workflows run on every PR | _name_ |
| Member 1: _fill in_ | | | | |
| Member 2: _fill in_ | | | | |
| Member 3: _fill in_ | | | | |
| Member 4: _fill in_ | | | | |
| Member 5: _fill in_ | | | | |

"Checked by" must be a real team member who read the output and ran it. Replace `_name_` only when that is true.

## What AI did not do

- It did not decide the health thresholds or what counts as a health-relevant indicator. Those come from Member 2's method note and Member 1's reviewed science files.
- It did not make any medical claim, and none is made in the app.
- It was not given real astronaut or personal data. All crew data in this project is simulated.

## Third-party code and data

| Item | Used for | License | Where cited |
|---|---|---|---|
| Open-source libraries | Frontend, backend, tests | MIT, BSD-3-Clause, Apache-2.0, OFL-1.1 | [licensing-notes.md](licensing-notes.md), section 4 |
| NASA OSDR EDA sample (D01), RadLab sample (D02) | Environment context card | NASA terms, **verify** | [licensing-notes.md](licensing-notes.md), sections 1-2 |
| Robust statistics (median, MAD, 1.4826 factor) | Baseline method | Standard textbook method | [methods-note.md](methods-note.md), [thresholds.md](thresholds.md) |
