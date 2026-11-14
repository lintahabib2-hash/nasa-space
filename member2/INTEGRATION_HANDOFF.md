# Crew Vitals — Member 2 offline integration handoff

## Scope

This additive patch gives the existing Member 2 scientific modules a working **localhost-only, internet-independent** demo. It uses two real historical NASA sources, but **does not pretend to possess live astronaut telemetry** or clinically validate review flags. Each source stays separate from other persons, experiments, and missions.

Existing branch scripts (`analytics.py`, `bedrest_adapter.py`, `bedrest_preview_export.py`, `retrospective_trends.py`) are not overwritten by this patch.

## Quick start (from repository root)

Requires Python 3.11+. **No external Python packages are needed for this local API**; the earlier NASA preprocessing scripts still need pandas.

First prepare actual research files using the existing Member 2 scripts (already done on the development laptop). Use local paths **outside** Git so that raw data are never accidentally redistributed.

```bash
cd ~/Projects/NASA_SpaceApps_Hackathon/nasa-space
python -m unittest discover -s member2/tests -v
python member2/offline_api.py \
  --db ../member2/reports/crew_checkins.sqlite3 \
  --bedrest-json ../member2/reports/bedrest_trends.json \
  --eda-csv ../member2/data/raw/RR-1_EDA_Telemetry_table.csv
```

Open http://127.0.0.1:8766 in a browser. Disconnect Wi-Fi, reload, enter **your own actual** check-in, and confirm it persists across restart. Do not expose the server to other machines or to the public internet. SQLite contains user-entered information and is NOT a secure multi-user medical database.

If a file does not exist locally, omit the matching `--bedrest-json` or `--eda-csv` flag. No example records are invented; the module responds that the dataset is unavailable.

## HTTP endpoints (localhost)

- `GET /api/health` — server status and which local reference files are available
- `GET /api/research/bedrest` — original source-labeled 207-row NASA analog trend JSON, loaded from `--bedrest-json`
- `GET /api/research/environment` — validated and downsampled historical NASA RR-1 EDA preview, loaded from `--eda-csv`; optional handoff to Member 4
- `POST /api/checkins` — validate and store a **real user-entered** local sleep duration
- `GET /api/checkins?subject_id=crew_01` — stored local check-ins for that identifier
- `GET /api/analytics/latest?subject_id=crew_01` — latest prior-only personalized median/MAD assessment with explicit quality status

Example POST (not a real astronaut measurement; **replace with your own actual sleep duration and current UTC timestamp**):

```json
{
  "subject_id": "crew_01",
  "study_id": "local_demo",
  "source_id": "local_checkin",
  "provenance_kind": "crew_self_report",
  "measurement": "sleep_duration",
  "value": 7.5,
  "units": "hours",
  "timestamp_utc": "REPLACE_WITH_ACTUAL_UTC_TIMESTAMP"
}
```

This small API intentionally accepts **sleep duration only**. It does not claim to monitor heart rate, oxygen saturation or other biomedical signals without appropriate source-specific validation. `source_id` is not a NASA source for local check-ins.

## Team ownership and handoff

1. **Member 1 — Amna:** science/communications and challenge-specific official NASA/CSA references, award-eligibility confirmation, final slides and submission narrative.
2. **Member 2 — Sachin:** analytics, input/data quality, leakage-safe trends, NASA bed-rest adapter and retrospective viewer, reproducible tests, local check-in analytics. Maintains PR #1.
3. **Member 3 — Husnain:** integrate the browser UI via same-origin HTTP endpoints; preserve source labels, missing data, and non-diagnostic wording. May replace the included research UI with the main frontend.
4. **Member 4 — Bilal:** verify NASA EDA instrument context and telemetry units; replace optional EDA preview with a reviewed environmental/radiation pipeline. Never present experimental CO2 readings as a person's exposure.
5. **Member 5 — Linta:** daily cognitive check-in input and evidence-backed method. Evaluate CSA PRET only after retrieving and validating actual underlying files; cannot claim NASA cognitive measurements from a local browser response-time game.
6. **Member 6 — Hammad:** integration/backend deployment owner, confirm shared contracts, merge/test branches, local SQLite audit policy, public demonstration access and final repo README. This local prototype is a fallback, not a silent replacement of integration ownership.

## Important scientific and product constraints

- In-flight telemetry, environmental instrumentation, human analog observations and new self-reports are **different populations and provenance classes**; never join by guessed timestamps.
- No medical diagnoses or operational safety decisions. An absence of a demo statistical flag is not evidence of health.
- Source sample size for the bed-rest study is three; pre-test reference is insufficient for most participants.
- Bed-rest analysis uses **calendar dates**, not invented minute-level timestamps. NASA EDA time values represent minute-level environmental controller times.
- A retrospective prior-14-day median is not a validated medical threshold. Current `analytics.py` uses an illustrative MAD/persistence rule on time-stamped local check-ins.
- Raw ZIP, downloaded CSV, locally generated derived JSON, and SQLite files remain outside repository until source redistribution rights and user privacy are confirmed.
- Demo requires Python process and files **installed locally**. It does not run in a browser without a local server. It needs no internet once installed and populated.

## Reproducibility / acceptance checklist

- `python -m unittest discover -s member2/tests -v` passes.
- `GET /api/health` shows `mode: local_offline`.
- Research endpoints work offline with the two already-downloaded datasets.
- A new local check-in is persisted to SQLite and returned by `GET /api/checkins`.
- The first check-in reports insufficient history, not a fake anomaly score.
- Invalid/future/duplicate check-ins are rejected.
- Main dashboard shows labeled research units, study phases, missing observations and direct source URLs.
- Integration owner confirms API contracts and creates a reviewable PR; final public deployment uses a separate privacy/design review.
