"""Frozen seven-event community additive review gate; all preexisting records and gaps stay intact."""
import argparse
from collections import Counter
import copy
import json
from pathlib import Path
import subprocess

from validate_official_schedule_audit import validate

BASE = "16fce3b01284cc8dad338feba9a0fa7fb2970792"
SPEC = Path(__file__).resolve().parents[1] / "research/community_review_20261113/publishable.json"
WEEKS = ("2026-11-14", "2026-11-21")
KEY = "verified_community_followup_20261113"


def load_spec():
    spec = json.loads(SPEC.read_text(encoding="utf-8"))
    if spec["base_data_production_sha"] != BASE or len(spec["records"]) != 7:
        raise ValueError("wrong immutable review specification")
    return spec["records"]


def expected_outputs(read_old, records, stamp):
    """Construct exactly the approved additions without rewriting old evidence."""
    manifest = copy.deepcopy(read_old("manifest.json"))
    manifest["generated"] = stamp
    outputs = {"manifest.json": manifest}
    all_ids = []
    for week in WEEKS:
        batch = [r for r in records if r["week"] == week]
        if len(batch) != {"2026-11-14": 2, "2026-11-21": 5}[week]:
            raise ValueError("exactly two/five independent events per frozen weekend")
        ids = [r["event"]["id"] for r in batch]
        all_ids.extend(ids)
        shard = week + "-events-reviewed-community-20261113.json"
        outputs[shard] = [r["event"] for r in batch]
        next(w for w in manifest["weekends"] if w["sat"] == week)["count"] += len(batch)
        doc = copy.deepcopy(read_old(week + ".json"))
        doc["generated"] = stamp
        doc["event_files"].append(shard)
        for field in ("published_count", "candidate_count"):
            doc["coverage"][field] += len(batch)
            next(w for w in doc["coverage"]["wards"] if w["ward"] == "中野区")[field] += len(batch)
        outputs[week + ".json"] = doc
        ver = copy.deepcopy(read_old(week + "-verification.json"))
        ver["events"].extend(r["verification"] for r in batch)
        for field in ("total", "verified"):
            ver["summary"][field] += len(batch)
        outputs[week + "-verification.json"] = ver
        dec = copy.deepcopy(read_old(week + "-decisions.json"))
        for row in batch:
            audit = copy.deepcopy(row["decision"])
            if dec.get("rubric_version") == "family-fit-v1":
                # Preserve the historical week's audit-envelope contract. The
                # actual new evaluation and public event remain canonical v2;
                # do not relabel or rewrite any old evaluation to migrate it.
                audit["canonical_family_fit_v2"] = copy.deepcopy(audit["family_fit"])
                audit["family_fit"]["rubric_version"] = "family-fit-v1"
                audit["family_fit"]["evaluation_rubric_version"] = "family-fit-v2"
                audit["compatibility_note"] = "Historical v1 audit envelope only; canonical_family_fit_v2 and public event retain actual family-fit-v2 assessment."
            dec["decisions"].append(audit)
        for field in ("candidate_total", "published"):
            dec["summary"][field] += len(batch)
        outputs[week + "-decisions.json"] = dec
        run = copy.deepcopy(read_old(week + "-run.json"))
        for field in ("published", "verified"):
            run["summary"][field] += len(batch)
        run[KEY] = {"new_event_ids": ids, "base_data_production_sha": BASE,
                    "prompt": {"version": "v1.15", "path": "prompts/tokyo_family_events_complete_prompt_v1.15.txt", "resolved": True},
                    "reviewed_on": "2026-11-13", "source_failures_remain_unverified": True,
                    "old_events_changed": 0, "old_events_removed": 0,
                    "whole_source_parity_complete": False}
        outputs[week + "-run.json"] = run
    history = copy.deepcopy(read_old("update_history.json"))
    history["history"].append({"run_id": "reviewed-community-20261113",
        "run_type": "manual_official_add_only", "status": "verified_subset",
        "as_of_jst": "2026-11-13", "executed_at": stamp,
        "base_data_production_sha": BASE, "target_weekends": list(WEEKS),
        "added_weekly_records": 7, "new_event_ids": all_ids,
        "removed_weekly_records": 0, "changed_existing_records": 0,
        "source_failures_remain_unverified": True, "content_review_complete": False,
        "recovery_pool_total": 430, "priority_candidate_rows_read": 80,
        "distinct_priority_detail_pages_read": 61,
        "official_evidence_urls": [r["event"]["official_url"] for r in records],
        "note": "主催者の提供本文/申込案内で開催日・会場を確認した7件のみ追加。時刻未記載6件は空欄。月会費・別枠のパントリー申込を明示し、問合せ受付時間を開催時刻に流用しない。既存220件・履歴・ソース取得失敗は保持。"})
    outputs["update_history.json"] = history
    return outputs


def compare_outputs(actual, expected):
    if set(actual) != set(expected):
        raise ValueError("unexpected changed paths")
    for name in expected:
        if actual[name] != expected[name]:
            raise ValueError("unapproved data or prior-evidence mutation: " + name)


def check(base, directory):
    if base != BASE:
        raise ValueError("only exact pre-review production baseline permitted")
    directory = Path(directory)
    old = lambda name: json.loads(subprocess.check_output(["git", "show", BASE + ":site/data/" + name]))
    current = lambda name: json.loads((directory / name).read_text(encoding="utf-8"))
    stamp = current("manifest.json")["generated"]
    if stamp <= old("manifest.json")["generated"]:
        raise ValueError("manifest timestamp must advance")
    expected = expected_outputs(old, load_spec(), stamp)
    changed = subprocess.check_output(["git", "diff", "--name-only", BASE, "HEAD"], text=True).splitlines()
    if set(changed) != {"site/data/" + p for p in expected}:
        raise ValueError("only the twelve reviewed data files may change")
    compare_outputs({p: current(p) for p in expected}, expected)
    config = current("discovery_sources.json")
    before_errors, after_errors = Counter(), Counter()
    for w in old("manifest.json")["weekends"]:
        day = w["sat"]
        before_errors.update(validate(old(day + "-run.json"), old(day + ".json"), old(day + "-decisions.json"), config, ()))
        after_errors.update(validate(current(day + "-run.json"), current(day + ".json"), current(day + "-decisions.json"), config, ()))
    if before_errors != after_errors:
        raise ValueError("historical source failures changed")
    print("COMMUNITY REVIEW GATE PASS: seven verified additions; all old facts/history/source debt unchanged")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-ref", required=True)
    parser.add_argument("--data-dir", default="site/data")
    args = parser.parse_args()
    check(args.base_ref, args.data_dir)
