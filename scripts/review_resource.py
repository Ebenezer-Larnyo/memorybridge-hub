"""Human-reviewed resource ledger administration. No automatic approvals."""
import argparse
import json
from pathlib import Path
from quality import DATA, build, read_inputs, validate_ledger

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    queue = sub.add_parser("queue", help="Show resources awaiting human review")
    queue.add_argument("--limit", type=int, default=20)
    import_cmd = sub.add_parser("import", help="Import ONE completed, evidence-backed JSON review")
    import_cmd.add_argument("--file", type=Path, required=True)
    import_cmd.add_argument("--replace", action="store_true", help="Explicitly replace an existing review")
    args = parser.parse_args()
    resources, ledger = read_inputs()
    if args.command == "queue":
        validate_ledger(resources, ledger)
        pending = build(resources, ledger)["review-queue.json"]["items"]
        for i, item in enumerate(pending[:max(1, min(args.limit, 50))], 1):
            print(f"{i}. [{item['priority_score']}] {item['title']} | {item['url']}")
            print("   Flags: " + ", ".join(item["flags"]))
        return
    candidate = json.loads(args.file.read_text(encoding="utf-8"))
    if not isinstance(candidate, dict):
        raise ValueError("The review file must contain one JSON object")
    current = [r for r in ledger["reviews"] if r["url"] != candidate.get("url")]
    if len(current) != len(ledger["reviews"]) and not args.replace:
        raise ValueError("Existing review: use --replace to explicitly update")
    new_ledger = {"version": 1, "reviews": current + [candidate]}
    validate_ledger(resources, new_ledger)
    (DATA / "reviews.json").write_text(
        json.dumps(new_ledger, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("Recorded reviewer-provided decision; run python scripts/quality.py --write")
    print("Have another reviewer audit approvals before merging them into main.")

if __name__ == "__main__":
    main()
