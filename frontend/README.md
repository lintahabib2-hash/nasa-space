# frontend/ (React + Vite + TypeScript)

| Folder | Owner |
|---|---|
| `src/components/` (layout, body-map, status, charts, evidence-drawer, environment-selector) | M3 |
| `src/features/dashboard/` | M3 |
| `src/features/checkin/`, `reaction-time/`, `reminders/`, `gamification/`, `camera/` | M5 |
| `src/features/environment-context/` | M4 |
| `src/services/`, `src/sw/`, `src/types/`, `public/data/` | M6 |
| `tests/unit/` | each component owner |
| `tests/e2e/` | M6 |

Rule: the UI only uses JSON from the API or snapshot. Do not put medical thresholds or rules in components.

_TODO (M6): scaffold with Vite (`npm create vite@latest`, react-ts), then add the run, test and build commands._
