"""NASA CFT70 nutrition reference audit; no clinical interpretation.

Uses only within-subject numeric PRE_TEST day labels to construct a fixed
descriptive reference. Preserves nonstandard day labels and keeps 2D/3D echo
measurements separate from the daily dietary-intake data.
"""

import argparse
import csv
import hashlib
import io
import json
import math
from collections import Counter, defaultdict
from pathlib import Path
from statistics import median
from zipfile import ZipFile

INTAKE_MEMBER = "MR016G_CFT70_DAILY_INTAKE/MR016G_CFT70_DAILY_INTAKE"
ECHO_2D_MEMBER = "BRSMCF_CFT70/BRSMCF_CFT70_2D_Echo_All"
ECHO_3D_MEMBER = "BRSMCF_CFT70/BRSMCF_CFT70_3D_Echo_All"
INTAKE_SOURCE_ID = "NASA_NLSP_MR016G_CFT70"
ECHO_SOURCE_ID = "NASA_NLSP_BRSMCF_CFT70"
INTAKE_URL = "https://nlsp.nasa.gov/search/data/details/72616c68-3046-5d36-8f1d-a26d856107ff?dataType=EXPERIMENTS"
ECHO_URL = "https://nlsp.nasa.gov/search/data/details/9af6f9ba-3730-54ab-a82a-1a32798667ae?dataType=EXPERIMENTS"
PHASES = ("PRE_TEST", "IN_TEST", "POST_TEST")
MIN_PRE_OBSERVATIONS = 5


def read_member(path, member):
    with ZipFile(path) as archive:
        return archive.read(member)


def read_csv(raw):
    try:
        decoded = raw.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise ValueError("Expected UTF-8 NASA tabular source") from exc
    return list(csv.DictReader(io.StringIO(decoded, newline="")))


def _positive_finite(raw):
    try:
        number = float(raw)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"Non-numeric daily intake: {raw!r}") from exc
    if not math.isfinite(number) or number <= 0:
        raise ValueError(f"Invalid daily intake: {raw!r}")
    return number


def _numeric_day(phase, label):
    if label.isdecimal():
        number = int(label)
        if number < 0 or (number == 0 and phase != "POST_TEST"):
            raise ValueError(f"Invalid {phase} day number: {label}")
        return number
    if phase == "PRE_TEST" and label in {"X1", "X2"}:
        return None
    raise ValueError(f"Unrecognized {phase} day label: {label!r}")


def analyze_intake(rows, sha256=""):
    """Validate the CFT70 dietary-intake table and return phase-only references."""
    required = {"ID", "Subject", "Group", "Test_Phase", "BR_Day", "Daily Energy Intake (kcal/day)"}
    if not rows or not required.issubset(rows[0]):
        raise ValueError("CFT70 daily intake columns missing or table empty")
    keys, ids, by_subject, group_by_subject = set(), set(), defaultdict(list), {}
    for row in rows:
        ident = str(row["ID"]).strip()
        subject = str(row["Subject"]).strip()
        group = str(row["Group"]).strip()
        phase = str(row["Test_Phase"]).strip()
        label = str(row["BR_Day"]).strip()
        if not ident or not subject or not group or phase not in PHASES:
            raise ValueError(f"Invalid identifier/group/phase in row: {row!r}")
        if ident in ids:
            raise ValueError(f"Duplicate source row ID: {ident}")
        ids.add(ident)
        key = (subject, phase, label)
        if key in keys:
            raise ValueError(f"Duplicate subject-phase-day: {key}")
        keys.add(key)
        if subject in group_by_subject and group_by_subject[subject] != group:
            raise ValueError("Conflicting intervention group for same subject")
        group_by_subject[subject] = group
        day_number = _numeric_day(phase, label)
        intake = _positive_finite(row["Daily Energy Intake (kcal/day)"])
        by_subject[subject].append({
            "study_phase": phase, "study_day_label": label,
            "numeric_study_day": day_number,
            "energy_kcal_per_day": intake,
            "quality_state": "valid",
        })

    results = []
    excluded_special = 0
    for subject in sorted(by_subject):
        observations = by_subject[subject]
        reference_values = [
            r["energy_kcal_per_day"] for r in observations
            if r["study_phase"] == "PRE_TEST" and r["numeric_study_day"] is not None
        ]
        n_pre = len(reference_values)
        center = median(reference_values) if n_pre >= MIN_PRE_OBSERVATIONS else None
        mad = median(abs(x-center) for x in reference_values) if center is not None else None
        extras = sorted(r["study_day_label"] for r in observations
                        if r["study_phase"] == "PRE_TEST" and r["numeric_study_day"] is None)
        excluded_special += len(extras)
        phase_counts = {ph: sum(r["study_phase"] == ph for r in observations) for ph in PHASES}
        phase_medians = {ph: (median([r["energy_kcal_per_day"] for r in observations if r["study_phase"] == ph])
                              if phase_counts[ph] else None) for ph in PHASES}
        decorated = []
        for row in observations:
            phase = row["study_phase"]
            baseline_included = phase == "PRE_TEST" and row["numeric_study_day"] is not None
            diff = row["energy_kcal_per_day"]-center if center is not None and phase != "PRE_TEST" else None
            decorated.append({
                **row,
                "included_in_pre_reference": baseline_included,
                "difference_from_pre_reference_kcal_day": round(diff, 4) if diff is not None else None,
                "interpretation": "descriptive_only" if diff is not None else "not_compared",
            })
        # PRE numbering counts backward from the intervention; retain source labels.
        decorated.sort(key=lambda r: (
            PHASES.index(r["study_phase"]),
            (-(r["numeric_study_day"]) if r["study_phase"] == "PRE_TEST" else r["numeric_study_day"])
                if r["numeric_study_day"] is not None else 999,
            r["study_day_label"],
        ))
        results.append({
            "subject_id": subject,
            "group": group_by_subject[subject],
            "pre_reference_n": n_pre,
            "pre_reference_median_kcal_day": center,
            "pre_reference_mad_kcal_day": mad,
            "excluded_ambiguous_pre_day_labels": extras,
            "phase_counts": phase_counts,
            "phase_median_energy_kcal_day": phase_medians,
            "observations": decorated,
        })
    return {
        "schema_version": "1.0",
        "source_id": INTAKE_SOURCE_ID,
        "source_url": INTAKE_URL,
        "provenance_kind": "analog_measured",
        "study": "CFT70 human bed-rest analog",
        "measurement": "recorded_daily_energy_intake",
        "unit": "kcal/day",
        "time_precision": "study_phase_day_label_only",
        "source_file_sha256": sha256,
        "records": len(rows),
        "subjects": len(results),
        "phase_rows": dict(Counter(x["study_phase"] for x in sum(by_subject.values(), []))),
        "ambiguous_pre_day_rows_excluded_from_reference": excluded_special,
        "reference_definition": "Same-subject numeric PRE_TEST days only; at least five values; no in/post values in baseline",
        "interpretation_warning": (
            "Study intake was controlled/adjusted by protocol; a difference does not "
            "imply clinical deterioration or diagnose an astronaut. No synthetic times."
        ),
        "participants": results,
    }


def analyze_echo_coverage(two_d_rows, three_d_rows):
    """Report echo availability, not falsely claim longitudinal cardiac baselines."""
    for label, rows in [("2D", two_d_rows), ("3D", three_d_rows)]:
        if not rows or not {"Subject", "Test_Phase"}.issubset(rows[0]):
            raise ValueError(f"Missing {label} subject/phase fields")
    def stats(rows):
        subjects = {str(r["Subject"]) for r in rows}
        pre = Counter(str(r["Subject"]) for r in rows if r["Test_Phase"] == "PRE_TEST")
        return {"rows": len(rows), "subjects": len(subjects),
                "pre_rows_per_subject_distribution": dict(Counter(pre[s] for s in subjects))}
    two = stats(two_d_rows); three = stats(three_d_rows)
    duplicates = len(three_d_rows) - len({
        (str(r["Subject"]), r["Test_Phase"], str(r.get("BR_Day")))
        for r in three_d_rows
    })
    return {
        "source_id": ECHO_SOURCE_ID,
        "source_url": ECHO_URL,
        "provenance_kind": "analog_measured",
        "2d_all": two,
        "3d_all": three,
        "3d_repeat_rows_ignoring_analyzer": duplicates,
        "interpretation": (
            "2D offers one PRE_TEST exam per person; 3D has repeated analyst records at "
            "same phase/day. Neither yields five independent pre-intervention cardiac days."
        ),
        "measurement_units": "not_verified_in_table_headers",
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--intake-archive", required=True)
    parser.add_argument("--echo-archive", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    intake_bytes = read_member(args.intake_archive, INTAKE_MEMBER)
    intake = analyze_intake(read_csv(intake_bytes), hashlib.sha256(intake_bytes).hexdigest())
    cardiac = analyze_echo_coverage(
        read_csv(read_member(args.echo_archive, ECHO_2D_MEMBER)),
        read_csv(read_member(args.echo_archive, ECHO_3D_MEMBER)),
    )
    intake_ids = {s["subject_id"] for s in intake["participants"]}
    with ZipFile(args.echo_archive) as archive:
        two_d = read_csv(archive.read(ECHO_2D_MEMBER))
    overlap = len(intake_ids & {str(r["Subject"]) for r in two_d})
    output = {
        "nutrition": intake,
        "cardiovascular_coverage": cardiac,
        "shared_participant_ids_intake_and_2d": overlap,
        "no_cross_study_merging": True,
        "not_medical_diagnosis": True,
    }
    dest = Path(args.out)
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(output, indent=2, allow_nan=False), encoding="utf-8")
    print(f"Nutrition: {intake['records']} rows / {intake['subjects']} subjects")
    print(f"Phase rows: {intake['phase_rows']}")
    print("Excluded ambiguous PRE labels:", intake["ambiguous_pre_day_rows_excluded_from_reference"])
    print("Echo 2D/3D rows:", cardiac["2d_all"]["rows"], cardiac["3d_all"]["rows"])
    print("Intake and 2D participant overlap:", overlap)
    print("Saved:", dest)


if __name__ == "__main__":
    main()
