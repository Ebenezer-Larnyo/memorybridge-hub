"""Automatic directory screening is conservative and never fabricates human reviews."""
import copy
import datetime as dt
import sys
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
import auto_screen
import quality

class AutoScreenTests(unittest.TestCase):
    def setUp(self):
        self.today=dt.date(2026,11,21)
        self.item={"title":"A dementia caregiver education and support resource",
            "url":"https://www.who.int/publications/i/item/9789241515863",
            "organization":"WHO","kind":"Public health","region":"Global",
            "topics":["Daily care","Caregiver support"],"language":"English",
            "description":"A WHO training and support program for people providing care to someone living with dementia.",
            "status":"Link checked; content not reviewed","checked":"2026-11-20"}
        self.resources={"updated":"2026-11-20","resources":[self.item]}
        self.empty={"version":1,"reviews":[]}
        self.policy,self.allowed,self.sensitive=auto_screen.read_policy()
    def screen(self,item=None):
        return auto_screen.screen_one(item or self.item,self.policy,self.allowed,self.sensitive,self.today)
    def test_curated_publisher_with_recent_link_and_complete_metadata_passes(self):
        self.assertTrue(self.screen()["passed"])
        out=quality.build(self.resources,self.empty,self.today)
        self.assertEqual(out["quality-report.json"]["stats"]["automated_screened"],1)
        self.assertEqual(out["quality-report.json"]["stats"]["human_reviewed_current"],0)
        self.assertEqual(out["quality-report.json"]["stats"]["manual_screen_pending"],0)
        self.assertEqual(out["quality-index.json"]["review_index"],{})
        self.assertEqual(len(out["quality-index.json"]["auto_screen_index"]),1)
        self.assertIn("NOT clinical or human",out["quality-index.json"]["auto_screen_index"][self.item["url"]]["scope"])
    def test_clinical_topics_never_autoscreen(self):
        for topic in ("Symptoms","Diagnosis","Treatment & medication","Financial & legal","End of life & hospice"):
            x={**self.item,"topics":[topic]}
            with self.subTest(topic=topic):
                result=self.screen(x)
                self.assertFalse(result["passed"])
                self.assertIn("clinically_or_legally_sensitive_topic",result["checks"])
    def test_publisher_impersonation_and_near_miss_domain_rejected(self):
        for url in ("https://who.int.evil.example/caregiving",
                    "http://www.who.int/publications/i/item/9789241515863",
                    "https://www.who.int.evil.example/","https://www.who.int:8443/test",
                    "https://www.who.int/login"):
            x={**self.item,"url":url}
            with self.subTest(url=url):self.assertFalse(self.screen(x)["passed"])
        for org in ("WHO International","Fake WHO","Alzheimer's Researchers"):
            with self.subTest(org=org):
                x={**self.item,"organization":org}
                self.assertIn("publisher_not_allowlisted",self.screen(x)["checks"])
    def test_stale_and_future_link_dates_fail(self):
        for when in (None,"2026-10-01","2026-11-22","not a date"):
            with self.subTest(when=when):
                x={**self.item,"checked":when}
                self.assertIn("link_not_recently_checked",self.screen(x)["checks"])
    def test_placeholder_and_language_failure(self):
        x={**self.item,"description":"Visit the original organization for information and support.","language":"Not tagged"}
        r=self.screen(x)
        self.assertIn("description_incomplete",r["checks"])
        self.assertIn("language_not_tagged",r["checks"])
    def test_clinical_trial_page_mistagged_as_research_remains_pending(self):
        x={**self.item,"title":"Participate in a clinical trial",
           "url":"https://www.who.int/clinical-trials/participation",
           "topics":["Research & awareness"]}
        self.assertIn("sensitive_title_or_url",self.screen(x)["checks"])
    def test_suspicious_medical_claim_blocks_auto_badge(self):
        x={**self.item,"description":"An instant cure for dementia is promised; this needs a specialist to assess the source claims."}
        self.assertIn("potentially_misleading_claim",self.screen(x)["checks"])
    def test_manual_exclusion_always_beats_automated_screen(self):
        review={"url":self.item["url"],"reviewer_id":"reviewer01","reviewed_on":"2026-11-21",
            "evidence_url":self.item["url"],
            "notes":"This directory listing should be withheld because its metadata is incorrect.",
            "decision":"excluded",
            "criteria":{c:"concern" for c in quality.CRITERIA}}
        result=quality.build(self.resources,{"version":1,"reviews":[review]},self.today)
        self.assertEqual(result["quality-report.json"]["stats"]["excluded"],1)
        self.assertEqual(result["quality-report.json"]["stats"]["automated_screened"],0)
        self.assertEqual(result["quality-index.json"]["auto_screen_index"],{})
    def test_unlisted_resources_stay_in_manual_screen_queue(self):
        x={**self.item,"url":"https://example.org/caregiver-training"}
        result=quality.build({"updated":"2026-11-20","resources":[x]},self.empty,self.today)
        self.assertEqual(result["quality-report.json"]["stats"]["manual_screen_pending"],1)
        self.assertEqual(result["review-queue.json"]["total_pending"],1)
        self.assertEqual(result["quality-index.json"]["auto_screen_index"],{})
    def test_policy_has_conservative_source_and_topics_list(self):
        self.assertGreaterEqual(len(self.allowed),8)
        self.assertTrue({"Diagnosis","Treatment & medication","End of life & hospice"}.issubset(self.sensitive))
        self.assertEqual(self.policy["max_link_age_days"],7)
if __name__=="__main__":unittest.main()
