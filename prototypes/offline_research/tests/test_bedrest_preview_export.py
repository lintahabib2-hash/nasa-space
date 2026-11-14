"""Tests for bed-rest research preview export; no external data needed."""
from pathlib import Path
import sys
import unittest
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from bedrest_preview_export import create_preview


def row(day, value, quality="valid"):
    return {
        "subject_id": "C1G9999", "observation_date": f"2004-09-{day:02d}",
        "study_phase": "IN_TEST", "sleep_duration_hours": value,
        "sleep_efficiency_percent": 87.0 if value is not None else None,
        "sleep_latency_minutes": 13.0 if value is not None else None,
        "provenance_kind": "analog_measured",
        "source_id": "NASA_NLSP_BRSMAct_UTMB_C1", "quality_state": quality,
    }


class BedrestPreviewTests(unittest.TestCase):
    def test_keeps_calendar_dates_and_missing_values(self):
        preview = create_preview(pd.DataFrame([row(1, 7.5), row(2, None, "missing")]))
        subject = preview["participants"][0]
        self.assertEqual(preview["time_precision"], "calendar_date_only")
        self.assertEqual(subject["valid_rows"], 1)
        self.assertEqual(subject["observations"][0]["observed_on"], "2004-09-01")
        self.assertIsNone(subject["observations"][1]["sleep_duration_hours"])
        self.assertEqual(subject["phase_summary"]["IN_TEST"]["valid_nights"], 1)

    def test_rejects_duplicate_participant_date(self):
        with self.assertRaises(ValueError):
            create_preview(pd.DataFrame([row(1, 7.5), row(1, 7.0)]))

    def test_rejects_wrong_provenance(self):
        wrong = row(1, 7.0)
        wrong["provenance_kind"] = "nasa_measured"
        with self.assertRaises(ValueError):
            create_preview(pd.DataFrame([wrong]))

    def test_rejects_unknown_quality(self):
        with self.assertRaises(ValueError):
            create_preview(pd.DataFrame([row(1, 7.5, "healthy")]))

    def test_rejects_missing_measurement_labeled_valid(self):
        with self.assertRaises(ValueError):
            create_preview(pd.DataFrame([row(1, None, "valid")]))


if __name__ == "__main__":
    unittest.main()
