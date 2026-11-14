"""Regression cases for the illustrative daily persistence policy."""

import unittest

from backend.app.analytics.baseline import get_baseline_result


REFERENCE = (7.0, 7.2, 6.9, 7.1, 7.3, 7.05, 7.15)


def observation(when, value=5.0, **changes):
    return {
        "subject_id": "persistence_test_01",
        "study_id": "engineering_fixture",
        "source_id": "X01",
        "provenance_kind": "simulated",
        "measurement": "sleep_duration",
        "units": "hours",
        "timestamp_utc": when,
        "value": value,
        **changes,
    }


def history(*recent):
    reference = [
        observation(f"2026-11-{day:02d}T07:00:00Z", value)
        for day, value in enumerate(REFERENCE, start=1)
    ]
    return reference + list(recent)


def daily_history():
    return history(
        observation("2026-11-08T07:00:00Z", 5.2),
        observation("2026-11-09T07:00:00Z", 5.1),
    )


class DailyPersistenceTests(unittest.TestCase):
    def assert_insufficient(self, result):
        self.assertEqual(result["status"], "insufficient_persistence_history")
        self.assertEqual(result["quality_state"], "limited_history")

    def test_three_daily_low_readings_require_review(self):
        result = get_baseline_result(
            daily_history(), observation("2026-11-10T07:00:00Z", 4.9)
        )
        self.assertEqual(result["status"], "review")
        self.assertEqual(result["reference_count"], len(REFERENCE))
        self.assertAlmostEqual(result["baseline_value"], 7.1)
        self.assertEqual(result["source_id"], "X01")
        self.assertEqual(result["provenance_kind"], "simulated")
        self.assertTrue(result["not_medical_diagnosis"])

    def test_three_daily_high_readings_require_review(self):
        result = get_baseline_result(
            history(
                observation("2026-11-08T07:00:00Z", 9.1),
                observation("2026-11-09T07:00:00Z", 9.2),
            ),
            observation("2026-11-10T07:00:00Z", 9.3),
        )
        self.assertEqual(result["status"], "review")
        self.assertGreater(result["robust_z"], 3)

    def test_three_readings_weeks_apart_are_not_persistent(self):
        result = get_baseline_result(
            history(
                observation("2026-11-08T07:00:00Z"),
                observation("2026-11-22T07:00:00Z"),
            ),
            observation("2026-12-06T07:00:00Z"),
        )
        self.assert_insufficient(result)
        self.assertIsNotNone(result["robust_z"])

    def test_skipped_day_is_not_bridged(self):
        self.assert_insufficient(get_baseline_result(
            history(
                observation("2026-11-08T07:00:00Z"),
                observation("2026-11-10T07:00:00Z"),
            ),
            observation("2026-11-11T07:00:00Z"),
        ))

    def test_two_recent_readings_on_same_day_do_not_fill_two_days(self):
        self.assert_insufficient(get_baseline_result(
            history(
                observation("2026-11-09T06:00:00Z"),
                observation("2026-11-09T07:00:00Z"),
            ),
            observation("2026-11-10T07:00:00Z"),
        ))

    def test_three_readings_within_one_day_are_not_persistent(self):
        self.assert_insufficient(get_baseline_result(
            history(
                observation("2026-11-10T05:00:00Z"),
                observation("2026-11-10T06:00:00Z"),
            ),
            observation("2026-11-10T07:00:00Z"),
        ))

    def test_calendar_days_are_normalized_to_utc(self):
        result = get_baseline_result(
            history(
                observation("2026-11-09T00:30:00+02:00"),
                observation("2026-11-10T00:30:00+02:00"),
            ),
            observation("2026-11-11T00:30:00+02:00"),
        )
        self.assertEqual(result["status"], "review")

    def test_distinct_local_dates_can_still_be_same_utc_day(self):
        self.assert_insufficient(get_baseline_result(
            history(
                observation("2026-11-08T20:00:00Z"),
                observation("2026-11-09T00:30:00+02:00"),
            ),
            observation("2026-11-10T00:30:00+02:00"),
        ))

    def test_consecutive_days_with_gap_just_under_48_hours_are_allowed(self):
        result = get_baseline_result(
            history(
                observation("2026-11-08T00:00:00.000001Z"),
                observation("2026-11-09T23:59:59.999999Z"),
            ),
            observation("2026-11-10T23:59:59.999999Z"),
        )
        self.assertEqual(result["status"], "review")

    def test_48_hour_gap_still_requires_consecutive_dates(self):
        self.assert_insufficient(get_baseline_result(
            history(
                observation("2026-11-08T00:00:00Z"),
                observation("2026-11-10T00:00:00Z"),
            ),
            observation("2026-11-11T00:00:00Z"),
        ))

    def test_missing_or_invalid_intervening_row_breaks_persistence(self):
        changes = (
            {"value": None},
            {"value": float("nan")},
            {"value": -1},
            {"value": 5.0, "quality_state": "missing"},
        )
        for change in changes:
            with self.subTest(change=change):
                records = daily_history() + [
                    observation("2026-11-08T12:00:00Z", **change)
                ]
                result = get_baseline_result(
                    records, observation("2026-11-10T07:00:00Z")
                )
                self.assert_insufficient(result)
                self.assertEqual(result["history_count"], 9)
                self.assertEqual(result["rejected_history_count"], 1)

    def test_daily_run_recovers_after_older_missing_row(self):
        records = daily_history() + [
            observation("2026-11-07T12:00:00Z", None)
        ]
        result = get_baseline_result(
            records, observation("2026-11-10T07:00:00Z")
        )
        self.assertEqual(result["status"], "review")
        self.assertEqual(result["rejected_history_count"], 1)

    def test_unlocatable_same_series_row_blocks_persistence(self):
        for when in (None, "not-a-timestamp", ""):
            with self.subTest(when=when):
                result = get_baseline_result(
                    daily_history() + [observation(when, None)],
                    observation("2026-11-10T07:00:00Z"),
                )
                self.assert_insufficient(result)
                self.assertEqual(result["rejected_history_count"], 1)

    def test_future_and_other_series_rows_cannot_block_daily_run(self):
        extras = (
            observation("2026-11-11T07:00:00Z", 7.0),
            observation("2026-11-11T07:00:00Z", None),
            observation(None, None, subject_id="another_crew_member"),
            observation(None, None, study_id="another_study"),
            observation(None, None, provenance_kind="manually_entered"),
            observation(None, None, source_id="another_source"),
        )
        for extra in extras:
            with self.subTest(extra=extra):
                result = get_baseline_result(
                    daily_history() + [extra],
                    observation("2026-11-10T07:00:00Z"),
                )
                self.assertEqual(result["status"], "review")
                self.assertEqual(result["history_count"], 9)

    def test_all_duplicate_copies_are_excluded_independent_of_input_order(self):
        duplicates = (
            observation("2026-11-09T07:00:00Z", 5.1),
            observation("2026-11-09T07:00:00Z", 9.0),
            observation("2026-11-09T09:00:00+02:00", 5.1),
        )
        current = observation("2026-11-10T07:00:00Z")
        for duplicate in duplicates:
            with self.subTest(duplicate=duplicate):
                records = daily_history() + [duplicate]
                result = get_baseline_result(records, current)
                self.assert_insufficient(result)
                self.assertEqual(result["history_count"], 8)
                self.assertEqual(result["rejected_history_count"], 2)
                self.assertEqual(
                    result, get_baseline_result(list(reversed(records)), current)
                )

    def test_missing_historical_row_at_current_instant_is_excluded(self):
        result = get_baseline_result(
            daily_history() + [observation("2026-11-10T07:00:00Z", None)],
            observation("2026-11-10T07:00:00Z"),
        )
        self.assertEqual(result["status"], "review")
        self.assertEqual(result["history_count"], 9)


if __name__ == "__main__":
    unittest.main()
