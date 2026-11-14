"""D01 OSDR Environmental Data App adapter

Owner: Member 4 (Environment & Radiation)

Reads the NASA OSDR EDA RR-1 telemetry export and builds the 300-point CO2 (ISS) series the
dashboard card shows. Integration notes (merged with Member 3's port):
- negative CO2 readings are quarantined (value null, quality_state "outlier"), never plotted;
- unreadable text such as "NA" is treated as missing instead of stopping the run;
- duplicate timestamps keep the first reading and are counted;
- the full telemetry export is not committed (re-use terms). Put it at
  data/nasa/osdr-eda/raw/RR-1_EDA_Telemetry_table.csv; without it, get_environment_series()
  returns the committed sample so the app and tests work from a clean checkout.

Rebuild the committed sample from the repository root:
    python -m backend.app.environment.osdr_eda
"""

import csv
import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Project root is 3 levels up from backend/app/environment/osdr_eda.py
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
INPUT_PATH = PROJECT_ROOT / "data" / "nasa" / "osdr-eda" / "raw" / "RR-1_EDA_Telemetry_table.csv"
OUTPUT_PATH = (
    PROJECT_ROOT
    / "frontend"
    / "src"
    / "features"
    / "environment-context"
    / "fixtures"
    / "environment.sample.json"
)
TIMESTAMP_COLUMN = "Controller_Time_GMT"
CO2_COLUMN = "CO2_ppm_ISS"
SAMPLE_SIZE = 300

Row = Tuple[datetime, Optional[float]]


def parse_timestamp(value: str) -> datetime:
    """Parse the source's minute-precision GMT timestamps as UTC."""
    parsed = datetime.strptime(value.strip(), "%Y-%m-%d %H:%M")
    return parsed.replace(tzinfo=timezone.utc)


def format_timestamp(value: datetime) -> str:
    """Format a UTC timestamp as ISO 8601 with an explicit Z suffix."""
    return value.isoformat(timespec="seconds").replace("+00:00", "Z")


def parse_co2_value(value: Optional[str]) -> Optional[float]:
    """Return a finite CO2 reading, or None for a missing, unreadable or non-finite reading."""
    if value is None or not value.strip():
        return None
    try:
        reading = float(value)
    except ValueError:
        return None  # e.g. "NA": unreadable, treated as missing rather than stopping the run
    if not math.isfinite(reading):
        return None
    return reading


def quality_of(value: Optional[float]) -> str:
    if value is None:
        return "missing"
    if value < 0:
        return "outlier"  # a negative concentration is physically impossible: quarantined
    return "valid"


def load_rows(path: Path, counts: Optional[Dict[str, int]] = None) -> List[Row]:
    """Read, validate, and chronologically sort telemetry rows.

    Duplicate timestamps keep the first reading; the number dropped is written to
    ``counts["duplicates"]`` when a dict is passed.
    """
    rows: List[Row] = []
    seen = set()
    duplicates = 0
    with path.open("r", encoding="utf-8-sig", newline="") as csv_file:
        reader = csv.DictReader(csv_file)
        fieldnames = reader.fieldnames or []
        missing_columns = [
            column
            for column in (TIMESTAMP_COLUMN, CO2_COLUMN)
            if column not in fieldnames
        ]
        if missing_columns:
            raise ValueError(
                "Telemetry CSV is missing required columns: "
                + ", ".join(missing_columns)
            )

        for line_number, row in enumerate(reader, start=2):
            timestamp_text = row.get(TIMESTAMP_COLUMN)
            if timestamp_text is None or not timestamp_text.strip():
                raise ValueError(
                    "Missing timestamp in telemetry CSV at line "
                    + str(line_number)
                )
            try:
                timestamp = parse_timestamp(timestamp_text)
            except ValueError as error:
                raise ValueError(
                    "Invalid telemetry value at line "
                    + str(line_number)
                    + ": "
                    + str(error)
                ) from error
            if timestamp in seen:
                duplicates += 1
                continue
            seen.add(timestamp)
            rows.append((timestamp, parse_co2_value(row.get(CO2_COLUMN))))

    if not rows:
        raise ValueError("Telemetry CSV contains no data rows")
    rows.sort(key=lambda row: row[0])
    if counts is not None:
        counts["duplicates"] = duplicates
    return rows


def downsample(rows: List[Row], target_size: int) -> List[Row]:
    """Select evenly spaced rows including both endpoints."""
    sample_size = min(target_size, len(rows))
    if sample_size == len(rows):
        return rows
    if sample_size == 1:
        return [rows[0]]

    last_index = len(rows) - 1
    return [
        rows[(index * last_index) // (sample_size - 1)]
        for index in range(sample_size)
    ]


def build_sample(rows: List[Row], duplicates: int = 0) -> Dict[str, object]:
    """Build the JSON document in M3's required environment fixture shape."""
    points = []
    for timestamp, value in downsample(rows, SAMPLE_SIZE):
        quality = quality_of(value)
        points.append({
            "timestamp_utc": format_timestamp(timestamp),
            "value": value if quality == "valid" else None,
            "quality_state": quality,
        })
    missing_count = sum(quality_of(value) == "missing" for _, value in rows)
    outlier_count = sum(quality_of(value) == "outlier" for _, value in rows)

    return {
        "source_id": "NASA_OSDR_EDA_RR1",
        "registry_id": "D01",
        "source_url": "https://visualization.osdr.nasa.gov/eda/",
        "citation": (
            "Data and visualizations are courtesy of the Environmental Data "
            "Application (EDA) (https://visualization.osdr.nasa.gov/eda/). "
            "Version: not displayed on the site (accessed 14 Nov 2026)."
        ),
        "display_title": "NASA RR-1 EDA: historical experimental environment",
        "provenance_kind": "nasa_measured",
        # Sensor/instrument ID is not given in the EDA export; do not imply a confirmed name.
        "instrument": "RR-1 habitat environmental telemetry (sensor ID not given in the EDA export)",
        "mission": "RR-1",
        "location": "ISS rodent habitat",
        "population": (
            "experimental environment, not individual astronaut physiology"
        ),
        "subject_id": None,
        "time_start_utc": format_timestamp(rows[0][0]),
        "time_end_utc": format_timestamp(rows[-1][0]),
        "time_precision": "minute",
        "row_count": len(rows),
        "series": [
            {
                "measurement": "co2_iss",
                "label": "CO2 (ISS)",
                "units": "ppm",
                "points": points,
            }
        ],
        "quality_summary": {
            "missing_count": missing_count,
            "outlier_count": outlier_count,
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


def get_environment_series(path: Optional[Path] = None) -> Dict[str, object]:
    """Load rows, build sample data, and return the environment series dictionary.

    Uses the full telemetry export when it is present locally; otherwise returns the committed
    300-point sample (works offline and from a clean checkout).
    """
    source = Path(path) if path is not None else INPUT_PATH
    if source.exists():
        counts: Dict[str, int] = {}
        rows = load_rows(source, counts)
        return build_sample(rows, counts.get("duplicates", 0))
    with OUTPUT_PATH.open(encoding="utf-8") as json_file:
        return json.load(json_file)


def main() -> None:
    if not INPUT_PATH.exists():
        raise SystemExit(f"Telemetry export not found at {INPUT_PATH}. See data/nasa/osdr-eda/README.md.")
    sample = get_environment_series(INPUT_PATH)
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT_PATH.open("w", encoding="utf-8", newline="\n") as json_file:
        json.dump(sample, json_file, indent=2, allow_nan=False)
        json_file.write("\n")
    print("Successfully generated environment sample fixture at:", OUTPUT_PATH)


if __name__ == "__main__":
    main()
