"""get_environment_series(): source_id, instrument, units, quality_state

Owner: Member 4 (Environment & Radiation).

Returns one historical NASA environment series with its metadata. By default it reads the committed
sample snapshot (works offline and from a clean checkout); pass ``raw_csv`` to rebuild from a local
copy of the full RR-1 EDA export instead.
"""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Dict, Optional

from . import osdr_eda

REQUIRED_KEYS = ("source_id", "citation", "provenance_kind", "instrument", "series", "limitations")


def get_environment_series(raw_csv: Optional[Path] = None, snapshot: Path = osdr_eda.SNAPSHOT_PATH) -> Dict[str, object]:
    if raw_csv is not None:
        rows, duplicates = osdr_eda.load_rows(Path(raw_csv))
        data = osdr_eda.build_sample(rows, duplicates)
    else:
        with Path(snapshot).open(encoding="utf-8") as f:
            data = json.load(f)
    validate(data)
    return data


def validate(data: Dict[str, object]) -> None:
    """Contract checks the dashboard relies on. Raises ValueError on a broken series."""
    for key in REQUIRED_KEYS:
        if key not in data:
            raise ValueError(f"Environment series missing {key}")
    if data.get("subject_id") is not None:
        raise ValueError("Environment data must not carry a crew subject_id")
    for s in data["series"]:  # type: ignore[union-attr]
        for key in ("measurement", "units", "points"):
            if key not in s:
                raise ValueError(f"Series missing {key}")
        previous = None
        for p in s["points"]:
            v = p["value"]
            if v is not None and (not isinstance(v, (int, float)) or not math.isfinite(v)):
                raise ValueError("Non-finite environment value")
            if v is None and p["quality_state"] == "valid":
                raise ValueError("Missing value marked valid")
            if previous is not None and p["timestamp_utc"] < previous:
                raise ValueError("Environment timestamps not in order")
            previous = p["timestamp_utc"]
