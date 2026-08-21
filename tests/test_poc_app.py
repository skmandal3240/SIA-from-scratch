import tempfile
import unittest
from pathlib import Path

import poc_app


class PocAppTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        poc_app.STATE_DIR = Path(self.temp_dir.name)
        poc_app.STATE_FILE = poc_app.STATE_DIR / "draft.json"
        poc_app.app.config.update(TESTING=True)
        self.client = poc_app.app.test_client()

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_health_and_core_pages(self):
        for path in ["/", "/company", "/documents", "/support", "/gpu", "/review"]:
            response = self.client.get(path)
            self.assertEqual(response.status_code, 200, path)
        health = self.client.get("/healthz")
        self.assertEqual(health.json["ok"], True)
        self.assertEqual(health.headers["X-Content-Type-Options"], "nosniff")
        self.assertEqual(health.headers["X-Frame-Options"], "DENY")

    def test_company_save_and_export(self):
        response = self.client.post(
            "/company",
            data={
                "company_name": "Demo AI Private Limited",
                "alternate_name": "Demo Intelligence Private Limited",
                "state": "Bihar",
                "district": "Madhubani",
                "city": "Madhubani",
                "postal_code": "847211",
                "founder_name": "Demo Founder",
                "founder_email": "founder@example.com",
                "founder_age": "21",
                "has_second_member": "true",
                "second_member_name": "Demo Member",
                "has_second_director": "true",
                "second_director_name": "Demo Director",
                "ai_product": "Hindi-first assistant",
                "target_users": "Small businesses",
                "dsc_status": "planned",
                "authorised_capital": "review",
                "paid_up_capital": "review",
                "shareholding_notes": "review",
            },
            follow_redirects=False,
        )
        self.assertEqual(response.status_code, 200)
        export = self.client.get("/export.json")
        self.assertEqual(export.status_code, 200)
        self.assertEqual(export.json["company_profile"]["district"], "Madhubani")
        self.assertIn("review_gate", export.json)

    def test_document_flags_are_metadata_only(self):
        response = self.client.post("/documents", data={"office_proof_uploaded": "true"})
        self.assertEqual(response.status_code, 200)
        export = self.client.get("/export.json").json
        self.assertTrue(export["company_profile"]["district"] == "Madhubani")
        self.assertIn("CA/CS/lawyer review", export["review_gate"])


if __name__ == "__main__":
    unittest.main()
