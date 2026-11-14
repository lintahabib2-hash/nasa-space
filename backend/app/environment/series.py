"""Common environment series wrappers: get_environment_series()

Owner: Member 4 (Environment & Radiation)

Returns source_id, instrument, units and quality for the primary NASA environment series,
after checking the contract the dashboard relies on.
"""

import math
from typing import Any, Dict

from .osdr_eda import get_environment_series as get_eda_series

REQUIRED_KEYS = ("source_id", "citation", "provenance_kind", "instrument", "series", "limitations")


def get_environment_series() -> Dict[str, Any]:
    """Return the primary NASA RR-1 EDA environment series."""
    data = get_eda_series()
    validate(data)
    return data


def validate(data: Dict[str, Any]) -> None:
    """Raise ValueError if the series breaks the environment contract."""
    for key in REQUIRED_KEYS:
        if key not in data:
            raise ValueError(f"Environment series missing {key}")
    if data.get("subject_id") is not None:
        raise ValueError("Environment data must not carry a crew subject_id")
    for series in data["series"]:
        for key in ("measurement", "units", "points"):
            if key not in series:
                raise ValueError(f"Series missing {key}")
        previous = None
        for point in series["points"]:
            value = point["value"]
            if value is not None and (not isinstance(value, (int, float)) or not math.isfinite(value)):
                raise ValueError("Non-finite environment value")
            if value is None and point["quality_state"] == "valid":
                raise ValueError("Missing value marked valid")
            if previous is not None and point["timestamp_utc"] < previous:
                raise ValueError("Environment timestamps not in order")
            previous = point["timestamp_utc"]
