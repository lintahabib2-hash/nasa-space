# Crew Vitals — Member 2 Integration Contract

## Status

Member 2 scientific implementation is ready for integration review.

Branch: feature/member2-analytics
Pull request: #1

The independently validated localhost research console is
not the team's deployed production backend.

## Production analytics

Primary import:

    from backend.app.analytics import get_baseline_result

Function:

    get_baseline_result(prior_records, current_record)

Each input observation identifies one series with:

- subject_id
- study_id
- source_id
- provenance_kind
- measurement
- units

Numerical analysis also requires `value` and a timezone-aware
`timestamp_utc`, normalized to UTC. Missing current values or
timestamps produce `status=unknown`; they are never imputed.
Omitted/null values and omitted/null/empty timestamps are
treated as absent; other malformed supplied values are rejected.

Series metadata must be non-empty text. The measurement must
be supported, units must match, and any supplied value must
be finite and within the documented input-format bounds.
Any supplied timestamp must be valid. Malformed supplied
fields raise `ValueError`, even when another field is missing.
The bounds are form constraints, not clinical reference ranges.

`quality_state` is optional for existing callers. If supplied,
it must be `valid` or `missing`. A current observation marked
`missing` produces `unknown` after its supplied fields have
been validated. Historical observations marked `missing`
cannot contribute numeric values to the reference.

History is restricted to the same subject, study, source,
provenance, measurement and units, with earlier timestamps.
Missing and invalid same-series historical records are excluded
and counted. Every record in a duplicate timestamp group is
excluded, so input ordering cannot decide which value wins.

The provisional daily demonstration policy requires the two
most recent eligible historical observations and the current
observation to fall on three consecutive UTC calendar dates,
with no adjacent elapsed-time gap above 48 hours. Same-day
readings cannot fill daily slots; no daily aggregation is
performed. Three sparse readings across weeks produce
`insufficient_persistence_history`, never `review`.

Excluded same-series observations retain a timing barrier:
missing or invalid records within the candidate persistence
window prevent a persistence decision. If a same-series
record has no usable timestamp, its position is unknown and
persistence cannot be established safely. Older barriers
outside the candidate window do not interrupt that window.

This timing policy is an engineering convention selected for
the daily demo, pending agreement with the integration team.
It is not a NASA-derived or clinically validated threshold.
The policy does not supply timestamps for date-only research
records or alter the separate historical research processors.

The result includes statistical status, historical count,
rejected-history count, reference information, reasons,
quality information and not_medical_diagnosis.

The rule is illustrative and non-diagnostic.

## Production research adapters

Located in backend/app/adapters/:

- nlsp_actigraphy.py
- nlsp_preview.py
- nlsp_trends.py
- cft70_nutrition.py
- osd575_serum.py
- osd569_cbc.py
- simulated_crew.py

X01 scenarios are synthetic engineering fixtures.

All NASA processors preserve source provenance and study
separation. Do not join independent populations into one
person's longitudinal record.

## Standalone offline reference application

Existing entry point:

    python prototypes/offline_research/offline_api.py --help

The application uses Python's ThreadingHTTPServer and
SQLite, not FastAPI.

Its local read-only endpoints include:

- GET /api/health
- GET /api/research/bedrest
- GET /api/research/environment
- GET /api/research/cft70
- GET /api/research/inspiration4
- GET /api/research/radlab
- GET /api/analytics/latest?subject_id=...
- GET /api/checkins?subject_id=...

Locally entered sleep durations are accepted by:

    POST /api/checkins

The API is localhost-only and has no production
authentication system.

## Offline data preparation

Acquired NASA research files and generated JSON outputs
remain outside the public repository.

Do not commit raw human research data or local SQLite
databases without confirmed authorization.

Pandas is required for several preprocessing adapters.

Prepared research files are supplied using startup options:
--bedrest-json, --eda-csv, --cft70-json,
--cmp-json, --cbc-json and --radlab-csv.

Unconfigured sources must report unavailable, rather than
displaying invented fallback measurements.

## Verification

Legacy suite:

    python -m unittest discover -s prototypes/offline_research/tests -q

Production suites:

    python -m unittest discover -s backend/tests/unit -p 'test_baseline.py' -q
    python -m unittest discover -s backend/tests/unit -p 'test_member2_adapter_paths.py' -q
    python -m unittest discover -s backend/tests/unit -p 'test_simulated_crew.py' -q
    python -m unittest discover -s backend/tests/unit -p 'test_review_fixes.py' -q
    python -m unittest discover -s backend/tests/unit -p 'test_persistence.py' -q
    python -m unittest discover -s backend/tests/unit -p 'test_validation.py' -q

The dedicated Member 2 workflow checks dependency consistency
and executes these suites. Frontend verification remains:

    cd frontend
    npm test
    npm run typecheck
    npm run build

Passing these checks does not establish a connected
check-in-to-FastAPI-to-dashboard flow.

## Integration boundaries

Member 4 owns the production environment/radiation
interface and its verified context data.

Member 5 owns the check-in and reaction-time experience.

Member 6 owns FastAPI routes, shared schemas, deployment,
integration QA and the final backend interface.

The frontend must not turn research comparisons into
medical diagnoses, crew readiness scores or individual
radiation exposure claims.

The prototypes/offline_research/ directory provides a working compatibility
reference. Do not delete it until production imports,
data contracts, offline behavior and regression tests have
been verified in the integrated app.

## Scientific limitations

See docs/methods-note.md for statistical methods,
data provenance, reference construction, limitations,
uncertainties and research interpretation.
