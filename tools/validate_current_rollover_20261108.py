#!/usr/bin/env python3
import argparse, json, pathlib, subprocess, sys

BASE="1d1687321f82279d6e46899f1fc453169bba5b1d"
TARGETS=[
 ("2026-11-07",1,"full",52),("2026-11-14",2,"full",41),("2026-11-21",3,"preview",30),
 ("2026-11-28",4,"preview",25),("2026-12-05",5,"announcement",29),("2026-12-12",6,"announcement",18)
]
CARRY={
 "v15-8bc88232815c","v15-ad2f72f74ab7","v15-0c6fcb6bf768","v15-7b30b706f728",
 "ongoing-20261128-v15-237c930495e3","ongoing-20261128-v15-97ee0aaed408","ongoing-20261128-v15-d7b35a2aa60b",
 "ongoing-20261128-r16-a998e43102c9","ongoing-20261128-r16-d1fc65f778d6","ongoing-20261128-r16-c2947a676a15",
 "ongoing-20261128-v15-5e0e43c28e84","official-2026-sumida-light-garden","v15-974166027816"
}
NEW={
 "verified-20261212-ota-bicycle":"https://www.city.ota.tokyo.jp/seikatsu/sumaimachinami/kotsuanzen/event/oyakojitensha.html",
 "verified-20261212-koto-sazanami":"https://www.city.koto.lg.jp/380291/ekokkuru/event/r8/12/261212_wakuwakusazanami.html",
 "verified-20261212-sumida-gosai-tour":"https://sumida-artfest.jp/programs/7572/",
 "verified-20261213-sumida-startbox":"https://startbox.jp/event/3246/",
 "announced-20261212-sumida-bion":"https://sumida-artfest.jp/events/"
}
EXCLUDED={"koto-20261213-christmas-art-waitlist","nakano-official-bfc62ea2972443b4"}
PROMOTED={
 "v15-dbcd6b0db9e1","v15-bf81ae6846bf","v15-43179f997df8","v15-974166027816","v15-a09d13a8ee25",
 "v15-d94b3ac9893d","v15-beb844967090","v15-f60029928c5d","official-2026-nihonbashi-komichi","official-2026-haneda-museum"
}
ALLOWED={
 "site/data/manifest.json","site/data/update_history.json","site/data/2026-11-14-verification.json",
 *{f"site/data/{d}.json" for d,_,_,_ in TARGETS[:-1]},
 *{f"site/data/{d}-run.json" for d,_,_,_ in TARGETS[:-1]},
 "site/data/2026-12-12.json","site/data/2026-12-12-run.json","site/data/2026-12-12-verification.json",
 "site/data/2026-12-12-decisions.json","site/data/2026-12-12-events-current-verified.json"
}

def load(p): return json.loads(pathlib.Path(p).read_text(encoding="utf-8"))
def show(ref,p): return json.loads(subprocess.check_output(["git","show",f"{ref}:{p}"],text=True))
def bundle_events_from_base(ref,sat):
    w=show(ref,f"site/data/{sat}.json"); out=list(w.get("events") or [])
    for f in w.get("event_files") or []: out += show(ref,f"site/data/{f}")
    return out

def fail(errors,msg): errors.append(msg)

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--data-dir",default="site/data"); ap.add_argument("--evidence-dir",required=True); ap.add_argument("--base-ref",required=True); a=ap.parse_args()
    errors=[]; d=pathlib.Path(a.data_dir); e=pathlib.Path(a.evidence_dir)
    if a.base_ref!=BASE: fail(errors,f"unexpected base ref {a.base_ref}")
    changed=set(subprocess.check_output(["git","diff","--name-only",a.base_ref,"HEAD"],text=True).splitlines())
    if changed!=ALLOWED: fail(errors,f"changed paths mismatch: extra={sorted(changed-ALLOWED)} missing={sorted(ALLOWED-changed)}")
    manifest=load(d/"manifest.json")
    got=[(x.get("sat"),x.get("horizon_index"),x.get("publication_tier"),x.get("count")) for x in manifest.get("weekends",[])]
    if got!=TARGETS: fail(errors,f"manifest target mismatch: {got}")
    if manifest.get("default")!="2026-11-07": fail(errors,"manifest default must be current weekend 2026-11-07")
    if manifest.get("holidays")!=[{"date":"2026-11-23","name":"勤労感謝の日","weekend_sat":"2026-11-21"}]: fail(errors,"11/23 holiday mapping mismatch")
    roll=manifest.get("current_rollover") or {}
    if roll.get("base_data_production_sha")!=BASE or roll.get("evidence_workflow_run_id")!=42456012607 or roll.get("evidence_artifact_id")!=13607681119:
        fail(errors,"manifest rollover provenance mismatch")
    # Immutable source evidence.
    summary=load(e/"summary.json"); plan=load(e/"plan.json"); requests=load(e/"requests.json")
    if summary.get("base_data_production_sha")!=BASE or plan.get("base_data_production_sha")!=BASE: fail(errors,"evidence base SHA mismatch")
    if summary.get("as_of_jst")!="2026-11-08" or summary.get("request_count")!=588 or summary.get("requests_success")!=583 or summary.get("candidate_links_unverified")!=844:
        fail(errors,"evidence summary counts mismatch")
    req_fail=summary.get("required_source_failures_outstanding") or []
    if len(req_fail)!=3 or {x.get("id") for x in req_fail}!={"tamemap_nakano"} or any("403" not in str(x.get("error")) for x in req_fail):
        fail(errors,"Tamemap failure ledger mismatch")
    ward_fail=summary.get("ward_failures") or []
    if len(ward_fail)!=1 or ward_fail[0].get("ward")!="練馬区" or len(ward_fail[0].get("errors") or [])!=2:
        fail(errors,"Nerima legacy calendar failure ledger mismatch")
    if len([x for x in requests if x.get("kind")=="ai_cross" and x.get("week")=="2026-12-12"])!=69:
        fail(errors,"expected exactly 69 Dec12 AI cross query requests")
    # Existing event shards must not be touched; changed path allowlist enforces this. Full-tier 11/14 must now be fully verified.
    v14=load(d/"2026-11-14-verification.json")
    if len(v14.get("events") or [])!=41 or any(x.get("status")!="verified" for x in v14.get("events") or []): fail(errors,"11/14 full tier is not 41/41 verified")
    promoted={x.get("id") for x in v14.get("events") or [] if x.get("id") in PROMOTED}
    if promoted!=PROMOTED: fail(errors,"11/14 promoted id set mismatch")
    # New week.
    w12=load(d/"2026-12-12.json"); ev=[]
    for f in w12.get("event_files") or []: ev += load(d/f)
    ids={x.get("id") for x in ev}
    if len(ev)!=18 or ids!=(CARRY|set(NEW)): fail(errors,f"Dec12 published IDs mismatch ({len(ev)})")
    # Carryovers must be byte-for-field equal to prior protected event objects.
    old={x.get("id"):x for x in bundle_events_from_base(a.base_ref,"2026-12-05")}
    for eid in CARRY:
        cur=next((x for x in ev if x.get("id")==eid),None)
        if eid not in old or cur!=old[eid]: fail(errors,f"carryover changed instead of being preserved: {eid}")
    for eid,url in NEW.items():
        cur=next((x for x in ev if x.get("id")==eid),None)
        if not cur or cur.get("official_url")!=url or cur.get("date_start") not in ("2026-12-12","2026-12-13"):
            fail(errors,f"new official event facts mismatch: {eid}")
    vr=load(d/"2026-12-12-verification.json")
    if vr.get("summary",{}).get("total")!=18 or set(x.get("id") for x in vr.get("events") or [])!=ids: fail(errors,"Dec12 verification parity mismatch")
    if any(x.get("status") not in ("verified","announced") for x in vr.get("events") or []): fail(errors,"Dec12 invalid verification status")
    dec=load(d/"2026-12-12-decisions.json"); rows=dec.get("decisions") or []
    if len(rows)!=20 or {x.get("candidate_id") for x in rows if x.get("decision")=="published"}!=ids or {x.get("candidate_id") for x in rows if x.get("decision")=="excluded"}!=EXCLUDED:
        fail(errors,"Dec12 decision audit mismatch")
    run=load(d/"2026-12-12-run.json"); ro=run.get("read_only_evidence") or {}
    if run.get("prompt",{}).get("version")!="v1.15" or ro.get("workflow_run_id")!=42456012607 or ro.get("candidate_links_unverified")!=844:
        fail(errors,"Dec12 run provenance mismatch")
    # Update history must be append-only and accurately describe unresolved evidence.
    before=show(a.base_ref,"site/data/update_history.json"); after=load(d/"update_history.json")
    if after.get("history",[])[:len(before.get("history",[]))]!=before.get("history",[]): fail(errors,"update history not append-only")
    if len(after.get("history",[]))!=len(before.get("history",[]))+1: fail(errors,"expected exactly one history append")
    last=after["history"][-1]
    if last.get("run_type")!="verified_current_horizon_subset" or last.get("base_data_production_sha")!=BASE or last.get("unverified_candidate_links")!=844 or last.get("source_failures_remain_unverified") is not True:
        fail(errors,"history provenance/failure ledger mismatch")
    if errors:
        for x in errors: print("ERROR:",x)
        return 1
    print("CURRENT ROLLOVER PASS: protected 5-week data preserved; 11/14 verified; Dec12 verified subset added; unresolved source failures remain explicit.")
    return 0
if __name__=="__main__": sys.exit(main())
