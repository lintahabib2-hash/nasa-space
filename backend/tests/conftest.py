"""Shared pytest fixtures

Owner: Member 6 (Backend, Integration, QA & Deployment)
"""

import copy
from datetime import datetime, timedelta, timezone

import pytest
from fastapi.testclient import TestClient

from backend.app.config import Settings
from backend.app.main import create_app
from backend.app.services import open_repository

SCENARIO_SUBJECTS = {
    "stable": "X01_stable",
    "drift": "X01_downward_drift",
    "missing": "X01_missing_observation",
}


@pytest.fixture()
def settings():
    return Settings(db_path=":memory:", seed_simulated=True)


@pytest.fixture()
def repo(settings):
    r = open_repository(settings)
    yield r
    r.close()


@pytest.fixture()
def empty_repo(settings):
    r = open_repository(Settings(db_path=":memory:", seed_simulated=False))
    yield r
    r.close()


@pytest.fixture()
def client(settings, repo):
    return TestClient(create_app(settings, repo))


def make_observation(day: int, value, subject="crew_test", measurement="sleep_duration", **over):
    base = datetime(2026, 11, 1, 7, 0, tzinfo=timezone.utc) + timedelta(days=day - 1)
    rec = {
        "source_id": "TEST", "provenance_kind": "simulated", "subject_id": subject,
        "study_id": "test_study", "measurement": measurement, "value": value, "units": "hours",
        "timestamp_utc": base.isoformat().replace("+00:00", "Z"),
        "quality_state": "missing" if value is None else "valid",
    }
    rec.update(over)
    return rec


def make_checkin(day: int = 20, sleep: float = 7.0, subject: str = "crew_01"):
    """A schema-valid check-in (shared/schemas/checkin.schema.json)."""
    ts = (datetime(2026, 11, 1, 7, 0, tzinfo=timezone.utc) + timedelta(days=day - 1)).isoformat().replace("+00:00", "Z")

    def env(measurement, value, units):
        return {
            "source_id": "crew-vitals-daily-check-in", "provenance_kind": "manually_entered",
            "subject_id": subject, "study_id": "local_checkin", "measurement": measurement,
            "value": value, "units": units, "timestamp_utc": ts, "quality_state": "valid", "reference_url": None,
        }

    return {
        "schema": "crew-vitals/checkin@1", "record_id": f"checkin-{subject}-{day}", "subject_id": subject,
        "timestamp_utc": ts, "local_day": ts[:10], "method": "self_reported",
        "provenance_kind": "manually_entered", "source_id": "crew-vitals-daily-check-in",
        "indicators": {
            "sleep_duration": env("sleep_duration", sleep, "hours"),
            "mood": env("mood", 3, "score_1_5"),
            "stress": env("stress", 2, "score_1_5"),
            "exercise_minutes": env("exercise_minutes", 30, "minutes"),
        },
    }


@pytest.fixture()
def checkin_factory():
    return lambda **kw: copy.deepcopy(make_checkin(**kw))
