"""Observation envelope (source_id, provenance_kind, subject_id, study_id, ...).

Owner: Member 6 (Backend, Integration, QA & Deployment)

One measurement of one thing for one subject at one UTC instant. Field names are exactly
the ones Member 2's analytics consumes (`get_baseline_result(records, current)`), so
`Observation.to_record()` can be passed straight in. Mirrors shared/schemas/envelope.schema.json.
"""

import math
import re
from datetime import datetime, timezone
from typing import Optional, Union

from pydantic import BaseModel, ConfigDict, StrictFloat, StrictInt, field_validator, model_validator

from .provenance import ProvenanceKind, QualityState

_ID = re.compile(r"^[A-Za-z0-9_.:-]{1,80}$")


def normalize_utc(value: str) -> str:
    """Return an ISO-8601 UTC string ending in Z; reject naive or malformed timestamps."""
    if not isinstance(value, str):
        raise ValueError("timestamp_utc must be a string")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError("timestamp_utc must be ISO-8601") from exc
    if parsed.tzinfo is None:
        raise ValueError("timestamp_utc must include a UTC offset (use Z)")
    return parsed.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


class Observation(BaseModel):
    model_config = ConfigDict(extra="forbid", use_enum_values=True)

    source_id: str
    provenance_kind: ProvenanceKind
    subject_id: str
    study_id: str
    measurement: str
    # Strict: a JSON string like "7" is rejected rather than silently coerced.
    value: Optional[Union[StrictInt, StrictFloat]] = None
    units: str
    timestamp_utc: str
    quality_state: QualityState = QualityState.VALID
    reference_url: Optional[str] = None

    @field_validator("source_id", "subject_id", "study_id", "measurement")
    @classmethod
    def _identifier(cls, v: str) -> str:
        if not _ID.match(v):
            raise ValueError("must be 1-80 characters: letters, digits, _ . : -")
        return v

    @field_validator("units")
    @classmethod
    def _units(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("units must not be empty")
        return v

    @field_validator("value")
    @classmethod
    def _finite(cls, v):
        if v is None:
            return None
        if not math.isfinite(v):
            raise ValueError("value must be finite (no NaN or Infinity)")
        return float(v)

    @field_validator("timestamp_utc")
    @classmethod
    def _utc(cls, v: str) -> str:
        return normalize_utc(v)

    @model_validator(mode="after")
    def _missing_is_explicit(self) -> "Observation":
        # A missing reading must say so, and a reading marked valid must have a value.
        if self.value is None and self.quality_state != QualityState.MISSING.value:
            raise ValueError('a null value requires quality_state "missing"')
        if self.value is not None and self.quality_state == QualityState.MISSING.value:
            raise ValueError('quality_state "missing" requires a null value')
        return self

    def to_record(self) -> dict:
        """Plain dict in the shape the analytics module expects."""
        return self.model_dump()
