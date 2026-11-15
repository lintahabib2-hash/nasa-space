# Thresholds and rationale (demo rules, mirrored in README)

> Owner: Member 6 (Backend, Integration, QA & Deployment). The rules themselves are implemented and owned by
> Member 2 in `backend/app/analytics/baseline.py`; the method is described in [methods-note.md](methods-note.md).
> This page is the one-page summary for judges and for the README.

**These are illustrative demonstration rules. They are not clinically calibrated, not validated, and not NASA limits.**
A result of `no_persistent_flag` does **not** mean healthy. `review` means "worth a look", never a diagnosis.

## The rule in one paragraph

Each person is compared **only with their own earlier readings** of the same series (same study, source, provenance and
units). The most recent reading is scored against the median of that person's reference readings, scaled by the
median absolute deviation (MAD). A reading is flagged for review only when **three consecutive daily readings** are
all on the same side of the threshold, so one noisy day never raises a flag.

## Parameters

The block below is checked against the code by a test (`backend/tests/unit/test_docs_match_code.py`), so this page cannot drift.

```
MIN_REFERENCE = 5
PERSISTENCE_COUNT = 3
DEMO_Z_THRESHOLD = 3.0
```

| Parameter | Value | Why this value |
|---|---|---|
| Robust z-score | `(current - median) / (1.4826 x MAD)` | Median and MAD ignore outliers in the history. The factor 1.4826 makes MAD comparable to a standard deviation for roughly bell-shaped data. |
| `DEMO_Z_THRESHOLD` | 3.0 | A common "clearly outside the person's usual range" cut for robust scores. Strict on purpose: a false alarm costs trust more than a slightly later flag in a demo. Not a medical limit. |
| `PERSISTENCE_COUNT` | 3 consecutive readings | Suppresses single-day noise (a bad night, a sensor glitch) and matches the "sustained drift" story. |
| Daily cadence | 3 consecutive UTC dates, at most 48 h between neighbours | Persistence means days in a row, not three readings spread over weeks. Provisional engineering convention. |
| `MIN_REFERENCE` | 5 valid prior readings | Fewer points give an unstable median. Below this the answer is `insufficient_history`, never a guess. |
| Reserved readings | the 2 readings before the current one are not used for the reference | Stops a developing drift from becoming its own "normal". |

## Safe fallbacks (never a false "healthy")

| Situation | Status | Why |
|---|---|---|
| Latest reading missing or invalid | `unknown` | A gap is shown as a gap, not as "fine". |
| Fewer than 5 valid prior readings | `insufficient_history` | Not enough to define "usual". |
| History has zero spread (MAD = 0) | `insufficient_scale` | A z-score is undefined; no score is forced. |
| Readings not on consecutive days | `insufficient_persistence_history` | The persistence rule cannot be applied safely. |
| Series has no stored readings | `no_observations` | (API only) nothing to score. |
| 3 consecutive days beyond 3.0, same side | `review` | The only flag the app raises. |
| Otherwise | `no_persistent_flag` | "No sustained change from this person's own baseline". Not "healthy". |

## Accepted input ranges

Readings outside these physical bounds are rejected before scoring (typos, unit mix-ups). They are input sanity limits, not health thresholds.

| Measurement | Units | Accepted range |
|---|---|---|
| sleep_duration | hours | 0 to 24 |
| mood, stress | score 1-5 | whole numbers 1 to 5 |
| exercise_minutes | minutes | 0 to 1440 |
| resting_heart_rate | bpm | 20 to 250 |
| body_temperature | degC | 25 to 45 |
| oxygen_saturation | percent | 50 to 100 |
| systolic_bp / diastolic_bp | mmHg | 40 to 300 / 20 to 200 |
| blood_glucose | mg/dL | 10 to 1000 |
| radiation_badge_daily_dose | uSv/day | 0 to 100000 |

## What the numbers do not claim

- No diagnosis, probability, risk score or validated fitness-for-duty score.
- The environment (radiation) context is historical instrument data. It is never combined with a crew reading and is
  not anyone's personal dose.
- Thresholds were not tuned on real astronaut data. Crew data in this submission is simulated.
