"""Deterministic X01 engineering scenarios.

These are synthetic fixtures, NOT NASA measurements,
actual astronaut observations, or clinical test cases.
"""

REFERENCE = (7.0, 7.2, 6.9, 7.1, 7.3, 7.05, 7.15)

SCENARIOS = {
    "stable": {
        "recent": (7.1, 7.2),
        "current": 7.1,
        "expected_status": "no_persistent_flag",
    },
    "downward_drift": {
        "recent": (6.5, 6.0),
        "current": 5.5,
        "expected_status": "review",
    },
    "missing_observation": {
        "recent": (None, 7.1, 7.2),
        "current": 7.0,
        "expected_status": "no_persistent_flag",
    },
}


def observation(subject_id, day, value):
    return {
        "subject_id": subject_id,
        "study_id": "X01_engineering_fixture",
        "source_id": "X01",
        "provenance_kind": "simulated",
        "measurement": "sleep_duration",
        "value": value,
        "units": "hours",
        "timestamp_utc": f"2026-11-{day:02d}T07:00:00Z",
        "quality_state": "missing" if value is None else "valid",
    }


def build_scenario(name):
    if name not in SCENARIOS:
        raise ValueError(f"Unknown X01 scenario: {name}")

    config = SCENARIOS[name]
    subject = f"X01_{name}"
    values = (*REFERENCE, *config["recent"])

    history = [
        observation(subject, day, value)
        for day, value in enumerate(values, start=1)
    ]

    current = observation(
        subject,
        len(values) + 1,
        config["current"],
    )

    return {
        "scenario_id": name,
        "source_id": "X01",
        "provenance_kind": "simulated",
        "dataset_type": "engineering_fixture_only",
        "not_real_astronaut_data": True,
        "history": history,
        "current": current,
        "expected_status": config["expected_status"],
    }
