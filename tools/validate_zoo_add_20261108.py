#!/usr/bin/env python3
"""One-event official organizer supplement; exact production baseline, no waiver."""
import argparse
import copy
import json
from pathlib import Path
import re
import subprocess
import sys
from collections import Counter
from validate_official_schedule_audit import validate

BASE = "45c2688a84a0e045ece7d756d7df028b784526d6"
ID = "verified-20261115-itabashi-zoo-park-festa"
OFFICIAL = "https://itabashi-park-zoo.com/cat_main/%EF%BC%92%EF%BC%90%EF%BC%92%EF%BC%96%E5%B9%B4%E3%80%80zoo%E3%83%91%E3%83%BC%E3%82%AF%E3%83%95%E3%82%A7%E3%82%B9%E3%82%BF%E3%81%AE%E3%81%8A%E7%9F%A5%E3%82%89%E3%81%9B/"
WEEK = "2026-11-14"
SHARD = WEEK + "-events-verified-zoo-20261108.json"
CHANGED = {f"site/data/{n}" for n in ("manifest.json","update_history.json",WEEK+".json",
    WEEK+"-run.json",WEEK+"-verification.json",WEEK+"-decisions.json",SHARD)}

def old(name):
    return json.loads(subprocess.check_output(["git","show",BASE+":site/data/"+name],text=True))

def new(name):
    return json.loads(Path("site/data",name).read_text(encoding="utf8"))

def check(value, why):
    if not value: raise ValueError(why)

def main():
    p=argparse.ArgumentParser();p.add_argument("--base-ref",required=True);p.add_argument("--data-dir",default="site/data")
    a=p.parse_args()
    check(a.base_ref==BASE and a.data_dir=="site/data","Only exact registered production baseline and directory allowed")
    changed=set(subprocess.check_output(["git","diff","--name-only",BASE,"HEAD"],text=True).splitlines())
    check(changed==CHANGED,"Forbidden changed files: "+str(sorted(changed^CHANGED)))
    m0,m1=old("manifest.json"),new("manifest.json")
    expected=copy.deepcopy(m0)
    expected["generated"]=m1["generated"]
    next(w for w in expected["weekends"] if w["sat"]==WEEK)["count"]+=1
    check(expected==m1,"Manifest changed beyond exactly +1 in 11/14")
    h0,h1=old("update_history.json"),new("update_history.json")
    check(h0["history"]==h1["history"][:-1] and len(h1["history"])==len(h0["history"])+1,"History not strictly append-only")
    record=h1["history"][-1]
    check(record.get("new_event_ids")==[ID] and record.get("added_weekly_records")==1 and
          record.get("removed_weekly_records")==0 and record.get("changed_existing_records")==0 and
          record.get("unresolved_required_source_failures")==3 and
          record.get("unverified_candidate_links_remaining")==859 and
          record.get("source_failures_remain_unverified")==True,"Missing exact event proof / unresolved source backlog")
    w0,w1=old(WEEK+".json"),new(WEEK+".json")
    expected=copy.deepcopy(w0);expected["generated"]=w1["generated"];expected["event_files"].append(SHARD)
    expected["coverage"]["published_count"]+=1;expected["coverage"]["candidate_count"]+=1
    orig=next(x for x in w0["coverage"]["wards"] if x["ward"]=="板橋区")
    row=next(x for x in expected["coverage"]["wards"] if x["ward"]=="板橋区")
    target=next(x for x in w1["coverage"]["wards"] if x["ward"]=="板橋区")
    row["published_count"]+=1;row["candidate_count"]+=1;row["note"]=target["note"]
    check(target["note"].startswith(orig["note"]) and expected==w1,"Prior ward stats/crawl evidence changed")
    old_ev=[e for path in w0["event_files"] for e in old(path)]
    new_ev=[e for path in w1["event_files"] for e in new(path)]
    check(len(new_ev)==len(old_ev)+1 and new_ev[:len(old_ev)]==old_ev,"Existing events altered/deleted")
    ev=new(SHARD)
    check(len(ev)==1 and new_ev[-1]==ev[0],"Exact single additive event required")
    x=ev[0]
    check(x.get("id")==ID and x.get("date_start")==x.get("date_end")=="2026-11-15"
          and x.get("ward")=="板橋区" and x.get("official_url")==x.get("source")==x.get("url")==OFFICIAL
          and x.get("family_fit",{}).get("rubric_version")=="family-fit-v1" and
          x.get("family_fit",{}).get("grade")=="A" and x.get("reservation",{}).get("required") is None
          and x.get("price") is None and x.get("indoor_outdoor")=="屋外" and
          x.get("image")=="", "Unverified or unauthorized independent zoo facts")
    v0,v1=old(WEEK+"-verification.json"),new(WEEK+"-verification.json")
    check(v0["events"]==v1["events"][:-1],"Historical verification edited")
    ver=v1["events"][-1]
    check(ver.get("id")==ID and ver.get("status")=="verified" and ver.get("source")==OFFICIAL
          and all(ver.get("fields",{}).get(k)=="pass" for k in ("name","date","venue"))
          and all(ver.get("fields",{}).get(k)=="unknown" for k in ("time","price","reservation")),"No honest verification")
    expected=copy.deepcopy(v0);expected["events"].append(ver);expected["summary"]["total"]+=1;expected["summary"]["verified"]+=1
    check(expected==v1,"Verification other fields changed")
    d0,d1=old(WEEK+"-decisions.json"),new(WEEK+"-decisions.json")
    check(d0["decisions"]==d1["decisions"][:-1],"Prior candidate decisions modified")
    de=d1["decisions"][-1]
    check(de.get("candidate_id")==ID and de.get("decision")=="published" and
          any(z.get("url")==OFFICIAL for z in de.get("evidence",[])),"Missing public organizer source in decision")
    expected=copy.deepcopy(d0);expected["decisions"].append(de);expected["summary"]["candidate_total"]+=1;expected["summary"]["published"]+=1
    check(expected==d1,"Previous decision counters changed")
    r0,r1=old(WEEK+"-run.json"),new(WEEK+"-run.json")
    expected=copy.deepcopy(r0)
    for key in ("published","verified","candidates"):expected["summary"][key]+=1
    expected["summary"]["thumbnail_coverage"]=round(expected["summary"]["thumbnail_count"]/expected["summary"]["published"],3)
    key="verified_zoo_park_festa_20261108"
    check(key in r1 and key not in r0 and r1[key].get("new_event_ids")==[ID] and
          r1[key].get("source_failures_remain_unverified")==True and
          r1[key].get("old_events_changed")==r1[key].get("old_events_removed")==0,"Run lacks new proof")
    expected[key]=r1[key]
    check(expected==r1,"Original run source statuses or other fields changed")
    cfg=new("discovery_sources.json");baseline_errors=Counter();current_errors=Counter()
    for week in m0["weekends"]:
        sat=week["sat"]
        baseline_errors.update(validate(old(sat+"-run.json"),old(sat+".json"),old(sat+"-decisions.json"),cfg,()))
        current_errors.update(validate(new(sat+"-run.json"),new(sat+".json"),new(sat+"-decisions.json"),cfg,()))
    check(baseline_errors==current_errors,"Old source error findings altered: "+str(current_errors-baseline_errors))
    print("EXACT ZOO ADD PASS: +1, no deletion, 859 link leads and all historical source errors intact")

if __name__=="__main__":
    try:main()
    except (ValueError,KeyError,TypeError,subprocess.CalledProcessError) as e:
        print("ZOO EXACT RELEASE BLOCKER",e,file=sys.stderr);sys.exit(1)
