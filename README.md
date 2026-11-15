# Crew Vitals

NASA Space Apps Challenge 2026: *Create Health Monitoring Software for Astronauts on Space Missions*.

Crew Vitals is an offline-first tool that helps astronauts check their own readiness. It compares
each crew member's daily check-in to their own baseline, flags drift with a plain-language "why",
and shows real NASA-measured environment or radiation data in a separate panel for context.

> **Decision support, not a diagnosis.** Crew Vitals is not a medical device. It does not diagnose
> or predict clinical conditions. Its thresholds are documented demo rules.

## Repository layout

```
.
├── .github/          CI/CD workflows, PR template, CODEOWNERS             (M6)
├── docs/             Source registry, decision log, methods, audits, QA   (all; see file owners)
├── shared/           Single source of truth shared by backend + frontend
│   ├── schemas/      JSON Schemas: envelope, API response, check-in, env  (M6, M5)
│   ├── knowledge/    knowledge.json, source-registry.json                 (M1)
│   └── mocks/        Mock JSON for early integration                      (M6)
├── data/             Small, licensed dataset snapshots
│   ├── simulated/    X01 simulated crew traces                            (M2)
│   ├── nasa/         D01 EDA, D02 RadLab (M4) · D03 NLSP, D06 OSD-575 (M2)
│   ├── external/     E01/E02, parser tests only                           (M2, M6)
│   └── fallback/     Cited static chart if NASA export fails              (M4)
├── backend/          Python FastAPI
│   ├── app/
│   │   ├── api/          HTTP routes                                      (M6)
│   │   ├── contracts/    Pydantic models mirroring shared/schemas         (M6)
│   │   ├── storage/      Local persistence                                (M6)
│   │   ├── analytics/    Baseline, robust z-score, persistence, fallbacks (M2)
│   │   ├── adapters/     Simulated crew, NLSP, OSD-575, signal parsers    (M2)
│   │   ├── environment/  get_environment_series(), EDA / RadLab adapters  (M4)
│   │   └── checkin/      Check-in + reaction-time models and bounds       (M5)
│   ├── scripts/      Seed data, fetch NASA data, export static snapshot
│   └── tests/        unit/ (per module owner) · integration/ (M6)
├── frontend/         React + Vite + TypeScript
│   ├── public/data/  Static API snapshot so the deployed app works offline (M6)
│   └── src/
│       ├── components/   Layout, body map, status chips, charts,
│       │                 evidence drawer, environment selector           (M3)
│       ├── features/
│       │   ├── dashboard/            (M3)
│       │   ├── checkin/ reaction-time/ reminders/
│       │   │   gamification/ camera/ (M5)
│       │   └── environment-context/  (M4)
│       ├── services/     API client, local storage                       (M6)
│       ├── sw/           Service worker                                  (M6)
│       └── types/        TS contract types                               (M6)
├── presentation/     Pitch script, slides, demo video, screenshots       (M1)
└── submission/       Final checklist and portal links                    (M6)
```

Each placeholder file says which member owns it. Ownership is also in [.github/CODEOWNERS](.github/CODEOWNERS).

## Team and branches

| Member | Name | Role | Branch |
|---|---|---|---|
| M1 | Amna | Coordination, Science Lead, Slides and Demo Video | `feature/member1-science-pitch` |
| M2 | Sachin | Data Science and Analytics Engine | `feature/member2-analytics` |
| M3 | Husnain | Frontend and UX | `feature/member3-frontend` |
| M4 | Bilal | Environment and Radiation | `integration/member4-environment` |
| M5 | Linta | Cognitive and Daily Check-In | `feature/member5-checkin` |
| M6 | Hammad | Backend, Integration, QA and Deployment (integrator) | `feature/member6-integration` |

See [CONTRIBUTING.md](CONTRIBUTING.md) for the branch and PR workflow.

## Ground rules

1. **Provenance on every value.** Each value carries one of these badges: `nasa_measured`, `analog_measured`,
   `external_earth`, `simulated` or `manually_entered`. Never label simulated data as NASA data.
2. **Never mix sources.** Do not join crew, rodent-habitat, rover or Earth data on timestamp.
3. **No invented medical claims.** No diagnoses, no probabilities and no validated fitness score.
4. **Radiation honesty.** An instrument's dose rate is not a person's effective dose and not a cancer risk.
5. **Cite everything.** This includes NASA and CSA pages, datasets, tools, AI assistance and code.

## Setup

**Live app:** https://lintahabib2-hash.github.io/nasa-space/ (works offline after the first visit; header badge shows **Offline ready**).
It goes live once a repo admin sets **Settings → Pages → Source: GitHub Actions**; until then the Deploy workflow
tests and builds but does not publish. For the full app (frontend on Vercel, API on Render, both free; `vercel.json` and
`render.yaml` are ready), follow [docs/deployment.md](docs/deployment.md#full-deployment-vercel--render-free).

### Run it

Needs Node 20+ (frontend) and Python 3.11+ (backend, optional).

```bash
# Frontend: one command to start. Uses the bundled simulated scenarios; no backend needed.
cd frontend && npm ci && npm run dev          # http://localhost:5173

# Backend API (optional): FastAPI + local SQLite
pip install -r backend/requirements.txt
uvicorn backend.app.main:app --port 8000      # interactive docs at http://127.0.0.1:8000/docs
```

### Test it

```bash
pip install -r backend/requirements-dev.txt && python -m pytest                    # 140+ backend tests
cd frontend && npm run verify                                                      # typecheck, unit tests, build, browser tests
```

`npm run verify` includes the **offline test**: it loads the production build, switches the network off, and checks two
contrasting scenarios, missing data, and a saved check-in. See [docs/offline-qa-checklist.md](docs/offline-qa-checklist.md).
Deployment, release steps and the live-URL check are in [docs/deployment.md](docs/deployment.md).

### Threshold rationale (demo rules, not clinical)

Each person is compared only with **their own** earlier readings: a robust z-score `(current - median) / (1.4826 x MAD)`,
flagged for **review** only when **3 consecutive daily readings** are beyond **|z| = 3.0** on the same side, using at least
**5** prior readings. Missing data gives `unknown`, too little history gives `insufficient_history`, and a flat history gives
`insufficient_scale`; the app never reports "healthy" because data is missing. These are illustrative rules, not clinically
calibrated and not NASA limits. Full table and reasons: [docs/thresholds.md](docs/thresholds.md). Data formats and API
routes: [docs/data-contract.md](docs/data-contract.md).

### What is simulated

All crew data in this repository is **simulated** and labelled so everywhere it appears. The environment card shows
historical NASA instrument data (never a person's dose) with its citation and limitations.

Submission links and the final checklist: [submission/links.md](submission/links.md), [submission/checklist.md](submission/checklist.md).
