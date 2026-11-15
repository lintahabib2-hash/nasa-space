"""The static offline snapshot equals what the live API answers

Owner: Member 6 (Backend, Integration, QA & Deployment)
"""

import hashlib
import json
import math

import pytest
from jsonschema import Draft202012Validator

from backend.app.config import REPO_ROOT, Settings
from backend.tests.conftest import SCENARIO_SUBJECTS

SNAP = REPO_ROOT / "frontend/public/data"
SCHEMAS = REPO_ROOT / "shared/schemas"


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def validator(name):
    return Draft202012Validator(load(SCHEMAS / name))


def test_committed_snapshot_is_up_to_date():
    from backend.scripts.export_static_snapshot import build_files
    stale = [str(p.relative_to(REPO_ROOT)) for p, text in build_files(Settings()).items()
             if not p.exists() or p.read_text(encoding="utf-8") != text]
    assert not stale, f"run: python backend/scripts/export_static_snapshot.py  (stale: {stale})"


def test_snapshot_baselines_equal_live_api(client):
    snap = load(SNAP / "baselines.json")
    for subject in SCENARIO_SUBJECTS.values():
        assert snap[subject] == client.get("/api/baseline/all", params={"subject_id": subject}).json()


def test_snapshot_environment_equals_live_api(client):
    assert load(SNAP / "environment.json") == client.get("/api/environment").json()


def test_snapshot_files_match_their_schemas():
    assert not list(validator("environment-series.schema.json").iter_errors(load(SNAP / "environment.json")))
    assert not list(validator("snapshot-manifest.schema.json").iter_errors(load(SNAP / "manifest.json")))
    resp = validator("api-response.schema.json")
    for subject, results in load(SNAP / "baselines.json").items():
        for r in results:
            assert not list(resp.iter_errors(r)), (subject, r)


def test_manifest_hashes_and_sizes_match_the_files():
    manifest = load(SNAP / "manifest.json")
    for name, meta in manifest["files"].items():
        data = (SNAP / name).read_bytes()
        assert hashlib.sha256(data).hexdigest() == meta["sha256"], name
        assert len(data) == meta["bytes"], name


@pytest.mark.parametrize("name", ["stable", "drift", "missing"])
def test_mocks_are_valid_api_responses(name):
    assert not list(validator("api-response.schema.json").iter_errors(load(REPO_ROOT / f"shared/mocks/baseline-{name}.json")))


def test_no_nan_or_infinity_in_any_snapshot_file():
    def walk(x):
        if isinstance(x, float):
            assert math.isfinite(x)
        elif isinstance(x, dict):
            [walk(v) for v in x.values()]
        elif isinstance(x, list):
            [walk(v) for v in x]
    for f in SNAP.glob("*.json"):
        text = f.read_text(encoding="utf-8")
        assert "NaN" not in text and "Infinity" not in text, f.name
        walk(json.loads(text))
