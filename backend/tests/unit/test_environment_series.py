"""Environment series metadata, units and input hygiene (Member 4, D01 NASA OSDR EDA RR-1).

Member 4's tests (structure, 300 points, null handling) converted from pytest to the project's
unittest runner, plus the integration tests for input hygiene and the environment contract.
"""

import math
import tempfile
import unittest
from pathlib import Path

from backend.app.environment import osdr_eda
from backend.app.environment.osdr_eda import parse_co2_value
from backend.app.environment.series import get_environment_series, validate

HEADER = "Controller_Time_GMT,CO2_ppm_ISS\n"


def csv_file(body, header=HEADER):
    handle = tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False, encoding="utf-8")
    handle.write(header + body)
    handle.close()
    return Path(handle.name)


def build(body):
    counts = {}
    rows = osdr_eda.load_rows(csv_file(body), counts)
    return osdr_eda.build_sample(rows, counts["duplicates"])


class Member4SeriesStructure(unittest.TestCase):
    """Member 4's original assertions."""

    def test_environment_series_has_m3_co2_structure_and_300_points(self):
        environment = get_environment_series()

        self.assertEqual(environment["source_id"], "NASA_OSDR_EDA_RR1")
        self.assertEqual(len(environment["series"]), 1)

        co2_series = environment["series"][0]
        self.assertEqual(co2_series["measurement"], "co2_iss")
        self.assertEqual(co2_series["label"], "CO2 (ISS)")
        self.assertEqual(co2_series["units"], "ppm")

        points = co2_series["points"]
        self.assertEqual(len(points), 300)
        timestamps = [point["timestamp_utc"] for point in points]
        self.assertEqual(timestamps, sorted(timestamps))
        self.assertEqual(timestamps[0], environment["time_start_utc"])
        self.assertEqual(timestamps[-1], environment["time_end_utc"])

        for point in points:
            value = point["value"]
            self.assertTrue(value is None or math.isfinite(value))
            self.assertEqual(point["quality_state"], "missing" if value is None else "valid")

    def test_missing_or_non_finite_co2_values_become_null(self):
        for value in [None, "", " ", "NaN", "Infinity", "-Infinity"]:
            with self.subTest(value=value):
                self.assertIsNone(parse_co2_value(value))

    def test_zero_co2_reading_is_not_treated_as_missing(self):
        self.assertEqual(parse_co2_value("0"), 0.0)


class SnapshotContract(unittest.TestCase):
    def setUp(self):
        self.data = get_environment_series()

    def test_metadata_and_attribution(self):
        self.assertEqual(self.data["provenance_kind"], "nasa_measured")
        self.assertIn("visualization.osdr.nasa.gov/eda", self.data["citation"])
        self.assertTrue(self.data["instrument"])
        self.assertIsNone(self.data["subject_id"], "environment data must never carry a crew id")

    def test_wording_is_not_personal_dose(self):
        self.assertIn("not personal exposure", " ".join(self.data["limitations"]).lower())


class AdapterInputHygiene(unittest.TestCase):
    def test_blank_and_unreadable_values_are_missing_not_zero(self):
        data = build("2014-09-20 03:59,\n2014-09-20 04:04,NA\n2014-09-20 04:09,2600\n")
        points = data["series"][0]["points"]
        self.assertEqual([p["value"] for p in points], [None, None, 2600.0])
        self.assertEqual(data["quality_summary"]["missing_count"], 2)

    def test_negative_reading_is_quarantined(self):
        data = build("2014-09-20 03:59,-500\n2014-09-20 04:04,2600\n")
        first = data["series"][0]["points"][0]
        self.assertIsNone(first["value"])
        self.assertEqual(first["quality_state"], "outlier")
        self.assertEqual(data["quality_summary"]["outlier_count"], 1)

    def test_duplicate_timestamps_dropped_and_rows_sorted(self):
        data = build("2014-09-20 04:04,2600\n2014-09-20 03:59,2500\n2014-09-20 03:59,2700\n")
        points = data["series"][0]["points"]
        self.assertEqual([p["value"] for p in points], [2500.0, 2600.0])
        self.assertEqual(data["quality_summary"]["duplicate_timestamps_dropped"], 1)

    def test_missing_column_and_bad_timestamp_are_rejected(self):
        with self.assertRaises(ValueError):
            osdr_eda.load_rows(csv_file("2014-09-20 03:59:00,2600\n"))  # seconds: not the export's format
        with self.assertRaises(ValueError):
            osdr_eda.load_rows(csv_file("2014-09-20 03:59,2600\n", header="time,co2\n"))

    def test_full_export_path_is_used_when_present(self):
        data = osdr_eda.get_environment_series(csv_file("2014-09-20 03:59,2600\n2014-09-20 04:04,2610\n"))
        self.assertEqual(data["row_count"], 2)

    def test_validate_rejects_crew_id_and_nan(self):
        data = build("2014-09-20 03:59,2600\n")
        data["subject_id"] = "crew_01"
        with self.assertRaises(ValueError):
            validate(data)
        data["subject_id"] = None
        data["series"][0]["points"][0]["value"] = float("nan")
        with self.assertRaises(ValueError):
            validate(data)


if __name__ == "__main__":
    unittest.main()
