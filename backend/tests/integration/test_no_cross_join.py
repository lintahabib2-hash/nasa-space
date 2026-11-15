"""No sources are joined on timestamp across different studies or locations

Owner: Member 6 (Backend, Integration, QA & Deployment)
"""

from backend.tests.conftest import make_observation


def baseline(client, subject="X01_stable"):
    return client.get("/api/baseline", params={"subject_id": subject, "measurement": "sleep_duration"}).json()


def test_other_sources_for_the_same_subject_never_enter_the_history(client):
    before = baseline(client)
    # Same subject + measurement, overlapping timestamps (days 1-9, before the latest reading),
    # but a DIFFERENT source/study and very different values (within the input bounds).
    noise = [make_observation(d, 12.0 + d, subject="X01_stable", source_id="OTHER_SOURCE",
                              study_id="other_study", provenance_kind="analog_measured") for d in range(1, 10)]
    assert client.post("/api/observations", json=noise).status_code == 201
    after = baseline(client)
    assert after == before, "a different source changed the result: cross-join leaked"


def test_environment_series_carries_no_subject_and_no_crew_id(client):
    env = client.get("/api/environment").json()
    assert env["subject_id"] is None
    crew_ids = {o["subject_id"] for o in client.get("/api/observations").json()["observations"]}
    assert not crew_ids & {env["source_id"], env["registry_id"]}


def test_environment_source_never_appears_as_a_crew_observation(client):
    env = client.get("/api/environment").json()
    sources = {o["source_id"] for o in client.get("/api/observations").json()["observations"]}
    assert env["source_id"] not in sources


def test_crew_responses_never_contain_environment_fields(client):
    for b in client.get("/api/baseline/all", params={"subject_id": "X01_drift"}).json() + [baseline(client)]:
        assert not {"series", "instrument", "mission", "location"} & set(b)


def test_environment_cannot_be_requested_as_a_crew_subject(client):
    env = client.get("/api/environment").json()
    r = client.get("/api/baseline", params={"subject_id": env["source_id"], "measurement": env["series"][0]["measurement"]})
    assert r.json()["status"] == "no_observations"


def test_baseline_uses_only_the_latest_series_when_a_subject_has_two(client):
    """Two studies for one subject are scored separately, never pooled."""
    client.post("/api/observations", json=[
        make_observation(d, 7.0 + (d % 3) * 0.1, subject="two_series", study_id="A", source_id="SRC_A") for d in range(1, 10)])
    client.post("/api/observations", json=[
        make_observation(d, 3.0 + (d % 3) * 0.1, subject="two_series", study_id="B", source_id="SRC_B") for d in range(1, 12)])
    r = baseline(client, "two_series")
    assert r["study_id"] == "B" and r["baseline_value"] < 4, "series A (about 7 h) must not blend into series B"
