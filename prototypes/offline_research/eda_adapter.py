"""Read a locally obtained NASA OSDR RR-1 EDA telemetry CSV for offline research.

This is historical *research-environment* data, never a person's health record.
The original NASA CSV is deliberately not bundled or silently downloaded.
"""
from __future__ import annotations

import csv
from datetime import datetime, timezone
from math import ceil, isfinite
from pathlib import Path
from statistics import median

SOURCE_ID = "NASA_OSDR_EDA_RR1"
SOURCE_URL = "https://visualization.osdr.nasa.gov/eda/"
FIELDS = (
    "Controller_Time_GMT", "Temp_degC_Ground", "Temp_degC_ISS",
    "RH_percent_Ground", "RH_percent_ISS", "CO2_ppm_Ground", "CO2_ppm_ISS",
)
NUMERIC = FIELDS[1:]


def load_eda_preview(csv_path: str | Path, max_points: int = 300) -> dict:
    """Validate all rows and sample a chart preview without changing raw data."""
    if not 2 <= max_points <= 2000:
        raise ValueError("max_points must be between 2 and 2000")
    observations = []
    last_time = None
    with open(csv_path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames or not set(FIELDS).issubset(reader.fieldnames):
            raise ValueError("The expected seven RR-1 EDA columns are missing")
        for index, raw in enumerate(reader, 2):
            try:
                parsed = datetime.strptime(raw["Controller_Time_GMT"].strip(), "%Y-%m-%d %H:%M").replace(tzinfo=timezone.utc)
                if last_time is not None and parsed <= last_time:
                    raise ValueError("Non-increasing/duplicate timestamps")
                numeric = {key: float(raw[key]) for key in NUMERIC}
                if not all(isfinite(value) for value in numeric.values()):
                    raise ValueError("Non-finite instrument reading")
                if any(numeric[c] < 0 or numeric[c] > 100 for c in ("RH_percent_Ground", "RH_percent_ISS")):
                    raise ValueError("Relative humidity outside 0–100%")
                if any(numeric[c] < 0 for c in ("CO2_ppm_Ground", "CO2_ppm_ISS")):
                    raise ValueError("Negative CO2 reading")
            except (ValueError, TypeError, AttributeError, KeyError) as exc:
                raise ValueError(f"Invalid NASA EDA row {index}: {exc}") from exc
            last_time = parsed
            observations.append({"observed_at_utc": parsed.isoformat().replace("+00:00", "Z"), **numeric})
    if not observations:
        raise ValueError("EDA table contains no observations")
    stride = max(1, ceil(len(observations) / max_points))
    preview = observations[::stride]
    if preview[-1] is not observations[-1]:
        preview.append(observations[-1])
    return {
        "source_id": SOURCE_ID,
        "source_url": SOURCE_URL,
        "display_title": "NASA RR-1 EDA — historical experimental environment",
        "provenance_kind": "environment_measured",
        "population": "experimental environment: not individual astronaut physiology",
        "time_precision": "minute",
        "units": {"Temp_degC_Ground": "degC", "Temp_degC_ISS": "degC", "RH_percent_Ground": "%", "RH_percent_ISS": "%", "CO2_ppm_Ground": "ppm", "CO2_ppm_ISS": "ppm"},
        "row_count": len(observations),
        "preview_count": len(preview),
        "time_start_utc": observations[0]["observed_at_utc"],
        "time_end_utc": observations[-1]["observed_at_utc"],
        "median_co2_iss_ppm": round(median(o["CO2_ppm_ISS"] for o in observations), 3),
        "instrument_context_validation": "requires source-document review before interpreting exposure",
        "observations": preview,
    }
