#!/usr/bin/env python3
"""Fail-closed audit of the 2026-11-08 official, additive event-gap recovery.

The baseline 2026-11-08 horizon has acknowledged missing required-source
provenance. Never label those sources checked or fabricate crawler evidence.
Instead prove the complete baseline source-error multiset is unchanged while
checking exactly the permitted additional event records and official URLs.
"""
import argparse
from collections import Counter
import copy
import json
from pathlib import Path
import re
import subprocess
import sys
from urllib.parse import urlsplit

from validate_official_schedule_audit import validate as audit_official_sources

EXPECTED = {
    "2026-11-14": (
        "gap-20261114-nakano-new-face-market",
        "gap-20261114-shinjuku-hokusan-kids",
        "gap-20261114-shinjuku-okubo-center",
    ),
    "2026-11-21": (
        "gap-20261123-nakano-higashi-bosai",
        "gap-20261123-nakano-egota-craft",
        "gap-20261123-edogawa-kasai-super-fes",
        "gap-20261123-edogawa-walking",
        "gap-20261123-toshima-ikebiz-festa",
        "gap-20261123-shinjuku-mochitsuki",
    ),
    "2026-11-28": (
        "gap-20261129-shinjuku-kashiwa",
        "gap-20261129-shinjuku-goalball",
    ),
}
ALLOWED_HOSTS = {
    "www.city.shinjuku.lg.jp",
    "www.city.tokyo-nakano.lg.jp",
    "library.city.tokyo-nakano.lg.jp",
    "www.city.edogawa.tokyo.jp",
    "www.toshima-plaza.jp",
}
SHARD_SUFFIX = "-events-gap-recovery-20261108.json"


def check(ok, description):
    if not ok:
        raise ValueError(description)


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def baseline_file(ref, path):
    return json.loads(subprocess.check_output(
        ["git", "show", f"{ref}:{path}"], text=True, encoding="utf-8"
    ))


def run_audit(data_dir, week, baseline_ref, source_config, rules):
    sat = week["sat"]
    current_run = read_json(data_dir / week["run_file"])
    current_dec = read_json(data_dir / current_run["source_data"]["decision_file"])
    old_week = baseline_file(baseline_ref, f"site/data/{sat}.json")
    old_run = baseline_file(baseline_ref, f"site/data/{old_week['run_file']}")
    old_dec = baseline_file(baseline_ref, f"site/data/{old_run['source_data']['decision_file']}")
    before = Counter(audit_official_sources(old_run, old_week, old_dec, source_config, rules))
    after = Counter(audit_official_sources(current_run, week, current_dec, source_config, rules))
    check(after == before, f"{sat}: new, removed, or disguised discovery/source-audit findings: " +
          str(dict(after - before)) + " / " + str(dict(before - after)))
    print(f"UNCHANGED_PREEXISTING_SOURCE_DEBT {sat}: {sum(before.values())} findings carried, none cleared by assertion")
    return old_week, old_run, old_dec, current_run, current_dec


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", default="site/data", type=Path)
    parser.add_argument("--base-ref", required=True)
    args = parser.parse_args()
    base = args.base_ref
    check(re.fullmatch(r"[a-f0-9]{40}", base) is not None, "real 40-character baseline SHA required")
    # CI fetches data-staging --depth=1 before running this check, which can
    # mark HEAD shallow despite its GitHub-verified parent. Compare immutable
    # baseline trees and records directly; do not rely on ancestry flags.
    subprocess.run(["git", "cat-file", "-e", f"{base}^{{commit}}"], check=True)
    data_dir = args.data_dir
    baseline_manifest = baseline_file(base, "site/data/manifest.json")
    current_manifest = read_json(data_dir / "manifest.json")
    check([w["sat"] for w in baseline_manifest["weekends"]] ==
          [w["sat"] for w in current_manifest["weekends"]],
          "rolling horizon dates must be preserved")
    delta = {sat: len(ids) for sat, ids in EXPECTED.items()}
    for old, new in zip(baseline_manifest["weekends"], current_manifest["weekends"]):
        check(new["count"] == old["count"] + delta.get(old["sat"], 0),
              f"unexpected manifest weekly count for {old['sat']}")
    check(current_manifest.get("current_rollover") == baseline_manifest.get("current_rollover"),
          "source collection debt/current rollover must be preserved")

    baseline_history = baseline_file(base, "site/data/update_history.json")
    current_history = read_json(data_dir / "update_history.json")
    older = baseline_history.get("history", [])
    records = current_history.get("history", [])
    check(records[:-1] == older, "prior update history cannot change")
    entry = records[-1]
    check(entry.get("run_id") == "manual-official-gap-recovery-2026-11-08" and
          entry.get("run_type") == "manual_official_add_only" and
          entry.get("removed_weekly_records") == 0 and
          entry.get("changed_existing_records") == 0 and
          entry.get("added_weekly_records") == 11,
          "last history record is not the approved 11-event non-destructive addition")
    listed_ids = [i for sat in EXPECTED for i in EXPECTED[sat]]
    check(Counter(entry.get("new_event_ids", [])) == Counter(listed_ids),
          "history IDs must exactly cover the 11 reviewed events")
    check(entry.get("unverified_candidate_links_remaining") == 844 and
          entry.get("unresolved_required_source_failures") == 3 and
          entry.get("source_failures_remain_unverified") is True,
          "unresolved source/candidate issues must remain visible")

    changed = set(subprocess.check_output(
        ["git", "diff", "--name-only", base, "HEAD"], text=True
    ).splitlines())
    expected_files = {"site/data/manifest.json", "site/data/update_history.json"}
    for sat in EXPECTED:
        expected_files |= {
            f"site/data/{sat}.json",
            f"site/data/{sat}-run.json",
            f"site/data/{sat}-decisions.json",
            f"site/data/{sat}-verification.json",
            f"site/data/{sat}{SHARD_SUFFIX}",
        }
    check(changed == expected_files,
          "unapproved modified paths: " + str(sorted(changed ^ expected_files)))

    source_config = read_json(data_dir / "discovery_sources.json")
    rules_path = Path(__file__).resolve().parents[1] / "policy" / "temporary_source_exceptions.json"
    rules = (read_json(rules_path).get("exceptions", []) if rules_path.exists() else [])
    found = []
    for entry_week in current_manifest["weekends"]:
        sat = entry_week["sat"]
        week = read_json(data_dir / entry_week["file"])
        old_week, _, old_dec, run, dec = run_audit(data_dir, week, base, source_config, rules)
        if sat not in EXPECTED:
            continue
        new_shard = sat + SHARD_SUFFIX
        check(week["event_files"] == old_week["event_files"] + [new_shard],
              f"{sat}: existing event shards changed")
        added = read_json(data_dir / new_shard)
        check(len(added) == len(EXPECTED[sat]), f"{sat}: wrong event count")
        check([r.get("id") for r in added] == list(EXPECTED[sat]), f"{sat}: unexpected added ID or ordering")
        ver = read_json(data_dir / week["verification_file"])
        old_ver = baseline_file(base, f"site/data/{sat}-verification.json")
        check(ver["events"][:len(old_ver["events"])] == old_ver["events"],
              f"{sat}: older verification records changed")
        check(dec["decisions"][:len(old_dec["decisions"])] == old_dec["decisions"],
              f"{sat}: older publication decisions changed")
        checks = {r.get("id"): r for r in ver["events"]}
        for ev in added:
            eid = ev["id"]
            found.append(eid)
            src = ev.get("official_url", "")
            host = urlsplit(src).netloc.lower()
            check(host in ALLOWED_HOSTS and urlsplit(src).scheme == "https" and
                  ev.get("url") == src and ev.get("source") == src,
                  f"{eid}: must cite an approved original organizer/public institution URL")
            row = checks.get(eid, {})
            check(row.get("status") == "verified" and row.get("source") == src and
                  all(row.get("fields", {}).get(k) == "pass" for k in ("name", "date", "venue")),
                  f"{eid}: official verification incomplete")
            check(ev.get("date_start") == ev.get("date_end") and
                  ev.get("date_start") in ("2026-11-14", "2026-11-23", "2026-11-29"),
                  f"{eid}: event day not in approved scope")
            check(ev.get("family_fit", {}).get("grade") in ("A", "B"),
                  f"{eid}: family-fit grade missing")
        check(run.get("manual_gap_recovery_20261108", {}).get("event_ids") == list(EXPECTED[sat]),
              f"{sat}: run addition evidence mismatch")
    check(Counter(found) == Counter(listed_ids), "missing or unexpected additions")
    print(f"PASS: {len(found)} new official events only; zero old records removed or modified; baseline source gaps not waived")


if __name__ == "__main__":
    try:
        main()
    except (ValueError, KeyError, IndexError, subprocess.CalledProcessError) as exc:
        print("OFFICIAL GAP RECOVERY AUDIT FAIL:", exc, file=sys.stderr)
        sys.exit(1)
