"""Source-preserving CBC comparison tests using clearly synthetic fixtures."""
import sys
import unittest
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from inspiration4_cbc import PRE, POST, METRICS, analyze_cbc

BASE = {
    "HEMOGLOBIN": (14., 11., 18.),
    "HEMATOCRIT": (43., 30., 56.),
    "WHITE BLOOD CELL COUNT": (6., 3., 11.),
    "RED BLOOD CELL COUNT": (4.8, 3., 7.),
    "PLATELET COUNT": (250., 140., 400.),
}


def fixture():
    rows = []
    for sid, offset in (("C001", 0), ("C003", 1)):
        for index, point in enumerate(PRE + POST):
            for analyte, (_, unit) in METRICS.items():
                base, low, high = BASE[analyte]
                value = round(base + offset + 0.1 * index, 5)
                if sid == "C003" and point == "L-92" and analyte == "PLATELET COUNT":
                    value = 12.9
                rows.append({
                    "ANALYTE": analyte, "VALUE": value,
                    "RANGE_MIN": low, "RANGE_MAX": high,
                    "UNITS": unit, "TEST_TYPE": "CBC",
                    "SUBJECT_ID": sid, "TEST_DATE": point,
                })
    return pd.DataFrame(rows)


def pick(result, subject, measurement, timepoint="R+1"):
    return next(r for r in result["records"]
                if r["subject_id"] == subject
                and r["measurement"] == measurement
                and r["timepoint"] == timepoint)


class CBCResearchTests(unittest.TestCase):
    def test_reference_and_original_hemoglobin_units(self):
        result = analyze_cbc(fixture())
        self.assertEqual(len(result["records"]), 40)
        rec = pick(result, "C001", "hemoglobin")
        self.assertAlmostEqual(rec["preflight_reference_median"], 14.1)
        self.assertAlmostEqual(rec["difference_from_reference"], 0.2)
        self.assertEqual(rec["units"], "g/dL")
        self.assertTrue(rec["not_medical_diagnosis"])

    def test_source_platelet_anomaly_is_flagged_not_repaired(self):
        rec = pick(analyze_cbc(fixture()), "C003", "platelet_count")
        self.assertEqual(rec["reference_status"], "source_range_review")
        self.assertIn("preflight_L-92_outside_source_range", rec["source_range_flags"])

    def test_postflight_does_not_change_reference(self):
        frame = fixture()
        before = pick(analyze_cbc(frame), "C001", "hemoglobin")
        mask = ((frame.SUBJECT_ID == "C001") & (frame.TEST_DATE == "R+194")
                & (frame.ANALYTE == "HEMOGLOBIN"))
        frame.loc[mask, "VALUE"] = 9999.
        after = pick(analyze_cbc(frame), "C001", "hemoglobin")
        self.assertEqual(before["preflight_reference_median"], after["preflight_reference_median"])

    def test_missing_preflight_blocks_comparison(self):
        frame = fixture()
        mask = ((frame.SUBJECT_ID == "C001") & (frame.TEST_DATE == "L-44")
                & (frame.ANALYTE == "HEMOGLOBIN"))
        frame.loc[mask, "VALUE"] = None
        rec = pick(analyze_cbc(frame), "C001", "hemoglobin")
        self.assertEqual(rec["reference_status"], "insufficient_history")
        self.assertIsNone(rec["difference_from_reference"])

    def test_duplicate_measurement_rejected(self):
        frame = fixture()
        frame = pd.concat([frame, frame.iloc[[0]]], ignore_index=True)
        with self.assertRaises(ValueError):
            analyze_cbc(frame)

    def test_wrong_units_rejected(self):
        frame = fixture()
        frame.loc[0, "UNITS"] = "%"
        with self.assertRaises(ValueError):
            analyze_cbc(frame)

    def test_nonfinite_value_rejected(self):
        frame = fixture()
        frame.loc[0, "VALUE"] = float("inf")
        with self.assertRaises(ValueError):
            analyze_cbc(frame)

    def test_inverted_source_range_rejected(self):
        frame = fixture()
        frame.loc[0, "RANGE_MIN"] = 999.
        with self.assertRaises(ValueError):
            analyze_cbc(frame)


if __name__ == "__main__":
    unittest.main()
