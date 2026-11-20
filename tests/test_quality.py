"""Review provenance and queue tests: no network requests, no fabricated approvals."""
import datetime as dt
import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("quality", ROOT / "scripts/quality.py")
quality = importlib.util.module_from_spec(spec)
spec.loader.exec_module(quality)

class TestQuality(unittest.TestCase):
    def setUp(self):
        self.today = dt.date(2026, 11, 20)
        self.resources = {"updated": "2026-11-20", "resources": [{
            "url": "https://example.org/info", "title": "Dementia support",
            "description": "Visit the original organization for information and support.",
            "organization": "Example", "region": "US", "language": "Not tagged",
            "kind": "Government", "topics": ["Caregiver support"],
            "status": "Link checked; content not reviewed", "checked": "2026-11-20"
        }]}
        self.approved = {"url": "https://example.org/info", "reviewer_id": "reviewer01",
                         "reviewed_on": "2026-11-20", "decision": "approved",
                         "evidence_url": "https://example.org/info",
                         "notes": "The listing accurately matches the inspected source and its intended audience.",
                         "criteria": {key: "pass" for key in quality.CRITERIA}}
    def test_no_automatic_approval(self):
        report = quality.build(self.resources, {"version": 1, "reviews": []}, self.today)
        self.assertEqual(report["quality-report.json"]["stats"]["human_reviewed_current"], 0)
        self.assertEqual(report["quality-report.json"]["stats"]["descriptions_missing"], 1)
        self.assertEqual(report["quality-report.json"]["stats"]["language_untagged"], 1)
        self.assertEqual(len(report["review-queue.json"]["items"]), 1)
        self.assertEqual(report["quality-index.json"]["review_index"], {})
    def test_valid_human_approval(self):
        output = quality.build(self.resources, {"version": 1, "reviews": [self.approved]}, self.today)
        self.assertEqual(output["quality-report.json"]["stats"]["human_reviewed_current"], 1)
        self.assertEqual(output["review-queue.json"]["items"], [])
        self.assertEqual(output["quality-index.json"]["review_index"]["https://example.org/info"]["decision"], "approved")
    def test_reject_unsubstantiated_approval(self):
        review = {**self.approved, "criteria": {**self.approved["criteria"], "medical_safety_screen": "concern"}}
        with self.assertRaises(ValueError):
            quality.build(self.resources, {"version": 1, "reviews": [review]}, self.today)
    def test_reject_unknown_and_duplicate_reviews(self):
        bad = {**self.approved, "url": "https://other.org/no"}
        with self.assertRaises(ValueError):
            quality.build(self.resources, {"version": 1, "reviews": [bad]}, self.today)
        with self.assertRaises(ValueError):
            quality.build(self.resources, {"version": 1, "reviews": [self.approved, self.approved]}, self.today)
    def test_expiration_removes_approval_label(self):
        old = {**self.approved, "reviewed_on": "2026-01-01"}
        report = quality.build(self.resources, {"version": 1, "reviews": [old]}, self.today)
        self.assertEqual(report["quality-report.json"]["stats"]["human_reviewed_current"], 0)
        self.assertEqual(report["quality-report.json"]["stats"]["review_due"], 1)
        self.assertTrue(report["quality-index.json"]["review_index"]["https://example.org/info"]["review_due"])
    def test_flagged_resource_is_queued(self):
        bad = {**self.approved, "decision": "needs_revision",
               "criteria": {**self.approved["criteria"], "description_accuracy": "concern"}}
        output = quality.build(self.resources, {"version": 1, "reviews": [bad]}, self.today)
        self.assertEqual(output["quality-report.json"]["stats"]["needs_revision"], 1)
        self.assertIn("correction_requested", output["review-queue.json"]["items"][0]["flags"])
    def test_current_directory_remains_unapproved(self):
        resources, ledger = quality.read_inputs()
        quality.validate_ledger(resources, ledger)
        report = quality.build(resources, ledger)
        self.assertEqual(report["quality-report.json"]["stats"]["human_reviewed_current"],
                         sum(1 for review in ledger["reviews"] if review["decision"] == "approved"
                             and (dt.datetime.now(dt.timezone.utc).date()
                                  - dt.date.fromisoformat(review["reviewed_on"])).days <= 180))

if __name__ == "__main__":
    unittest.main()
