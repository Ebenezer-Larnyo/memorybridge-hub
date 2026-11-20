"""Resource-audit artifacts. Never infer human approval from automated crawling.

The authoritative human-review ledger is data/reviews.json. This tool validates
its provenance before publishing minimal, non-sensitive UI review metadata.
"""
import argparse
import datetime as dt
import json
import re
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit

DATA = Path(__file__).resolve().parents[1] / "data"
REVIEW_STATES = {"approved", "needs_revision", "excluded"}
CRITERIA = (
    "source_identity", "topic_relevance", "description_accuracy", "currency",
    "geographic_fit", "language_verified", "accessibility_spotcheck",
    "medical_safety_screen",
)
PLACEHOLDER = re.compile(r"^(?:Visit (?:the original|source)|Automatically discovered)", re.I)
HIGH_PRIORITY = {"Diagnosis", "Treatment & medication", "Caregiver support",
                 "Respite & services", "Daily care", "End of life & hospice"}

def canonical(url):
    if not isinstance(url, str):
        raise ValueError("URL must be a string")
    p = urlsplit(url)
    if p.scheme != "https" or not p.netloc or p.username or p.password:
        raise ValueError("Resource URLs must be public HTTPS URLs")
    return urlunsplit((p.scheme, p.netloc.lower(), p.path or "/", "", ""))

def date(value):
    try:
        return dt.date.fromisoformat(value)
    except (ValueError, TypeError):
        raise ValueError("Review date must be YYYY-MM-DD") from None

def read_inputs():
    resources = json.loads((DATA / "resources.json").read_text(encoding="utf-8"))
    ledger = json.loads((DATA / "reviews.json").read_text(encoding="utf-8"))
    if not isinstance(resources.get("resources"), list):
        raise ValueError("Invalid resources directory")
    if ledger.get("version") != 1 or not isinstance(ledger.get("reviews"), list):
        raise ValueError("Review ledger must contain version=1 and reviews=[]")
    return resources, ledger

def validate_ledger(resources, ledger, today=None):
    today = today or dt.datetime.now(dt.timezone.utc).date()
    urls = {}
    for item in resources["resources"]:
        key = canonical(item["url"])
        if key in urls:
            raise ValueError("Duplicate resource URL: " + key)
        urls[key] = item["url"]
    checked = {}
    for review in ledger["reviews"]:
        if not isinstance(review, dict):
            raise ValueError("Each review must be an object")
        key = canonical(review.get("url"))
        if key not in urls:
            raise ValueError("Review URL is not in the directory: " + key)
        if key in checked:
            raise ValueError("Duplicate review: " + key)
        checked[key] = review
        if review.get("decision") not in REVIEW_STATES:
            raise ValueError("Unknown review decision for " + key)
        reviewer = review.get("reviewer_id")
        if not isinstance(reviewer, str) or not re.fullmatch(r"[A-Za-z0-9_-]{2,40}", reviewer):
            raise ValueError("Use a pseudonymous reviewer_id of 2-40 characters")
        review_day = date(review.get("reviewed_on"))
        if review_day > today:
            raise ValueError("Future review date for " + key)
        evidence_url = review.get("evidence_url")
        canonical(evidence_url)
        notes = review.get("notes")
        if not isinstance(notes, str) or len(notes.strip()) < 30 or len(notes) > 2000:
            raise ValueError("Review notes must be 30-2000 characters for " + key)
        criteria = review.get("criteria")
        if not isinstance(criteria, dict) or set(criteria) != set(CRITERIA):
            raise ValueError("Incomplete review checklist for " + key)
        if any(value not in ("pass", "concern", "not_applicable") for value in criteria.values()):
            raise ValueError("Unknown checklist value for " + key)
        if review["decision"] == "approved" and any(value != "pass" for value in criteria.values()):
            raise ValueError("Approval requires all eight criteria to pass for " + key)
        if review["decision"] == "needs_revision" and all(value == "pass" for value in criteria.values()):
            raise ValueError("A needs_revision decision must identify at least one concern")
    return checked

def build(resources, ledger, today=None):
    today = today or dt.datetime.now(dt.timezone.utc).date()
    validated = validate_ledger(resources, ledger, today)
    index = {}
    queue = []
    counts = dict(total=len(resources["resources"]), human_reviewed_current=0,
                  review_due=0, needs_revision=0, excluded=0, awaiting_review=0,
                  link_checked=0, descriptions_missing=0, language_untagged=0)
    for item in resources["resources"]:
        key = canonical(item["url"])
        review = validated.get(key)
        if item.get("checked"):
            counts["link_checked"] += 1
        placeholder = not item.get("description") or bool(PLACEHOLDER.match(item["description"]))
        missing_lang = item.get("language") in (None, "", "Not tagged")
        if placeholder:
            counts["descriptions_missing"] += 1
        if missing_lang:
            counts["language_untagged"] += 1
        due = bool(review and (today - date(review["reviewed_on"])).days > 180)
        decision = review["decision"] if review else None
        if review:
            # Public index deliberately omits reviewer identity, notes and checklist details.
            index[item["url"]] = {"decision": decision,
                                   "reviewed_on": review["reviewed_on"],
                                   "review_due": due}
        if decision == "approved" and not due:
            counts["human_reviewed_current"] += 1
        elif decision == "approved":
            counts["review_due"] += 1
        elif decision == "needs_revision":
            counts["needs_revision"] += 1
        elif decision == "excluded":
            counts["excluded"] += 1
        else:
            counts["awaiting_review"] += 1
        if decision == "excluded" or (decision == "approved" and not due):
            continue
        flags = []
        if decision == "needs_revision":
            flags.append("correction_requested")
        elif due:
            flags.append("review_expired")
        else:
            flags.append("no_human_review")
        if placeholder:
            flags.append("description_placeholder")
        if missing_lang:
            flags.append("language_not_tagged")
        if not item.get("checked"):
            flags.append("link_not_recently_checked")
        score = (30 if decision == "needs_revision" else 20 if due else 0)
        score += 9 if item.get("kind") in ("Government", "University", "Public health") else 0
        score += 8 if set(item.get("topics", [])) & HIGH_PRIORITY else 0
        score += 6 if placeholder else 0
        score += 4 if missing_lang else 0
        score += 3 if not item.get("checked") else 0
        queue.append({
            "url": item["url"], "title": item["title"],
            "organization": item["organization"], "region": item.get("region", ""),
            "language": item.get("language", "Not tagged"),
            "topics": item.get("topics", []), "priority_score": score,
            "flags": flags,
        })
    queue.sort(key=lambda x: (-x["priority_score"], x["organization"].lower(),
                              x["title"].lower(), x["url"]))
    # Avoid a top-50 backlog dominated by one publisher or jurisdiction.
    # Fill a balanced first pass, then use global priority for remaining slots.
    prioritized, deferred = [], []
    org_count, region_count = {}, {}
    for item in queue:
        org, region = item["organization"], item["region"]
        if (len(prioritized) < 50 and org_count.get(org, 0) < 5
                and region_count.get(region, 0) < 15):
            prioritized.append(item)
            org_count[org] = org_count.get(org, 0) + 1
            region_count[region] = region_count.get(region, 0) + 1
        else:
            deferred.append(item)
    prioritized += deferred[:max(0, 50 - len(prioritized))]
    public_index = {"version": 1, "review_index": index, "stats": counts,
                    "review_scope": "Human-reviewed means directory quality assessment, not clinical validation."}
    public_report = {"version": 1, "directory_updated": resources.get("updated"),
                     "stats": counts, "review_queue_total": len(queue),
                     "priority_queue_size": min(50, len(queue)),
                     "disclaimer": "A crawler link check is not a clinical content review."}
    review_queue = {"version": 1, "directory_updated": resources.get("updated"),
                    "total_pending": len(queue), "items": prioritized[:50],
                    "notice": "Automated triage only. No resource has been approved by this queue."}
    return {"quality-index.json": public_index, "quality-report.json": public_report,
            "review-queue.json": review_queue}

def write_artifacts(result):
    for name, data in result.items():
        (DATA / name).write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

def check_artifacts(result):
    for name, expected in result.items():
        path = DATA / name
        if not path.exists():
            raise ValueError(name + " missing: run python scripts/quality.py --write")
        if json.loads(path.read_text(encoding="utf-8")) != expected:
            raise ValueError(name + " is stale: run python scripts/quality.py --write")

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", action="store_true", help="Validate and regenerate public QA artifacts")
    group.add_argument("--check", action="store_true", help="Reject invalid or stale QA artifacts")
    args = parser.parse_args()
    resources, ledger = read_inputs()
    result = build(resources, ledger)
    if args.write:
        write_artifacts(result)
    else:
        check_artifacts(result)
    print("Quality audit:", result["quality-report.json"]["stats"])

if __name__ == "__main__":
    main()
