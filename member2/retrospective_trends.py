"""Prior-only retrospective analysis of NASA bed-rest sleep data."""

import argparse
import json
from datetime import date
from math import isfinite
from pathlib import Path
from statistics import median

WINDOW_DAYS = 14
MIN_HISTORY = 5
SOURCE_ID = "NASA_NLSP_BRSMAct_UTMB_C1"


def add_trends(data):
    if (
        data.get("source_id") != SOURCE_ID
        or data.get("provenance_kind") != "analog_measured"
        or data.get("time_precision") != "calendar_date_only"
    ):
        raise ValueError("Unexpected dataset provenance")

    participants = []
    seen_subjects = set()

    for participant in data["participants"]:
        sid = participant["subject_id"]
        if sid in seen_subjects:
            raise ValueError("Duplicate subject")
        seen_subjects.add(sid)

        rows = sorted(
            participant["observations"],
            key=lambda row: row["observed_on"],
        )

        if len({r["observed_on"] for r in rows}) != len(rows):
            raise ValueError("Duplicate participant dates")

        analyzed = []

        for row in rows:
            current_day = date.fromisoformat(row["observed_on"])
            phase = row["study_phase"]
            quality = row["quality_state"]
            value = row["sleep_duration_hours"]

            if quality not in ("valid", "missing"):
                raise ValueError("Unknown quality state")

            if quality == "valid":
                if (
                    isinstance(value, bool)
                    or not isinstance(value, (int, float))
                    or not isfinite(value)
                    or not 0 <= value <= 24
                ):
                    raise ValueError("Invalid sleep duration")

            prior = []

            for old in analyzed:
                lag = (
                    current_day -
                    date.fromisoformat(old["observed_on"])
                ).days

                if (
                    1 <= lag <= WINDOW_DAYS
                    and old["study_phase"] == phase
                    and old["quality_state"] == "valid"
                ):
                    prior.append(old["sleep_duration_hours"])

            baseline = (
                median(prior)
                if len(prior) >= MIN_HISTORY
                else None
            )

            if quality == "missing":
                status = "missing_observation"
            elif baseline is None:
                status = "insufficient_reference"
            else:
                status = "descriptive_reference_available"

            analyzed.append({
                **row,
                "prior_reference_count": len(prior),
                "prior_14d_median_sleep_hours": (
                    round(baseline, 4)
                    if baseline is not None else None
                ),
                "difference_from_reference_hours": (
                    round(value - baseline, 4)
                    if baseline is not None and quality == "valid"
                    else None
                ),
                "trend_quality": status,
            })

        participants.append({
            **participant,
            "observations": analyzed,
        })

    return {
        **data,
        "analysis_method": {
            "name": "prior_only_phase_specific_rolling_median",
            "window_calendar_days": WINDOW_DAYS,
            "minimum_valid_reference_observations": MIN_HISTORY,
            "future_data_used": False,
            "clinical_validation": False,
            "interpretation": "Retrospective descriptive statistics only",
        },
        "participants": participants,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input_json")
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    source = json.loads(
        Path(args.input_json).read_text(encoding="utf-8")
    )
    result = add_trends(source)

    output = Path(args.out)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(result, indent=2, allow_nan=False),
        encoding="utf-8",
    )

    print(f"Saved trends: {output}")
    print(f"Participants: {len(result['participants'])}")


if __name__ == "__main__":
    main()
