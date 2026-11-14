import sys
import unittest
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from inspiration4_reference import analyze, METRICS


TIMEPOINTS = (
    "L-92", "L-44", "L-3",
    "R+1", "R+45", "R+82", "R+194"
)


def fixture():
    rows = []

    for sid, start in [("C001", 100), ("C002", 300)]:
        for index, point in enumerate(TIMEPOINTS):
            row = {"Sample Name": f"{sid}_serum_{point}"}

            for offset, column in enumerate(METRICS.values()):
                row[column] = (
                    start + offset +
                    [0, 2, 1, 8, 7, 5, 6][index]
                )

            rows.append(row)

    return pd.DataFrame(rows)


def selected(result, subject, metric, point):
    return next(
        r for r in result["records"]
        if r["subject_id"] == subject
        and r["measurement"] == metric
        and r["timepoint"] == point
    )


class Inspiration4Tests(unittest.TestCase):

    def test_individual_preflight_median(self):
        result = analyze(fixture())

        self.assertEqual(len(result["records"]), 40)

        record = selected(
            result, "C001", "glucose", "R+1"
        )

        self.assertEqual(
            record["preflight_reference_median"], 101
        )
        self.assertEqual(
            record["difference_from_reference"], 7
        )

    def test_subjects_not_mixed(self):
        result = analyze(fixture())

        a = selected(result, "C001", "glucose", "R+1")
        b = selected(result, "C002", "glucose", "R+1")

        self.assertEqual(a["preflight_reference_median"], 101)
        self.assertEqual(b["preflight_reference_median"], 301)

    def test_postflight_data_cannot_change_reference(self):
        frame = fixture()
        original = selected(
            analyze(frame), "C001", "glucose", "R+1"
        )

        col = METRICS["glucose"]
        mask = frame["Sample Name"] == "C001_serum_R+194"
        frame.loc[mask, col] = 9999

        updated = selected(
            analyze(frame), "C001", "glucose", "R+1"
        )

        self.assertEqual(
            original["preflight_reference_median"],
            updated["preflight_reference_median"]
        )

    def test_missing_preflight_value_blocks_reference(self):
        frame = fixture()
        col = METRICS["glucose"]

        frame.loc[
            frame["Sample Name"] == "C001_serum_L-44",
            col
        ] = float("nan")

        record = selected(
            analyze(frame), "C001", "glucose", "R+1"
        )

        self.assertIsNone(
            record["preflight_reference_median"]
        )
        self.assertEqual(
            record["quality_state"], "insufficient_data"
        )

    def test_duplicate_specimen_rejected(self):
        frame = fixture()
        frame = pd.concat(
            [frame, frame.iloc[[0]]], ignore_index=True
        )

        with self.assertRaises(ValueError):
            analyze(frame)

    def test_infinite_value_rejected(self):
        frame = fixture()
        frame[METRICS["glucose"]] = (
            frame[METRICS["glucose"]].astype(float)
        )
        frame.loc[0, METRICS["glucose"]] = float("inf")

        with self.assertRaises(ValueError):
            analyze(frame)


if __name__ == "__main__":
    unittest.main()
