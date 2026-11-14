# Daily check-in schema and input bounds

> Owner: Member 5 (Cognitive & Daily Check-In). Converted to the React app by Member 3 from Linta's
> original `nasa-space-upload` app.

- **Machine-readable schema:** [`shared/schemas/checkin.schema.json`](../shared/schemas/checkin.schema.json)
- **Code:** `frontend/src/features/checkin/checkinSchema.ts` (fields, bounds, validation)
- **Storage:** browser `localStorage`, key `crew-vitals.checkins.v1` (`{ checkins: [], reactionTests: [] }`)

## Record

```json
{
  "schema": "crew-vitals/checkin@1",
  "record_id": "uuid",
  "subject_id": "crew_01",
  "timestamp_utc": "2026-11-14T10:00:00.000Z",
  "local_day": "2026-11-14",
  "method": "self_reported",
  "provenance_kind": "manually_entered",
  "source_id": "crew-vitals-daily-check-in",
  "indicators": {
    "sleep_duration": {
      "source_id": "crew-vitals-daily-check-in", "provenance_kind": "manually_entered",
      "subject_id": "crew_01", "study_id": "local_checkin",
      "measurement": "sleep_duration", "value": 7.5, "units": "hours",
      "timestamp_utc": "2026-11-14T10:00:00.000Z", "quality_state": "valid", "reference_url": null
    }
  }
}
```

## Fields and input bounds

These are **input-format bounds, not health or safety thresholds**.

| Measurement | Units | Bounds | Required |
|---|---|---|---|
| `sleep_duration` | hours | 0–24 | yes |
| `mood` | score_1_5 | integer 1–5 | yes |
| `stress` | score_1_5 | integer 1–5 | yes |
| `exercise_minutes` | minutes | integer 0–1,440 | yes |
| `resting_heart_rate` | bpm | integer 20–250 | no |
| `body_temperature` | degC | 25–45 | no |
| `oxygen_saturation` | percent | integer 50–100 | no |
| `systolic_bp` / `diastolic_bp` | mmHg | integer 40–300 / 20–200; both or neither; systolic > diastolic | no |
| `blood_glucose` | mg/dL | integer 10–1,000 | no |
| `radiation_badge_daily_dose` | uSv/day | 0–100,000 | no |

Only complete, valid check-ins are stored. Invalid input shows a message and saves nothing.

## Changes from the original app (for Linta to confirm)

| Original | Now | Why |
|---|---|---|
| `subject_id: null` | `crew_01` (from `VITE_SUBJECT_ID`) | Member 2's API rejects check-ins without a subject ID |
| `sleep_hours`, `heart_rate`, `blood_pressure_systolic`/`_diastolic` | `sleep_duration`, `resting_heart_rate`, `systolic_bp`/`diastolic_bp` | Same names as Member 2's analytics and the dashboard |
| units `celsius`, `self_rating_1_to_5` | `degC`, `score_1_5` | Same units as the analytics fixtures |
| stress 0–10 | stress 1–5 | Project Guide §4: "Mood and stress: self-rated 1 to 5 scale" |
| no radiation entry | optional `radiation_badge_daily_dose` | Project Guide §1 lists the radiation badge reading in the daily check-in |
| record had no `schema` field | `schema: "crew-vitals/checkin@1"` | Versioning for the shared contract |

## Open integration points

- **Member 2:** `member2/offline_api.py` currently accepts `provenance_kind: "crew_self_report"` and `sleep_duration` only.
  The check-in uses `manually_entered` (the Project Guide's provenance list). Agree on one value.
- **Member 6:** sync these local records to the API or IndexedDB, and feed them to the dashboard's analytics.
