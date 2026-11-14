"""Transparent, non-diagnostic crew observation analytics."""

from datetime import datetime, timezone
from math import isfinite
from statistics import median


MIN_REFERENCE = 5
PERSISTENCE_COUNT = 3
DEMO_Z_THRESHOLD = 3.0

REQUIRED = (
    "subject_id", "study_id", "source_id",
    "provenance_kind", "measurement", "value",
    "units", "timestamp_utc",
)

SERIES_ID = (
    "subject_id", "study_id", "source_id",
    "provenance_kind", "measurement", "units",
)


def timestamp(value):
    if not isinstance(value, str):
        raise ValueError("Timestamp must be text")

    dt = datetime.fromisoformat(
        value.replace("Z", "+00:00")
    )

    if dt.tzinfo is None:
        raise ValueError("Timestamp must include timezone")

    return dt.astimezone(timezone.utc)


def validated(record):
    if not isinstance(record, dict):
        raise ValueError("Observation must be an object")

    for field in REQUIRED:
        if field not in record or record[field] is None:
            raise ValueError(f"Missing field: {field}")

    if isinstance(record["value"], bool):
        raise ValueError("Boolean is not a measurement")

    try:
        value = float(record["value"])
    except (ValueError, TypeError):
        raise ValueError("Non-numeric measurement") from None

    if not isfinite(value):
        raise ValueError("Non-finite measurement")

    if record["measurement"] == "sleep_duration":
        if record["units"] != "hours":
            raise ValueError("Sleep duration requires hours")
        if not 0 <= value <= 24:
            raise ValueError("Invalid sleep duration")

    return timestamp(record["timestamp_utc"]), value


def get_observations(records, current):
    """Return valid, prior-only observations of the same series."""

    current_time, _ = validated(current)
    accepted = []
    rejected = 0
    seen_times = set()

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
            when, value = validated(record)
        except (ValueError, TypeError, OverflowError):
            rejected += 1
            continue

        if when >= current_time:
            continue

        if when in seen_times:
            rejected += 1
            continue

        seen_times.add(when)
        accepted.append((when, value))

    accepted.sort(key=lambda item: item[0])
    return accepted, rejected


def get_baseline_result(records, current):
    """Compare a current observation with prior personal history."""

    _, current_value = validated(current)
    history, rejected = get_observations(records, current)

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
            (timestamp(current["timestamp_utc"]), current_value)
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

    result["robust_z"] = round(score(current_value), 3)

    if not recent:
        result["status"] = "insufficient_persistence_history"
        result["quality_state"] = "limited_history"
        result["reasons"] = [
            "More observations needed to assess persistence"
        ]
        return result

    scores = [score(value) for _, value in recent]

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
            f"Three consecutive observations {direction} "
            "the personal statistical reference"
        ]
    else:
        result["status"] = "no_persistent_flag"
        result["reasons"] = [
            "No sustained deviation under the demonstration rule"
        ]

    return result
