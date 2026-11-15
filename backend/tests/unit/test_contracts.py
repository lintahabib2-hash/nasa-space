"""Observation envelope: Pydantic model and shared JSON schema must agree.

Owner: Member 6 (Backend, Integration, QA & Deployment)
"""

import json
import math
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator
from pydantic import ValidationError

from backend.app.config import REPO_ROOT
from backend.app.contracts import Observation

SCHEMA = Draft202012Validator(json.loads((REPO_ROOT / "shared/schemas/envelope.schema.json").read_text(encoding="utf-8")))


def good(**over):
    rec = {
        "source_id": "X01", "provenance_kind": "simulated", "subject_id": "s1", "study_id": "st",
        "measurement": "sleep_duration", "value": 7.0, "units": "hours",
        "timestamp_utc": "2026-11-01T07:00:00Z", "quality_state": "valid",
    }
    rec.update(over)
    return rec


# (label, record, should_be_valid)
CASES = [
    ("valid", good(), True),
    ("valid missing", good(value=None, quality_state="missing"), True),
    ("unknown provenance", good(provenance_kind="real_astronaut"), False),
    ("null value but valid", good(value=None), False),
    ("missing but has value", good(quality_state="missing"), False),
    ("empty units", good(units=" "), False),
    ("bad id characters", good(subject_id="a b"), False),
    ("string value", good(value="7"), False),
    ("naive timestamp", good(timestamp_utc="2026-11-01T07:00:00"), False),
    ("unknown quality", good(quality_state="great"), False),
]


@pytest.mark.parametrize("label,record,valid", CASES, ids=[c[0] for c in CASES])
def test_pydantic_and_json_schema_agree(label, record, valid):
    try:
        Observation.model_validate(record)
        pydantic_ok = True
    except ValidationError:
        pydantic_ok = False
    schema_ok = not list(SCHEMA.iter_errors(record))
    assert pydantic_ok is valid, f"pydantic disagreed on {label}"
    assert schema_ok is valid, f"JSON schema disagreed on {label}"


@pytest.mark.parametrize("bad", [math.nan, math.inf, -math.inf])
def test_non_finite_values_are_rejected(bad):
    with pytest.raises(ValidationError):
        Observation.model_validate(good(value=bad))


def test_timestamps_are_normalised_to_utc_z():
    obs = Observation.model_validate(good(timestamp_utc="2026-11-01T12:00:00+05:00"))
    assert obs.timestamp_utc == "2026-11-01T07:00:00Z"
    obs = Observation.model_validate(good(timestamp_utc="2026-11-01T07:00:00.000Z"))
    assert obs.timestamp_utc == "2026-11-01T07:00:00Z"


def test_unexpected_fields_are_forbidden():
    with pytest.raises(ValidationError):
        Observation.model_validate(good(diagnosis="none"))


def test_to_record_is_analytics_ready():
    rec = Observation.model_validate(good()).to_record()
    assert rec["provenance_kind"] == "simulated" and isinstance(rec["provenance_kind"], str)
    assert rec["quality_state"] == "valid"
