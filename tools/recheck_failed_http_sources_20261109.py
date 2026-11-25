#!/usr/bin/env python3
"""Targeted actual HTTP replay of frozen 17 failures + required Tamemap routes.

HTTP errors remain explicit blockers.  Success of a municipal INDEX is
supplemental discovery, never equivalent to the original detail or source.
"""
import argparse
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
import threading
from urllib.parse import urlsplit

from followup_unresolved_617_urls_20261109 import fetch, safe_public_url
from http_source_diagnostics import official_index_fallback_proof, suggested_official_index

TAMEMAP = [
    "https://pc.tamemap.net/1311401/calendar/2026-11?lat=35.7089745&lng=139.6630981&level=5000&locale=ja",
    "https://pc.tamemap.net/1311401/calendar/2026-12?lat=35.7089745&lng=139.6630981&level=5000&locale=ja",
    "https://pc.tamemap.net/1311401/new_arrival?lat=35.7089745&lng=139.6630981&level=5000&locale=ja",
]

def recheck(original_failures, workers=5, fetcher=None):
    prior=[x for x in original_failures if x.get("status")=="http_error"]
    if len(prior)!=17 or Counter(x.get("http_status") for x in prior)!={404:15,403:2}:
        raise ValueError("expected EXACT 17 original HTTP failures: 15 404 and 2 403")
    requests=[x["url"] for x in prior]+TAMEMAP
    if len(set(requests))!=20 or not all(safe_public_url(u) for u in requests):
        raise ValueError("invalid, duplicate, or non-public source URLs")
    host_guard=defaultdict(lambda:threading.BoundedSemaphore(2))
    read=fetcher or (lambda u:fetch(u,host_guard))
    with ThreadPoolExecutor(max_workers=max(1,min(workers,5))) as ex:
        checked=list(ex.map(read,requests))
    found={x["url"]:x for x in checked}
    # This is independent, additive official-index evidence only.
    indexes=sorted({u for r in checked if r.get("status")=="http_error"
                    for u in [suggested_official_index(r["url"],r.get("http_status"))] if u})
    with ThreadPoolExecutor(max_workers=3) as ex:
        supplemental=list(ex.map(read,indexes))
    index_checks={x["url"]:x for x in supplemental}
    rows=[]
    for x in prior:
        r=found[x["url"]]
        proof=official_index_fallback_proof(x["url"],r.get("http_status"),
                   lambda u:index_checks.get(u,{"status":"error"}))
        rows.append({"url":x["url"],"group":"old_detail_link",
            "previous_http_status":x["http_status"],
            "current_http_status":r.get("http_status"),
            "current_retrieval_status":r.get("status"),
            "current_error_kind":r.get("error_kind"),
            "current_response_server":r.get("response_server"),
            "current_response_title":r.get("response_title"),
            "current_error_body_sha256":r.get("error_body_sha256"),
            "final_url":r.get("final_url"),
            "official_index_fallback":proof,
            "original_status_not_masked_by_index":True,
            "individual_event_verified":False})
    for url in TAMEMAP:
        r=found[url]
        rows.append({"url":url,"group":"required_tamemap",
            "previous_http_status":403,
            "current_http_status":r.get("http_status"),
            "current_retrieval_status":r.get("status"),
            "current_error_kind":r.get("error_kind"),
            "current_response_server":r.get("response_server"),
            "current_response_title":r.get("response_title"),
            "current_error_body_sha256":r.get("error_body_sha256"),
            "official_index_fallback":None,
            "original_status_not_masked_by_index":True,
            "individual_event_verified":False})
    current_errors=Counter((r["group"],r["current_http_status"],r["current_retrieval_status"]) for r in rows)
    return {
       "generated_at_jst":datetime.now(timezone(timedelta(hours=9))).isoformat(timespec="seconds"),
       "kind":"fail_closed_http_error_recheck_not_event_completeness",
       "original_detail_errors":17,"required_tamemap_paths":3,
       "rechecked_urls":len(rows),"official_index_urls_rechecked":len(indexes),
       "official_indexes_reachable":sum(
           r["status"]=="checked_body_not_individually_verified" for r in supplemental),
       "summary":[{"group":g,"http_status":s,"retrieval_status":k,"count":n}
                  for (g,s,k),n in sorted(current_errors.items(),key=lambda x:str(x[0]))],
       "responses":rows,
       "index_responses":[{"url":r["url"],"status":r["status"],
                           "http_status":r.get("http_status"),
                           "title":r.get("page_title"),
                           "error_kind":r.get("error_kind")}
                          for r in supplemental],
       "all_event_decisions_unresolved":True,
       "no_source_registry_changes":True,
       "no_bypass_of_cloudflare":True,
       "published_data_modified":False,
       "note":"Official index reachability never changes failed article / Tamemap source status. Publish only after verified individual event decisions.",
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--prior-summary",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    args=p.parse_args()
    original=json.loads(args.prior_summary.read_text(encoding="utf8"))
    data=recheck(original["source_url_failures"])
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(data,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    print(json.dumps({k:v for k,v in data.items() if k not in ("responses","index_responses")},
          ensure_ascii=False,indent=2))

if __name__=="__main__":
    main()
