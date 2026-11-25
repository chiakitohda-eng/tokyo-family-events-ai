#!/usr/bin/env python3
"""One-event evidence-based, additive data release guard. Do not waive new audit failures."""
import argparse
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

from validate_official_schedule_audit import validate as source_validate

WEEK = "2026-11-28"
ID = "official-20261128-minato-neighbors-garden-party4"
SHARD = "2026-11-28-events-neighbors-official-20261117.json"
OFFICIAL = "https://ikou.nttud.co.jp/topics/detail/id/n28054.html"
PATH = "site/data/"
ALLOWED = {
    PATH + "manifest.json",
    PATH + WEEK + ".json",
    PATH + WEEK + "-verification.json",
    PATH + WEEK + "-decisions.json",
    PATH + WEEK + "-run.json",
    PATH + SHARD,
    PATH + "update_history.json",
}
AXES = ("child_target", "interactivity", "age_fit", "stay_flexibility", "burden", "cost", "reservation", "family_value")

def load_before(base, name):
    return json.loads(subprocess.check_output(["git", "show", base + ":" + PATH + name], text=True))

def load_after(directory, name):
    return json.loads((directory / name).read_text(encoding="utf-8"))

def bundle(load, entry):
    week = load(entry["file"])
    records = list(week.get("events") or [])
    for name in week.get("event_files") or []:
        records.extend(load(name))
    return week, records

def assert_equal(a, b, label):
    if a != b:
        raise ValueError("previous data changed: " + label)

def check(base, directory):
    if not re.fullmatch(r"[0-9a-f]{40}", base):
        raise ValueError("fixed 40-character baseline SHA required")
    changed = set(subprocess.check_output(["git", "diff", "--name-only", base, "HEAD"], text=True).splitlines())
    if changed != ALLOWED:
        raise ValueError("only the seven declared data paths are permitted: " + str(sorted(changed ^ ALLOWED)))
    old = lambda name: load_before(base, name)
    new = lambda name: load_after(directory, name)
    prior, current = old("manifest.json"), new("manifest.json")
    for key, value in prior.items():
        if key != "weekends":
            assert_equal(value, current.get(key), "manifest." + key)
    if len(prior["weekends"]) != 6 or len(current["weekends"]) != 6:
        raise ValueError("six published weeks must remain unchanged")
    for b, a in zip(prior["weekends"], current["weekends"]):
        if b["sat"] != WEEK:
            assert_equal(b, a, "unrelated manifest week")
        else:
            for k, v in b.items():
                if k != "count":
                    assert_equal(v, a.get(k), "target manifest metadata " + k)
            if a["count"] != b["count"] + 1:
                raise ValueError("target manifest count must increase by one")
    before_week, before_events = bundle(old, next(x for x in prior["weekends"] if x["sat"] == WEEK))
    after_week, after_events = bundle(new, next(x for x in current["weekends"] if x["sat"] == WEEK))
    for k, v in before_week.items():
        if k not in ("event_files", "coverage"):
            assert_equal(v, after_week.get(k), "target week metadata " + k)
    if after_week.get("event_files") != before_week["event_files"] + [SHARD]:
        raise ValueError("new event shard must be appended exactly")
    if after_events[:-1] != before_events or len(after_events) != len(before_events) + 1:
        raise ValueError("all prior published records must be byte-for-byte equivalent as JSON")
    item = after_events[-1]
    if (item.get("id"), item.get("name"), item.get("ward"),
        item.get("date_start"), item.get("date_end"), item.get("official_url")) != (
         ID, "NEIGHBORS’ GARDEN PARTY #4", "港区", "2026-11-28", "2026-11-29", OFFICIAL):
        raise ValueError("unexpected new event identity or unsupported official URL")
    if not item.get("price") or not item.get("venue") or not item.get("time"):
        raise ValueError("new event lacks verified primary facts")
    for k, v in before_week["coverage"].items():
        if k not in ("candidate_count", "published_count", "wards"):
            assert_equal(v, after_week["coverage"].get(k), "original source coverage " + k)
    for k in ("candidate_count", "published_count"):
        if after_week["coverage"][k] != before_week["coverage"][k] + 1:
            raise ValueError("coverage " + k + " must increase by one")
    for before_ward, after_ward in zip(before_week["coverage"]["wards"], after_week["coverage"]["wards"]):
        if before_ward["ward"] != after_ward["ward"]:
            raise ValueError("ward coverage identity changed")
        if before_ward["ward"] != "港区":
            assert_equal(before_ward, after_ward, "unrelated ward coverage")
        else:
            for k, v in before_ward.items():
                if k not in ("candidate_count", "published_count", "note"):
                    assert_equal(v, after_ward.get(k), "unchanged source count " + k)
            if any(after_ward[k] != before_ward[k] + 1 for k in ("candidate_count", "published_count")):
                raise ValueError("Minato candidate and publication counts must increase by one")
    proof = new(WEEK + "-verification.json")
    old_proof = old(WEEK + "-verification.json")
    if proof["events"][:-1] != old_proof["events"] or len(proof["events"]) != len(old_proof["events"]) + 1:
        raise ValueError("previous individual verification rows changed")
    v = proof["events"][-1]
    if v.get("id") != ID or v.get("status") != "verified" or v.get("source") != OFFICIAL:
        raise ValueError("new candidate requires verified organizer proof")
    for field in ("name", "date", "venue", "time", "price", "reservation", "official_url"):
        if v.get("fields", {}).get(field) != "pass":
            raise ValueError("unverified event field: " + field)
    if proof["summary"]["total"] != old_proof["summary"]["total"] + 1 or proof["summary"]["verified"] != old_proof["summary"]["verified"] + 1:
        raise ValueError("verification totals do not reconcile")
    for k in old_proof["summary"]:
        if k not in ("total", "verified"):
            assert_equal(old_proof["summary"][k], proof["summary"].get(k), "prior verification summary")
    d, old_d = new(WEEK + "-decisions.json"), old(WEEK + "-decisions.json")
    if d["decisions"][:-1] != old_d["decisions"] or len(d["decisions"]) != len(old_d["decisions"]) + 1:
        raise ValueError("prior decision records changed")
    new_decision = d["decisions"][-1]
    if new_decision.get("candidate_id") != ID or new_decision.get("decision") != "published":
        raise ValueError("missing one new published decision")
    if new_decision.get("family_fit") != item.get("family_fit"):
        raise ValueError("family fit of event and decision must match")
    for k in ("candidate_total", "published"):
        if d["summary"][k] != old_d["summary"][k] + 1:
            raise ValueError("decision summary mismatch: " + k)
    for k in old_d["summary"]:
        if k not in ("candidate_total", "published"):
            assert_equal(old_d["summary"][k], d["summary"].get(k), "prior decision summary")
    fit = item["family_fit"]
    review = fit.get("review") or {}
    if fit.get("overall") != "A" or set(review.get("axes_checked") or []) != set(AXES):
        raise ValueError("eight axes and stated overall grade required")
    if review.get("method") != "individual_evidence_review" or review.get("reviewed_on") != "2026-11-17":
        raise ValueError("evidence review method and date required")
    for e in review.get("evidence") or []:
        excerpt = e.get("quote")
        if e.get("url") != OFFICIAL or e.get("checked_at") != "2026-11-17" or e.get("hash_scope") != "exact_utf8_quote" or not isinstance(excerpt, str):
            raise ValueError("explicit official excerpt evidence is required")
        if hashlib.sha256(excerpt.encode("utf-8")).hexdigest() != e.get("sha256"):
            raise ValueError("official excerpt content hash does not match")
    if len(review.get("evidence") or []) < 2:
        raise ValueError("need both family activity and date excerpts")
    run, old_run = new(WEEK + "-run.json"), old(WEEK + "-run.json")
    for k, v in old_run.items():
        if k not in ("summary",):
            assert_equal(v, run.get(k), "original run proof " + k)
    for k in old_run["summary"]:
        if k in ("published", "verified", "candidates"):
            if run["summary"][k] != old_run["summary"][k] + 1:
                raise ValueError("run count must increase by one: " + k)
        else:
            assert_equal(old_run["summary"][k], run["summary"].get(k), "original summary " + k)
    addendum = run.get("manual_verified_subset_20261117") or {}
    if addendum.get("event_id") != ID or addendum.get("base_data_production_sha") != base or addendum.get("required_source_errors_still_unresolved") is not True:
        raise ValueError("missing explicit unresolved-source addendum")
    hist, old_hist = new("update_history.json"), old("update_history.json")
    if hist["history"][:-1] != old_hist["history"] or len(hist["history"]) != len(old_hist["history"]) + 1:
        raise ValueError("historic release history must remain append only")
    h = hist["history"][-1]
    if h.get("new_event_ids") != [ID] or h.get("added_weekly_records") != 1 or h.get("removed_weekly_records") != 0 or h.get("base_data_production_sha") != base:
        raise ValueError("one-item history and baseline proof required")
    # Existing audit failures may be retained, but new failures are NEVER waived.
    policy = new("discovery_sources.json")
    old_errors, new_errors = [], []
    for old_entry, new_entry in zip(prior["weekends"], current["weekends"]):
        old_week, new_week = old(old_entry["file"]), new(new_entry["file"])
        old_run_file, new_run_file = old(old_week["run_file"]), new(new_week["run_file"])
        old_dec_file = old(old_run_file["source_data"]["decision_file"])
        new_dec_file = new(new_run_file["source_data"]["decision_file"])
        old_errors.extend(source_validate(old_run_file, old_week, old_dec_file, policy, ()))
        new_errors.extend(source_validate(new_run_file, new_week, new_dec_file, policy, ()))
    if old_errors != new_errors:
        raise ValueError("changed source audit failure list; no waiver for new errors")
    print("SAFE_VERIFIED_ADD_ONE_PASS event=" + ID)
    print("EXISTING_SOURCE_DEBT_RETAINED_UNCHANGED count=" + str(len(old_errors)))

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-ref", required=True)
    parser.add_argument("--data-dir", default="site/data")
    args = parser.parse_args()
    try:
        check(args.base_ref, Path(args.data_dir))
    except (KeyError, TypeError, ValueError, OSError, subprocess.CalledProcessError) as exc:
        print("SAFE_ONE_ITEM_RELEASE_BLOCKER: " + str(exc), file=sys.stderr)
        return 2
    return 0

if __name__ == "__main__":
    sys.exit(main())
