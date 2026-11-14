import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from analytics import get_baseline_result


def obs(day, value, subject="crew_01"):
    return {
        "subject_id": subject,
        "study_id": "demo-001",
        "source_id": "X01",
        "provenance_kind": "simulated",
        "measurement": "sleep_duration",
        "value": value,
        "units": "hours",
        "timestamp_utc": f"2026-11-{day:02d}T07:00:00Z",
    }


NORMAL = [7.0, 7.2, 6.9, 7.1, 7.3, 7.05, 7.15]


class AnalyticsTests(unittest.TestCase):

    def test_sustained_decrease(self):
        values = NORMAL + [5.2, 5.1]
        history = [obs(i, x) for i, x in enumerate(values, 1)]
        result = get_baseline_result(history, obs(10, 4.9))
        self.assertEqual(result["status"], "review")

    def test_one_spike_is_not_persistent(self):
        values = NORMAL + [7.1, 7.2]
        history = [obs(i, x) for i, x in enumerate(values, 1)]
        result = get_baseline_result(history, obs(10, 4.9))
        self.assertEqual(result["status"], "no_persistent_flag")

    def test_short_history(self):
        history = [obs(i, 7.0) for i in range(1, 4)]
        result = get_baseline_result(history, obs(10, 6.0))
        self.assertEqual(result["status"], "insufficient_history")

    def test_zero_mad(self):
        history = [obs(i, 7.0) for i in range(1, 10)]
        result = get_baseline_result(history, obs(10, 5.0))
        self.assertEqual(result["status"], "insufficient_scale")

    def test_future_data_is_excluded(self):
        history = [obs(i, 7.0) for i in range(11, 16)]
        result = get_baseline_result(history, obs(10, 6.0))
        self.assertEqual(result["history_count"], 0)

    def test_subjects_are_separate(self):
        history = [obs(i, 7.0, "crew_02")
                   for i in range(1, 10)]
        result = get_baseline_result(history, obs(10, 6.0))
        self.assertEqual(result["history_count"], 0)

    def test_invalid_sleep_is_rejected(self):
        with self.assertRaises(ValueError):
            get_baseline_result([], obs(10, -2.0))


if __name__ == "__main__":
    unittest.main()
