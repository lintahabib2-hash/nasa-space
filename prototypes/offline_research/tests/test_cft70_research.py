import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from cft70_research import analyze_intake, analyze_echo_coverage

def row(n, subject="A", phase="PRE_TEST", day="1", value=2100, group="Control"):
    return {
        "ID": str(n), "Subject": subject, "Group": group,
        "Test_Phase": phase, "BR_Day": day,
        "Daily Energy Intake (kcal/day)": str(value),
    }

def good_rows():
    return [row(i, day=str(i), value=2000 + 10*i) for i in range(1, 6)] + [
        row(6, phase="IN_TEST", day="1", value=3000),
        row(7, phase="POST_TEST", day="0", value=2500),
    ]

class CFT70ResearchTests(unittest.TestCase):
    def test_subject_specific_pre_only_reference(self):
        d=analyze_intake(good_rows())
        p=d["participants"][0]
        self.assertEqual(p["pre_reference_n"],5)
        self.assertEqual(p["pre_reference_median_kcal_day"],2030)
        self.assertEqual(p["pre_reference_mad_kcal_day"],10)
        self.assertEqual(p["observations"][-2]["difference_from_pre_reference_kcal_day"], 970)
    def test_future_or_intervention_does_not_change_baseline(self):
        a=analyze_intake(good_rows())["participants"][0]
        rows=good_rows()
        rows[-1]["Daily Energy Intake (kcal/day)"]="9000"
        b=analyze_intake(rows)["participants"][0]
        self.assertEqual(a["pre_reference_median_kcal_day"],b["pre_reference_median_kcal_day"])
    def test_subjects_do_not_mix(self):
        r=good_rows()+[row(i+7,subject="B",day=str(i),value=5000) for i in range(1,6)]
        d=analyze_intake(r)
        self.assertEqual([x["pre_reference_median_kcal_day"] for x in d["participants"]],[2030,5000])
    def test_ambiguous_pre_day_excluded_preserved(self):
        d=analyze_intake(good_rows()+[row(8,day="X1",value=9999)])
        p=d["participants"][0]
        self.assertEqual(p["pre_reference_median_kcal_day"],2030)
        self.assertEqual(p["excluded_ambiguous_pre_day_labels"],["X1"])
        self.assertEqual(d["ambiguous_pre_day_rows_excluded_from_reference"],1)
        self.assertTrue(any(o["study_day_label"]=="X1" for o in p["observations"]))
    def test_duplicate_phase_day_rejected(self):
        with self.assertRaises(ValueError):
            analyze_intake(good_rows()+[row(8,day="1")])
    def test_conflicting_group_rejected(self):
        with self.assertRaises(ValueError):
            analyze_intake(good_rows()+[row(8,day="X1",group="Exercise A")])
    def test_nonfinite_and_negative_rejected(self):
        for bad in ["NaN","inf","-4","0"]:
            rows=good_rows()
            rows[0]["Daily Energy Intake (kcal/day)"]=bad
            with self.subTest(value=bad), self.assertRaises(ValueError):
                analyze_intake(rows)
    def test_insufficient_pre_history(self):
        d=analyze_intake([row(1),row(2,phase="IN_TEST",day="1")])
        p=d["participants"][0]
        self.assertIsNone(p["pre_reference_median_kcal_day"])
        self.assertIsNone(p["observations"][-1]["difference_from_pre_reference_kcal_day"])
    def test_echo_repeat_coverage_not_independent_baselines(self):
        two=[{"Subject":"A","Test_Phase":"PRE_TEST"}, {"Subject":"A","Test_Phase":"IN_TEST"}]
        three=[{"Subject":"A","Test_Phase":"PRE_TEST","BR_Day":"2","analyzer":"X"},
               {"Subject":"A","Test_Phase":"PRE_TEST","BR_Day":"2","analyzer":"Y"}]
        d=analyze_echo_coverage(two,three)
        self.assertEqual(d["2d_all"]["pre_rows_per_subject_distribution"],{1:1})
        self.assertEqual(d["3d_repeat_rows_ignoring_analyzer"],1)

if __name__=="__main__":
    unittest.main()
