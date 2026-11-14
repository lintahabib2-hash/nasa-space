"""D01 OSDR Environmental Data App adapter

Owner: Member 4 (Environment & Radiation)
"""

import csv
import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Project root is 3 levels up from backend/app/environment/osdr_eda.py
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
INPUT_PATH = PROJECT_ROOT / "data" / "nasa" / "osdr-eda" / "RR-1_EDA_Telemetry_table.csv"
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


def parse_timestamp(value: str) -> datetime:
    """Parse the source's minute-precision GMT timestamps as UTC."""
    parsed = datetime.strptime(value.strip(), "%Y-%m-%d %H:%M")
    return parsed.replace(tzinfo=timezone.utc)


def format_timestamp(value: datetime) -> str:
    """Format a UTC timestamp as ISO 8601 with an explicit Z suffix."""
    return value.isoformat(timespec="seconds").replace("+00:00", "Z")


def parse_co2_value(value: Optional[str]) -> Optional[float]:
    """Return a finite CO2 reading, or None for a missing/non-finite reading."""
    if value is None or not value.strip():
        return None

    reading = float(value)
    if not math.isfinite(reading):
        return None
    return reading


def load_rows(path: Path) -> List[Tuple[datetime, Optional[float]]]:
    """Read, validate, and chronologically sort telemetry rows."""
    rows: List[Tuple[datetime, Optional[float]]] = []
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
                co2_value = parse_co2_value(row.get(CO2_COLUMN))
            except ValueError as error:
                raise ValueError(
                    "Invalid telemetry value at line "
                    + str(line_number)
                    + ": "
                    + str(error)
                ) from error
            rows.append((timestamp, co2_value))

    if not rows:
        raise ValueError("Telemetry CSV contains no data rows")
    rows.sort(key=lambda row: row[0])
    return rows


def downsample(
    rows: List[Tuple[datetime, Optional[float]]], target_size: int
) -> List[Tuple[datetime, Optional[float]]]:
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


def build_sample(
    rows: List[Tuple[datetime, Optional[float]]]
) -> Dict[str, object]:
    """Build the JSON document in M3's required environment fixture shape."""
    points = [
        {
            "timestamp_utc": format_timestamp(timestamp),
            "value": value,
            "quality_state": "valid" if value is not None else "missing",
        }
        for timestamp, value in downsample(rows, SAMPLE_SIZE)
    ]
    missing_count = sum(value is None for _, value in rows)

    return {
        "source_id": "NASA_OSDR_EDA_RR1",
        "source_url": "https://visualization.osdr.nasa.gov/eda/",
        "citation": (
            "Data and visualizations are courtesy of the Environmental Data "
            "Application (EDA) (https://visualization.osdr.nasa.gov/eda/). "
            "Version: not displayed on the site (accessed 14 Nov 2026)."
        ),
        "display_title": "NASA RR-1 EDA: historical experimental environment",
        "provenance_kind": "nasa_measured",
        "instrument": "ISS Environmental Telemetry Sensor",
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
            "outlier_count": 0,
            "notes": "Verified against EDA RR-1 telemetry",
        },
        "limitations": [
            "Historical instrument data. Not personal exposure or effective dose."
        ],
        "is_fallback_not_ingested": False,
    }


def get_environment_series() -> Dict[str, object]:
    """Load rows, build sample data, and return the environment series dictionary."""
    rows = load_rows(INPUT_PATH)
    return build_sample(rows)


def main() -> None:
    sample = get_environment_series()
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT_PATH.open("w", encoding="utf-8", newline="\n") as json_file:
        json.dump(sample, json_file, indent=2, allow_nan=False)
        json_file.write("\n")
    print("Successfully generated environment sample fixture at:", OUTPUT_PATH)


if __name__ == "__main__":
    main()
