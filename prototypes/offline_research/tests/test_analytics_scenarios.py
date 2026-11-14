import sys
import unittest
from pathlib import Path

sys.path.insert(
    0, str(Path(__file__).resolve().parents[1])
)

from analytics import get_baseline_result


def observation(day, value):
    return {
        "subject_id": "scenario_01",
        "study_id": "engineering-fixture",
        "source_id": "SIMULATED_TEST",
        "provenance_kind": "simulated",
        "measurement": "sleep_duration",
        "value": value,
        "units": "hours",
        "timestamp_utc": f"2026-11-{day:02d}T07:00:00Z",
    }


REFERENCE = [7.0, 7.2, 6.9, 7.1, 7.3, 7.05, 7.15]


class ScenarioTests(unittest.TestCase):

    def test_stable_history_has_no_persistent_flag(self):
        values = REFERENCE + [7.1, 7.2]
        history = [
            observation(i, value)
            for i, value in enumerate(values, 1)
        ]

        result = get_baseline_result(
            history, observation(10, 7.1)
        )

        self.assertEqual(
            result["status"], "no_persistent_flag"
        )
        self.assertTrue(result["not_medical_diagnosis"])

    def test_gradual_downward_drift(self):
        values = REFERENCE + [6.5, 6.0]
        history = [
            observation(i, value)
            for i, value in enumerate(values, 1)
        ]

        result = get_baseline_result(
            history, observation(10, 5.5)
        )

        self.assertEqual(result["status"], "review")
        self.assertLess(result["robust_z"], -3.0)

    def test_missing_record_not_imputed(self):
        history = [
            observation(i, value)
            for i, value in enumerate(REFERENCE, 1)
        ]

        history.extend([
            observation(8, None),
            observation(9, 7.1),
            observation(10, 7.2),
        ])

        result = get_baseline_result(
            history, observation(11, 7.0)
        )

        self.assertEqual(result["history_count"], 9)
        self.assertEqual(
            result["rejected_history_count"], 1
        )
        self.assertEqual(
            result["status"], "no_persistent_flag"
        )


if __name__ == "__main__":
    unittest.main()
