# Data contract: shared envelope and common API response

> Owner: Member 6 (Backend, Integration, QA & Deployment)
>
> Source of truth: `shared/schemas/*.schema.json`. Mirrored by `backend/app/contracts/` (Pydantic) and
> `frontend/src/types/contracts.ts` (TypeScript). Tests assert the mirrors agree (`backend/tests/unit/test_contracts.py`).
> Changing a schema needs a PR reviewed by M6 and every member who uses it.

## 1. Observation envelope (`envelope.schema.json`)

One measurement of one thing for one subject at one UTC instant. Everything the analytics engine reads has this shape.

| Field | Type | Rule |
|---|---|---|
| `source_id` | string | Registry ID of where it came from (e.g. `X01`, `crew-vitals-daily-check-in`) |
| `provenance_kind` | enum | `nasa_measured`, `analog_measured`, `external_earth`, `simulated`, `manually_entered`, `crew_self_report` |
| `subject_id` | string | Crew member or study subject. Environment data has none. |
| `study_id` | string | Study / dataset the reading belongs to |
| `measurement` | string | e.g. `sleep_duration` |
| `value` | number or null | Finite only. A string, NaN or Infinity is rejected. `null` means missing. |
| `units` | string | Non-blank |
| `timestamp_utc` | string | ISO-8601 with a UTC offset; stored as `...Z`. Naive timestamps are rejected. |
| `quality_state` | enum | `valid`, `missing`, `outlier`, `unknown`. **`value` is null if and only if `quality_state` is `missing`.** |
| `reference_url` | string or null | Optional link to the source |

Unknown extra fields are rejected.

## 2. Common API response (`api-response.schema.json`)

What `/api/baseline` returns per indicator (Member 2's `get_baseline_result()` output). Extra analytics fields are allowed.

| Field | Meaning |
|---|---|
| `status` | `no_persistent_flag`, `review`, `insufficient_history`, `insufficient_scale`, `insufficient_persistence_history`, `unknown`, `no_observations` |
| `reasons` | Non-empty list. Every status explains itself in words. |
| `severity_basis` | Always names the rule used (`unvalidated_demo_statistical_rule`) |
| `not_medical_diagnosis` | Always `true` |
| `robust_z`, `baseline_value`, `current_value` | Numbers when scored; `null` when not. `review` requires all three. |
| `provenance_kind`, `source_id`, `study_id`, `units` | Carried through from the data that was scored |
| `history_count`, `rejected_history_count` | How many prior readings were used / excluded (gaps are counted, not hidden) |

## 3. Environment series (`environment-series.schema.json`)

Member 4's `get_environment_series()`. Historical instrument data with its citation, instrument, limitations and a
`subject_id` that is always `null`. It is served on its own route and **never merged into a crew response**.

## 4. Check-in record (`checkin.schema.json`)

Member 5's daily check-in. Each indicator inside it is an envelope (section 1) with `provenance_kind: manually_entered`.
`POST /api/checkins` validates against this schema, stores the record, and turns its indicators into observations in one transaction.

## 5. API routes (`uvicorn backend.app.main:app`)

| Route | Purpose |
|---|---|
| `GET /api/health` | Status, row counts, `contains_real_astronaut_data: false` |
| `GET /api/observations?subject_id&measurement&study_id` | Stored observations |
| `POST /api/observations` | Store one or a list; the whole batch is validated first (all or nothing) |
| `GET /api/baseline?subject_id&measurement` | Latest reading of one series vs. its own history |
| `GET /api/baseline/all?subject_id` | One result per measurement |
| `POST /api/checkins`, `GET /api/checkins` | Submit / list daily check-ins |
| `GET /api/environment` | NASA environment series. On failure: **503**, never substitute data. |
| `GET /api/knowledge`, `GET /api/sources` | Member 1's reviewed files, unchanged |

Errors: invalid data is **422** `{ "error": "invalid_data", "detail": "..." }`. Writes are idempotent: the same series and
timestamp overwrites, so a retried request cannot create the duplicate-timestamp groups the analytics refuses to score.

## 6. Offline snapshot (`snapshot-manifest.schema.json`)

`python backend/scripts/export_static_snapshot.py` runs the same service functions as the routes against the simulated X01
scenarios and writes `frontend/public/data/{environment,knowledge,sources,baselines,manifest}.json`
(plus `shared/mocks/baseline-*.json`). Output is deterministic; CI runs `--check` and fails if it is stale. The frontend
`apiClient` uses the live API when `VITE_API_BASE` is set and otherwise, or when the API is down, the snapshot, and reports which one answered.

## 7. Rules every module must keep

1. Provenance on every value. Simulated is never labelled NASA.
2. Series are never mixed: baselines use only readings with the same study, source, provenance and units. If a subject has two series for a measurement, the series with the most recent reading is scored on its own.
3. Missing is explicit (`null` + `missing`), never `0`, never imputed, never "healthy".
4. Environment data stays separate from crew data.
5. Every output says it is not a diagnosis.
