"""Observations + baseline + environment together

Owner: Member 6 (Backend, Integration, QA & Deployment)

Exercises the real modules through the real HTTP API: Member 2's analytics, Member 4's NASA
environment adapter, Member 5's check-in schema, and Member 6's storage and routes.
"""

import json

import pytest
from fastapi.testclient import TestClient
from jsonschema import Draft202012Validator

from backend.app.config import REPO_ROOT, Settings
from backend.app.main import create_app
from backend.tests.conftest import SCENARIO_SUBJECTS, make_checkin

RESPONSE_SCHEMA = Draft202012Validator(json.loads((REPO_ROOT / "shared/schemas/api-response.schema.json").read_text(encoding="utf-8")))
X01 = json.loads((REPO_ROOT / "data/simulated/X01_crew_scenarios.json").read_text(encoding="utf-8"))
EXPECTED = {s["scenario_id"]: s["expected_status"] for s in X01["scenarios"]}


def baseline(client, subject, measurement="sleep_duration"):
    r = client.get("/api/baseline", params={"subject_id": subject, "measurement": measurement})
    assert r.status_code == 200, r.text
    return r.json()


def test_stable_scenario_gives_no_flag(client):
    r = baseline(client, SCENARIO_SUBJECTS["stable"])
    assert r["status"] == EXPECTED["stable"] == "no_persistent_flag"
    assert r["provenance_kind"] == "simulated" and r["source_id"] == "X01"


def test_drift_scenario_gives_review_with_reason(client):
    r = baseline(client, SCENARIO_SUBJECTS["drift"])
    assert r["status"] == EXPECTED["downward_drift"] == "review"
    assert r["robust_z"] < -3 and r["current_value"] < r["baseline_value"]
    assert any("below" in reason for reason in r["reasons"])


def test_missing_observation_is_handled_not_hidden(client):
    r = baseline(client, SCENARIO_SUBJECTS["missing"])
    assert r["status"] == EXPECTED["missing_observation"]
    assert r["rejected_history_count"] >= 1, "the gap must be counted, not silently ignored"


def test_missing_latest_reading_gives_unknown_never_healthy(client):
    client.post("/api/observations", json={
        "source_id": "X01", "provenance_kind": "simulated", "subject_id": "X01_stable",
        "study_id": "X01_engineering_fixture", "measurement": "sleep_duration", "value": None,
        "units": "hours", "timestamp_utc": "2026-11-20T07:00:00Z", "quality_state": "missing"})
    r = baseline(client, "X01_stable")
    assert r["status"] == "unknown" and r["current_value"] is None and r["robust_z"] is None


def test_every_scenario_response_matches_the_shared_schema(client):
    for subject in SCENARIO_SUBJECTS.values():
        errors = list(RESPONSE_SCHEMA.iter_errors(baseline(client, subject)))
        assert not errors, [e.message for e in errors]


def test_crew_baseline_and_nasa_environment_work_in_one_session(client):
    crew = baseline(client, SCENARIO_SUBJECTS["drift"])
    env = client.get("/api/environment").json()
    assert crew["provenance_kind"] == "simulated" and env["provenance_kind"] == "nasa_measured"
    assert env["series"][0]["points"], "environment series must carry data"
    assert env["citation"] and env["limitations"]


def test_new_checkins_build_history_and_trigger_a_review(client):
    """8 stable daily check-ins, then 3 short-sleep days -> review (the demo rule)."""
    stable = [7.0, 7.2, 6.9, 7.1, 7.3, 7.05, 7.15, 7.1]
    for day, hours in enumerate(stable, start=1):
        assert client.post("/api/checkins", json=make_checkin(day=day, sleep=hours)).status_code == 201
    mid = baseline(client, "crew_01")
    assert mid["status"] == "no_persistent_flag"
    last = None
    for day, hours in zip((9, 10, 11), (5.0, 4.8, 5.2)):
        last = client.post("/api/checkins", json=make_checkin(day=day, sleep=hours)).json()
    sleep = next(b for b in last["baselines"] if b["measurement"] == "sleep_duration")
    assert sleep["status"] == "review"
    assert sleep["provenance_kind"] == "manually_entered"
    assert client.get("/api/checkins", params={"subject_id": "crew_01"}).json()["count"] == 11


def test_resubmitting_the_same_checkin_does_not_change_the_result(client):
    for day in range(1, 9):
        client.post("/api/checkins", json=make_checkin(day=day, sleep=7.0 + day * 0.01))
    before = baseline(client, "crew_01")
    client.post("/api/checkins", json=make_checkin(day=8, sleep=7.0 + 8 * 0.01))
    assert baseline(client, "crew_01") == before


def test_data_persists_across_an_app_restart(tmp_path):
    db = str(tmp_path / "cv.sqlite3")
    first = TestClient(create_app(Settings(db_path=db)))
    first.post("/api/checkins", json=make_checkin(day=1))
    first.app.state.repo.close()
    second = TestClient(create_app(Settings(db_path=db)))
    assert second.get("/api/checkins", params={"subject_id": "crew_01"}).json()["count"] == 1
    assert second.get("/api/health").json()["observations"] == 31 + 4
