"""HTTP routes.

Owner: Member 6 (Backend, Integration, QA & Deployment)
"""

import pytest

from backend.tests.conftest import make_checkin, make_observation


def test_health_reports_counts_and_no_real_data(client):
    body = client.get("/api/health").json()
    assert body["status"] == "ok" and body["observations"] == 31 and body["contains_real_astronaut_data"] is False


def test_observations_filtering(client):
    r = client.get("/api/observations", params={"subject_id": "X01_stable"}).json()
    assert r["count"] == 10 and all(o["subject_id"] == "X01_stable" for o in r["observations"])


def test_post_observation_valid_and_invalid(client):
    assert client.post("/api/observations", json=make_observation(1, 7.0)).status_code == 201
    r = client.post("/api/observations", json=[make_observation(2, 7.0), make_observation(3, 7.0, provenance_kind="made_up")])
    assert r.status_code == 422
    assert client.get("/api/observations", params={"subject_id": "crew_test"}).json()["count"] == 1


def test_baseline_for_unknown_subject_is_no_observations_not_an_error(client):
    r = client.get("/api/baseline", params={"subject_id": "ghost", "measurement": "sleep_duration"})
    assert r.status_code == 200 and r.json()["status"] == "no_observations"


def test_baseline_requires_parameters(client):
    assert client.get("/api/baseline", params={"subject_id": "x"}).status_code == 422


def test_baseline_all_lists_every_measurement(client, checkin_factory):
    client.post("/api/checkins", json=checkin_factory(day=1))
    r = client.get("/api/baseline/all", params={"subject_id": "crew_01"}).json()
    assert sorted(x["measurement"] for x in r) == ["exercise_minutes", "mood", "sleep_duration", "stress"]


def test_checkin_post_returns_baselines_and_is_listed(client, checkin_factory):
    r = client.post("/api/checkins", json=checkin_factory(day=1))
    assert r.status_code == 201
    body = r.json()
    assert body["observations_stored"] == 4 and len(body["baselines"]) == 4
    assert all(b["not_medical_diagnosis"] is True for b in body["baselines"])
    assert client.get("/api/checkins", params={"subject_id": "crew_01"}).json()["count"] == 1


def test_invalid_checkin_is_a_422_with_a_readable_reason(client, checkin_factory):
    bad = checkin_factory(day=1)
    bad["indicators"]["sleep_duration"]["value"] = 99
    r = client.post("/api/checkins", json=bad)
    assert r.status_code == 422 and "sleep_duration" in r.json()["detail"]


def test_environment_route_serves_nasa_series(client):
    r = client.get("/api/environment")
    assert r.status_code == 200
    body = r.json()
    assert body["provenance_kind"] == "nasa_measured" and body["subject_id"] is None


def test_environment_failure_is_503_never_fake_data(client, monkeypatch):
    def boom():
        raise ValueError("Environment series missing citation")
    monkeypatch.setattr("backend.app.api.environment.environment_payload", boom)
    r = client.get("/api/environment")
    assert r.status_code == 503
    assert r.json()["detail"]["error"] == "environment_unavailable"
    assert "series" not in r.json()["detail"]


def test_knowledge_and_sources_are_served_unchanged(client):
    assert "indicators" in client.get("/api/knowledge").json()
    assert "sources" in client.get("/api/sources").json()


def test_cors_allows_local_frontend_only(client):
    ok = client.get("/api/health", headers={"Origin": "http://localhost:5173"})
    assert ok.headers.get("access-control-allow-origin") == "http://localhost:5173"
    other = client.get("/api/health", headers={"Origin": "https://evil.example"})
    assert "access-control-allow-origin" not in other.headers


@pytest.mark.parametrize("method", ["put", "delete", "patch"])
def test_write_methods_other_than_post_are_not_exposed(client, method):
    assert getattr(client, method)("/api/observations").status_code == 405
