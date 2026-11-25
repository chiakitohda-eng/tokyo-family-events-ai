#!/usr/bin/env python3
"""Auditable all-record triage for a 2026-11-08 real crawl, NOT full event verification.

Outputs exactly one row per harvested candidate. A navigation link is never
mistaken for an omitted event, nor is a same-URL multi-event page an exact match.
Source HTTP failures and undated leads remain explicitly unresolved.
"""
import argparse
from collections import Counter, defaultdict
from datetime import date,timedelta
import json,re,unicodedata
from pathlib import Path
from urllib.parse import urlsplit

def read(path): return json.loads(Path(path).read_text(encoding="utf8"))
def norm(value): return re.sub(r"[\s　・〜～「」『』()（）【】\[\]《》・,、。—ー\-]", "",unicodedata.normalize("NFKC",str(value or "")).lower())
def url(value):
    try:
        p=urlsplit(value)
        return p.netloc.lower().removeprefix("www.")+p.path.rstrip("/") if p.scheme=="https" and p.netloc else ""
    except (ValueError,TypeError):return ""
def near_name(a,b):
    a,b=norm(a),norm(b)
    return len(a)>5 and len(b)>5 and (a==b or (len(a)>=10 and a in b) or (len(b)>=10 and b in a))
def in_scope(c,days):
    return bool(set(c.get("matched_dates") or c.get("dates") or [])&days)
def actual_dates(c):
    if not c.get("date_start") or not c.get("date_end"):return set()
    try:
        start,end=date.fromisoformat(c["date_start"]),date.fromisoformat(c["date_end"])
        if end<start or (end-start).days>370:return set()
        return {(start+timedelta(days=i)).isoformat() for i in range((end-start).days+1)}
    except (TypeError,ValueError):return set()
def discovery_key(c):
    return (url(c.get("discovery_url") or c.get("official_url") or ""),
            norm(c.get("name")),tuple(sorted(c.get("matched_dates") or [])),
            c.get("date_start"),c.get("date_end"))
def nav_only(c):
    name=norm(c.get("name"));p=urlsplit(c.get("discovery_url") or "")
    path=p.path.lower().rstrip("/")
    exact={"イベント情報","イベント検索","イベントカレンダーを見る","イベント一覧","年間イベントガイド","ホーム","ホームページ","トップページ","子育て","文化スポーツ","メニュー","観光情報","ニュース","お知らせ","記事一覧","公式サイト","すべて見る","もっと見る","お問い合わせ","施設紹介","イベント掲載希望の方はこちら","イベント情報を見る","リンク集","交通アクセス","地図","地域情報"}
    if name in {norm(x) for x in exact} and not c.get("matched_dates") and not c.get("date_start"):return True
    if not c.get("matched_dates") and not c.get("date_start") and re.search(r"/(index(?:\.html?)?|event|events|search|calendar|category|sitemap|guide|link|links|access|contact)(?:/)?$",path):
        return bool(len(name)<25 or re.search(r"一覧|カレンダー|検索|カテゴリ|アクセス|サイト|情報",name))
    return False

def load_published(root):
    manifest=read(root/"manifest.json")
    rows=[]; decisions=[]
    weekend_days=set()
    for w in manifest["weekends"]:
        sat=date.fromisoformat(w["sat"]);sun=date.fromisoformat(w["sun"])
        weekend_days.update({str(sat),str(sun)})
    weekend_days.update(h["date"] for h in manifest.get("holidays",[]))
    # A current manifest may use date-ranges for ongoing events; data identity
    # must still be matched by URL+title, not by URL alone.
    for w in manifest["weekends"]:
        meta=read(root/w["file"])
        group=list(meta.get("events") or [])
        for shard in meta.get("event_files") or []:group+=read(root/shard)
        if len(group)!=w["count"]:raise ValueError("Published shard count mismatch "+w["sat"])
        for e in group:rows.append({"week":w["sat"],**e})
        decpath=root/(w["sat"]+"-decisions.json")
        if decpath.exists():
            for d in read(decpath).get("decisions",[]):decisions.append({"week":w["sat"],**d})
    return manifest,rows,decisions,weekend_days

def triage(pool,published,decisions,days):
    by_url=defaultdict(list)
    for e in published:
        for key in ("official_url","url"):
            u=url(e.get(key))
            if u:by_url[u].append(e)
    dec_by_url=defaultdict(list)
    for d in decisions:
        for v in d.get("evidence") or []:
            u=url(v.get("url"))
            if u:dec_by_url[u].append(d)
    seen={}
    result=[]
    for c in pool:
        cid=c["candidate_id"];label=c.get("name","")
        u=url(c.get("official_url") or c.get("discovery_url"))
        matches=by_url.get(u,[])
        explicit=actual_dates(c)
        calendar=set(c.get("matched_dates") or [])
        reason="";classification="";ref=[]
        key=discovery_key(c)
        if key in seen:
            classification,reason="duplicate_discovery_observation","Same title, URL and date evidence as another harvested link; not a second separate event"
            ref=[seen[key]]
        elif explicit and not (explicit & days):
            classification,reason="dated_out_of_calendar_scope","Verified structured date range does not intersect published weekend/weekday-holiday target"
        else:
            strong=[m for m in matches if near_name(label,m.get("name")) and
                    (not explicit or bool(explicit&actual_dates(m))) and
                    (not calendar or bool(calendar&actual_dates(m)))]
            if strong:
                classification,reason="published_individual_identity_match","Same official URL and compatible event name; source/date needs no new record for this identity"
                ref=[m.get("id") for m in strong[:5]]
            elif nav_only(c):
                classification,reason="navigation_or_index_not_event","Index, category, search or general navigation URL without an event date"
            else:
                reviewed=[d for d in dec_by_url.get(u,[]) if near_name(label,d.get("name")) and d.get("decision") in ("excluded","duplicate")]
                if reviewed:
                    classification,reason="previously_reviewed_excluded_or_duplicate","Identical title and primary URL have an existing explicit exclusion/duplicate decision"
                    ref=[str(x.get("candidate_id")) for x in reviewed[:5]]
                elif matches:
                    classification,reason="same_url_different_event_unresolved","A listed event uses the same URL, but title/participation identity is not proven equivalent"
                    ref=[m.get("id") for m in matches[:5]]
                elif explicit&days:
                    classification,reason="dated_official_event_needs_decision","Actual structured event date intersects a target day; individual inclusion/exclusion decision needed"
                elif calendar&days:
                    classification,reason="calendar_day_hint_needs_official_detail","Official calendar associates the page with a target day; individual event date and suitability still need verification"
                elif calendar:
                    classification,reason="calendar_hint_outside_target_or_unresolved","Calendar day is not a target weekend/holiday; page may still describe ongoing dates, needs detail before final exclusion"
                else:
                    classification,reason="undated_link_needs_event_identity_review","Title/link alone does not prove a dated family event, nor prove harmless navigation"
        if key not in seen:seen[key]=cid
        result.append({
            "candidate_id":cid,"name":label,"url":c.get("official_url") or c.get("discovery_url"),
            "source_id":c.get("source_id") or (c.get("discovered_via") or {}).get("source_id"),
            "channel":(c.get("discovered_via") or {}).get("channel"),
            "ward":c.get("ward") or (c.get("discovered_via") or {}).get("ward"),
            "date_start":c.get("date_start"),"date_end":c.get("date_end"),
            "calendar_hints":sorted(calendar),
            "classification":classification,"rationale":reason,"matched_published_or_duplicate_ids":ref,
            "individual_organizer_detail_verified_in_this_audit":False,
            "publication_approved_by_this_audit":False,
        })
    return result

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--evidence-dir",type=Path,required=True)
    p.add_argument("--published-dir",type=Path,required=True)
    p.add_argument("--output-dir",type=Path,required=True)
    args=p.parse_args()
    summary=read(args.evidence_dir/"summary.json")
    pool=read(args.evidence_dir/"candidate_pool.json")
    manifest,events,decisions,days=load_published(args.published_dir)
    assert summary["candidate_links_unverified"]==len(pool)==859
    assert summary["read_only"] is True and summary["publishable"] is False
    rows=triage(pool,events,decisions,days)
    assert len(rows)==len(pool) and len(set(x["candidate_id"] for x in rows))==len(pool)
    totals=Counter(x["classification"] for x in rows)
    unresolved=[x for x in rows if x["classification"] in (
        "dated_official_event_needs_decision","calendar_day_hint_needs_official_detail",
        "same_url_different_event_unresolved","undated_link_needs_event_identity_review",
        "calendar_hint_outside_target_or_unresolved")]
    priority={k:i for i,k in enumerate(("dated_official_event_needs_decision",
                "calendar_day_hint_needs_official_detail","same_url_different_event_unresolved",
                "calendar_hint_outside_target_or_unresolved","undated_link_needs_event_identity_review"))}
    unresolved.sort(key=lambda x:(priority[x["classification"]],x.get("date_start") or
        (x["calendar_hints"][0] if x["calendar_hints"] else "9999"),x.get("ward") or "",x["candidate_id"]))
    report={
      "kind":"per_link_reconciliation_triage_not_a_full_candidate_coverage_claim",
      "as_of_jst":summary["as_of_jst"],"baseline_sha":summary["base_data_production_sha"],
      "published_manifest_generated":manifest["generated"],
      "published_event_rows":len(events),"published_decision_rows":len(decisions),
      "input_candidate_links":len(pool),"classified_input_rows":len(rows),
      "classification_totals":dict(sorted(totals.items())),
      "priority_individual_review_remaining":len(unresolved),
      "unique_unresolved_discovery_urls":len({url(x["url"]) for x in unresolved}),
      "required_source_failures":summary.get("required_source_failures_outstanding") or
                                  summary.get("required_source_failures") or [],
      "record_completeness":"every link triaged, individual event verification NOT done for unresolved cases",
      "publication_permitted":False,
      "no_auto_discard":"calendar hints, same-URL distinct subevents, undated titles require source confirmation",
      "next_actions":["Read each dated or official calendar event detail","Confirm date, organizer, venue, booking and child-fit",
        "Compare with published event by normalized name, venue and date", "Assign final published/excluded/duplicate decision",
        "Do not publish until strict staging tests and existing production data-only approval"],
    }
    args.output_dir.mkdir(parents=True,exist_ok=True)
    (args.output_dir/"all_859_triage.json").write_text(json.dumps(rows,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    (args.output_dir/"summary.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    (args.output_dir/"priority_review.json").write_text(json.dumps(unresolved,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    print(json.dumps(report,ensure_ascii=False,indent=2))

if __name__=="__main__":main()
