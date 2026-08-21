import unittest

from poc_data import default_draft
from poc_rules import gpu_plan, match_programs, readiness


class PocRulesTests(unittest.TestCase):
    def complete_profile(self):
        draft = default_draft()
        draft.update(
            {
                "founder_name": "Demo Founder",
                "founder_email": "founder@example.com",
                "founder_age": "21",
                "has_second_member": True,
                "second_member_name": "Demo Member",
                "has_second_director": True,
                "second_director_name": "Demo Director",
                "ai_product": "A Hindi-first private AI assistant for small businesses.",
                "target_users": "Small businesses in India",
                "address_line": "Demo office, Madhubani",
                "postal_code": "847211",
                "office_proof_uploaded": True,
                "director_proofs_uploaded": True,
                "dsc_status": "planned",
                "authorised_capital": "professional review",
                "paid_up_capital": "professional review",
                "shareholding_notes": "Review with a company secretary",
            }
        )
        return draft

    def test_default_profile_exposes_second_person_gates(self):
        report = readiness(default_draft())
        self.assertEqual(report["overall"], "incomplete")
        self.assertIn("second member/subscriber", " ".join(report["issues"]))
        self.assertIn("second director", " ".join(report["issues"]))

    def test_complete_profile_still_requires_professional_review(self):
        report = readiness(self.complete_profile())
        self.assertEqual(report["overall"], "professional_review_required")
        self.assertTrue(any(item["status"] == "professional_review" for item in report["items"]))

    def test_minor_profile_is_blocked(self):
        draft = self.complete_profile()
        draft["founder_age"] = "17"
        report = readiness(draft)
        self.assertEqual(report["overall"], "blocked")
        self.assertTrue(any("below 18" in warning for warning in report["warnings"]))

    def test_bihar_support_is_conditional_not_guaranteed(self):
        matches = {item["id"]: item for item in match_programs(self.complete_profile())}
        self.assertEqual(matches["bihar-policy"]["status"], "requires_verification")
        self.assertEqual(matches["bihar-policy"]["support_type"], "state_support_verify_grant_or_loan")

    def test_support_types_are_not_all_called_grants(self):
        matches = match_programs(self.complete_profile())
        types = {item["support_type"] for item in matches}
        self.assertIn("in_kind_compute_or_discount", types)
        self.assertIn("accelerator_or_co_investment", types)
        self.assertIn("direct_grant_or_seed_support", types)

    def test_gpu_plan_is_transparent_and_has_no_price_promise(self):
        plan = gpu_plan({"model_params_b": "1", "workload_type": "parameter-efficient fine-tuning", "gpu_hours": "20", "storage_gb": "40", "budget_inr": "0"})
        self.assertGreater(plan["estimated_memory_gb"], 0)
        self.assertEqual(plan["inputs"]["budget_inr"], 0)
        self.assertTrue(all("price" not in route["why"].lower() or "pricing" in route["why"].lower() for route in plan["routes"]))
        self.assertIn("No cash budget", plan["recommendations"][0])


if __name__ == "__main__":
    unittest.main()
