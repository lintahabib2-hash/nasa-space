import unittest

from backend.app.analytics.baseline import get_baseline_result
from backend.app.analytics.validation import validated
from member2.analytics import get_baseline_result as legacy_result


def observation(day, value):
    return {
        "subject_id": "crew_test_01",
        "study_id": "engineering_fixture",
        "source_id": "SIMULATED_TEST",
        "provenance_kind": "simulated",
        "measurement": "sleep_duration",
        "value": value,
        "units": "hours",
        "timestamp_utc": f"2026-11-{day:02d}T07:00:00Z",
    }


class ProductionBaselineTests(unittest.TestCase):

    def test_production_and_legacy_share_implementation(self):
        self.assertIs(get_baseline_result, legacy_result)

    def test_persistent_decrease_requires_review(self):
        values = [
            7.0, 7.2, 6.9, 7.1, 7.3,
            7.05, 7.15, 5.2, 5.1,
        ]
        history = [
            observation(i, value)
            for i, value in enumerate(values, 1)
        ]

        result = get_baseline_result(
            history, observation(10, 4.9)
        )
        self.assertEqual(result["status"], "review")
        self.assertTrue(result["not_medical_diagnosis"])

    def test_future_observations_are_excluded(self):
        result = get_baseline_result(
            [observation(11, 7.0)],
            observation(10, 6.0),
        )
        self.assertEqual(result["history_count"], 0)

    def test_invalid_sleep_units_rejected(self):
        record = observation(10, 6.0)
        record["units"] = "minutes"

        with self.assertRaises(ValueError):
            validated(record)


if __name__ == "__main__":
    unittest.main()
