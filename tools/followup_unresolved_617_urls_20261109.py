#!/usr/bin/env python3
"""Read-only bounded detail crawl for all still-unresolved source URLs.

This crawler is evidence gathering, not a decision engine.  A title, date
mention or HTTP 200 can never certify an event, and HTTP 403 is NEVER zero.
"""
import argparse
import concurrent.futures
from collections import Counter,defaultdict
from datetime import datetime,timezone,timedelta
from html.parser import HTMLParser
import hashlib,json,re,threading
from pathlib import Path
from urllib.parse import urlsplit
from urllib.request import Request,urlopen
from urllib.error import HTTPError,URLError
from http_source_diagnostics import (diagnostic_for_http_error, suggested_official_index, official_index_fallback_proof)

MAX_BYTES=750000
DATE_PAT=re.compile(r"(?:20[0-3]\d|令和[0-9０-９]{1,3})\s*[年./-]\s*(?:1[012]|[1-9])\s*[月./-]\s*(?:[0-3]?\d)\s*日?|(?:11|12)\s*月\s*(?:[0-3]?\d)\s*日|(?:11|12)\s*[/.-]\s*(?:[0-3]?\d)")
TARGET_PAT=re.compile(r"(?:2026\s*[年./-])?\s*(?:11\s*[月./-]\s*(?:7|8|14|15|21|22|23|28|29)|12\s*[月./-]\s*(?:5|6|12|13))\s*日?(?!\d)")
CHILD_PAT=re.compile(r"子ども|こども|キッズ|親子|幼児|小学生|工作|ワークショップ|体験|動物|遊び|ファミリー|フリーマーケット|祭り|フェスタ|マルシェ")
class VisibleText(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True);self.skip=0;self.parts=[];self.title=[];self.in_title=False
    def handle_starttag(self,tag,attrs):
        if tag in ("script","style","noscript","svg"):self.skip+=1
        if tag=="title":self.in_title=True
    def handle_endtag(self,tag):
        if tag in ("script","style","noscript","svg"):self.skip=max(0,self.skip-1)
        if tag=="title":self.in_title=False
    def handle_data(self,data):
        if self.skip:return
        s=" ".join(data.split())
        if s:
            if self.in_title:self.title.append(s)
            self.parts.append(s)
def fetch(url,host_guard):
    host=urlsplit(url).hostname or ""
    sem=host_guard[host]
    with sem:
        try:
            req=Request(url,headers={
              "User-Agent":"TokyoFamilyEventsEvidence/1.0 (+github.com/toodataa-ai/tokyo-family-events-ai)",
              "Accept":"text/html,application/xhtml+xml,application/xml;q=0.8,text/plain;q=0.5,*/*;q=0.1"})
            with urlopen(req,timeout=9) as r:
                status=r.status;ct=(r.headers.get("Content-Type") or "").lower()
                final=r.geturl();raw=r.read(MAX_BYTES+1)
            if len(raw)>MAX_BYTES:
                return {"url":url,"status":"page_too_large","http_status":status,"bytes_read":len(raw),"final_url":final}
            if not any(x in ct for x in ("html","text/plain","xml")):
                return {"url":url,"status":"unsupported_content_type","http_status":status,"content_type":ct}
            enc="utf-8"
            m=re.search(r"charset\s*=\s*([a-z0-9_-]+)",ct)
            if m:enc=m.group(1)
            try:rawtext=raw.decode(enc,errors="replace")
            except LookupError:rawtext=raw.decode("utf-8",errors="replace")
            page=VisibleText();page.feed(rawtext)
            text=" ".join(page.parts)
            dates=[]
            for match in list(DATE_PAT.finditer(text))[:90]:
                near=text[max(0,match.start()-100):min(len(text),match.end()+135)]
                dates.append({"date_text":match.group(0),"context":near[:250],
                              "matches_target_day_pattern":bool(TARGET_PAT.search(match.group(0)))})
            return {"url":url,"status":"checked_body_not_individually_verified",
                 "http_status":status,"final_url":final,"content_type":ct,
                 "sha256":hashlib.sha256(raw).hexdigest(),"bytes_read":len(raw),
                 "page_title":" ".join(page.title)[:220],
                 "dates_mentioned":dates[:50],"date_mentions_total":len(dates),
                 "has_target_day_text_hint":bool(TARGET_PAT.search(text)),
                 "has_family_text_hint":bool(CHILD_PAT.search(text)),
                 "visible_text_length":len(text)}
        except HTTPError as e:
            # HTTP 404, 403 and bot/security challenge pages must retain the
            # original *failed* status. Persist only bounded response metadata.
            return {"url":url,"status":"http_error","error":str(e)[:220],
                    **diagnostic_for_http_error(e)}
        except (URLError,TimeoutError,OSError,ValueError,UnicodeError) as e:
            return {"url":url,"status":"error","error":str(e)[:220]}

def safe_public_url(value):
    from ipaddress import ip_address
    try:
        p=urlsplit(value)
        host=p.hostname or ""
        if p.scheme!="https" or not host or p.port not in (None,443) or p.username or p.password:
            return False
        if "." not in host or host.endswith((".local",".internal",".test",".invalid")):
            return False
        try: ip_address(host); return False
        except ValueError: return True
    except ValueError:return False

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--queue",type=Path,required=True)
    p.add_argument("--output-dir",type=Path,required=True)
    p.add_argument("--workers",type=int,default=12)
    a=p.parse_args()
    queue=json.loads(a.queue.read_text(encoding="utf8"))
    assert len(queue)==750
    by_url=defaultdict(list)
    for item in queue:
        value=item.get("url") or ""
        if safe_public_url(value):by_url[value].append(item)
    requests=list(by_url)
    guards=defaultdict(lambda:threading.BoundedSemaphore(2))
    with concurrent.futures.ThreadPoolExecutor(max_workers=min(16,max(1,a.workers))) as ex:
        pages=list(ex.map(lambda u:fetch(u,guards),requests))
    # Re-check the KNOWN official city index once per host (after the
    # failed detail request has released its per-host semaphore). The index
    # is only a discovery fallback, never an event-detail verification.
    fallback_urls = sorted({u for r in pages
                            if r.get("status")=="http_error"
                            for u in [suggested_official_index(
                                r["url"],r.get("http_status"))] if u})
    with concurrent.futures.ThreadPoolExecutor(max_workers=min(3,max(1,a.workers))) as ex:
        fallback_pages=list(ex.map(lambda u:fetch(u,guards),fallback_urls))
    fallback_results={r["url"]:r for r in fallback_pages}
    for record in pages:
        if record.get("status")!="http_error":
            continue
        proof=official_index_fallback_proof(
            record["url"],record.get("http_status"),
            lambda u:fallback_results.get(u,{"status":"error"}))
        if proof is not None:
            record["official_index_fallback"]=proof
    reviewed={r["url"]:r for r in pages}
    linked=[]
    for item in queue:
        r=reviewed.get(item.get("url")) or {"status":"invalid_source_url"}
        linked.append({"candidate_id":item["candidate_id"],"initial_classification":item["classification"],
           "url":item.get("url"),"http_fetch_status":r["status"],
           "target_day_text_hint":r.get("has_target_day_text_hint"),
           "family_text_hint":r.get("has_family_text_hint"),
           "individually_verified":False,"final_inclusion_decision":"pending_organizer_date_venue_family_fit_review"})
    totals=Counter(r["status"] for r in pages)
    report={"kind":"source_page_detail_retrieval_not_event_decision","queue_rows":len(queue),
        "distinct_https_source_urls":len(requests),"pages_by_retrieval_status":dict(totals),
        "http_checked_pages":totals["checked_body_not_individually_verified"],
        "pages_with_target_day_text_hint":sum(bool(r.get("has_target_day_text_hint")) for r in pages),
        "pages_with_family_text_hint":sum(bool(r.get("has_family_text_hint")) for r in pages),
        "source_url_failures":[{
            "url":r["url"],"status":r["status"],
            "http_status":r.get("http_status"),"error":r.get("error"),
            "error_kind":r.get("error_kind"),
            "final_url":r.get("final_url"),
            "response_server":r.get("response_server"),
            "response_title":r.get("response_title"),
            "error_body_sha256":r.get("error_body_sha256"),
            "cloudflare_challenge_detected":r.get("cloudflare_challenge_detected"),
            "official_index_fallback":r.get("official_index_fallback")}
            for r in pages if r["status"]!="checked_body_not_individually_verified"],
        "failed_detail_urls_remain_unverified":True,
        "http_error_signatures_recorded":True,
        "official_index_fallbacks_probed":len(fallback_urls),
        "official_index_fallbacks_reachable":sum(
            r.get("status")=="checked_body_not_individually_verified"
            for r in fallback_pages),
        "events_verified_by_this_scan":0,"final_decisions_by_this_scan":0,"publication_permitted":False,
        "note":"Target date and child-language snippets are only candidate hints. Each independently named event still needs individual official date, venue, family-fit, duplicate and reservation/fee checks. Original 3 Tamemap 403 remain open."}
    a.output_dir.mkdir(parents=True,exist_ok=True)
    for name,obj in (("summary.json",report),("source_pages.json",pages),("per_candidate_url_status.json",linked)):
        (a.output_dir/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    print(json.dumps(report,ensure_ascii=False,indent=2))

if __name__=="__main__":main()
