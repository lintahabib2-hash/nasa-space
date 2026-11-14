"""Audit NASA NLSP UTMB Campaign 1 human bed-rest actigraphy (not spaceflight telemetry).

Input: original BRSMAct ZIP downloaded from NASA's Life Sciences Portal.
This script does not mix the two CSV-like tables or invent observation times.
Requires: Python 3.9+ and pandas.
"""
from __future__ import annotations

from io import BytesIO
from pathlib import Path
from zipfile import ZipFile
import argparse
import hashlib
import json
import pandas as pd

SOURCE_URL = "https://nlsp.nasa.gov/search/data/details/e26501eb-7d7a-5012-8c8e-c5bdb3eecaf6?dataType=DATASETS"
SOURCE_ID = "NASA_NLSP_BRSMAct_UTMB_C1"
MAIN_SUFFIX = "/BRSMACT_Campagin_1_Actigraphy"  # spelling from NASA archive


def clock_to_minutes(value):
    """Parse H:M, H:M:S, or literal 0; missing -> NA. Never interpret H:M as decimal hours."""
    if pd.isna(value):
        return float("nan")
    text = str(value).strip()
    if text == "0":
        return 0.0
    fields = text.split(":")
    if len(fields) not in (2, 3):
        raise ValueError(f"Unexpected clock duration: {text!r}")
    h, m = int(fields[0]), int(fields[1])
    sec = int(fields[2]) if len(fields) == 3 else 0
    if h < 0 or not 0 <= m < 60 or not 0 <= sec < 60:
        raise ValueError(f"Invalid clock duration: {text!r}")
    return h * 60 + m + sec / 60


def load_and_audit(zip_path: str | Path):
    zip_path = Path(zip_path)
    with ZipFile(zip_path) as archive:
        names = [n for n in archive.namelist() if n.endswith(MAIN_SUFFIX)]
        if len(names) != 1:
            raise ValueError("Could not uniquely locate the all-participant main table")
        original_bytes = archive.read(names[0])
        raw = pd.read_csv(BytesIO(original_bytes))

    mandatory = {"Subject", "Date", "Test_Phase", "BR_Day", "Sleep Latency (hours)", "Sleep Duration (hours)", "Sleep Efficiency (%)"}
    if not mandatory.issubset(raw.columns):
        raise ValueError(f"Missing columns: {mandatory - set(raw.columns)}")

    clean = pd.DataFrame({
        "subject_id": raw["Subject"].astype(str),
        "observation_date": pd.to_datetime(raw["Date"], format="%m/%d/%Y", errors="raise").dt.strftime("%Y-%m-%d"),
        "study_phase": raw["Test_Phase"],
        "bed_rest_day": raw["BR_Day"],
        "sleep_latency_minutes": raw["Sleep Latency (hours)"].map(clock_to_minutes),
        "sleep_duration_hours": raw["Sleep Duration (hours)"].map(clock_to_minutes) / 60,
        "sleep_efficiency_percent": pd.to_numeric(raw["Sleep Efficiency (%)"], errors="raise"),
    })
    clean["provenance_kind"] = "analog_measured"
    clean["source_id"] = SOURCE_ID
    clean["quality_state"] = "valid"
    required_measurements = ["sleep_latency_minutes", "sleep_duration_hours", "sleep_efficiency_percent"]
    missing_rows = clean[required_measurements].isna().any(axis=1)
    clean.loc[missing_rows, "quality_state"] = "missing"

    if clean.duplicated(["subject_id", "observation_date"]).any():
        raise ValueError("Duplicate participant-date rows in main table")
    bad = clean["sleep_duration_hours"].lt(0) | clean["sleep_duration_hours"].gt(24) | clean["sleep_efficiency_percent"].lt(0) | clean["sleep_efficiency_percent"].gt(100)
    if bad.any():
        raise ValueError(f"Invalid durations or efficiency in {int(bad.sum())} rows")

    clean = clean.sort_values(["subject_id", "observation_date"]).reset_index(drop=True)
    audit = {
        "source_id": SOURCE_ID,
        "source_url": SOURCE_URL,
        "dataset_type": "measured human bed-rest analog, NOT in-flight astronaut data",
        "archive_filename": zip_path.name,
        "main_table_md5": hashlib.md5(original_bytes).hexdigest(),
        "rows": int(len(clean)),
        "subjects": int(clean.subject_id.nunique()),
        "date_start": clean.observation_date.min(),
        "date_end": clean.observation_date.max(),
        "valid_measurement_rows": int((clean.quality_state == "valid").sum()),
        "missing_measurement_rows": int((clean.quality_state == "missing").sum()),
        "phase_rows": clean.study_phase.value_counts().to_dict(),
        "phase_by_subject": {subject: g.study_phase.value_counts().to_dict() for subject, g in clean.groupby("subject_id")},
        "valid_pre_test_rows_by_subject": {subject: int(((g.study_phase == "PRE_TEST") & (g.quality_state == "valid")).sum()) for subject, g in clean.groupby("subject_id")},
        "observation_time_available": False,
        "interpretation_warning": "Only a calendar date is provided; never present readings as minute-level telemetry or claim pre-flight baseline adequacy.",
    }
    return clean, audit


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("zip_file", help="Original NASA NLSP BRSMAct ZIP archive")
    parser.add_argument("--out", help="Optional cleaned CSV destination outside repo")
    args = parser.parse_args()
    clean, audit = load_and_audit(args.zip_file)
    print(json.dumps(audit, indent=2))
    if args.out:
        output = Path(args.out)
        output.parent.mkdir(parents=True, exist_ok=True)
        clean.to_csv(output, index=False)
        print("Saved cleaned observations:", output)


if __name__ == "__main__":
    main()
