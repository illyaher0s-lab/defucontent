#!/usr/bin/env python3
"""Validate one-topic copy review records; not a judge of creative quality.

Usage: python scripts/validate_copy_review.py review.json
JSON: {
  "candidates": [{"id":"v1","title":"...","body":"..."}, ... five],
  "reviews": [{"id":"v1","decision":"selected|rejected",
               "consumer_value":"...","reason":"...","risk":"clear|needs_check"}, ... five],
  "selected_ids": ["v1","v3","v4"],
  "shortfall_reason": "..."  # only if fewer than three selected
}
"""
import json
import sys
from pathlib import Path


def validate(data):
    errors = []
    candidates = data.get("candidates", [])
    reviews = data.get("reviews", [])
    selected = data.get("selected_ids", [])
    if not isinstance(candidates, list) or len(candidates) != 5:
        errors.append("Must provide five candidate drafts")
        candidates = candidates if isinstance(candidates, list) else []
    if not isinstance(reviews, list) or len(reviews) != 5:
        errors.append("Must provide one review for each of five drafts")
        reviews = reviews if isinstance(reviews, list) else []
    if not isinstance(selected, list) or not 1 <= len(selected) <= 3:
        errors.append("Must select one to three drafts")
        selected = selected if isinstance(selected, list) else []
    if len(selected) < 3 and not str(data.get("shortfall_reason", "")).strip():
        errors.append("Fewer than three selections requires shortfall_reason")

    candidate_map = {}
    for item in candidates:
        if not isinstance(item, dict):
            errors.append("Candidate is not an object")
            continue
        ident = item.get("id")
        if not isinstance(ident, str) or not ident.strip() or ident in candidate_map:
            errors.append("Candidate IDs must be unique, nonempty strings")
            continue
        candidate_map[ident] = item
        if not isinstance(item.get("title"), str) or not item["title"].strip():
            errors.append(f"{ident}: missing cover title")
        if not isinstance(item.get("body"), str) or not item["body"].strip():
            errors.append(f"{ident}: missing copy body")

    review_map = {}
    for item in reviews:
        if not isinstance(item, dict):
            errors.append("Review is not an object")
            continue
        ident = item.get("id")
        if not isinstance(ident, str) or not ident.strip() or ident in review_map:
            errors.append("Review IDs must be unique, nonempty strings")
            continue
        review_map[ident] = item
        if item.get("decision") not in ("selected", "rejected"):
            errors.append(f"{ident}: decision must be selected or rejected")
        if not isinstance(item.get("consumer_value"), str) or not item["consumer_value"].strip():
            errors.append(f"{ident}: consumer_value missing")
        if not isinstance(item.get("reason"), str) or not item["reason"].strip():
            errors.append(f"{ident}: specific review reason missing")
        if item.get("risk") not in ("clear", "needs_check"):
            errors.append(f"{ident}: risk must be clear or needs_check")

    if set(candidate_map) != set(review_map):
        errors.append("Every candidate must have exactly one matching review")
    if len(selected) != len(set(selected)):
        errors.append("Selected IDs must be unique")
    if set(selected) - set(candidate_map):
        errors.append("Selected IDs must exist in candidates")
    decision_selected = {key for key, item in review_map.items()
                         if item.get("decision") == "selected"}
    if set(selected) != decision_selected:
        errors.append("Selected IDs must match individual review decisions")

    for ident in selected:
        item = candidate_map.get(ident, {})
        body = item.get("body", "")
        if isinstance(body, str) and len(body) > 150:
            errors.append(f"{ident}: selected copy exceeds 150 characters")
        if review_map.get(ident, {}).get("risk") != "clear":
            errors.append(f"{ident}: unresolved factual risk in selected copy")
    return errors


def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: python scripts/validate_copy_review.py review.json")
    try:
        data = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            raise ValueError("Root must be a JSON object")
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        sys.exit(f"Invalid input: {exc}")
    errors = validate(data)
    if errors:
        for error in errors:
            print(f"FAIL: {error}", file=sys.stderr)
        sys.exit(1)
    print(f"PASS: reviewed {len(data['reviews'])} drafts, selected {len(data['selected_ids'])}")


if __name__ == "__main__":
    main()
