"""Transparent, non-diagnostic crew observation analytics."""

from datetime import datetime, timezone
from math import isfinite
from statistics import median

from .persistence import persistence_reasons


MIN_REFERENCE = 5
PERSISTENCE_COUNT = 3
DEMO_Z_THRESHOLD = 3.0

USABLE_STATES = ("valid",)
FLAGGED_STATES = ("missing", "outlier", "unknown")

REQUIRED = (
    "subject_id", "study_id", "source_id",
    "provenance_kind", "measurement", "value",
    "units", "timestamp_utc",
)

SERIES_ID = (
    "subject_id", "study_id", "source_id",
    "provenance_kind", "measurement", "units",
)


# Input-format bounds shared with Member 5's check-in form.
# These are NOT clinical reference ranges or alert thresholds.
MEASUREMENT_RULES = {
    "sleep_duration": ("hours", 0, 24, False),
    "mood": ("score_1_5", 1, 5, True),
    "stress": ("score_1_5", 1, 5, True),
    "exercise_minutes": ("minutes", 0, 1440, True),
    "resting_heart_rate": ("bpm", 20, 250, True),
    "body_temperature": ("degC", 25, 45, False),
    "oxygen_saturation": ("percent", 50, 100, True),
    "systolic_bp": ("mmHg", 40, 300, True),
    "diastolic_bp": ("mmHg", 20, 200, True),
    "blood_glucose": ("mg/dL", 10, 1000, True),
    "radiation_badge_daily_dose": ("uSv/day", 0, 100000, False),
}


def timestamp(value):
    if not isinstance(value, str):
        raise ValueError("Timestamp must be text")

    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
        if dt.tzinfo is None:
            raise ValueError("Timestamp must include timezone")
        return dt.astimezone(timezone.utc)
    except (ValueError, OverflowError):
        raise ValueError("Timestamp must be valid and timezone-aware") from None


def _validated_fields(record, *, allow_missing=False):
    """Validate supplied fields before interpreting genuine missingness."""
    if not isinstance(record, dict):
        raise ValueError("Observation must be an object")

    for field in SERIES_ID:
        if not isinstance(record.get(field), str) or not record[field].strip():
            raise ValueError(f"Missing or invalid series metadata: {field}")

    rule = MEASUREMENT_RULES.get(record["measurement"])
    if rule is None:
        raise ValueError("Unsupported measurement")

    units, minimum, maximum, integer = rule
    if record["units"] != units:
        raise ValueError("Measurement units mismatch")

    # Project Guide §6 quality states. "outlier" and "unknown" are legitimate flags from an
    # adapter; they are treated like a missing reading (never scored), not as malformed input.
    if "quality_state" in record and record["quality_state"] not in USABLE_STATES + FLAGGED_STATES:
        raise ValueError("Unsupported observation quality state")

    raw_time = record.get("timestamp_utc")
    when = None if raw_time is None or raw_time == "" else timestamp(raw_time)

    raw_value = record.get("value")
    if raw_value is None:
        value = None
    else:
        if isinstance(raw_value, bool):
            raise ValueError("Boolean is not a measurement")

        try:
            value = float(raw_value)
        except (ValueError, TypeError, OverflowError):
            raise ValueError("Non-numeric measurement") from None

        if not isfinite(value):
            raise ValueError("Non-finite measurement")

        if not minimum <= value <= maximum:
            raise ValueError("Measurement outside allowed input bounds")

        if integer and not value.is_integer():
            raise ValueError("Expected an integer measurement")

    if not allow_missing and (
        when is None or value is None or record.get("quality_state") in FLAGGED_STATES
    ):
        raise ValueError("Measurement or timestamp missing")

    return when, value


def validated(record):
    """Return a usable timestamp/value pair, or raise ValueError."""
    return _validated_fields(record)


def _select_observations(records, current, current_time):
    """Keep rejected times so filtering cannot manufacture continuity."""
    accepted = []
    rejected = 0
    barriers = []
    by_time = {}

    if isinstance(records, (str, bytes, dict)):
        raise ValueError("Historical observations must be a collection of records")
    try:
        records = iter(records)
    except TypeError:
        raise ValueError("Historical observations must be iterable") from None

    for record in records:
        if not isinstance(record, dict):
            rejected += 1
            continue

        if any(
            record.get(key) != current[key]
            for key in SERIES_ID
        ):
            continue

        try:
            when = timestamp(record.get("timestamp_utc"))
        except ValueError:
            rejected += 1
            barriers.append(None)
            continue

        if when >= current_time:
            continue

        by_time.setdefault(when, []).append(record)

    for when, group in by_time.items():
        # Exclude every copy, including a valid value paired with an invalid
        # duplicate. Input order must not decide which observation is used.
        if len(group) != 1:
            rejected += len(group)
            barriers.append(when)
            continue

        try:
            _, value = validated(group[0])
        except ValueError:
            rejected += 1
            barriers.append(when)
            continue
        accepted.append((when, value))

    accepted.sort(key=lambda item: item[0])
    return accepted, rejected, barriers


def get_observations(records, current):
    """Return valid, prior-only observations of the same series."""
    current_time, _ = validated(current)
    history, rejected, _ = _select_observations(records, current, current_time)
    return history, rejected


def get_baseline_result(records, current):
    """Compare a current observation with prior personal history."""

    current_time, current_value = _validated_fields(current, allow_missing=True)

    flagged = current.get("quality_state") in FLAGGED_STATES
    if current_value is None or current_time is None or flagged:
        state = current.get("quality_state")
        reason = (
            f"Latest measurement flagged as {state}; no status computed"
            if flagged and state != "missing" and current_value is not None
            else "Latest measurement or timestamp missing"
        )
        return {
            "subject_id": current["subject_id"],
            "study_id": current["study_id"],
            "source_id": current["source_id"],
            "provenance_kind": current["provenance_kind"],
            "measurement": current["measurement"],
            "units": current["units"],
            "timestamp_utc": current.get("timestamp_utc"),
            "current_value": None,
            "history_count": 0,
            "rejected_history_count": 0,
            "baseline_value": None,
            "robust_z": None,
            "status": "unknown",
            "quality_state": "missing",
            "reasons": [reason],
            "severity_basis": "unvalidated_demo_statistical_rule",
            "not_medical_diagnosis": True,
        }

    history, rejected, barriers = _select_observations(records, current, current_time)

    result = {
        "subject_id": current["subject_id"],
        "measurement": current["measurement"],
        "current_value": current_value,
        "units": current["units"],
        "source_id": current["source_id"],
        "study_id": current["study_id"],
        "provenance_kind": current["provenance_kind"],
        "history_count": len(history),
        "rejected_history_count": rejected,
        "baseline_value": None,
        "robust_z": None,
        "status": "unknown",
        "quality_state": "insufficient_history",
        "reasons": [],
        "severity_basis": "unvalidated_demo_statistical_rule",
        "not_medical_diagnosis": True,
    }

    if len(history) < MIN_REFERENCE:
        result["status"] = "insufficient_history"
        result["reasons"] = ["Not enough prior observations"]
        return result

    # Reserve the last two historical observations to test
    # whether the current deviation is persistent.
    if len(history) >= MIN_REFERENCE + PERSISTENCE_COUNT - 1:
        reference = history[:-2]
        recent = history[-2:] + [
            (current_time, current_value)
        ]
    else:
        reference = history
        recent = []

    values = [value for _, value in reference]
    center = median(values)
    mad = median(abs(value - center) for value in values)

    result["baseline_value"] = center
    result["reference_count"] = len(reference)
    result["reference_start_utc"] = reference[0][0].isoformat()
    result["reference_end_utc"] = reference[-1][0].isoformat()

    if mad == 0:
        result["status"] = "insufficient_scale"
        result["quality_state"] = "insufficient_scale"
        result["reasons"] = [
            "Reference readings have zero median absolute deviation"
        ]
        return result

    def score(value):
        return (value - center) / (1.4826 * mad)

    current_score = score(current_value)
    scores = [score(value) for _, value in recent]
    if not all(isfinite(z) for z in [current_score, *scores]):
        result["status"] = "insufficient_scale"
        result["quality_state"] = "insufficient_scale"
        result["reasons"] = [
            "Reference spread is too small to compute finite statistical scores"
        ]
        return result

    result["robust_z"] = round(current_score, 3)

    cadence_reasons = persistence_reasons(recent, barriers) if recent else []
    if not recent or cadence_reasons:
        result["status"] = "insufficient_persistence_history"
        result["quality_state"] = "limited_history"
        result["reasons"] = cadence_reasons or [
            "More observations needed to assess persistence"
        ]
        return result

    sustained_high = all(
        z >= DEMO_Z_THRESHOLD for z in scores
    )
    sustained_low = all(
        z <= -DEMO_Z_THRESHOLD for z in scores
    )

    result["quality_state"] = "adequate_for_demo"

    if sustained_high or sustained_low:
        direction = "above" if sustained_high else "below"
        result["status"] = "review"
        result["reasons"] = [
            f"Three observations on consecutive UTC dates {direction} "
            "the personal statistical reference"
        ]
    else:
        result["status"] = "no_persistent_flag"
        result["reasons"] = [
            "No sustained deviation under the demonstration rule"
        ]

    return result
