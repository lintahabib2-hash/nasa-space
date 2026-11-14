import unittest

from backend.app.adapters.simulated_crew import (
    SCENARIOS,
    build_scenario,
)
from backend.app.analytics.baseline import get_baseline_result


class SimulatedCrewTests(unittest.TestCase):

    def evaluate(self, name):
        case = build_scenario(name)
        return get_baseline_result(
            case["history"], case["current"]
        )

    def test_stable(self):
        result = self.evaluate("stable")
        self.assertEqual(
            result["status"], "no_persistent_flag"
        )

    def test_downward_drift(self):
        result = self.evaluate("downward_drift")
        self.assertEqual(result["status"], "review")
        self.assertLess(result["robust_z"], -3)

    def test_missing_is_not_imputed(self):
        case = build_scenario("missing_observation")
        self.assertEqual(
            sum(x["value"] is None for x in case["history"]),
            1,
        )

        result = self.evaluate("missing_observation")
        self.assertEqual(result["rejected_history_count"], 1)
        self.assertEqual(result["history_count"], 9)

    def test_provenance_and_subject_isolation(self):
        cases = [
            build_scenario(name)
            for name in SCENARIOS
        ]

        self.assertEqual(
            len({c["current"]["subject_id"] for c in cases}),
            3,
        )

        for case in cases:
            self.assertTrue(case["not_real_astronaut_data"])

            for record in [*case["history"], case["current"]]:
                self.assertEqual(record["source_id"], "X01")
                self.assertEqual(
                    record["provenance_kind"], "simulated"
                )

        mixed_history = [
            record
            for case in cases
            for record in case["history"]
        ]

        stable = cases[0]

        self.assertEqual(
            get_baseline_result(
                mixed_history, stable["current"]
            ),
            get_baseline_result(
                stable["history"], stable["current"]
            ),
        )


if __name__ == "__main__":
    unittest.main()
