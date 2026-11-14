import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from retrospective_trends import add_trends


def dataset(records):
    return {
        "source_id": "NASA_NLSP_BRSMAct_UTMB_C1",
        "provenance_kind": "analog_measured",
        "time_precision": "calendar_date_only",
        "participants": [{
            "subject_id": "TEST_01",
            "observations": records,
        }],
    }


def row(day, value, phase="IN_TEST"):
    return {
        "observed_on": f"2004-09-{day:02d}",
        "study_phase": phase,
        "quality_state": "valid" if value is not None else "missing",
        "sleep_duration_hours": value,
    }


def results(records):
    return add_trends(dataset(records))["participants"][0]["observations"]


class RetrospectiveTests(unittest.TestCase):

    def test_uses_prior_history_only(self):
        records = [row(i, v) for i, v in enumerate(
            [7.0, 7.1, 7.2, 7.3, 7.4, 5.0], start=1
        )]
        last = results(records)[-1]
        self.assertEqual(
            last["prior_14d_median_sleep_hours"], 7.2
        )
        self.assertEqual(
            last["difference_from_reference_hours"], -2.2
        )

    def test_future_records_do_not_change_past(self):
        base = [row(i, 7.0 + i / 10) for i in range(1, 7)]
        before = results(base)[-1]
        after = results(base + [row(7, 2.0)])[-2]
        self.assertEqual(before, after)

    def test_phase_history_is_separate(self):
        records = [
            *[row(i, 7.0, "PRE_TEST") for i in range(1, 6)],
            row(6, 5.0, "IN_TEST"),
        ]
        last = results(records)[-1]
        self.assertEqual(last["prior_reference_count"], 0)
        self.assertEqual(
            last["trend_quality"], "insufficient_reference"
        )

    def test_missing_data_is_not_imputed(self):
        records = [
            *[row(i, 7.0) for i in range(1, 6)],
            row(6, None),
        ]
        last = results(records)[-1]
        self.assertEqual(last["trend_quality"], "missing_observation")
        self.assertIsNone(last["difference_from_reference_hours"])

    def test_duplicate_dates_rejected(self):
        with self.assertRaises(ValueError):
            results([row(1, 7.0), row(1, 6.0)])


if __name__ == "__main__":
    unittest.main()
