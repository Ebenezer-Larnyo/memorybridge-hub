"""Trusted issue intake must not accept spoofed, incomplete or irrelevant reviews."""
import datetime as dt
import json
import sys
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
import review_issue
import quality

class ReviewIssueTests(unittest.TestCase):
    def setUp(self):
        self.directory={"resources":[{"title":"Care resources","url":"https://example.org/help",
            "organization":"Example","region":"US","kind":"Government",
            "description":"Example public source","language":"English",
            "topics":["Caregiver support"],"status":"Automatically discovered; not reviewed"}]}
        self.ledger={"version":1,"reviews":[]}
        self.payload={"url":"https://example.org/help","decision":"approved",
            "evidence_url":"https://example.org/help",
            "notes":"The original page was inspected for all eight relevant directory criteria.",
            "criteria":{key:"pass" for key in quality.CRITERIA},
            "replace_existing":False}
    def event(self):
        f=chr(96)*3
        return {"action":"opened","issue":{"number":12,"title":"Naviboa resource review: Care resources",
            "created_at":"2026-11-20T18:30:00Z","user":{"login":"sample-reviewer"},
            "body":"NAVIBOA_REVIEW_V1\n"+f+"json\n"+json.dumps(self.payload)+"\n"+f}}
    def test_trusted_identity_is_derived_from_github(self):
        record,ledger=review_issue.issue_to_record(self.event(),self.directory,self.ledger)
        self.assertEqual(record["reviewer_id"],"gh_sample-reviewer")
        self.assertEqual(record["reviewed_on"],"2026-11-20")
        stats=quality.build(self.directory,ledger,dt.date(2026,11,20))["quality-report.json"]["stats"]
        self.assertEqual(stats["human_reviewed_current"],1)
    def test_incomplete_evidence_not_approved(self):
        self.payload["criteria"]["medical_safety_screen"]="concern"
        with self.assertRaises(ValueError):
            review_issue.issue_to_record(self.event(),self.directory,self.ledger)
    def test_needs_revision_requires_concern(self):
        self.payload["decision"]="needs_revision"
        with self.assertRaises(ValueError):
            review_issue.issue_to_record(self.event(),self.directory,self.ledger)
        self.payload["criteria"]["description_accuracy"]="concern"
        record,_=review_issue.issue_to_record(self.event(),self.directory,self.ledger)
        self.assertEqual(record["decision"],"needs_revision")
    def test_unknown_resource_rejected(self):
        self.payload["url"]="https://unknown.example/resource"
        with self.assertRaises(ValueError):
            review_issue.issue_to_record(self.event(),self.directory,self.ledger)
    def test_forged_reviewer_identity_rejected(self):
        self.payload["reviewer_id"]="another-user"
        with self.assertRaises(ValueError):
            review_issue.issue_to_record(self.event(),self.directory,self.ledger)
    def test_existing_review_requires_explicit_replacement(self):
        record,_=review_issue.issue_to_record(self.event(),self.directory,self.ledger)
        self.ledger["reviews"]=[record]
        with self.assertRaises(ValueError):
            review_issue.issue_to_record(self.event(),self.directory,self.ledger)
        self.payload["replace_existing"]=True
        _,ledger=review_issue.issue_to_record(self.event(),self.directory,self.ledger)
        self.assertEqual(len(ledger["reviews"]),1)
    def test_unexpected_field_rejected(self):
        self.payload["medical_certified"]=True
        with self.assertRaises(ValueError):
            review_issue.issue_to_record(self.event(),self.directory,self.ledger)
    def test_malformed_and_non_opened_rejected(self):
        event=self.event();event["issue"]["body"]="not a review"
        with self.assertRaises(ValueError):
            review_issue.issue_to_record(event,self.directory,self.ledger)
        event=self.event();event["action"]="edited"
        with self.assertRaises(ValueError):
            review_issue.issue_to_record(event,self.directory,self.ledger)
    def test_dangerous_url_rejected(self):
        self.payload["evidence_url"]="javascript:alert(1)"
        with self.assertRaises(ValueError):
            review_issue.issue_to_record(self.event(),self.directory,self.ledger)
    def test_notes_must_be_documented(self):
        self.payload["notes"]="Looks fine."
        with self.assertRaises(ValueError):
            review_issue.issue_to_record(self.event(),self.directory,self.ledger)
if __name__=="__main__":unittest.main()
