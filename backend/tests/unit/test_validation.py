"""Regression tests for malformed inputs hidden by missing observations."""

import unittest
import json

from backend.app.analytics.baseline import get_baseline_result, validated


def observation(**changes):
    return {
        "subject_id": "crew_01",
        "study_id": "engineering_fixture",
        "source_id": "X01",
        "provenance_kind": "simulated",
        "measurement": "sleep_duration",
        "value": 7.0,
        "units": "hours",
        "timestamp_utc": "2026-11-14T06:00:00Z",
        **changes,
    }


class ObservationValidationTests(unittest.TestCase):
    def test_missingness_cannot_hide_invalid_measurement_or_units(self):
        for missing in ({"value": None}, {"timestamp_utc": None}, {"quality_state": "missing"}):
            for malformed in ({"measurement": "invented"}, {"units": "minutes"}):
                with self.subTest(missing=missing, malformed=malformed):
                    with self.assertRaises(ValueError):
                        get_baseline_result([], observation(**{**missing, **malformed}))

    def test_missing_timestamp_cannot_hide_invalid_value(self):
        for value in (True, False, "invalid", "", [], {}, float("nan"), float("inf"), -1, 25, 10**400):
            with self.subTest(value_type=type(value).__name__):
                with self.assertRaises(ValueError):
                    get_baseline_result([], observation(value=value, timestamp_utc=None))

    def test_missing_value_cannot_hide_invalid_timestamp(self):
        for when in (False, 0, [], {}, " ", "bad", "2026-11-14", "0001-01-01T00:00:00+14:00"):
            with self.subTest(timestamp=when):
                with self.assertRaises(ValueError):
                    get_baseline_result([], observation(value=None, timestamp_utc=when))

    def test_missing_marker_cannot_hide_invalid_supplied_value(self):
        with self.assertRaises(ValueError):
            get_baseline_result([], observation(value=float("nan"), quality_state="missing"))

    def test_metadata_is_validated_by_both_public_entry_points(self):
        for field in ("subject_id", "study_id", "source_id", "provenance_kind", "measurement", "units"):
            for bad in (None, "", "  ", [], {}):
                for function in (validated, lambda row: get_baseline_result([], row)):
                    with self.subTest(field=field, bad=bad):
                        with self.assertRaises(ValueError):
                            function(observation(**{field: bad}))

    def test_unknown_quality_states_are_rejected(self):
        for quality in (None, "", "invalid", True, [], {}):
            with self.subTest(quality=quality):
                with self.assertRaises(ValueError):
                    get_baseline_result([], observation(value=None, quality_state=quality))
                with self.assertRaises(ValueError):
                    validated(observation(quality_state=quality))

    def test_genuinely_missing_current_is_unknown(self):
        for missing in ({"value": None}, {"timestamp_utc": None}, {"timestamp_utc": ""}, {"quality_state": "missing"}):
            with self.subTest(missing=missing):
                result = get_baseline_result([], observation(**missing))
                self.assertEqual(result["status"], "unknown")
                self.assertIsNone(result["current_value"])
                self.assertIsNone(result["robust_z"])

    def test_omitted_value_or_timestamp_is_unknown(self):
        for field in ("value", "timestamp_utc"):
            row = observation()
            del row[field]
            self.assertEqual(get_baseline_result([], row)["status"], "unknown")

    def test_missing_current_retains_scientific_identity(self):
        row = observation(value=None)
        result = get_baseline_result([], row)
        for field in ("subject_id", "study_id", "source_id", "provenance_kind", "measurement", "units"):
            self.assertEqual(result[field], row[field])
        self.assertTrue(result["not_medical_diagnosis"])
        self.assertEqual(result["severity_basis"], "unvalidated_demo_statistical_rule")

    def test_direct_validation_requires_a_usable_observation(self):
        for missing in ({"value": None}, {"timestamp_utc": ""}, {"quality_state": "missing"}):
            with self.subTest(missing=missing):
                with self.assertRaises(ValueError):
                    validated(observation(**missing))

    def test_optional_quality_and_timezone_offsets_remain_supported(self):
        for quality in ({}, {"quality_state": "valid"}):
            when, value = validated(observation(timestamp_utc="2026-11-14T11:30:00+05:30", **quality))
            self.assertEqual(when.isoformat(), "2026-11-14T06:00:00+00:00")
            self.assertEqual(value, 7.0)

    def test_direct_validation_normalizes_conversion_overflow(self):
        for row in (observation(value=10**400), observation(timestamp_utc="9999-12-31T23:59:59-14:00")):
            with self.assertRaises(ValueError):
                validated(row)

    def test_tiny_reference_spread_cannot_produce_infinite_json_scores(self):
        values = [0.0, 5e-324, 1e-323, 1.5e-323, 2e-323, 2.5e-323, 3e-323, 24.0, 24.0]
        history = [
            observation(value=value, timestamp_utc=f"2026-11-{day:02d}T06:00:00Z")
            for day, value in enumerate(values, start=1)
        ]
        result = get_baseline_result(history, observation(value=24.0, timestamp_utc="2026-11-10T06:00:00Z"))
        self.assertEqual(result["status"], "insufficient_scale")
        self.assertIsNone(result["robust_z"])
        json.dumps(result, allow_nan=False)

    def test_integer_measurements_reject_fractional_values(self):
        for measurement, units, value in (("mood", "score_1_5", 2.5), ("exercise_minutes", "minutes", 20.5)):
            with self.subTest(measurement=measurement):
                with self.assertRaises(ValueError):
                    validated(observation(measurement=measurement, units=units, value=value))

    def test_non_object_current_is_rejected(self):
        for row in (None, [], "missing"):
            with self.subTest(row=row):
                with self.assertRaises(ValueError):
                    get_baseline_result([], row)

    def test_invalid_history_collection_is_rejected_for_valid_current(self):
        for records in (None, {}, "history"):
            with self.subTest(records=records):
                with self.assertRaises(ValueError):
                    get_baseline_result(records, observation())


if __name__ == "__main__":
    unittest.main()
