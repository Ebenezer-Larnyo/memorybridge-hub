"""Review-issue intake: turns a trusted user's review into a PR proposal, not approval.

GitHub Actions checks collaborator permission before invoking this script.
"""
import argparse
import datetime as dt
import json
import re
from pathlib import Path
from quality import DATA, CRITERIA, canonical, read_inputs, validate_ledger, build, write_artifacts

PREFIX = "NAVIBOA_REVIEW_V1\n" + chr(96)*3 + "json\n"
SUFFIX = "\n" + chr(96)*3
EXPECTED = {"url", "decision", "evidence_url", "notes", "criteria", "replace_existing"}

def issue_to_record(event, resource_data, ledger):
    issue = event.get("issue")
    if event.get("action") != "opened" or not isinstance(issue, dict):
        raise ValueError("Expected an opened GitHub issue")
    if not str(issue.get("title", "")).startswith("Naviboa resource review: "):
        raise ValueError("Not a Naviboa review issue")
    body = issue.get("body")
    if not isinstance(body, str) or len(body) > 6500:
        raise ValueError("Review issue body is missing or too large")
    if not (body.startswith(PREFIX) and body.endswith(SUFFIX)):
        raise ValueError("Invalid Naviboa review issue format")
    try:
        payload = json.loads(body[len(PREFIX):-len(SUFFIX)])
    except (ValueError, TypeError) as exc:
        raise ValueError("Invalid JSON review payload") from exc
    if not isinstance(payload, dict) or set(payload) != EXPECTED:
        raise ValueError("Review payload fields are incomplete or unexpected")
    if type(payload["replace_existing"]) is not bool:
        raise ValueError("replace_existing must be a boolean")
    author = issue.get("user")
    login = author.get("login") if isinstance(author, dict) else None
    if not isinstance(login, str) or not re.fullmatch(r"[A-Za-z0-9-]{1,39}", login):
        raise ValueError("Invalid GitHub reviewer identity")
    try:
        review_date = dt.datetime.fromisoformat(issue["created_at"].replace("Z", "+00:00")).astimezone(dt.timezone.utc).date().isoformat()
    except (KeyError, ValueError, TypeError):
        raise ValueError("Missing or invalid GitHub issue timestamp") from None
    urls = {canonical(item["url"]): item["url"] for item in resource_data["resources"]}
    key = canonical(payload["url"])
    if key not in urls:
        raise ValueError("Review URL is not in the directory")
    existing = [r for r in ledger["reviews"] if canonical(r["url"]) == key]
    if existing and not payload["replace_existing"]:
        raise ValueError("An existing review requires explicit replacement")
    notes = payload["notes"]
    if not isinstance(notes, str) or not 30 <= len(notes.strip()) <= 1200:
        raise ValueError("Review notes must contain 30–1200 characters")
    if not isinstance(payload["criteria"], dict) or set(payload["criteria"]) != set(CRITERIA):
        raise ValueError("All eight review criteria must be supplied")
    record = {
        "url": urls[key],
        "reviewer_id": "gh_" + login[:37],
        "reviewed_on": review_date,
        "decision": payload["decision"],
        "evidence_url": payload["evidence_url"],
        "notes": notes.strip(),
        "criteria": payload["criteria"],
    }
    proposed = {"version": 1, "reviews": [r for r in ledger["reviews"] if canonical(r["url"]) != key] + [record]}
    validate_ledger(resource_data, proposed)
    return record, proposed

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--event", type=Path, required=True)
    args = parser.parse_args()
    event = json.loads(args.event.read_text(encoding="utf-8"))
    data, ledger = read_inputs()
    record, proposed = issue_to_record(event, data, ledger)
    (DATA / "reviews.json").write_text(json.dumps(proposed, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_artifacts(build(data, proposed))
    print("VALIDATED REVIEW PROPOSAL (not published or approved)")
    print("Resource:", record["url"])
    print("Decision proposed:", record["decision"])
    print("Issue author:", record["reviewer_id"])

if __name__ == "__main__":
    main()
