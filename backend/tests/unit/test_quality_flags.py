"""Project Guide §6 quality states "outlier" and "unknown" are safe states, not crashes (integration fix)."""

import unittest

from backend.app.analytics.baseline import get_baseline_result, validated


def observation(day, value=7.0, **extra):
    return {
        "subject_id": "crew_test_01", "study_id": "engineering_fixture", "source_id": "SIMULATED_TEST",
        "provenance_kind": "simulated", "measurement": "sleep_duration", "value": value, "units": "hours",
        "timestamp_utc": f"2026-11-{day:02d}T06:00:00Z", **extra,
    }


HISTORY = [observation(d, 7.0 + 0.1 * (d % 3)) for d in range(1, 11)]


class QualityFlags(unittest.TestCase):
    def test_flagged_current_reading_is_unknown_with_reason(self):
        for state in ("outlier", "unknown"):
            with self.subTest(state=state):
                result = get_baseline_result(HISTORY, observation(11, 2.0, quality_state=state))
                self.assertEqual(result["status"], "unknown")
                self.assertIn(state, result["reasons"][0])
                self.assertIsNone(result["robust_z"])

    def test_flagged_history_is_excluded_not_scored(self):
        history = HISTORY + [observation(11, 1.0, quality_state="outlier")]
        result = get_baseline_result(history, observation(12, 7.1))
        self.assertEqual(result["rejected_history_count"], 1)
        self.assertNotEqual(result["status"], "review")

    def test_flagged_reading_cannot_be_used_directly(self):
        for state in ("outlier", "unknown"):
            with self.subTest(state=state), self.assertRaises(ValueError):
                validated(observation(1, quality_state=state))

    def test_malformed_states_still_rejected(self):
        for state in ("bogus", "", None):
            with self.subTest(state=state), self.assertRaises(ValueError):
                get_baseline_result(HISTORY, observation(11, quality_state=state))


if __name__ == "__main__":
    unittest.main()
