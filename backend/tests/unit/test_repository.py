"""Local persistence rules.

Owner: Member 6 (Backend, Integration, QA & Deployment)
"""

import json
import sqlite3

import pytest

from backend.app.config import REPO_ROOT
from backend.app.storage import Repository, RepositoryError
from backend.tests.conftest import make_checkin, make_observation

SCHEMA = REPO_ROOT / "shared/schemas/checkin.schema.json"


@pytest.fixture()
def repo():
    r = Repository(":memory:", SCHEMA)
    yield r
    r.close()


def test_add_and_list_roundtrip_sorted(repo):
    repo.add_observations([make_observation(3, 7.0), make_observation(1, 7.2), make_observation(2, 6.9)])
    days = [o["timestamp_utc"][8:10] for o in repo.list_observations(subject_id="crew_test")]
    assert days == ["01", "02", "03"]


def test_same_series_and_timestamp_overwrites_not_duplicates(repo):
    repo.add_observations([make_observation(1, 7.0)])
    repo.add_observations([make_observation(1, 6.0)])
    rows = repo.list_observations()
    assert len(rows) == 1 and rows[0]["value"] == 6.0


def test_different_sources_at_same_time_are_kept_apart(repo):
    repo.add_observations([make_observation(1, 7.0), make_observation(1, 9.0, source_id="OTHER")])
    assert len(repo.list_observations()) == 2


def test_bad_batch_writes_nothing(repo):
    with pytest.raises(RepositoryError, match=r"observation\[1\]"):
        repo.add_observations([make_observation(1, 7.0), make_observation(2, float("nan"))])
    assert repo.counts()["observations"] == 0


def test_missing_value_is_stored_as_null_and_flagged(repo):
    repo.add_observations([make_observation(1, None)])
    (row,) = repo.list_observations()
    assert row["value"] is None and row["quality_state"] == "missing"


def test_filters(repo):
    repo.add_observations([make_observation(1, 7.0), make_observation(1, 3.0, measurement="mood", units="score_1_5"),
                           make_observation(1, 7.0, subject="other")])
    assert len(repo.list_observations(subject_id="crew_test", measurement="mood")) == 1
    assert repo.subjects() == ["crew_test", "other"]
    assert repo.measurements("crew_test") == ["mood", "sleep_duration"]


def test_checkin_is_stored_and_derives_observations(repo):
    n = repo.add_checkin(make_checkin(day=5, sleep=7.5))
    assert n == 4
    assert len(repo.list_checkins("crew_01")) == 1
    sleep = repo.list_observations(subject_id="crew_01", measurement="sleep_duration")
    assert sleep[0]["value"] == 7.5 and sleep[0]["provenance_kind"] == "manually_entered"


def test_resubmitting_a_checkin_is_idempotent(repo):
    repo.add_checkin(make_checkin(day=5))
    repo.add_checkin(make_checkin(day=5))
    assert repo.counts() == {"observations": 4, "checkins": 1}


@pytest.mark.parametrize("mutate,fragment", [
    (lambda c: c["indicators"]["sleep_duration"].update(value=99), "sleep_duration"),
    (lambda c: c.update(extra="x"), "extra"),
    (lambda c: c.update(provenance_kind="simulated"), "provenance_kind"),
    (lambda c: c["indicators"].pop("mood"), "mood"),
    (lambda c: c["indicators"]["mood"].update(value=3.5), "mood"),
])
def test_invalid_checkins_are_rejected_and_nothing_is_stored(repo, mutate, fragment):
    c = make_checkin()
    mutate(c)
    with pytest.raises(RepositoryError):
        repo.add_checkin(c)
    assert repo.counts() == {"observations": 0, "checkins": 0}


def test_checkin_indicator_for_another_subject_is_rejected(repo):
    c = make_checkin()
    c["indicators"]["mood"]["subject_id"] = "someone_else"
    with pytest.raises(RepositoryError, match="does not match"):
        repo.add_checkin(c)
    assert repo.counts()["checkins"] == 0


def test_data_survives_reopening_the_database(tmp_path):
    path = str(tmp_path / "db" / "cv.sqlite3")
    r1 = Repository(path, SCHEMA)
    r1.add_checkin(make_checkin(day=2))
    r1.close()
    r2 = Repository(path, SCHEMA)
    assert r2.counts() == {"observations": 4, "checkins": 1}
    r2.close()


def test_database_from_a_newer_version_is_refused(tmp_path):
    path = tmp_path / "cv.sqlite3"
    db = sqlite3.connect(path)
    db.execute("PRAGMA user_version = 99")
    db.commit()
    db.close()
    with pytest.raises(RepositoryError, match="newer app version"):
        Repository(str(path), SCHEMA)


def test_seed_refuses_a_file_not_labelled_simulated(repo, tmp_path):
    f = tmp_path / "x.json"
    f.write_text(json.dumps({"provenance_kind": "nasa_measured", "not_real_astronaut_data": False, "scenarios": []}))
    with pytest.raises(RepositoryError, match="not labelled simulated"):
        repo.seed_simulated(f)


def test_seed_loads_all_x01_scenarios(repo):
    n = repo.seed_simulated(REPO_ROOT / "data/simulated/X01_crew_scenarios.json")
    assert n == 31
    assert set(repo.subjects()) == {"X01_stable", "X01_downward_drift", "X01_missing_observation"}
