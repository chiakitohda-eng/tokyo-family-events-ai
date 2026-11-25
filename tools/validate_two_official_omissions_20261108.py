#!/usr/bin/env python3
"""Exact, fail-closed proof for two individually confirmed public events.

This is a scoped supplement, NOT a waiver for any unfinished source discovery.
It must not be reused for another production baseline or event set.
"""
from collections import Counter
import argparse
import json
from pathlib import Path
import subprocess
import sys

BASE = "890cef441ec2dfcc6393989634eb080225d6d9c9"
PREFIX = "site/data/"
EXPECTED = {
    "2026-11-14": {
        "id": "verified-20261114-nakano-nogata-editing",
        "url": "https://kodomo-smile.metro.tokyo.lg.jp/events/4231",
        "ward": "中野区", "day": "2026-11-14", "rubric": "family-fit-v1",
    },
    "2026-11-21": {
        "id": "verified-20261121-meguro-shinobu-playpark",
        "url": "https://shinobu-kg.com/park/",
        "ward": "目黒区", "day": "2026-11-21", "rubric": "family-fit-v2",
    }
}
ALLOWED = {PREFIX + p for p in ("manifest.json", "update_history.json")}
for sat in EXPECTED:
    ALLOWED.update(PREFIX + sat + suffix for suffix in (
        ".json", "-run.json", "-verification.json", "-decisions.json",
        "-events-verified-omissions-20261108.json",
    ))

def require(ok, description):
    if not ok: raise ValueError(description)

def data(name):
    return json.loads(Path(PREFIX + name).read_text(encoding="utf-8"))

def old(name):
    return json.loads(subprocess.check_output(
        ["git", "show", BASE + ":" + PREFIX + name], text=True))

def bundle(week, load):
    obj = load(week["file"])
    return [*obj.get("events", []), *(e for s in obj["event_files"] for e in load(s))]

def run():
    p = argparse.ArgumentParser()
    p.add_argument("--base-ref", required=True)
    p.add_argument("--data-dir", default="site/data")
    args = p.parse_args()
    require(args.base_ref == BASE, "unapproved baseline SHA")
    require(args.data_dir == "site/data", "unapproved publication data directory")
    changed = set(subprocess.check_output(
        ["git", "diff", "--name-only", BASE, "HEAD"], text=True).splitlines())
    require(changed == ALLOWED,
            "unexpected file modification or missing proof: " + str(sorted(changed ^ ALLOWED)))
    old_manifest, new_manifest = old("manifest.json"), data("manifest.json")
    require(new_manifest["generated"] != old_manifest["generated"], "missing update timestamp")
    old_copy = json.loads(json.dumps(old_manifest))
    old_copy["generated"] = new_manifest["generated"]
    for item in old_copy["weekends"]:
        if item["sat"] in EXPECTED: item["count"] += 1
    require(new_manifest == old_copy,
            "manifest changed beyond exactly one newly verified event in each week")
    old_h, new_h = old("update_history.json"), data("update_history.json")
    require(new_h["schema_version"] == old_h["schema_version"], "history schema changed")
    require(new_h["history"][:-2] == old_h["history"] and len(new_h["history"]) == len(old_h["history"])+2,
            "historical update history changed or unexpected number of additions")
    ids = []
    for sat, spec in EXPECTED.items():
        old_week, new_week = old(sat+".json"), data(sat+".json")
        shard = sat+"-events-verified-omissions-20261108.json"
        require(new_week["event_files"] == old_week["event_files"]+[shard],
                sat + ": event shard list not append only")
        old_wcopy = json.loads(json.dumps(old_week))
        old_wcopy["event_files"].append(shard)
        old_wcopy["generated"] = new_week["generated"]
        old_wcopy["coverage"]["candidate_count"] += 1
        old_wcopy["coverage"]["published_count"] += 1
        ward = next(x for x in old_wcopy["coverage"]["wards"] if x["ward"] == spec["ward"])
        ward["candidate_count"] += 1
        ward["published_count"] += 1
        ward["note"] = next(x for x in new_week["coverage"]["wards"] if x["ward"] == spec["ward"])["note"]
        require(ward["note"].startswith(next(x["note"] for x in old_week["coverage"]["wards"]
                                              if x["ward"] == spec["ward"])),
                sat+": preexisting exploration note changed")
        require(new_week == old_wcopy, sat+": source coverage or old week metadata changed")
        prior = bundle({"file":sat+".json"}, old)
        actual = bundle({"file":sat+".json"}, data)
        require(actual[:len(prior)] == prior and len(actual) == len(prior)+1,
                sat+": old event altered/deleted")
        extra = data(shard)
        require(len(extra) == 1 and actual[-1] == extra[0],
                sat+": extra record not the sole appended event")
        e = extra[0]
        require(e.get("id") == spec["id"] and e.get("official_url") == spec["url"] and
                e.get("url") == spec["url"] and e.get("source") == spec["url"] and
                e.get("ward") == spec["ward"] and
                e.get("date_start") == e.get("date_end") == spec["day"] and
                e.get("family_fit", {}).get("rubric_version") == spec["rubric"] and
                e.get("family_fit", {}).get("grade") == "A" and
                e.get("name") and e.get("venue") and e.get("time") and
                e.get("image", "") == "",
                sat+": independent fact/ID/official URL not supported")
        ids.append(spec["id"])
        old_ver, new_ver = old(sat+"-verification.json"), data(sat+"-verification.json")
        require(new_ver["events"][:-1] == old_ver["events"], sat+": old verification changed")
        ver = new_ver["events"][-1]
        require(ver.get("id") == spec["id"] and ver.get("status") == "verified" and
                ver.get("source") == spec["url"] and
                all(ver.get("fields",{}).get(k) == "pass" for k in ("name","date","venue","time")),
                sat+": insufficient official verification")
        old_vcopy = json.loads(json.dumps(old_ver))
        old_vcopy["events"].append(ver)
        old_vcopy["summary"]["total"] += 1
        old_vcopy["summary"]["verified"] += 1
        require(new_ver == old_vcopy, sat+": verification fields/counters changed")
        old_dec, new_dec = old(sat+"-decisions.json"), data(sat+"-decisions.json")
        require(new_dec["decisions"][:-1] == old_dec["decisions"], sat+": old decision changed")
        de = new_dec["decisions"][-1]
        require(de.get("candidate_id") == spec["id"] and de.get("decision") == "published" and
                any(row.get("url") == spec["url"] for row in de.get("evidence",[])),
                sat+": required individually evidenced decision absent")
        old_dcopy = json.loads(json.dumps(old_dec))
        old_dcopy["decisions"].append(de)
        old_dcopy["summary"]["candidate_total"] += 1
        old_dcopy["summary"]["published"] += 1
        require(new_dec == old_dcopy, sat+": other decision summary changed")
        old_run, new_run = old(sat+"-run.json"), data(sat+"-run.json")
        add_key = "verified_individual_omission_20261108"
        require(add_key not in old_run and add_key in new_run, sat+": missing new separate evidence")
        addon = new_run[add_key]
        require(addon.get("new_event_ids") == [spec["id"]] and
                addon.get("official_urls") == [spec["url"]] and
                addon.get("prior_events_changed") == 0 and
                addon.get("prior_events_removed") == 0 and
                addon.get("source_failures_remain_unverified") is True and
                addon.get("unreviewed_candidate_links_at_current_audit") == 859,
                sat+": requires preservation and explicit source backlog")
        old_rcopy = json.loads(json.dumps(old_run))
        # v1.5 full-tier runs include candidate and image summaries, while
        # older v1.15 preview runs deliberately omit those keys. Never invent them.
        if "candidates" in old_rcopy["summary"]:
            old_rcopy["summary"]["candidates"] += 1
        old_rcopy["summary"]["published"] += 1
        old_rcopy["summary"]["verified"] += 1
        if "thumbnail_count" in old_rcopy["summary"]:
            old_rcopy["summary"]["thumbnail_coverage"] = new_run["summary"].get("thumbnail_coverage")
            require(round(old_rcopy["summary"]["thumbnail_count"] / old_rcopy["summary"]["published"],3)
                        == new_run["summary"].get("thumbnail_coverage"),
                    sat+": thumbnail coverage falsely reported")
        old_rcopy[add_key] = addon
        require(new_run == old_rcopy,
                sat+": prior run source evidence/stage history changed")
    for row, spec in zip(new_h["history"][-2:],EXPECTED.values()):
        require(row.get("new_event_ids") == [spec["id"]] and
                row.get("added_weekly_records") == 1 and
                row.get("removed_weekly_records") == 0 and
                row.get("changed_existing_records") == 0 and
                row.get("unresolved_required_source_failures") == 3 and
                row.get("unverified_candidate_links_remaining") == 859 and
                row.get("source_failures_remain_unverified") is True,
                "new history row not an exact preserved non-destructive verified addition")
    # Compare actual strict source-failure results, not merely an 'unchanged' label.
    from validate_official_schedule_audit import validate
    from collections import Counter
    cfg = data("discovery_sources.json")
    baseline_gaps, current_gaps = Counter(), Counter()
    for w in old_manifest["weekends"]:
        sat = w["sat"]
        prior_w, actual_w = old(sat+".json"), data(sat+".json")
        before = validate(old(sat+"-run.json"),prior_w,old(sat+"-decisions.json"),cfg,())
        after = validate(data(sat+"-run.json"),actual_w,data(sat+"-decisions.json"),cfg,())
        baseline_gaps.update(before); current_gaps.update(after)
    require(baseline_gaps == current_gaps,
            "required-source failures masked/added: "+str(current_gaps-baseline_gaps))
    print("PASS EXACT TWO OFFICIAL EVENTS: "+", ".join(ids))
    print("PASS existing records and history untouched, source-audit backlog unchanged:",
          sum(baseline_gaps.values()),"historical audit findings")

if __name__ == "__main__":
    try: run()
    except (ValueError, KeyError, TypeError, subprocess.CalledProcessError) as exc:
        print("BATCH2 BLOCKER:", str(exc), file=sys.stderr)
        sys.exit(1)
