import unittest

from DressingExpert.dressingExpert import run
from DressingExpert.inference import infer


def rule(rule_id, condition, conclusion="", action=""):
    return {"id": rule_id, "condition": condition, "conclusion": conclusion, "action": action}


class InferenceTests(unittest.TestCase):
    def test_current_demo(self):
        result = run()
        self.assertEqual([r["id"] for r in result["matched_rules"]], ["R03", "R06", "R20"])
        self.assertEqual(result["conclusions"], ["check_needed", "change_needed"])
        self.assertEqual(result["action_details"][0]["action"], "change_dressing")

    def test_missing_and_false_are_distinct(self):
        rules = [rule("R1", "confirmed=false", "needs_check")]
        self.assertEqual(infer({}, rules)["missing_facts"], ["confirmed"])
        self.assertEqual(infer({"confirmed": None}, rules)["missing_facts"], ["confirmed"])
        self.assertEqual(infer({"confirmed": "unknown"}, rules)["missing_facts"], ["confirmed"])
        self.assertEqual(infer({"confirmed": False}, rules)["conclusions"], ["needs_check"])
        self.assertEqual(infer({"confirmed": True}, rules)["pending_rules"], [])

    def test_false_and_unknown_is_false(self):
        result = infer({"ph": "low"}, [rule("R1", "ph=high AND co2=high", "check")])
        self.assertEqual(result["pending_rules"], [])

    def test_chaining_with_reversed_order_and_cycle(self):
        rules = [rule("R2", "ready=true", "done=true"),
                 rule("R1", "start=true", "ready=true"),
                 rule("R3", "done=true", "ready=true")]
        facts = {"start": True}
        result = infer(facts, rules)
        self.assertTrue(result["facts"]["done"])
        self.assertEqual(len(result["matched_rules"]), 3)
        self.assertEqual(facts, {"start": True})

    def test_comma_and_numeric_comparisons(self):
        result = infer({"days": 3, "score": 0.5}, [rule("R1", "days>=3, score<0.7", "candidate")])
        self.assertEqual(result["conclusions"], ["candidate"])

    def test_cf_is_only_metadata(self):
        rules = [{**rule("R1", "ph=high", "check_needed"), "cf": "0.7"},
                 rule("R2", "check_needed>=0.7", "followup")]
        result = infer({"ph": "high"}, rules)
        self.assertEqual(result["conclusions"], ["check_needed"])
        self.assertEqual(result["missing_facts"], ["check_needed"])
        self.assertEqual(result["matched_rules"][0]["cf"], 0.7)

    def test_invalid_rules_and_conflicts(self):
        for rules in ([rule("R1", "x=1 AND")],
                      [rule("R1", "x=1"), rule("R1", "x=2")],
                      [rule("R1", "x=1", "x=2")]):
            with self.subTest(rules=rules), self.assertRaises(ValueError):
                infer({"x": 1}, rules)

    def test_boolean_is_not_numeric_score(self):
        with self.assertRaises(ValueError):
            infer({"score": True}, [rule("R1", "score>=0.7")])


if __name__ == "__main__":
    unittest.main()
