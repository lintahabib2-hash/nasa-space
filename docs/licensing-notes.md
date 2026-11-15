# Dataset licensing and attribution notes

> Owner: Member 6 (Backend, Integration, QA & Deployment). Source facts come from Member 1's
> [source-registry.md](source-registry.md) and Member 4's [environment-audit.md](environment-audit.md).
> **This is a project record, not legal advice.** Items marked "verify" must be confirmed against the provider's current terms before the final submission.

## 1. What data is actually in this repository

| Path | What it is | Origin | Redistribution status |
|---|---|---|---|
| `data/simulated/X01_crew_scenarios.json` | Team-made engineering scenarios (stable, downward drift, missing observation) | Created by the team | Ours. Labelled `simulated` / `not_real_astronaut_data`. |
| `frontend/src/features/dashboard/fixtures/`, `frontend/public/data/baselines.json`, `shared/mocks/` | Simulated crew bundles and API mocks generated from the scenarios above | Created by the team | Ours. Simulated. |
| `data/nasa/osdr-eda/RR-1_EDA_*.csv` | **Small approved sample** of NASA OSDR Environmental Data Application (EDA) tables (source D01) | NASA OSDR | See section 2. Only this small sample is stored, per the EDA re-use terms noted in the audit. |
| `data/nasa/radlab/first_100_rows.csv` | First 100 rows of a RadLab (D02) export | NASA OSDR RadLab | Small sample. **Verify** RadLab export terms before keeping it in the public repo. |
| `frontend/public/data/environment.json` | Derived from the EDA sample by `get_environment_series()` | NASA OSDR EDA (D01) | Derived from section 2 data; carries its citation. |

Nothing else is redistributed. Larger sources listed in the registry (NLSP bed-rest D03, OSD-575 D06, etc.) are **linked, not copied**
(`data/README.md`: "Commit only small, licensed snapshots"). The folders `data/nasa/nlsp-bedrest/` and `data/nasa/osd-575/` hold no data files.

## 2. Required attribution for NASA OSDR EDA data (D01)

The attribution text recorded in the audit, and carried by every environment response and snapshot (`citation` field):

> Data and visualizations are courtesy of the Environmental Data Application (EDA) (https://visualization.osdr.nasa.gov/eda/). Version: not displayed on the site (accessed 14 Nov 2026).

The app shows this text on the environment context card, together with the limitation that it is **historical instrument data
and not a person's dose**. Tests (`backend/tests/integration/test_provenance.py`) fail if the citation or limitations disappear.

**Verify:** the EDA re-use terms (the audit notes that "dataset reuse and licensing conditions must be checked before making reuse claims").
Until confirmed, make no claim that the data is public domain or openly licensed, and keep only the approved small sample in git.

## 3. Rules we follow

1. Never label simulated data as NASA data (enforced in the data contract and tests).
2. Cite the source ID (C01-C05, D01, D02, D03, D06, X01) on every value, chart and slide that uses it.
3. Do not commit raw datasets over the small approved samples; link them in the source registry instead.
4. Do not publish anything that identifies a real person. All crew data here is simulated.
5. NASA names and logos: used only to identify the challenge and the data source, with no implied endorsement.
   **Verify** NASA's media usage guidelines for the logo file in `frontend/public/images/` before the final submission.

## 4. Third-party software (all permissive; versions pinned in the lock files)

| Component | Used for | License |
|---|---|---|
| React, Vite, Recharts, Vitest, Testing Library | Frontend | MIT |
| Playwright Test, fake-indexeddb | Browser and storage tests | Apache-2.0 |
| FastAPI, Pydantic, jsonschema, pytest | Backend API, contracts, tests | MIT |
| Uvicorn, httpx, pandas | Server, test client, data parsing | BSD-3-Clause |
| Fontsource: Chakra Petch, Atkinson Hyperlegible, IBM Plex Mono | Bundled fonts (so the app renders offline) | SIL Open Font License 1.1 |

Licenses were read from the installed packages on 2026-11-15. The Open Font License requires keeping the license with redistributed font files; the fonts ship inside `dist/assets/` from the Fontsource packages unmodified.

## 5. Repository license

**Decision needed (M1/M6):** the repository has no `LICENSE` file yet. Add one (for example MIT for our code) before submission, and state
that the NASA data samples remain under their original terms (section 2).
