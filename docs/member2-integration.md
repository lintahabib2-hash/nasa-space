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

Each input observation requires:

- subject_id
- study_id
- source_id
- provenance_kind
- measurement
- value
- units
- timestamp_utc

The current record must have a valid timezone-aware timestamp.

History is restricted to the same subject, study, source,
provenance, measurement and units, with earlier timestamps.

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

    python member2/offline_api.py --help

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

    python -m unittest discover -s member2/tests -q

Production suites:

    python -m unittest discover -s backend/tests/unit -p 'test_baseline.py' -q
    python -m unittest discover -s backend/tests/unit -p 'test_member2_adapter_paths.py' -q
    python -m unittest discover -s backend/tests/unit -p 'test_simulated_crew.py' -q

The dedicated Member 2 workflow executes these suites.

## Integration boundaries

Member 4 owns the production environment/radiation
interface and its verified context data.

Member 5 owns the check-in and reaction-time experience.

Member 6 owns FastAPI routes, shared schemas, deployment,
integration QA and the final backend interface.

The frontend must not turn research comparisons into
medical diagnoses, crew readiness scores or individual
radiation exposure claims.

The member2/ directory provides a working compatibility
reference. Do not delete it until production imports,
data contracts, offline behavior and regression tests have
been verified in the integrated app.

## Scientific limitations

See docs/methods-note.md for statistical methods,
data provenance, reference construction, limitations,
uncertainties and research interpretation.
