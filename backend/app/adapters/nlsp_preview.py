"""Produce a dated, source-labeled research preview from NASA bed-rest data.

This is an exploratory output, not clinical interpretation and not assumed
licensed for public redistribution. It preserves date-only observations.
"""
from pathlib import Path
import argparse
import json
import pandas as pd

SOURCE_URL = "https://nlsp.nasa.gov/search/data/details/e26501eb-7d7a-5012-8c8e-c5bdb3eecaf6?dataType=DATASETS"
SOURCE_ID = "NASA_NLSP_BRSMAct_UTMB_C1"
REQUIRED = {"subject_id", "observation_date", "study_phase", "sleep_duration_hours", "sleep_efficiency_percent", "sleep_latency_minutes", "provenance_kind", "source_id", "quality_state"}
MEASURES = ("sleep_duration_hours", "sleep_efficiency_percent", "sleep_latency_minutes")


def clean_number(value):
    return None if pd.isna(value) else round(float(value), 4)


def create_preview(frame):
    missing = REQUIRED - set(frame.columns)
    if missing:
        raise ValueError(f"Missing columns: {sorted(missing)}")
    if frame.duplicated(["subject_id", "observation_date"]).any():
        raise ValueError("Duplicate subject/date records")
    if not frame["source_id"].eq(SOURCE_ID).all() or not frame["provenance_kind"].eq("analog_measured").all():
        raise ValueError("Unexpected source or provenance")
    if not frame["study_phase"].isin(["PRE_TEST", "IN_TEST", "POST_TEST"]).all():
        raise ValueError("Unrecognized study phase")
    dates = pd.to_datetime(frame["observation_date"], format="%Y-%m-%d", errors="raise")
    if dates.isna().any():
        raise ValueError("Missing observation dates")
    if not frame["quality_state"].isin(["valid", "missing"]).all():
        raise ValueError("Unexpected quality state")

    if frame.loc[frame["quality_state"] == "valid", list(MEASURES)].isna().any().any():
        raise ValueError("A row labeled valid has missing measurements")

    participants = []
    for sid, group in frame.sort_values(["subject_id", "observation_date"]).groupby("subject_id"):
        observations = []
        for _, row in group.iterrows():
            observations.append({
                "observed_on": row["observation_date"],
                "study_phase": row["study_phase"],
                "quality_state": row["quality_state"],
                **{col: clean_number(row[col]) for col in MEASURES},
            })
        participants.append({
            "subject_id": sid,
            "row_count": len(group),
            "valid_rows": int((group["quality_state"] == "valid").sum()),
            "phase_counts": {k: int(v) for k, v in group["study_phase"].value_counts().items()},
            "phase_summary": {
                phase: {
                    "valid_nights": int((ph["quality_state"] == "valid").sum()),
                    "median_sleep_hours": clean_number(ph["sleep_duration_hours"].dropna().median()) if ph["sleep_duration_hours"].notna().any() else None,
                    "median_efficiency_percent": clean_number(ph["sleep_efficiency_percent"].dropna().median()) if ph["sleep_efficiency_percent"].notna().any() else None,
                }
                for phase, ph in group.groupby("study_phase")
            },
            "observations": observations,
        })

    return {
        "schema_version": "1.0",
        "display_title": "NASA UTMB Bed-rest Actigraphy — retrospective research",
        "source_id": SOURCE_ID,
        "source_url": SOURCE_URL,
        "provenance_kind": "analog_measured",
        "time_precision": "calendar_date_only",
        "study_population": "human bed-rest analog participants, not in-flight astronauts",
        "clinical_status": "not_validated_for_health_diagnosis",
        "units": {"sleep_duration_hours": "hours", "sleep_efficiency_percent": "percent", "sleep_latency_minutes": "minutes"},
        "row_count": len(frame),
        "participants": participants,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("clean_csv")
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    preview = create_preview(pd.read_csv(args.clean_csv))
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(preview, indent=2, allow_nan=False), encoding="utf-8")
    print(f"Wrote {out} | {preview['row_count']} rows | {len(preview['participants'])} participants")

if __name__ == "__main__":
    main()
