# shared/

This folder holds the contracts and knowledge that the backend and the frontend both use.

| Folder | Owner | Expected files |
|---|---|---|
| `schemas/` | M6 (check-in schema: M5) | `envelope.schema.json`, `api-response.schema.json`, `checkin.schema.json`, `environment-series.schema.json` |
| `knowledge/` | M1 | `knowledge.json` (hazard/region cards, guidance tiers), `source-registry.json` |
| `mocks/` | M6 | Mock API responses for each scenario (stable, drift, missing data), so modules can merge early |

Envelope fields (Project Guide §6): `source_id`, `provenance_kind`, `subject_id`, `study_id`,
`measurement`, `value`, `units`, `timestamp_utc`, `quality_state`, `reference_url`.
