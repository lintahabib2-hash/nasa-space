"""Descriptive, participant-specific Inspiration4 CBC comparisons.

Reads NASA's original submitted long-form CBC table. Does not silently
repair unusual source values or claim clinical baseline validity.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path
from statistics import median

import pandas as pd

PRE = ("L-92", "L-44", "L-3")
POST = ("R+1", "R+45", "R+82", "R+194")
METRICS = {
    "HEMOGLOBIN": ("hemoglobin", "g/dL"),
    "HEMATOCRIT": ("hematocrit", "%"),
    "WHITE BLOOD CELL COUNT": ("white_blood_cell_count", "Thousand/uL"),
    "RED BLOOD CELL COUNT": ("red_blood_cell_count", "Million/uL"),
    "PLATELET COUNT": ("platelet_count", "Thousand/uL"),
}
NEEDED = {
    "ANALYTE", "VALUE", "RANGE_MIN", "RANGE_MAX", "UNITS",
    "TEST_TYPE", "SUBJECT_ID", "TEST_DATE",
}


def analyze_cbc(frame):
    """Use three pre-flight results per person and analyte, if present."""
    if not NEEDED <= set(frame.columns):
        raise ValueError(f"Missing columns: {sorted(NEEDED - set(frame.columns))}")
    selected = frame[frame["ANALYTE"].isin(METRICS)].copy()
    if selected.empty:
        raise ValueError("No selected CBC measurements")
    for key in ("SUBJECT_ID", "TEST_DATE", "ANALYTE", "UNITS", "TEST_TYPE"):
        if selected[key].isna().any():
            raise ValueError(f"Missing required metadata: {key}")
    if not selected["SUBJECT_ID"].astype(str).str.fullmatch(r"C\d{3}").all():
        raise ValueError("Unexpected participant identifier")
    if not selected["TEST_DATE"].isin(PRE + POST).all():
        raise ValueError("Unexpected measurement timepoint")
    if not selected["TEST_TYPE"].eq("CBC").all():
        raise ValueError("Expected CBC assay records")
    if selected.duplicated(["SUBJECT_ID", "TEST_DATE", "ANALYTE"]).any():
        raise ValueError("Duplicate subject/timepoint/analyte")
    for analyte, (_, expected_unit) in METRICS.items():
        rows = selected[selected["ANALYTE"].eq(analyte)]
        if not rows["UNITS"].eq(expected_unit).all():
            raise ValueError(f"Source unit mismatch for {analyte}")
    for field in ("VALUE", "RANGE_MIN", "RANGE_MAX"):
        raw = selected[field].astype("string")
        converted = pd.to_numeric(raw, errors="coerce")
        invalid = raw.notna() & raw.str.strip().ne("") & converted.isna()
        if invalid.any():
            raise ValueError(f"Non-numeric {field}")
        if converted.dropna().map(lambda value: not math.isfinite(float(value))).any():
            raise ValueError(f"Non-finite {field}")
        selected[field] = converted
    invalid_range = (
        selected["RANGE_MIN"].notna()
        & selected["RANGE_MAX"].notna()
        & (selected["RANGE_MIN"] > selected["RANGE_MAX"])
    )
    if invalid_range.any():
        raise ValueError("Inverted source range")
    records = []
    for sid in sorted(selected["SUBJECT_ID"].unique()):
        subject = selected[selected["SUBJECT_ID"].eq(sid)]
        for analyte, (metric, units) in METRICS.items():
            rows = subject[subject["ANALYTE"].eq(analyte)]
            if rows.empty:
                continue
            by_point = {r.TEST_DATE: r for r in rows.itertuples(index=False)}
            pre_rows = [by_point.get(t) for t in PRE]
            valid_pre = [r for r in pre_rows if r is not None and pd.notna(r.VALUE)]
            reference = (
                float(median(float(r.VALUE) for r in valid_pre))
                if len(valid_pre) == 3 else None
            )
            pre_flags = []
            for r in valid_pre:
                if (
                    (pd.notna(r.RANGE_MIN) and r.VALUE < r.RANGE_MIN)
                    or (pd.notna(r.RANGE_MAX) and r.VALUE > r.RANGE_MAX)
                ):
                    pre_flags.append(f"preflight_{r.TEST_DATE}_outside_source_range")
            for point in POST:
                row = by_point.get(point)
                observed = (
                    float(row.VALUE)
                    if row is not None and pd.notna(row.VALUE) else None
                )
                flags = list(pre_flags)
                if observed is not None and (
                    (pd.notna(row.RANGE_MIN) and observed < float(row.RANGE_MIN))
                    or (pd.notna(row.RANGE_MAX) and observed > float(row.RANGE_MAX))
                ):
                    flags.append("observed_outside_source_range")
                records.append({
                    "source_id": "NASA_OSDR_OSD-569",
                    "provenance_kind": "nasa_measured",
                    "subject_id": str(sid),
                    "measurement": metric,
                    "units": units,
                    "timepoint": point,
                    "time_precision": "mission_relative_day",
                    "observed_value": observed,
                    "preflight_reference_median": reference,
                    "preflight_reference_count": len(valid_pre),
                    "difference_from_reference": (
                        round(observed - reference, 5)
                        if observed is not None and reference is not None else None
                    ),
                    "quality_state": "valid" if observed is not None else "missing",
                    "reference_status": (
                        "insufficient_history" if reference is None
                        else "source_range_review" if pre_flags
                        else "provisional_three_sample_reference"
                    ),
                    "source_range_flags": flags,
                    "analysis_status": (
                        "descriptive_comparison"
                        if observed is not None and reference is not None
                        else "insufficient_data"
                    ),
                    "not_medical_diagnosis": True,
                })
    if not records:
        raise ValueError("No valid participant-level records")
    return {
        "study_id": "OSD-569",
        "analysis": "subject_specific_preflight_median",
        "source_table": "original submitted CBC",
        "reference_timepoints": list(PRE),
        "postflight_timepoints": list(POST),
        "clinical_validation": False,
        "limitations": [
            "Three widely spaced pre-flight measurements are not a clinical baseline",
            "Source values are preserved, including anomalous source-range measurements",
            "Source laboratory ranges are metadata, not diagnostic thresholds",
        ],
        "records": records,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input_csv")
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    path = Path(args.input_csv)
    result = analyze_cbc(pd.read_csv(path))
    result["source_sha256"] = hashlib.sha256(path.read_bytes()).hexdigest()
    output = Path(args.out)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, allow_nan=False), encoding="utf-8")
    print("Comparison records:", len(result["records"]))
    print("Subjects:", sorted({r["subject_id"] for r in result["records"]}))
    print("Records with source-range flags:", sum(bool(r["source_range_flags"]) for r in result["records"]))
    print("Saved:", output)


if __name__ == "__main__":
    main()
