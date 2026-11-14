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

| Member | Role | Branch |
|---|---|---|
| M1 | Coordination, Science Lead, Slides and Demo Video | `feature/member1-science-pitch` |
| M2 | Data Science and Analytics Engine | `feature/member2-analytics` |
| M3 | Frontend and UX | `feature/member3-frontend` |
| M4 | Environment and Radiation | `feature/member4-environment` |
| M5 | Cognitive and Daily Check-In | `feature/member5-checkin` |
| M6 | Backend, Integration, QA and Deployment (integrator) | `feature/member6-integration` |

See [CONTRIBUTING.md](CONTRIBUTING.md) for the branch and PR workflow.

## Ground rules

1. **Provenance on every value.** Each value carries one of these badges: `nasa_measured`, `analog_measured`,
   `external_earth`, `simulated` or `manually_entered`. Never label simulated data as NASA data.
2. **Never mix sources.** Do not join crew, rodent-habitat, rover or Earth data on timestamp.
3. **No invented medical claims.** No diagnoses, no probabilities and no validated fitness score.
4. **Radiation honesty.** An instrument's dose rate is not a person's effective dose and not a cancer risk.
5. **Cite everything.** This includes NASA and CSA pages, datasets, tools, AI assistance and code.

## Setup

_TODO (M6):_ add the one-command start, test commands, live URL and the threshold rationale here.
