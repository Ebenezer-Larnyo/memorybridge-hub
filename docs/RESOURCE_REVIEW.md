# Naviboa resource quality assurance — v4.1

## Purpose and scope
The crawler discovers public URLs and checks selected pages. **Successful link checking never signifies medical accuracy or human content approval.** The resource directory and Naviboa AI remain research prototypes. The review ledger starts empty; do not infer human approval from a government/university domain, page titles or automated summaries.

## Review governance
Reviewers should include information specialists and, for clinically sensitive content, a qualified health professional. Invite caregiver and lived-experience advisors to assess readability, cultural appropriateness and accessibility. The directory's *Human reviewed* badge means the eight **directory** criteria below were documented by an identified project reviewer. It does **not** imply medical advice, clinical certification, regulatory endorsement or research validation.

For each reviewed URL, inspect the actual source, not just crawler metadata. Record a pseudonymous team reviewer ID, evidence URL, review date and concrete supporting notes. Before approval, independently assess:
1. **Source identity:** publisher is identifiable and credible for the specific information.
2. **Topic relevance:** page substantially covers the assigned subject and audience.
3. **Description accuracy:** the directory description fairly reflects the page without misleading claims.
4. **Currency:** page is not obviously obsolete; time-sensitive facts are appropriately dated.
5. **Geographic fit:** applicability, services and country are correctly described.
6. **Language:** the language tag matches the page; do not infer language from an English title alone.
7. **Accessibility spot-check:** usable text, labels, readability and keyboard access in a basic manual check.
8. **Medical safety screen:** no misleading cure claims, unsupported medical directives or deceptive advertisements promoted by the listing.

A reviewer may select **approved** only when all eight criteria pass; **needs_revision** records a correctable problem and temporarily removes the listing from the public directory; **excluded** removes an unsafe, irrelevant or otherwise inappropriate listing. Re-check approved records after 180 days: the badge changes to *Review due* until a reviewer renews it. No automated process grants approval.

### Example review format (illustrative only; do not commit as an actual assessment)

    {
      "url": "https://example.org/sample-page",
      "reviewer_id": "reviewer01",
      "reviewed_on": "2026-11-20",
      "decision": "needs_revision",
      "evidence_url": "https://example.org/sample-page",
      "notes": "Illustrative review notes explaining what needs to be corrected and why.",
      "criteria": {
        "source_identity": "pass",
        "topic_relevance": "pass",
        "description_accuracy": "concern",
        "currency": "pass",
        "geographic_fit": "pass",
        "language_verified": "pass",
        "accessibility_spotcheck": "pass",
        "medical_safety_screen": "pass"
      }
    }

*Do not import the example above:* it is not a real source or a completed review. Human review decisions require actual source inspection and are entered only by reviewers.

### Reviewer workflow
1. Run `python scripts/review_resource.py queue --limit 20`; inspect the live URL.
2. Save **one completed review record** as a local JSON file (not containing patient data or contact details).
3. Run `python scripts/review_resource.py import --file my-review.json` (use `--replace` only for deliberate changes).
4. Run `python scripts/quality.py --write` and `python -m unittest discover -s tests`.
5. Inspect `data/quality-report.json` and `data/review-queue.json`. Have another reviewer check approvals, then commit the reviewed ledger and generated artifacts in a PR.

## Current review and metadata backlog
`data/review-queue.json` contains the top 50 **unreviewed or overdue** resources ranked for manual follow-up. Priority balances clinical/caregiver topics, source organization category and missing metadata; it is not a quality or safety score. The crawler never writes `data/reviews.json`; daily refreshes generate updated quality reports and queue entries without overwriting human decisions.

`data/quality-report.json` provides counts for verified human reviews, missing language tags and placeholder descriptions. Missing language labels should be fixed only using page evidence (e.g. the HTML `lang` attribute) or a manual review; guessing from organizational affiliation is not appropriate. Placeholder descriptions remain hidden from users until the page provides evidence for a replacement.

## Safety, ethics and privacy
- Review records should contain no patient narratives, health information or reviewer personal contact details. Public `quality-index.json` contains decisions and dates only, not internal reviewer notes or identities.
- The public interface hides **excluded** and **needs_revision** resources (including from Naviboa AI's candidate pool); it labels all remaining unreviewed entries accurately.
- Automated validations verify schema and workflow, not clinical quality. An ethics approval/determination is needed before recruiting participants or collecting human-subject data. Follow the research protocol in `docs/EVALUATION.md`.
- Source metadata can change daily; do not represent automated crawling as a substitute for clinical or cultural review.
