import unittest

from closeout import evaluate


def base_case():
    statuses = {
        "EXPO-01": "passed_live",
        "EXPO-02": "not_run",
        "EXPO-03": "accepted_receipt",
        "EXPO-04": "accepted_receipt",
        "EXPO-05": "partial",
        "EXPO-06": "partial",
        "EXPO-07": "partial",
        "EXPO-08": "partial",
        "EXPO-09": "partial",
        "EXPO-10": "partial",
        "EXPO-11": "passed_artifact",
        "EXPO-12": "partial",
    }
    return {
        "gates": [{"id": gate_id, "status": status} for gate_id, status in statuses.items()],
        "route_check": {
            "status": "PASS",
            "passed": 9,
            "total": 9,
            "new_requests_created": 0,
            "emails_sent": 0,
        },
    }


class CloseoutTests(unittest.TestCase):
    def test_current_case_is_public_go_only(self):
        result = evaluate(base_case())
        self.assertEqual(result["accepted_gates"], 4)
        self.assertEqual(result["verdicts"]["public_discovery_and_intake"], "GO")
        self.assertEqual(result["verdicts"]["commercial_transaction"], "NO_GO")
        self.assertEqual(result["verdicts"]["autonomous_operation"], "NO_GO")
        self.assertEqual(result["verdicts"]["full_exhibition_launch"], "NO_GO")

    def test_route_failure_closes_public_intake(self):
        case = base_case()
        case["route_check"]["status"] = "FAIL"
        self.assertEqual(evaluate(case)["verdicts"]["public_discovery_and_intake"], "NO_GO")

    def test_get_check_must_not_create_requests(self):
        case = base_case()
        case["route_check"]["new_requests_created"] = 1
        self.assertFalse(evaluate(case)["route_check"]["safe_get_only"])

    def test_partial_commercial_gate_is_not_accepted(self):
        result = evaluate(base_case())
        self.assertIn("EXPO-08", result["open_gate_ids"])

    def test_all_gates_produce_full_go(self):
        case = base_case()
        for gate in case["gates"]:
            gate["status"] = "accepted_live"
        result = evaluate(case)
        self.assertTrue(all(value == "GO" for value in result["verdicts"].values()))

    def test_missing_gate_is_rejected(self):
        case = base_case()
        case["gates"].pop()
        with self.assertRaises(ValueError):
            evaluate(case)

    def test_duplicate_gate_is_rejected(self):
        case = base_case()
        case["gates"].append(dict(case["gates"][0]))
        with self.assertRaises(ValueError):
            evaluate(case)


if __name__ == "__main__":
    unittest.main()
