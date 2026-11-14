# Contributing to Crew Vitals

## Branch workflow

`main` is protected. Only the integrator (M6) merges into it, and only through a pull request.

1. Start from your member branch:
   ```bash
   git fetch origin
   git checkout feature/memberN-<area>
   git pull --rebase origin main   # pick up other members' merged work often
   ```
2. Keep to the folders you own. CODEOWNERS and the header of each placeholder file say who owns what.
3. Open a PR into `main` early. Small PRs that use mock JSON are better than one large PR at the end.
4. If you need a change in a folder someone else owns, ask the owner or open a small PR they can review.

| Branch | Owner | Main folders |
|---|---|---|
| `feature/member1-science-pitch` | M1 | `docs/` (science files), `shared/knowledge/`, `presentation/` |
| `feature/member2-analytics` | M2 | `backend/app/analytics/`, `backend/app/adapters/`, `data/simulated/` |
| `feature/member3-frontend` | M3 | `frontend/src/components/`, `frontend/src/features/dashboard/` |
| `feature/member4-environment` | M4 | `backend/app/environment/`, `data/nasa/osdr-eda/`, `data/nasa/radlab/`, `frontend/src/features/environment-context/` |
| `feature/member5-checkin` | M5 | `backend/app/checkin/`, `frontend/src/features/{checkin,reaction-time,reminders,gamification,camera}/` |
| `feature/member6-integration` | M6 | `backend/app/{api,contracts,storage}/`, `frontend/src/{services,sw,types}/`, `shared/schemas/`, `.github/` |

If you need a short-lived sub-branch, name it `feature/memberN-<topic>` (for example `feature/member3-evidence-drawer`).

## Shared contracts

- `shared/schemas/` is the single source of truth for the data envelope, the common API response,
  the check-in object and the environment series.
- Backend Pydantic models (`backend/app/contracts/`) and frontend TS types (`frontend/src/types/`) mirror these schemas.
- Changing a schema needs a PR reviewed by M6 and by every member who uses that schema.

## Every PR must include

- The source ID(s) it uses (C01–C05, D01, D02, D03, D06, X01, ...).
- The command that runs and tests it.
- Provenance labels kept on all outputs.
- No restricted or identifiable data. Keep large datasets out of git and link to them instead.

## Commit messages

Use `type(scope): summary`. For example: `feat(analytics): add robust z-score`,
`docs(registry): add C04`, `test(checkin): bounds for heart rate`.
