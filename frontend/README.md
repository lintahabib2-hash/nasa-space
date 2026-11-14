# frontend/ (React + Vite + TypeScript)

The crew dashboard for Crew Vitals (Member 3, Frontend & UX).

> Decision support, not a diagnosis. The UI contains **no medical rules**. Every status, reason,
> baseline and reference band comes from the analytics output (Member 2). The UI only maps the
> `status` string to a colour, a symbol and a label (`src/features/dashboard/statusDisplay.ts`).

## Run

```bash
cd frontend
npm install
npm run dev          # http://localhost:5173 (simulated scenarios)
npm test             # unit and component tests (Vitest + Testing Library)
npm run typecheck
npm run build        # static build in dist/, deployable to any static host
```

Deep links for the demo video: `?crew=crew_02&env=mars` (crew: `crew_01`, `crew_02`, `crew_03`;
env: `station`, `spacecraft`, `lunar`, `mars`).

## Data modes

| `VITE_DATA_MODE` | Source | Notes |
|---|---|---|
| `fixtures` (default) | `src/features/dashboard/fixtures/*.json`, bundled | Works offline and on a static host. All values are **simulated** (X01) |
| `api` | Member 2's `member2/offline_api.py` on `127.0.0.1:8766`, proxied as `/api` | Today the API only provides self-reported **sleep duration** |

```bash
# api mode (Member 2's server must be running)
VITE_DATA_MODE=api VITE_SUBJECT_ID=crew_01 npm run dev
```

### Simulated fixtures

`scripts/make_fixtures.py` generates three pseudonymous scenarios (30 days, 10 indicators). They are
scored by Member 2's real `get_baseline_result()`, so the UI shows the engine's own output:

| Subject | Scenario | What it demonstrates |
|---|---|---|
| `crew_01` | stable | One noisy heart-rate reading (\|z\| ≥ 3) does **not** become a flag |
| `crew_02` | gradual_drift | Sleep, resting HR and exercise trigger `review` after 3 consecutive deviations |
| `crew_03` | missing_data | Missing latest reading → `unknown`, sparse glucose → `insufficient_history`, flat 1–5 scales → `insufficient_scale` |

```bash
git show origin/feature/member2-analytics:member2/analytics.py > /tmp/analytics.py
python scripts/make_fixtures.py --analytics /tmp/analytics.py
```

## What is where

| Path | Purpose |
|---|---|
| `src/components/layout/` | App shell, the always-visible "Decision support, not a diagnosis" banner |
| `src/components/body-map/` | Interactive SVG body map (keyboard operable) and the region detail panel |
| `src/components/status/` | Status chips: colour + distinct shape + text (✓ circle, ! triangle, ! octagon, ? dashed) |
| `src/components/charts/` | Trend chart with shaded personal reference band, plus an accessible data table |
| `src/components/evidence-drawer/` | Evidence drawer (sources, provenance, data quality, missing data, limitations) and provenance badge |
| `src/components/environment-selector/` | ISS / Spacecraft / Lunar / Mars selector and comms-delay banner |
| `src/features/dashboard/` | Page, data source, types, status display mapping, fixtures, draft knowledge cards |

## Accessibility checklist

- Status is never shown by colour alone: each tier has its own icon shape and a text label.
- Body map regions are `role="button"`, reachable with Tab and activated with Enter or Space.
- The evidence drawer is a modal dialog. Focus moves to Close, Tab is trapped, Escape closes it and focus returns to the opener.
- Selectors are native radio groups. The comms banner is an `aria-live` region.
- Every chart has a text summary (`aria-label`) and a "Show data table" view.
- Light and dark themes. Respects `prefers-reduced-motion` and forced-colors mode. Layout tested at 390 px width.

## Handoffs

**Needed from Member 2 (analytics API):**
- `reference_band: { low, high, basis }` on each result, for the shaded chart band. The fixture generator fills it in for now.
- An escalation status (e.g. `escalate`) for the red "contact flight surgeon" tier. The UI already supports it.
- A missing-latest-reading branch that returns `status: "unknown"` and `quality_state: "missing"` instead of an error.
- Measurements beyond `sleep_duration` in the live API, and a time-series endpoint per measurement.

**Needed from Member 1:** the reviewed `shared/knowledge/knowledge.json`. Replace the import in
`src/features/dashboard/dataSource.ts` (currently `fixtures/knowledge.draft.json`). Also verify the
comms-delay figures and add the C04/C05 URLs.

**For Member 4:** mount `EnvironmentContextCard` in the reserved "Historical NASA environment context"
slot at the bottom of `DashboardPage.tsx`. It is already styled to stay visually separate from crew data.

**For Member 6:** the Vite, TypeScript and Vitest setup is here. Service worker (`src/sw/`),
`src/services/apiClient.ts` and `src/types/contracts.ts` are still yours. Types to move into the shared
contract are in `src/features/dashboard/types.ts`.
