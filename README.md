# Crew Vitals

NASA Space Apps Challenge 2026

An offline-first astronaut health-monitoring and decision-support prototype.

## Member 5: Daily check-in

This small, dependency-free web app implements Member 5's daily check-in, JSON data contract, optional reaction-time activity, and local routine reminders/streaks. It does not diagnose, assess fitness, or provide medical advice.

## Development

Preserve data provenance and test every component. Use feature branches and pull requests for team contributions.

## Run

From this directory, start a local static server:

```powershell
python -m http.server 8000
```

Open <http://localhost:8000>. Data is stored in this browser's local storage; use **Export JSON** to download a copy. Clearing this browser's site data will remove saved entries.

## Check-in contract and input limits

Each check-in contains `timestamp_utc`, `indicators`, `method`, and `provenance_kind`, plus a local calendar day for streak calculation. Each indicator is an observation envelope:

```json
{
  "source_id": "crew-vitals-daily-check-in",
  "provenance_kind": "manually_entered",
  "subject_id": null,
  "study_id": null,
  "measurement": "sleep_hours",
  "value": 7.5,
  "units": "hours",
  "timestamp_utc": "2026-11-14T10:00:00.000Z",
  "quality_state": "valid",
  "reference_url": null
}
```

Required indicators are sleep (0–24 hours), mood (integer 1–5), stress (integer 0–10), and exercise (integer 0–1,440 minutes). Optional manual/device readings accept heart rate (20–250 bpm), body temperature (25–45 °C), oxygen saturation (50–100%), systolic and diastolic blood pressure (40–300 and 20–200 mmHg respectively; both are required together, and systolic must exceed diastolic), and blood glucose (10–1,000 mg/dL). These are input-format bounds, not health or safety thresholds. The form rejects out-of-range values and only stores completed check-ins.

Reaction activities store a five-round median response time in milliseconds, the UTC completion timestamp, the task name, and the timing method. Participation is optional. Browser/device input and display timing vary, so results are not standardized or suitable for clinical interpretation.

Daily reminders are local and work while the page is open. Browser notifications may be offered if supported and permitted; no server or background push is used. Streaks count consecutive local calendar days with at least one saved check-in.
