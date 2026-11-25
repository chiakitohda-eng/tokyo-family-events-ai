#!/usr/bin/env python3
"""Construct data-only, clean, scoped release tree from the current published baseline.

Do not copy unrelated December staging candidates, main code, application files,
unverified December event shards, policy, source registry, or static app differences.
No production branch is moved by this preparation script.
"""
from pathlib import Path
import json,shutil,subprocess,hashlib
BASE=Path("clean/site/data");SRC=Path("prepared/site/data")
FROZEN="fc6bec505975c6dabbddd404f33cd7d9f3f525e9"
OLD_ACTIVE=["2026-11-21","2026-11-28","2026-12-05","2026-12-12"]
NEW_ACTIVE=["2026-12-19","2026-12-26"]
SCOPED={
 "confirmed-20261219-nakano-rock-experience",
 "confirmed-20261220-nakano-ikebana",
 "tamemap-20261219-nakano-family-rhythm",
 "tamemap-20261220-nakano-forest-choir",
 "confirmed-20261226-nakano-wagakki",
 "tamemap-20261227-nakano-family-rhythm",
 "tamemap-20261226-nakano-tomocchao",
 "tamemap-20261227-nakano-mama-hot-kitchen",
}
def read(p):return json.loads(p.read_text())
def write(p,j):p.write_text(json.dumps(j,ensure_ascii=False,indent=2)+"\n")
def root():return Path("clean")
def loaded_events(base,sat):
 w=read(base/(sat+".json"))
 events=list(w.get("events") or [])
 for shard in w["event_files"]:events+=read(base/shard)
 return events
def main():
 before=read(BASE/"manifest.json");after=read(SRC/"manifest.json")
 assert sum(x["count"] for x in before["weekends"])==607
 assert [e["sat"] for e in after["weekends"]]==OLD_ACTIVE+NEW_ACTIVE
 assert sum(x["count"] for x in after["weekends"])==430
 for sat in NEW_ACTIVE:
  eventlist=loaded_events(SRC,sat)
  ids={e["id"] for e in eventlist}
  assert len(eventlist)==4 and ids<=SCOPED,("unexpected staged future item",sat)
 assert set(e["id"] for sat in NEW_ACTIVE for e in loaded_events(SRC,sat))==SCOPED
 changed=subprocess.check_output(["git","-C","prepared","diff","--name-only",FROZEN,"HEAD"],text=True).splitlines()
 required={"site/data/manifest.json","site/data/update_history.json",
           "site/data/2026-11-17-carried-announcement-rechecks.json"}
 for sat in OLD_ACTIVE:
  required|={f"site/data/{sat}.json",f"site/data/{sat}-run.json"}
 for sat in OLD_ACTIVE[:2]:required.add(f"site/data/{sat}-verification.json")
 for sat in NEW_ACTIVE:
  for suffix in (".json","-run.json","-verification.json","-decisions.json","-events-non-ng-verified-only-20261117.json"):
   required.add(f"site/data/{sat}{suffix}")
 image_shards={
   p for p in changed
   if p.startswith(("site/data/2026-11-21-events-","site/data/2026-11-28-events-"))
   and p.endswith(".json")
 }
 assert len(image_shards)==19,("unexpected image-modified file set",len(image_shards))
 allowed=required|image_shards
 missing=[x for x in allowed if not Path("prepared",x).exists()]
 assert not missing,missing
 for item in sorted(allowed):
  src=Path("prepared",item);dst=Path("clean",item)
  dst.parent.mkdir(parents=True,exist_ok=True)
  shutil.copy2(src,dst)
 # Do not hide that full source audit is still pending: manual specific subset only.
 manifest=read(BASE/"manifest.json")
 assert manifest["current_rollover"]["mode"]=="scoped_non_ng_candidate_not_release_ready"
 manifest["current_rollover"]["mode"]="manual_evidence_checked_subset_rollover"
 manifest["current_rollover"]["full_23_ward_25_source_audit_complete"]=False
 manifest["current_rollover"]["legacy_missing_source_errors_preserved"]=True
 write(BASE/"manifest.json",manifest)
 hist=read(BASE/"update_history.json")
 last=hist["history"][-1]
 assert last["run_id"]=="non-ng-candidate-20261117"
 last["run_type"]="manual_scoped_non_ng_release_requested"
 last["status"]="verified_subset_publication"
 last.pop("not_published",None)
 last["note"]="個別公式照合8件・旧14件の実URL文字照合を伴う限定公開。23区/必須25参照元の網羅完了を意味せず、ためまっぷ403を未解決のまま記録。過去607件を物理削除しない。"
 write(BASE/"update_history.json",hist)
 all_old=[]
 image_updates=0
 for sat in ("2026-11-07","2026-11-14")+tuple(OLD_ACTIVE):
  original=loaded_events(Path("baseline/site/data"),sat)
  now=loaded_events(BASE,sat)
  assert [x["id"] for x in original]==[x["id"] for x in now],("previous ID lost",sat)
  for x,y in zip(original,now):
   if x!=y:
    assert x.get("image") in (None,"") and y.get("image","").startswith("https://")
    assert {k:v for k,v in x.items() if k!="image"}=={k:v for k,v in y.items() if k!="image"}
    image_updates+=1
  all_old.extend(original)
 assert len(all_old)==607 and image_updates==42
 # Explicitly disallow any referenced non-NG event filename outside the 2 released shards.
 for sat in NEW_ACTIVE:
  week=read(BASE/(sat+".json"))
  assert week["event_files"]==[sat+"-events-non-ng-verified-only-20261117.json"]
 for sat in NEW_ACTIVE:
  record=read(BASE/(sat+"-verification.json"))
  assert record["summary"]["total"]==4
 audit=read(BASE/"2026-11-17-carried-announcement-rechecks.json")
 assert audit["verified"]==14 and audit["still_announced"]==0
 for row in audit["per_event"]:
  assert row["verified"] and row["http_status"]==200 and not row["missing"]
 for sat in OLD_ACTIVE[:2]:
  record=read(BASE/(sat+"-verification.json"))
  assert record["summary"]["announced"]==0 and record["summary"]["verified"]==record["summary"]["total"]
 # No other new paths are copied. Preserve prior main/static app/data refs verbatim.
 assert not any(BASE.glob("2026-12-19-events-carryover-*.json"))
 new_files=[x for x in allowed if not Path("baseline",x).exists()]
 print("CLEAN_SCOPED_EIGHT_REVIEW",json.dumps({
   "baseline":FROZEN,"active_count":430,"all_previous_records_physically_retained":607,
   "eight_new_ids":sorted(SCOPED),"old14_verified_against_10_live_official_urls":True,
   "photo_only_updated":image_updates,"new_release_files":sorted(new_files),
   "only_data_prefix_modified":True,"global_source_audit_still_pending":True},ensure_ascii=False))
if __name__=="__main__":main()
