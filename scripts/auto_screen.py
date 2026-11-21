"""Conservative rule-based DIRECTORY listing screening, not clinical approval.

No AI judgment, web-source guessing, medical content verification, or human-review
ledger mutation. Runs in the existing daily GitHub crawler pipeline.
"""
import datetime as dt
import json
import re
from pathlib import Path
from urllib.parse import urlsplit

DATA = Path(__file__).resolve().parents[1] / "data"
PLACEHOLDER = re.compile(r"^(?:Visit (?:the original|source)|Automatically discovered)", re.I)
DANGEROUS_CLAIM = re.compile(r"\b(?:miracle cure|guaranteed cure|instant cure|reverse(?:s|d)? dementia)\b", re.I)
SENSITIVE_HINT = re.compile(r"\b(?:clinical[- _]?trials?|prescriptions?|dos(?:e|ing)|medications?|drug(?:s)?|diagnos(?:e|is|tic)|symptoms?|treatments?|hospice|palliative|insurance|legal advice|cures?)\b", re.I)
NON_CONTENT = re.compile(r"(?:/donate|/checkout|/shop|/store|/sign[-_]?in|/register|/login)", re.I)

def read_policy():
    policy = json.loads((DATA / "auto-screen-policy.json").read_text(encoding="utf-8"))
    if policy.get("version") != 1 or not isinstance(policy.get("publisher_allowlist"), list):
        raise ValueError("Unsupported automated screen policy")
    if not 1 <= policy.get("max_link_age_days", 0) <= 30:
        raise ValueError("Invalid automatic-screen link age")
    if not 20 <= policy.get("min_description_chars", 0) <= 300:
        raise ValueError("Invalid automatic-screen description threshold")
    allowed = set()
    for entry in policy["publisher_allowlist"]:
        if not isinstance(entry, dict) or set(entry) != {"host", "organization", "kind"}:
            raise ValueError("Invalid publisher allowlist entry")
        host, org, kind = (entry[x] for x in ("host", "organization", "kind"))
        if not all(isinstance(x, str) and x for x in (host, org, kind)):
            raise ValueError("Empty source allowlist value")
        if not re.fullmatch(r"[a-z0-9.-]+", host):
            raise ValueError("Invalid allowed hostname")
        allowed.add((host, org, kind))
    if len(allowed) != len(policy["publisher_allowlist"]):
        raise ValueError("Duplicate publisher allowlist entry")
    excluded = policy.get("excluded_topics")
    if not isinstance(excluded, list) or not all(isinstance(x, str) for x in excluded):
        raise ValueError("Invalid excluded topics")
    return policy, allowed, set(excluded)

def screen_one(item, policy, allowed, sensitive, today=None):
    today = today or dt.datetime.now(dt.timezone.utc).date()
    problems = []
    try:
        url = urlsplit(item.get("url", ""))
        if (url.scheme != "https" or not url.hostname or url.username
                or url.password or url.port is not None or url.fragment
                or url.query or not re.fullmatch(r"[a-z0-9.-]+", url.hostname)):
            problems.append("url_not_eligible")
    except (TypeError, ValueError, AttributeError):
        url = None
        problems.append("url_not_eligible")
    if url and (url.hostname, item.get("organization"), item.get("kind")) not in allowed:
        problems.append("publisher_not_allowlisted")
    if url and NON_CONTENT.search(url.path):
        problems.append("non_information_page")
    checked = item.get("checked")
    try:
        delta = (today - dt.date.fromisoformat(checked)).days
        if delta < 0 or delta > policy["max_link_age_days"]:
            problems.append("link_not_recently_checked")
    except (TypeError, ValueError):
        problems.append("link_not_recently_checked")
    title = item.get("title")
    if not isinstance(title, str) or len(title.strip()) < 10:
        problems.append("title_missing_or_short")
    desc = item.get("description")
    if (not isinstance(desc, str) or len(desc.strip()) < policy["min_description_chars"]
            or PLACEHOLDER.match(desc)):
        problems.append("description_incomplete")
    if item.get("language") not in ("English", "Spanish"):
        problems.append("language_not_tagged")
    topics = item.get("topics")
    if not isinstance(topics, list) or not topics or any(not isinstance(t, str) for t in topics):
        problems.append("topics_missing")
    elif sensitive.intersection(topics):
        problems.append("clinically_or_legally_sensitive_topic")
    if DANGEROUS_CLAIM.search((title if isinstance(title,str) else "")
                              + " " + (desc if isinstance(desc,str) else "")):
        problems.append("potentially_misleading_claim")
    # Topic tags can be imperfect: also use the title and URL path to guard
    # against obvious sensitive pages misclassified as general awareness.
    if SENSITIVE_HINT.search((title if isinstance(title,str) else "") + " " + (url.path if url else "")):
        problems.append("sensitive_title_or_url")
    return {"passed": not problems, "checks": problems}

def screen_directory(resources, review_index, today=None):
    today = today or dt.datetime.now(dt.timezone.utc).date()
    policy, allow, sensitive = read_policy()
    accepted = {}
    failures = {}
    for item in resources["resources"]:
        if (review_index.get(item["url"]) or {}).get("decision") in ("excluded", "needs_revision", "approved"):
            continue
        outcome = screen_one(item, policy, allow, sensitive, today)
        if outcome["passed"]:
            accepted[item["url"]] = {
                "screened_on": today.isoformat(),
                "link_checked_on": item["checked"],
                "scope": "publisher, URL and directory metadata only; NOT clinical or human review"
            }
        else:
            for reason in outcome["checks"]:
                failures[reason] = failures.get(reason, 0) + 1
    return accepted, failures
