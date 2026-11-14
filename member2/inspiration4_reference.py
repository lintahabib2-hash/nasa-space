"""Inspiration4 subject-specific pre-flight references.

Historical descriptive comparisons, not clinical baselines,
medical alerts, or continuous astronaut telemetry.
"""

import argparse
import hashlib
import json
from pathlib import Path
from statistics import median

import pandas as pd


EXPECTED_SHA256 = (
    "5eb1e7f025dd8443a9e70111e62bc32"
    "afae3432753024489c5c013e401d709d9"
)

PRE = ("L-92", "L-44", "L-3")
POST = ("R+1", "R+45", "R+82", "R+194")

METRICS = {
    "glucose": "glucose_value_milligram_per_deciliter",
    "sodium": "sodium_value_millimol_per_liter",
    "potassium": "potassium_value_millimol_per_liter",
    "albumin": "albumin_value_gram_per_deciliter",
    "creatinine": "creatinine_value_milligram_per_deciliter",
}


def analyze(frame):
    if not {"Sample Name", *METRICS.values()} <= set(frame.columns):
        raise ValueError("Missing required measurement columns")

    samples = frame["Sample Name"].astype(str)
    if samples.duplicated().any():
        raise ValueError("Duplicate sample identifiers")

    parsed = samples.str.extract(
        r"^(C\d{3})_serum_(L-\d+|R\+\d+)$"
    )

    if parsed.isna().any().any():
        raise ValueError("Unrecognized sample identifiers")

    frame = frame.copy()
    frame["subject_id"] = parsed[0]
    frame["timepoint"] = parsed[1]

    if frame.duplicated(["subject_id", "timepoint"]).any():
        raise ValueError("Duplicate subject/timepoint")

    records = []

    for sid, group in frame.groupby("subject_id"):
        for metric, column in METRICS.items():
            values = pd.to_numeric(group[column], errors="raise")

            if not values.dropna().map(
                lambda x: bool(pd.notna(x) and abs(x) != float("inf"))
            ).all():
                raise ValueError("Non-finite measurement")

            group_values = dict(zip(group["timepoint"], values))

            pre_values = [
                float(group_values[t])
                for t in PRE
                if t in group_values and pd.notna(group_values[t])
            ]

            reference = (
                float(median(pre_values))
                if len(pre_values) == 3 else None
            )

            for point in POST:
                raw = group_values.get(point)
                observed = (
                    float(raw)
                    if raw is not None and pd.notna(raw)
                    else None
                )

                difference = (
                    observed - reference
                    if observed is not None and reference is not None
                    else None
                )

                records.append({
                    "source_id": "NASA_OSDR_OSD-575",
                    "provenance_kind": "nasa_measured",
                    "subject_id": sid,
                    "measurement": metric,
                    "source_column": column,
                    "timepoint": point,
                    "time_precision": "mission_relative_day",
                    "observed_value": observed,
                    "preflight_reference_median": reference,
                    "preflight_reference_count": len(pre_values),
                    "difference_from_reference": (
                        round(difference, 5)
                        if difference is not None else None
                    ),
                    "quality_state": (
                        "descriptive_comparison"
                        if difference is not None
                        else "insufficient_data"
                    ),
                    "not_medical_diagnosis": True,
                })

    return {
        "study_id": "OSD-575",
        "study_population": "Inspiration4 astronauts",
        "analysis": "subject_specific_preflight_median",
        "reference_timepoints": list(PRE),
        "postflight_timepoints": list(POST),
        "clinical_validation": False,
        "limitations": [
            "Only three widely spaced pre-flight samples",
            "Reference is descriptive, not a medical normal range",
            "No post-flight observations used in reference construction",
            "No diagnoses, probabilities, or readiness scores",
        ],
        "records": records,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input_csv")
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    source = Path(args.input_csv)
    actual = hashlib.sha256(source.read_bytes()).hexdigest()

    if actual != EXPECTED_SHA256:
        raise ValueError("Source checksum differs from audited file")

    result = analyze(pd.read_csv(source))

    output = Path(args.out)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(result, indent=2, allow_nan=False)
    )

    print("Subjects:", len({
        r["subject_id"] for r in result["records"]
    }))
    print("Comparison records:", len(result["records"]))
    print("Output:", output)


if __name__ == "__main__":
    main()
