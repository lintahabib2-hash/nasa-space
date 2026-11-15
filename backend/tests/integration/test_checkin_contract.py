"""Cross-team contract: a check-in exactly as Member 5's form builds it is accepted by the API.

shared/mocks/checkin.sample.json was produced by the frontend's real buildCheckin()
(frontend/src/features/checkin/checkinSchema.ts) with every optional vital filled in. If either side
changes the format, this test (or the frontend's checkin tests) fails instead of the live demo.
"""

import json
from pathlib import Path

SAMPLE = Path(__file__).resolve().parents[3] / "shared" / "mocks" / "checkin.sample.json"


def load_sample():
    return json.loads(SAMPLE.read_text(encoding="utf-8"))


def test_member5_record_is_accepted_and_every_indicator_stored(client):
    record = load_sample()
    response = client.post("/api/checkins", json=record)
    assert response.status_code == 201, response.text
    assert response.json()["observations_stored"] == len(record["indicators"]) == 11


def test_resending_the_same_record_does_not_duplicate_it(client):
    record = load_sample()
    assert client.post("/api/checkins", json=record).status_code == 201
    assert client.post("/api/checkins", json=record).status_code == 201  # offline outbox retry
    listed = client.get("/api/checkins", params={"subject_id": record["subject_id"]}).json()
    assert [c["record_id"] for c in listed["checkins"]].count(record["record_id"]) == 1


def test_self_reported_entries_keep_their_provenance_and_never_mix_with_simulated(client):
    record = load_sample()
    client.post("/api/checkins", json=record)
    result = client.get("/api/baseline", params={"subject_id": record["subject_id"], "measurement": "sleep_duration"}).json()
    assert result["provenance_kind"] == "manually_entered"
    assert result["not_medical_diagnosis"] is True


def test_out_of_bounds_value_is_refused(client):
    record = load_sample()
    record["record_id"] = "contract-bad-sleep"
    record["indicators"]["sleep_duration"]["value"] = 30
    assert client.post("/api/checkins", json=record).status_code == 422
