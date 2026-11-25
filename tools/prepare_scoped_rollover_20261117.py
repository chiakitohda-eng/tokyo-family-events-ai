#!/usr/bin/env python3
"""Build non-published, explicitly incomplete six-week scoped data candidate for manual verification.

Never assert full source coverage. No production refs are changed. The separate release
gate remains closed until authorized validation passes. The original data in site/data
is retained, including expired weeks and every missing-source error.
"""
from __future__ import annotations
from collections import Counter
from copy import deepcopy
from datetime import datetime, timedelta, timezone
from pathlib import Path
import json
import hashlib

DATA=Path("candidate/site/data")
BASE=Path("baseline/site/data")
IDS_19=[
 "confirmed-20261219-nakano-rock-experience",
 "confirmed-20261220-nakano-ikebana",
 "tamemap-20261219-nakano-family-rhythm",
 "tamemap-20261220-nakano-forest-choir",
]
IDS_26=[
 "confirmed-20261226-nakano-wagakki",
 "tamemap-20261227-nakano-family-rhythm",
 "tamemap-20261226-nakano-tomocchao",
 "tamemap-20261227-nakano-mama-hot-kitchen",
]
OLD_SATS=["2026-11-21","2026-11-28","2026-12-05","2026-12-12"]
ALL_SATS=OLD_SATS+["2026-12-19","2026-12-26"]
JST=timezone(timedelta(hours=9))
NOW=datetime.now(JST).isoformat(timespec="seconds")
BASE_SHA="fc6bec505975c6dabbddd404f33cd7d9f3f525e9"

def load(path):return json.loads(path.read_text())
def write(path,x):path.write_text(json.dumps(x,ensure_ascii=False,indent=2)+"\n")
def d(name):return DATA/name
def old(name):return BASE/name
def assert_same(a,b,why):
 if a!=b:raise AssertionError(why)
def loaded_events(sat):
 w=load(d(sat+".json"));z=list(w.get("events") or [])
 for f in w["event_files"]:z+=load(d(f))
 return z
def main():
 baseline=load(old("manifest.json"));staged=load(d("manifest.json"))
 assert_same([w["sat"] for w in baseline["weekends"]],[w["sat"] for w in staged["weekends"]],"Unexpected published baseline horizon")
 assert_same(sum(w["count"] for w in baseline["weekends"]),607,"Expected current published count has moved")
 source=load(d("2026-11-17-buckets-3-4-disposition.json"))
 approved={x["id"] for x in source["decisions"] if x["result"].endswith("staged_wait_week_rollover")}
 assert_same(approved,set(IDS_19+IDS_26),"The user's 8 non-NG event IDs changed")
 missing={x["id"] for x in source["decisions"] if x["result"].startswith("pending_")}
 assert_same(len(missing),6,"NG count drift")

 image_corrections=[]
 for sat in OLD_SATS:
  before=load(old(sat+".json"));now=load(d(sat+".json"))
  assert_same(before,now,"Old published weekend metadata changed before roll: "+sat)
  old_event_data=list(before.get("events") or [])
  new_event_data=list(now.get("events") or [])
  for filename in before["event_files"]:
   rows_before=load(old(filename));rows_after=load(d(filename))
   assert_same([r["id"] for r in rows_before],[r["id"] for r in rows_after],"Old event IDs changed "+filename)
   for a,b in zip(rows_before,rows_after):
    if a!=b:
     assert_same({k:v for k,v in a.items() if k!="image"},
                 {k:v for k,v in b.items() if k!="image"},
                 "Unauthorized published-event field change "+str(a["id"]))
     assert not a.get("image") and b.get("image","").startswith("https://"),"Only additive images allowed"
     image_corrections.append({"week":sat,"id":a["id"],"image":b["image"],"shard":filename})
 assert_same(len(image_corrections),42,"Image proposal was not the 42 verified-only scope")

 manifest=deepcopy(baseline)
 old_summary={w["sat"]:w for w in baseline["weekends"]}
 new_weeks=[]
 for i,sat in enumerate(ALL_SATS,1):
  tier="full" if i<=2 else "preview" if i<=4 else "announcement"
  if sat in old_summary:
   entry=deepcopy(old_summary[sat])
  else:
   entry={"sat":sat,"sun":(datetime.strptime(sat,"%Y-%m-%d")+timedelta(days=1)).strftime("%Y-%m-%d"),
          "label":("12/19(土)〜12/20(日)" if sat=="2026-12-19" else "12/26(土)〜12/27(日)"),
          "file":sat+".json","count":4}
  entry["horizon_index"]=i;entry["publication_tier"]=tier
  new_weeks.append(entry)

 # Do not erase prior holiday evidence or prior rollover metadata.
 manifest["weekends"]=new_weeks
 manifest["generated"]=NOW
 manifest["default"]="2026-11-21"
 manifest["previous_current_rollover"]=baseline.get("current_rollover")
 manifest["current_rollover"]={
  "as_of_jst":"2026-11-17",
  "mode":"scoped_non_ng_candidate_not_release_ready",
  "base_data_production_sha":BASE_SHA,
  "retired_week_starts":["2026-11-07","2026-11-14"],
  "new_week_starts":["2026-12-19","2026-12-26"],
  "scope_added_events":8,
  "required_source_failures_observed":2,
  "global_source_audit_complete":False,
  "production_release_authorized_only_after_validation":True,
 }
 write(d("manifest.json"),manifest)

 # All 4 baseline weeks are physically preserved but their internal horizon indices are rolled.
 for i,sat in enumerate(OLD_SATS,1):
  week=load(d(sat+".json"))
  run=load(d(sat+"-run.json"))
  tier="full" if i<=2 else "preview"
  week["horizon_index"]=i;week["publication_tier"]=tier
  run["horizon_index"]=i;run["publication_tier"]=tier
  run["scoped_rollover_20261117"]={
    "as_of_jst":"2026-11-17",
    "preserved_prior_evidence":True,
    "source_reaudit_20261117":"read-only HTTP spot check; does not imply 23-ward/25-source complete refresh",
    "full_tier_verification_not_yet_complete":i<=2,
    "old_event_ids_preserved":True,
  }
  write(d(sat+".json"),week)
  write(d(sat+"-run.json"),run)

 # The previously announced events are NOT silently upgraded: they must remain
 # blocked until a separate dated official-source per-event verification is complete.
 full_tier_pending={}
 for sat in OLD_SATS[:2]:
  ver=load(d(sat+"-verification.json"))
  full_tier_pending[sat]=[v["id"] for v in ver["events"] if v["status"]=="announced"]
 assert_same(sum(map(len,full_tier_pending.values())),14,"Expected 14 carried events need re-verification")

 # Only the eight identified non-NG records enter the two new visible calendar weeks.
 for i,(sat,ids) in enumerate((("2026-12-19",IDS_19),("2026-12-26",IDS_26)),5):
  oldweek=load(d(sat+".json"))
  events=loaded_events(sat)
  indexes={e["id"]:e for e in events}
  if any(i not in indexes for i in ids):raise ValueError("Missing selected event in staged week")
  selected=[deepcopy(indexes[x]) for x in ids]
  for ev in selected:
   if ev["id"] in missing:raise AssertionError("NG included in scoped release")
   if ev["id"]=="tamemap-20261227-nakano-mama-hot-kitchen":
    # Individual index date is kept in audit evidence; do not silently claim full HTTP response.
    review=ev["family_fit"]["review"]
    review["method"]="individual_evidence_review"
    review["evidence"]=[e for e in review["evidence"] if len(str(e.get("quote") or ""))>=12]
    review["limitations"].append("2026年当日個別の時刻/参加条件が未確認であり、過去の定期案内と月別索引の突合に限る。")
  shard=sat+"-events-non-ng-verified-only-20261117.json"
  write(d(shard),selected)
  w=deepcopy(oldweek)
  w["events"]=[]
  w["event_files"]=[shard]
  w["horizon_index"]=i
  w["publication_tier"]="announcement"
  w["coverage"]["published_count"]=len(ids)
  w["coverage"]["candidate_count"]=len(ids)
  w["coverage"]["excluded_count"]=0
  w["coverage"]["duplicate_removed"]=0
  for item in w["coverage"]["wards"]:
   item["candidate_count"]=len(ids) if item["ward"]=="中野区" else 0
   item["published_count"]=len(ids) if item["ward"]=="中野区" else 0
   item["status"]="pending_reaudit"
   item["queries"]=0
   item["sources_checked"]=0
   item["note"]="個別照合で認定した非NG候補のみ。全23区・必須参照元の完全監査は未実施。"
  write(d(sat+".json"),w)
  v=load(d(sat+"-verification.json"))
  index={x["id"]:x for x in v["events"]}
  v["events"]=[deepcopy(index[x]) for x in ids]
  counts=Counter(x["status"] for x in v["events"])
  v["summary"]={"total":len(ids),"verified":counts["verified"],"announced":counts["announced"]}
  v["verified_on"]="2026-11-17"
  write(d(sat+"-verification.json"),v)
  dd=load(d(sat+"-decisions.json"))
  decidx={x["candidate_id"]:x for x in dd["decisions"]}
  dd["decisions"]=[deepcopy(decidx[x]) for x in ids]
  dd["summary"]={"candidate_total":len(ids),"published":len(ids),"excluded":0,
                 "duplicate":0,"hard_excluded":0,"soft_excluded":0,"reason_counts":{}}
  for row,ev in zip(dd["decisions"],selected):
   row["family_fit"]=ev["family_fit"]
  write(d(sat+"-decisions.json"),dd)
  run=load(d(sat+"-run.json"))
  run["horizon_index"]=i;run["publication_tier"]="announcement"
  run["mode"]="manual_partial_non_ng_candidate_not_published"
  run["summary"].update({"wards_checked":0,"candidates":len(ids),"published":len(ids),
                         "excluded":0,"verified":counts["verified"],"announced":counts["announced"],
                         "source_audit_complete":False,"publication_ready":False})
  run["candidate_evidence"]["source_shards"]=[shard]
  run["scoped_addendum_20261117"]={
    "kind":"eight_non_ng_approved_only",
    "added_ids":ids,"verified":counts["verified"],"announced":counts["announced"],
    "publication_ready":False,"global_source_audit_complete":False,
    "as_of_jst":"2026-11-17","original_staged_week_candidates_preserved_elsewhere":True,
  }
  write(d(sat+"-run.json"),run)

 # Do not invent six-week all-sources audit or imply published 8.
 history=load(old("update_history.json"))
 current={"run_id":"non-ng-candidate-20261117","run_type":"manual_scoped_non_ng_candidate",
   "status":"pending_release_gate", "as_of_jst":"2026-11-17","executed_at":NOW,
   "base_data_production_sha":BASE_SHA,"target_weekends":ALL_SATS,
   "prior_active_week_records":607,"candidate_active_week_records":155+108+87+72+8,
   "added_weekly_records":8,"new_event_ids":IDS_19+IDS_26,
   "retired_from_active_rolling_window":["2026-11-07","2026-11-14"],
   "existing_event_records_physically_deleted":0,
   "image_only_updates":42,
   "full_tier_pending_verification":full_tier_pending,
   "global_required_source_audit_pending":True,
   "not_published":True,
   "source_failures_remain_unverified":True,
   "note":"未公開の対象8件と既存11/21・11/28の公式画像42件を統合し6週候補のみ準備。14既存announcedの正式再確認、全源監査とNG条件は未完で公開不可。既存607件の物理削除なし。"}
 history["history"].append(current)
 write(d("update_history.json"),history)

 total=sum(e["count"] for e in manifest["weekends"])
 assert_same(total,430,"Candidate week count drift")
 allids={}
 for week in manifest["weekends"]:
  events=loaded_events(week["sat"])
  ids=[e["id"] for e in events]
  assert_same(len(ids),len(set(ids)),"Duplicate event IDs "+week["sat"])
  assert_same(len(ids),week["count"],"Event count mismatch "+week["sat"])
  allids[week["sat"]]=ids
 for sat in OLD_SATS:
  old_week=load(old(sat+".json"))
  olds=list(old_week.get("events") or [])
  for filename in old_week["event_files"]:olds+=load(old(filename))
  assert_same([x["id"] for x in olds],allids[sat],"Previously published ID changed "+sat)
 for sat in ("2026-11-07","2026-11-14"):
  for filename in [sat+".json"]+load(old(sat+".json"))["event_files"]:
   assert_same(load(old(filename)),load(d(filename)),"Archived historical week was modified "+filename)
 print("SCOPED_ROLLOVER_PREPARED_NO_DEPLOY",json.dumps({
    "candidate_active_week_records":430,"new_non_ng":8,
    "previously_published_ids_physically_retained":607,
    "official_images_added":42,"full_tier_reverification_pending":full_tier_pending,
    "required_source_failures":"at least two Tamemap 403; global row reconciliation incomplete",
    "publish_ready":False},ensure_ascii=False))

if __name__=="__main__":main()
