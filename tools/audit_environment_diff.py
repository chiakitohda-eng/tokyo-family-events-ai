#!/usr/bin/env python3
"""Classify staging/main versus production differences against a reviewed inventory.

This is NOT a deployment command. The "report" mode is safe during development;
"--strict" is an explicit release-readiness review, not a substitute for
production-based release candidate validation or event-row deletion checks.
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INVENTORY = ROOT / ".github/staging-production-diff-baseline.json"


def git(*arguments):
    process = subprocess.run(
        ["git", *arguments], cwd=ROOT, capture_output=True, check=False
    )
    if process.returncode:
        raise RuntimeError(
            f"git {' '.join(arguments)}: {process.stderr.decode(errors='replace').strip()}"
        )
    return process.stdout


def tree(ref):
    """Map tracked blob paths to content SHAs without a local checkout of ref."""
    result = {}
    for record in git("ls-tree", "-rz", ref).split(b"\0"):
        if not record:
            continue
        metadata, path = record.split(b"\t", 1)
        mode, kind, sha = metadata.decode("ascii").split()
        if kind == "blob":
            result[path.decode("utf-8")] = sha
    return result


def differences(staging, production):
    """Blob comparisons deliberately ignore merge ancestry and commit histories."""
    found = {}
    for path in sorted(set(staging) | set(production)):
        if staging.get(path) == production.get(path):
            continue
        found[path] = (
            "staging_only" if path not in production
            else "production_only" if path not in staging
            else "different"
        )
    return found


def classify(actual, inventory):
    """Independently testable exact-path allowlist classifier."""
    approved = {entry["path"]: entry for entry in inventory["allowed_differences"]}
    if len(approved) != len(inventory["allowed_differences"]):
        raise ValueError("duplicate paths in baseline allowlist")
    invalid_entries = [
        path for path, entry in approved.items()
        if entry.get("kind") not in ("different", "staging_only", "production_only")
        or not entry.get("reason")
        or entry.get("disposition") != "intentional_staging_only"
    ]
    if invalid_entries:
        raise ValueError(f"invalid governance entries: {invalid_entries}")
    matching = sorted(path for path, kind in actual.items()
                      if path in approved and approved[path]["kind"] == kind)
    unclassified = sorted(path for path in actual if path not in approved)
    wrong_kind = sorted(path for path, kind in actual.items()
                        if path in approved and approved[path]["kind"] != kind)
    resolved = sorted(path for path in approved if path not in actual)
    surface = sorted(path for path in actual if path.startswith("site/")
                     or path.startswith("prompts/"))
    return {
        "approved": matching,
        "pending_release_paths": sorted(path for path in matching if approved[path].get("release_state") == "pending_release"),
        "unclassified": unclassified,
        "wrong_kind": wrong_kind,
        "resolved_allowlist": resolved,
        "site_or_prompt_differences": surface,
        "approved_count": len(matching),
        "actual_count": len(actual),
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ref", default="HEAD", help="Current staging/app candidate ref")
    parser.add_argument("--base", default="origin/production", help="Released app ref")
    parser.add_argument("--fetch", action="store_true",
                        help="Fetch released app HEAD before comparing")
    parser.add_argument("--strict", action="store_true",
                        help="Fail if any unclassified, changed-kind or resolved exemption; "
                             "also require baseline release HEAD to still match production")
    parser.add_argument("--json", action="store_true", help="Print machine-readable report")
    args = parser.parse_args(argv)

    if args.fetch:
        git("fetch", "--no-tags", "--depth=1", "origin",
            "+refs/heads/production:refs/remotes/origin/production")
    registry = json.loads(INVENTORY.read_text(encoding="utf-8"))
    if registry["schema_version"] != 1:
        raise ValueError("Unknown environment difference inventory version")
    actual = differences(tree(args.ref), tree(args.base))
    result = classify(actual, registry)
    production_sha = git("rev-parse", args.base).decode().strip()
    staging_sha = git("rev-parse", args.ref).decode().strip()
    release_shifted = (
        production_sha != registry["baseline_production_commit"]
    )
    result.update({
        "staging_sha": staging_sha,
        "production_sha": production_sha,
        "recorded_production_sha": registry["baseline_production_commit"],
        "release_baseline_moved": release_shifted,
        "approved_baseline_release": registry["baseline_app_release"],
        "audit_mode": "strict" if args.strict else "staging-report",
        "status": "needs_review" if (
            result["unclassified"] or result["wrong_kind"]
            or result["resolved_allowlist"] or release_shifted
        ) else "approved_difference_only",
        "actual_differences": actual,
    })
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(
            f"Environment diff: main/staging={staging_sha[:12]}, "
            f"production={production_sha[:12]}, "
            f"approved={result['approved_count']}, "
            f"unclassified={len(result['unclassified'])}, "
            f"wrong_kind={len(result['wrong_kind'])}, "
            f"resolved={len(result['resolved_allowlist'])}"
        )
        print(f"Baseline: {registry['baseline_app_release']}, state: {result['status']}")
        for label in ("unclassified", "wrong_kind", "resolved_allowlist"):
            for path in result[label]:
                print(f"  REVIEW {label}: {path}")
        if release_shifted:
            print("  REVIEW: released production SHA moved; reconcile baseline release")
        if result["site_or_prompt_differences"]:
            print("  NOTE: site/prompt differences can be valid staging work, "
                  "but are NOT approved for production by this inventory.")
            for path in result["site_or_prompt_differences"]:
                print(f"  PENDING APP CHANGE: {path}")
        for path in result["pending_release_paths"]:
            print(f"  REVIEWED STAGING ONLY, NOT APPROVED FOR RELEASE: {path}")
        print("Data branch is independent: compare data-staging and data-production "
              "using tools/validate_protected_events.py; this audit does not authorize deletions.")
    if args.strict and result["status"] != "approved_difference_only":
        print("FAIL: differences are not all recorded and reviewed", file=sys.stderr)
        return 1
    if result["status"] == "needs_review" and not args.strict:
        print("NOTICE: staging remains usable; review pending differences "
              "before any production promotion", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
