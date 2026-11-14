# Reaction-time activity: device timing limitations

> Owner: Member 5. Code: `frontend/src/features/reaction-time/`.

## What it records

Five rounds of a visual response task. After a random wait of 0.9–2.8 s the target turns orange,
and the response time is measured with `performance.now()`. The stored result is the **median** of
the five rounds:

```json
{
  "measurement": "visual_reaction_time_median",
  "task": "five_round_visual_response",
  "score": 280, "value": 280, "units": "milliseconds", "rounds": [300, 250, 400, 280, 260],
  "timestamp_utc": "2026-11-14T10:00:00.000Z",
  "method": "browser_performance_api; click_or_touch",
  "provenance_kind": "manually_entered", "subject_id": "crew_01"
}
```

Tapping before the target appears ends the attempt ("Too soon") and saves nothing.

## Limitations

- Screen refresh rate, touch versus mouse input, browser load and hardware all add delay and
  variability. Results are **not standardized** and must not be compared across devices.
- It is optional, personal tracking only. It is **not a validated cognitive test** and makes no
  clinical, mental-health, impairment or fitness-for-duty inference.
- No NASA cognitive measurement is claimed. CSA PRET (see Member 2's source registry) is a possible
  reference only after its underlying files have been checked.
