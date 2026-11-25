#!/usr/bin/env python3
"""Overlay only validated, read-only source status on the composed Pages tree.

The application stays sourced from production and event records stay sourced
from data-production. A connection report never approves an event update.
"""
import argparse
import datetime as dt
import hashlib
import json
from pathlib import Path
import re

from fixed_source_coverage_v3 import expand_urls, validate
from source_fallback_policy import apply_fallback_overlay


def validate_snapshot(report, registry):
    try:
        validate(report, registry)
        expected_digest = hashlib.sha256(json.dumps(
            registry["explicit_sources"], sort_keys=True,
            ensure_ascii=False).encode()).hexdigest()
        if (report.get("kind") != "registered_fixed_source_retrieval_and_link_leads"
                or report.get("registered_source_count") != len(registry["explicit_sources"])
                or report.get("protected_legacy_source_count") != 18
                or report.get("source_registry_digest") != expected_digest):
            raise ValueError("source snapshot does not match the protected registry")
        checked_at = dt.datetime.fromisoformat(report["generated_at_jst"])
        if checked_at.tzinfo is None:
            raise ValueError("source snapshot needs a timezone-aware timestamp")
        start, end = [dt.date.fromisoformat(x) for x in report["horizon"]]
        if end < start:
            raise ValueError("source snapshot has an invalid horizon")
        for source, row in zip(registry["explicit_sources"], report["sources"]):
            if any(row.get(key) != source.get(key) for key in
                   ("label", "origin", "required", "base_url")):
                raise ValueError("source identity or required flag changed")
            if any(row.get(key) is not None for key in (
                    "event_candidates_total", "published_count_from_source",
                    "excluded_count_from_source", "duplicate_count_from_source",
                    "unreviewed_count_from_source")):
                raise ValueError("connection reports cannot claim event coverage")
            checks = row["source_checks"]
            # An audit adapter exception is a real failure, never a success.
            if not checks and row.get("pages_expected") is None:
                if (row["retrieval_status"] != "source_error"
                        or row.get("pages_checked") != 0 or not row.get("errors")):
                    raise ValueError("missing source checks cannot establish success")
                continue
            expected_urls = expand_urls(source, start, end)
            if [c["url"] for c in checks] != expected_urls:
                raise ValueError("source checks do not cover the registered URLs")
            if any(c.get("status") not in ("checked", "error") for c in checks):
                raise ValueError("invalid per-request retrieval status")
            for check in checks:
                if "body" in check:
                    raise ValueError("raw HTML does not belong in a public source report")
                if check["status"] == "checked" and (
                        check.get("http_status") != 200
                        or not isinstance(check.get("bytes"), int)
                        or check["bytes"] <= 0
                        or not re.fullmatch(r"[0-9a-f]{64}", check.get("sha256", ""))):
                    raise ValueError("successful retrieval lacks HTTP/body evidence")
            count = sum(c["status"] == "checked" for c in checks)
            status = "checked" if count == len(checks) else (
                "partial_error" if count else "source_error")
            if (row["retrieval_status"] != status
                    or row["pages_expected"] != len(checks)
                    or row["pages_checked"] != count
                    or row["pages_failed"] != len(checks) - count):
                raise ValueError("source status disagrees with the request evidence")
        summary = report["summary"]
        for key, status in (("reachable_all_registered_urls", "checked"),
                            ("partial_errors", "partial_error"),
                            ("source_errors", "source_error")):
            if summary[key] != sum(r["retrieval_status"] == status
                                   for r in report["sources"]):
                raise ValueError("source summary disagrees with individual statuses")
        if (summary.get("event_candidates_count") is not None
                or summary.get("publication_gaps_confirmed") is not None):
            raise ValueError("connection reports cannot claim publication completeness")
    except (KeyError, TypeError, AttributeError) as error:
        raise ValueError("malformed source snapshot") from error
    return True


def compose_source_audit(snapshot_path, registry_path, pages_dir, fallback_snapshot_path=None):
    raw = Path(snapshot_path).read_bytes()
    report = json.loads(raw)
    registry = apply_fallback_overlay(json.loads(
        Path(registry_path).read_text(encoding="utf-8")))
    expected_digest = hashlib.sha256(json.dumps(
        registry["explicit_sources"], sort_keys=True, ensure_ascii=False).encode()).hexdigest()
    if report.get("source_registry_digest") != expected_digest and fallback_snapshot_path:
        # A new staging source is not approved for production. Keep the last
        # matching report, including every original failure and check timestamp.
        raw = Path(fallback_snapshot_path).read_bytes()
        report = json.loads(raw)
    validate_snapshot(report, registry)
    destination = Path(pages_dir) / "audit" / "fixed_sources.json"
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(raw)
    return destination


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--snapshot", required=True)
    parser.add_argument("--registry", required=True)
    parser.add_argument("--pages-dir", required=True)
    parser.add_argument("--fallback-snapshot")
    args = parser.parse_args()
    destination = compose_source_audit(args.snapshot, args.registry, args.pages_dir, args.fallback_snapshot)
    print("Validated source-status snapshot only: " + str(destination))


if __name__ == "__main__":
    main()
