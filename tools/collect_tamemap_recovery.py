#!/usr/bin/env python3
"""Collect Tamemap evidence where ordinary public requests are accessible.

This separate environment's results never satisfy or overwrite failed GitHub
Actions checks, verify event facts, or permit event publication.
"""
import argparse
from concurrent.futures import ThreadPoolExecutor
import datetime as dt
import json
from pathlib import Path

from fixed_source_coverage_v3 import expand_urls
from holiday_after_collect import inspect, now
from source_fallback_policy import apply_fallback_overlay

ENVIRONMENT_KIND = "managed_cloud_manual_recovery"
REGISTRY = Path(__file__).resolve().parents[1] / "site/data/discovery_sources.json"


def collect(manifest, fetcher=None):
    weeks = manifest.get("weekends", [])
    if len(weeks) != 6:
        raise ValueError("recovery requires the published six-week manifest")
    start, end = dt.date.fromisoformat(weeks[0]["sat"]), dt.date.fromisoformat(weeks[-1]["sun"])
    if end < start:
        raise ValueError("invalid six-week horizon")
    registry = apply_fallback_overlay(json.loads(REGISTRY.read_text(encoding="utf-8")))
    source = next(s for s in registry["explicit_sources"] if s["id"] == "tamemap_nakano")
    jobs = [{"kind": "explicit", "source_id": source["id"], "required": True,
             "url": url, "target_start": str(start), "target_end": str(end)}
            for url in expand_urls(source, start, end)]
    # Use inspect's normal declared collector UA and bounded HTTP body reader.
    with ThreadPoolExecutor(max_workers=2) as pool:
        pages = list(pool.map(lambda job: inspect(job, fetcher), jobs))
    metadata = {"environment_kind": ENVIRONMENT_KIND, "generated_at_jst": now(),
                "source_id": source["id"], "horizon": [str(start), str(end)],
                "publication_permitted": False, "event_details_verified": False,
                "required_github_actions_check_satisfied": False,
                "note": "Independent manual recovery evidence; retain GitHub Actions failures separately."}
    checks, candidates = [], {}
    for page in pages:
        checks.append({**{k: v for k, v in page.items() if k != "candidates"},
                       "environment_kind": ENVIRONMENT_KIND})
        for candidate in page["candidates"]:
            candidates.setdefault(candidate["candidate_id"], {
                **candidate, "status": "unverified", "environment_kind": ENVIRONMENT_KIND,
                "publication_permitted": False,
                "discovered_via": {"channel": "manual_source_recovery",
                                   "source_id": source["id"], "search_url": page["url"]}})
    summary = {"pages_requested": len(checks),
               "pages_checked": sum(c["status"] == "checked" for c in checks),
               "pages_failed": sum(c["status"] != "checked" for c in checks),
               "unverified_candidates": len(candidates)}
    return {"source_checks": {**metadata, "summary": summary, "checks": checks},
            "candidate_pool": {**metadata, "candidates": list(candidates.values())}}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args(argv)
    result = collect(json.loads(args.manifest.read_text(encoding="utf-8")))
    args.output_dir.mkdir(parents=True, exist_ok=True)
    for name, evidence in result.items():
        (args.output_dir / (name + ".json")).write_text(
            json.dumps(evidence, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result["source_checks"]["summary"], ensure_ascii=False))
    return 2 if result["source_checks"]["summary"]["pages_failed"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
