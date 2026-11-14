import unittest

from backend.app.analytics.baseline import (
    get_baseline_result,
    validated,
)


def observation(value=7.0, measurement="sleep_duration",
                units="hours", timestamp="2026-11-14T06:00:00Z"):
    return {
        "subject_id": "crew_01",
        "study_id": "demo",
        "source_id": "X01",
        "provenance_kind": "simulated",
        "measurement": measurement,
        "value": value,
        "units": units,
        "timestamp_utc": timestamp,
    }


class ReviewFixTests(unittest.TestCase):

    def test_missing_latest_value_is_unknown(self):
        result = get_baseline_result(
            [], observation(value=None)
        )
        self.assertEqual(result["status"], "unknown")
        self.assertIsNone(result["robust_z"])

    def test_missing_timestamp_is_unknown(self):
        result = get_baseline_result(
            [], observation(timestamp=None)
        )
        self.assertEqual(result["status"], "unknown")

    def test_missing_quality_flag_is_unknown(self):
        current = observation()
        current["quality_state"] = "missing"
        result = get_baseline_result([], current)
        self.assertEqual(result["status"], "unknown")

    def test_negative_exercise_rejected(self):
        with self.assertRaises(ValueError):
            validated(observation(-30, "exercise_minutes", "minutes"))

    def test_negative_heart_rate_rejected(self):
        with self.assertRaises(ValueError):
            validated(observation(-60, "resting_heart_rate", "bpm"))

    def test_incorrect_units_rejected(self):
        with self.assertRaises(ValueError):
            validated(observation(60, "resting_heart_rate", "hours"))

    def test_unknown_measurement_rejected(self):
        with self.assertRaises(ValueError):
            validated(observation(10, "invented_measurement", "units"))

    def test_valid_exercise_accepted(self):
        _, value = validated(
            observation(30, "exercise_minutes", "minutes")
        )
        self.assertEqual(value, 30.0)


if __name__ == "__main__":
    unittest.main()
