"""D01 NASA OSDR Environmental Data Application (EDA) adapter: RR-1 telemetry.

Owner: Member 4 (Environment & Radiation). Adapter written by Member 4 (Muhammad Bilal Hussain);
moved into the project structure during integration, with input-hygiene fixes:
negative readings are quarantined, unreadable text is treated as missing, duplicate timestamps
are dropped and counted.

The full RR-1 telemetry export is NOT committed (re-use terms; see data/nasa/osdr-eda/README.md).
Download it to data/nasa/osdr-eda/raw/RR-1_EDA_Telemetry_table.csv, then run:

    python -m backend.app.environment.osdr_eda

to rebuild the committed 300-point sample used by the dashboard.
"""

from __future__ import annotations

import csv
import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple

REPO_ROOT = Path(__file__).resolve().parents[3]
RAW_PATH = REPO_ROOT / "data" / "nasa" / "osdr-eda" / "raw" / "RR-1_EDA_Telemetry_table.csv"
SNAPSHOT_PATH = REPO_ROOT / "frontend" / "src" / "features" / "environment-context" / "fixtures" / "environment.sample.json"

TIMESTAMP_COLUMN = "Controller_Time_GMT"
CO2_COLUMN = "CO2_ppm_ISS"
SAMPLE_SIZE = 300

CITATION = (
    "Data and visualizations are courtesy of the Environmental Data Application (EDA) "
    "(https://visualization.osdr.nasa.gov/eda/). Version: not displayed on the site (accessed 14 Nov 2026)."
)

Row = Tuple[datetime, Optional[float], str]  # (timestamp, value or None, quality_state)


def parse_timestamp(value: str) -> datetime:
    """Parse the source's minute-precision GMT timestamps as UTC."""
    parsed = datetime.strptime(value.strip(), "%Y-%m-%d %H:%M")
    return parsed.replace(tzinfo=timezone.utc)


def format_timestamp(value: datetime) -> str:
    """ISO 8601 with an explicit Z suffix."""
    return value.isoformat(timespec="seconds").replace("+00:00", "Z")


def parse_co2(value: Optional[str]) -> Tuple[Optional[float], str]:
    """Return (reading, quality_state). Never returns 0 or NaN for a bad reading."""
    if value is None or not value.strip():
        return None, "missing"
    try:
        reading = float(value)
    except ValueError:
        return None, "missing"  # e.g. "NA": unreadable, treated as missing rather than crashing the run
    if not math.isfinite(reading):
        return None, "missing"
    if reading < 0:
        return None, "outlier"  # physically impossible concentration: quarantined, not plotted
    return reading, "valid"


def load_rows(path: Path = RAW_PATH) -> Tuple[List[Row], int]:
    """Read, validate and chronologically sort telemetry rows. Returns (rows, duplicates_dropped)."""
    rows: List[Row] = []
    seen = set()
    duplicates = 0
    with path.open("r", encoding="utf-8-sig", newline="") as csv_file:
        reader = csv.DictReader(csv_file)
        missing_columns = [c for c in (TIMESTAMP_COLUMN, CO2_COLUMN) if c not in (reader.fieldnames or [])]
        if missing_columns:
            raise ValueError("Telemetry CSV is missing required columns: " + ", ".join(missing_columns))

        for line_number, row in enumerate(reader, start=2):
            text = row.get(TIMESTAMP_COLUMN)
            if text is None or not text.strip():
                raise ValueError(f"Missing timestamp in telemetry CSV at line {line_number}")
            try:
                timestamp = parse_timestamp(text)
            except ValueError as error:
                raise ValueError(f"Invalid timestamp at line {line_number}: {error}") from error
            if timestamp in seen:
                duplicates += 1  # keep the first reading; input order must not silently double a point
                continue
            seen.add(timestamp)
            value, quality = parse_co2(row.get(CO2_COLUMN))
            rows.append((timestamp, value, quality))

    if not rows:
        raise ValueError("Telemetry CSV contains no data rows")
    rows.sort(key=lambda r: r[0])
    return rows, duplicates


def downsample(rows: List[Row], target_size: int = SAMPLE_SIZE) -> List[Row]:
    """Select evenly spaced rows including both endpoints."""
    size = min(target_size, len(rows))
    if size == len(rows):
        return rows
    if size == 1:
        return [rows[0]]
    last = len(rows) - 1
    return [rows[(i * last) // (size - 1)] for i in range(size)]


def build_sample(rows: List[Row], duplicates: int = 0) -> Dict[str, object]:
    """Build the environment series in the shape the dashboard card consumes."""
    points = [
        {"timestamp_utc": format_timestamp(t), "value": v, "quality_state": q}
        for t, v, q in downsample(rows)
    ]
    missing = sum(q == "missing" for _, _, q in rows)
    outliers = sum(q == "outlier" for _, _, q in rows)
    return {
        "source_id": "NASA_OSDR_EDA_RR1",
        "registry_id": "D01",
        "source_url": "https://visualization.osdr.nasa.gov/eda/",
        "citation": CITATION,
        "display_title": "NASA RR-1 EDA: historical experimental environment",
        "provenance_kind": "nasa_measured",
        "instrument": "RR-1 habitat environmental telemetry (sensor ID not given in the EDA export)",
        "mission": "RR-1",
        "location": "ISS rodent habitat",
        "population": "experimental environment, not individual astronaut physiology",
        "subject_id": None,
        "time_start_utc": format_timestamp(rows[0][0]),
        "time_end_utc": format_timestamp(rows[-1][0]),
        "time_precision": "minute",
        "row_count": len(rows),
        "series": [{"measurement": "co2_iss", "label": "CO2 (ISS)", "units": "ppm", "points": points}],
        "quality_summary": {
            "missing_count": missing,
            "outlier_count": outliers,
            "duplicate_timestamps_dropped": duplicates,
            "notes": (
                "Structure, timestamps and summary statistics checked against the EDA RR-1 tables. "
                "ISS CO2 repeats 2646 ppm for 1,837 consecutive readings (21-27 Sep 2014); cause not established."
            ),
        },
        "limitations": [
            "Historical instrument data. Not personal exposure or effective dose.",
            "Rodent-habitat environment, not astronaut cabin air or a crew member's record.",
            "Downsampled to 300 evenly spaced readings from the full export for display.",
        ],
        "is_fallback_not_ingested": False,
    }


def write_snapshot(sample: Dict[str, object], path: Path = SNAPSHOT_PATH) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as f:
        json.dump(sample, f, indent=2, allow_nan=False)
        f.write("\n")


def main() -> None:
    rows, duplicates = load_rows(RAW_PATH)
    write_snapshot(build_sample(rows, duplicates))


if __name__ == "__main__":
    main()
