"""Every output keeps provenance_kind, source_id and the citation

Owner: Member 6 (Backend, Integration, QA & Deployment)
"""

import json

from backend.app.config import REPO_ROOT
from backend.app.contracts import PROVENANCE_VALUES
from backend.tests.conftest import SCENARIO_SUBJECTS, make_checkin


def test_every_stored_observation_has_a_known_provenance_and_source(client):
    rows = client.get("/api/observations").json()["observations"]
    assert rows
    for r in rows:
        assert r["provenance_kind"] in PROVENANCE_VALUES
        assert r["source_id"] and r["study_id"]


def test_simulated_data_is_never_labelled_nasa_measured(client):
    rows = client.get("/api/observations").json()["observations"]
    x01 = [r for r in rows if r["source_id"] == "X01"]
    assert x01 and all(r["provenance_kind"] == "simulated" for r in x01)
    assert not [r for r in rows if r["provenance_kind"] == "nasa_measured"]


def test_every_baseline_carries_provenance_and_the_non_diagnostic_flag(client, checkin_factory):
    client.post("/api/checkins", json=checkin_factory(day=1))
    for subject in [*SCENARIO_SUBJECTS.values(), "crew_01"]:
        for b in client.get("/api/baseline/all", params={"subject_id": subject}).json():
            assert b["provenance_kind"] in PROVENANCE_VALUES, b
            assert b["source_id"], b
            assert b["not_medical_diagnosis"] is True
            assert b["severity_basis"] == "unvalidated_demo_statistical_rule"
            assert b["reasons"], "every status must explain itself"


def test_checkin_data_is_labelled_manually_entered(client, checkin_factory):
    client.post("/api/checkins", json=checkin_factory(day=1))
    rows = client.get("/api/observations", params={"subject_id": "crew_01"}).json()["observations"]
    assert rows and all(r["provenance_kind"] == "manually_entered" for r in rows)


def test_environment_output_keeps_source_citation_and_limits(client):
    env = client.get("/api/environment").json()
    assert env["source_id"] and env["registry_id"] and env["source_url"].startswith("https://")
    assert "courtesy of" in env["citation"].lower() or "nasa" in env["citation"].lower()
    assert any("not personal" in lim.lower() for lim in env["limitations"])
    assert env["provenance_kind"] == "nasa_measured"


def test_health_and_snapshot_declare_no_real_astronaut_data(client):
    assert client.get("/api/health").json()["contains_real_astronaut_data"] is False
    manifest = json.loads((REPO_ROOT / "frontend/public/data/manifest.json").read_text(encoding="utf-8"))
    assert manifest["contains_real_astronaut_data"] is False
