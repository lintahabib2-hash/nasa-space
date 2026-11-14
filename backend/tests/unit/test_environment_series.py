"""Environment series metadata, units and input hygiene (Member 4, D01 NASA OSDR EDA RR-1)."""

import math
import tempfile
import unittest
from pathlib import Path

from backend.app.environment import osdr_eda
from backend.app.environment.series import get_environment_series, validate

HEADER = "Controller_Time_GMT,CO2_ppm_ISS\n"


def csv_file(body):
    handle = tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False, encoding="utf-8")
    handle.write(HEADER + body)
    handle.close()
    return Path(handle.name)


class SnapshotContract(unittest.TestCase):
    def setUp(self):
        self.data = get_environment_series()

    def test_metadata_and_attribution(self):
        self.assertEqual(self.data["source_id"], "NASA_OSDR_EDA_RR1")
        self.assertEqual(self.data["provenance_kind"], "nasa_measured")
        self.assertIn("visualization.osdr.nasa.gov/eda", self.data["citation"])
        self.assertTrue(self.data["instrument"])
        self.assertIsNone(self.data["subject_id"], "environment data must never carry a crew id")

    def test_units_and_points(self):
        series = self.data["series"][0]
        self.assertEqual(series["units"], "ppm")
        points = series["points"]
        self.assertEqual(len(points), 300)
        stamps = [p["timestamp_utc"] for p in points]
        self.assertEqual(stamps, sorted(stamps))
        self.assertTrue(all(s.endswith("Z") for s in stamps))
        for p in points:
            if p["value"] is None:
                self.assertNotEqual(p["quality_state"], "valid")
            else:
                self.assertTrue(math.isfinite(p["value"]) and p["value"] >= 0)

    def test_wording_is_not_personal_dose(self):
        text = " ".join(self.data["limitations"]).lower()
        self.assertIn("not personal exposure", text)


class AdapterInputHygiene(unittest.TestCase):
    def build(self, body):
        rows, duplicates = osdr_eda.load_rows(csv_file(body))
        return osdr_eda.build_sample(rows, duplicates)

    def test_blank_and_unreadable_values_are_missing_not_zero(self):
        data = self.build("2014-09-20 03:59,\n2014-09-20 04:04,NA\n2014-09-20 04:09,2600\n")
        points = data["series"][0]["points"]
        self.assertEqual([p["value"] for p in points], [None, None, 2600.0])
        self.assertEqual(data["quality_summary"]["missing_count"], 2)

    def test_negative_reading_is_quarantined(self):
        data = self.build("2014-09-20 03:59,-500\n2014-09-20 04:04,2600\n")
        first = data["series"][0]["points"][0]
        self.assertIsNone(first["value"])
        self.assertEqual(first["quality_state"], "outlier")
        self.assertEqual(data["quality_summary"]["outlier_count"], 1)

    def test_duplicate_timestamps_dropped_and_rows_sorted(self):
        data = self.build("2014-09-20 04:04,2600\n2014-09-20 03:59,2500\n2014-09-20 03:59,2700\n")
        points = data["series"][0]["points"]
        self.assertEqual([p["value"] for p in points], [2500.0, 2600.0])
        self.assertEqual(data["quality_summary"]["duplicate_timestamps_dropped"], 1)

    def test_missing_column_and_bad_timestamp_are_rejected(self):
        with self.assertRaises(ValueError):
            osdr_eda.load_rows(csv_file("2014-09-20 03:59:00,2600\n"))  # seconds: not the export's format
        bad = tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False, encoding="utf-8")
        bad.write("time,co2\n2014-09-20 03:59,2600\n")
        bad.close()
        with self.assertRaises(ValueError):
            osdr_eda.load_rows(Path(bad.name))

    def test_validate_rejects_crew_id_and_nan(self):
        data = self.build("2014-09-20 03:59,2600\n")
        data["subject_id"] = "crew_01"
        with self.assertRaises(ValueError):
            validate(data)
        data["subject_id"] = None
        data["series"][0]["points"][0]["value"] = float("nan")
        with self.assertRaises(ValueError):
            validate(data)


if __name__ == "__main__":
    unittest.main()
