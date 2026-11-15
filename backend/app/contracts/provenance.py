"""Provenance kinds, quality states and analytics statuses (enums).

Owner: Member 6 (Backend, Integration, QA & Deployment)

These mirror shared/schemas/envelope.schema.json and the badges in the README ground rules.
A value with an unknown provenance kind is rejected at the API boundary, so a number can
never reach the UI without a label saying where it came from.
"""

from enum import Enum


class ProvenanceKind(str, Enum):
    NASA_MEASURED = "nasa_measured"
    ANALOG_MEASURED = "analog_measured"
    EXTERNAL_EARTH = "external_earth"
    SIMULATED = "simulated"
    MANUALLY_ENTERED = "manually_entered"
    CREW_SELF_REPORT = "crew_self_report"


class QualityState(str, Enum):
    VALID = "valid"
    MISSING = "missing"
    OUTLIER = "outlier"
    UNKNOWN = "unknown"


# Statuses emitted by backend/app/analytics (Member 2) plus "no_observations" (Member 6:
# the series has no stored readings at all). The UI maps these to chips in statusDisplay.ts.
BASELINE_STATUSES = (
    "no_persistent_flag",
    "review",
    "insufficient_history",
    "insufficient_scale",
    "insufficient_persistence_history",
    "unknown",
    "no_observations",
)

PROVENANCE_VALUES = tuple(p.value for p in ProvenanceKind)
QUALITY_VALUES = tuple(q.value for q in QualityState)
