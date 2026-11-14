"""Generate SIMULATED UI fixtures for the NASA Space Health Monitoring Agent (Member 3).

Every value written here is simulated (source_id X01, provenance_kind "simulated").
Nothing is NASA data. Status, reasons, baseline and robust z come from Member 2's
real engine, ``get_baseline_result()`` in ``member2/analytics.py``. The UI never computes
a status itself.

Usage (from frontend/):
    git show origin/feature/member2-analytics:member2/analytics.py > /tmp/analytics.py
    python scripts/make_fixtures.py --analytics /tmp/analytics.py

The script is deterministic (fixed seed and fixed as-of date). Member 2's seed script
(backend/scripts/seed_simulated_crew.py) should replace this once it is merged.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import random
from datetime import datetime, timedelta, timezone
from pathlib import Path
from statistics import median

AS_OF = datetime(2026, 11, 14, 6, 0, tzinfo=timezone.utc)
DAYS = 30
SEED = 20261114
OUT = Path(__file__).resolve().parents[1] / "src" / "features" / "dashboard" / "fixtures"
DEMO_Z = 3.0  # mirrors member2 analytics.DEMO_Z_THRESHOLD; used only to draw the band

# Simulation parameters only. These are NOT medical reference ranges.
INDICATORS = [
    # measurement, units, centre, noise sd, decimals, (min, max)
    ("sleep_duration", "hours", 7.2, 0.35, 1, (0, 24)),
    ("mood", "score_1_5", 4, 0.6, 0, (1, 5)),
    ("stress", "score_1_5", 2, 0.6, 0, (1, 5)),
    ("resting_heart_rate", "bpm", 58, 2.0, 0, (30, 200)),
    ("systolic_bp", "mmHg", 116, 4.0, 0, (60, 250)),
    ("diastolic_bp", "mmHg", 74, 3.0, 0, (30, 150)),
    ("blood_glucose", "mg/dL", 92, 5.0, 0, (20, 400)),
    ("body_temperature", "degC", 36.7, 0.15, 1, (30, 43)),
    ("radiation_badge_daily_dose", "uSv/day", 450, 25.0, 0, (0, 100000)),
    ("exercise_minutes", "minutes", 120, 12.0, 0, (0, 600)),
]

SCENARIOS = {
    "crew_01": {
        "scenario": "stable",
        "label": "Stable, with one noisy heart-rate reading today",
        # one isolated spike on the latest day: must NOT become a persistent flag
        "offsets": {"resting_heart_rate": {0: 14}},
        "missing": {},
    },
    "crew_02": {
        "scenario": "gradual_drift",
        "label": "Gradual multi-day drift (sleep down, resting heart rate up)",
        "offsets": {
            "sleep_duration": {4: -0.6, 3: -1.0, 2: -1.7, 1: -2.0, 0: -2.3},
            "resting_heart_rate": {4: 3, 3: 6, 2: 11, 1: 13, 0: 15},
            "exercise_minutes": {3: -30, 2: -50, 1: -60, 0: -70},
        },
        "missing": {},
    },
    "crew_03": {
        "scenario": "missing_data",
        "label": "Missing and sparse data (latest sleep missing, glucose rarely logged)",
        "offsets": {},
        "missing": {
            "sleep_duration": {0, 5, 6, 11, 17, 23},
            "blood_glucose": set(range(DAYS)) - {0, 9, 16},
            "body_temperature": {1, 2, 3, 8, 9, 15, 21},
            "exercise_minutes": {4, 12, 13, 20},
        },
    },
}


def load_member2(path: Path):
    spec = importlib.util.spec_from_file_location("member2_analytics", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)  # type: ignore[union-attr]
    return module


def iso(dt: datetime) -> str:
    return dt.isoformat().replace("+00:00", "Z")


def build_series(rng, measurement, centre, sd, decimals, bounds, offsets, missing):
    series = []
    for i in range(DAYS):
        days_ago = DAYS - 1 - i
        ts = AS_OF - timedelta(days=days_ago)
        if days_ago in missing:
            series.append({"timestamp_utc": iso(ts), "value": None, "quality_state": "missing"})
            continue
        value = centre + rng.gauss(0, sd) + offsets.get(days_ago, 0)
        value = min(max(value, bounds[0]), bounds[1])
        value = round(value, decimals) if decimals else int(round(value))
        series.append({"timestamp_utc": iso(ts), "value": value, "quality_state": "valid"})
    return series


def envelope(subject_id, measurement, units, point):
    return {
        "subject_id": subject_id, "study_id": "demo-001", "source_id": "X01",
        "provenance_kind": "simulated", "measurement": measurement,
        "value": point["value"], "units": units, "timestamp_utc": point["timestamp_utc"],
    }


def reference_band(result, records):
    """Recover the reference subset Member 2 used and express its demo z-band."""
    if result.get("baseline_value") is None or not result.get("reference_start_utc"):
        return None
    start = datetime.fromisoformat(result["reference_start_utc"])
    end = datetime.fromisoformat(result["reference_end_utc"])
    vals = [r["value"] for r in records
            if start <= datetime.fromisoformat(r["timestamp_utc"].replace("Z", "+00:00")) <= end]
    centre = median(vals)
    mad = median(abs(v - centre) for v in vals)
    if mad == 0:
        return None
    half = DEMO_Z * 1.4826 * mad
    return {
        "low": round(centre - half, 3), "high": round(centre + half, 3),
        "basis": "median ± 3 × 1.4826 × MAD of the reference readings (demo statistical rule)",
    }


def analyse(m2, subject_id, measurement, units, series):
    valid = [envelope(subject_id, measurement, units, p) for p in series if p["value"] is not None]
    latest = series[-1]
    if latest["value"] is None:
        # Member 2's engine needs a current value. A missing latest reading must
        # read as "unknown", never as healthy (Project Guide §10).
        return {
            "subject_id": subject_id, "measurement": measurement, "current_value": None,
            "units": units, "source_id": "X01", "study_id": "demo-001",
            "provenance_kind": "simulated", "history_count": len(valid),
            "rejected_history_count": 0, "baseline_value": None, "robust_z": None,
            "status": "unknown", "quality_state": "missing",
            "reasons": ["Latest scheduled observation is missing; no status computed"],
            "severity_basis": "unvalidated_demo_statistical_rule",
            "not_medical_diagnosis": True, "timestamp_utc": latest["timestamp_utc"],
            "result_origin": "fixture_generator: latest-missing branch",
        }
    current = valid[-1]
    result = m2.get_baseline_result(valid[:-1], current)
    result["timestamp_utc"] = current["timestamp_utc"]
    result["result_origin"] = "member2/analytics.py get_baseline_result()"
    band = reference_band(result, valid[:-1])
    if band:
        result["reference_band"] = band
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--analytics", required=True, type=Path,
                        help="Path to Member 2's analytics.py")
    args = parser.parse_args()
    m2 = load_member2(args.analytics)
    OUT.mkdir(parents=True, exist_ok=True)

    for n, (subject_id, spec) in enumerate(SCENARIOS.items()):
        rng = random.Random(SEED + n)
        indicators = []
        for measurement, units, centre, sd, decimals, bounds in INDICATORS:
            series = build_series(rng, measurement, centre, sd, decimals, bounds,
                                  spec["offsets"].get(measurement, {}),
                                  spec["missing"].get(measurement, set()))
            indicators.append({
                "measurement": measurement, "units": units,
                "source_id": "X01", "provenance_kind": "simulated", "study_id": "demo-001",
                "result": analyse(m2, subject_id, measurement, units, series),
                "series": series,
            })
        bundle = {
            "schema": "crew-vitals/ui-bundle@0.1",
            "subject_id": subject_id,
            "display_name": subject_id.replace("crew_", "Crew "),
            "scenario": spec["scenario"],
            "scenario_label": spec["label"],
            "source_id": "X01",
            "provenance_kind": "simulated",
            "study_id": "demo-001",
            "as_of_utc": iso(AS_OF),
            "generated_by": "frontend/scripts/make_fixtures.py (seeded) + member2/analytics.py get_baseline_result()",
            "notice": "SIMULATED demo data. Not NASA data and not a real astronaut record.",
            "indicators": indicators,
        }
        path = OUT / f"{subject_id}_{spec['scenario']}.json"
        path.write_text(json.dumps(bundle, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
        summary = ", ".join(f"{i['measurement']}={i['result']['status']}" for i in indicators)
        print(f"{path.name}: {summary}")


if __name__ == "__main__":
    main()
