# backend/ (Python FastAPI)

| Package | Owner | Responsibility |
|---|---|---|
| `app/api/`, `app/contracts/`, `app/storage/`, `app/main.py` | M6 | Routes, Pydantic contracts, local persistence |
| `app/analytics/`, `app/adapters/` | M2 | `get_observations()`, `get_baseline_result()`, median/MAD, persistence, safe fallbacks |
| `app/environment/` | M4 | `get_environment_series()`, EDA / RadLab adapters |
| `app/checkin/` | M5 | Check-in and reaction-time models and input bounds |
| `scripts/` | M2 / M4 / M6 | Seed simulated crew, fetch NASA data, export a static snapshot for offline deploy |
| `tests/unit/` | each module owner | QA data rules (Project Guide §10) |
| `tests/integration/` | M6 | End-to-end, provenance, no-cross-join |

**Offline and static deploy:** `scripts/export_static_snapshot.py` writes the API outputs to
`frontend/public/data/`. The deployed static site then runs fully offline without a live API.

_TODO (M6): add venv setup, run and test commands._
