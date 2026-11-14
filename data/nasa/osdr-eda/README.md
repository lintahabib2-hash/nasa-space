# D01 NASA OSDR Environmental Data Application (EDA): RR-1

Owner: Member 4 (Environment & Radiation).

- Source: https://visualization.osdr.nasa.gov/eda/ (accessed 14 Nov 2026; version not displayed on the site)
- Attribution: Data and visualizations are courtesy of the Environmental Data Application (EDA)
  (https://visualization.osdr.nasa.gov/eda/).
- Mission: RR-1. Rodent-habitat environment, **not** astronaut cabin air or any crew member's record.

## What is committed

Only the 300-point display sample the app uses:
`frontend/src/features/environment-context/fixtures/environment.sample.json`.
The full exports are not committed (re-use terms; repository policy: small snapshots only).

## Rebuilding the sample

1. From the EDA site, export the RR-1 tables and save the telemetry table as
   `data/nasa/osdr-eda/raw/RR-1_EDA_Telemetry_table.csv` (the `raw/` folder is git-ignored).
2. From the repository root: `python -m backend.app.environment.osdr_eda`

Audit notes: [docs/environment-audit.md](../../../docs/environment-audit.md).
