#!/usr/bin/env python3
"""Collect actual holiday-after discovery evidence; fail closed, never publish.

Use the released policy's expanded plan. This tool creates an auditable pool of
unverified candidate links, official schedule rows, and per-request HTTP logs.
Nothing written here is a publishable event or a completed decision.
"""
import argparse
import concurrent.futures
import datetime as dt
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import sys
import time
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urljoin, urlsplit
from urllib.request import Request, urlopen
import xml.etree.ElementTree as ET

from http_source_diagnostics import diagnostic_for_http_error, diagnostic_for_html_challenge
from nerima_annual_resolver import resolve_annual_schedule_urls
from official_schedule_discovery import extract_candidates
from nerima_forest_schedule import parse_schedule as parse_nerima_forest_schedule
from sankaku_event_listing import parse_listing as parse_sankaku_listing
from tamemap_calendar import calendar_leads as tamemap_calendar_leads

JST = dt.timezone(dt.timedelta(hours=9))
WARDS = [
    ("千代田区", "www.city.chiyoda.lg.jp"), ("中央区", "www.city.chuo.lg.jp"),
    ("港区", "www.city.minato.tokyo.jp"), ("新宿区", "www.city.shinjuku.lg.jp"),
    ("文京区", "www.city.bunkyo.lg.jp"), ("台東区", "www.city.taito.lg.jp"),
    ("墨田区", "www.city.sumida.lg.jp"), ("江東区", "www.city.koto.lg.jp"),
    ("品川区", "www.city.shinagawa.tokyo.jp"), ("目黒区", "www.city.meguro.tokyo.jp"),
    ("大田区", "www.city.ota.tokyo.jp"), ("世田谷区", "www.city.setagaya.lg.jp"),
    ("渋谷区", "www.city.shibuya.tokyo.jp"), ("中野区", "www.city.tokyo-nakano.lg.jp"),
    ("杉並区", "www.city.suginami.tokyo.jp"), ("豊島区", "www.city.toshima.lg.jp"),
    ("北区", "www.city.kita.lg.jp"), ("荒川区", "www.city.arakawa.tokyo.jp"),
    ("板橋区", "www.city.itabashi.tokyo.jp"), ("練馬区", "www.city.nerima.tokyo.jp"),
    ("足立区", "www.city.adachi.tokyo.jp"), ("葛飾区", "www.city.katsushika.lg.jp"),
    ("江戸川区", "www.city.edogawa.tokyo.jp"),
]
PHRASES = [
    "子ども 親子 キッズ イベント ワークショップ 体験",
    "祭り フェス マルシェ 文化 展示 無料",
    "鉄道 動物 科学 防災 消防 スタンプラリー",
]
HOLIDAY_PHRASES = (
    "祝日 子ども 親子 キッズ 体験 ワークショップ",
    "文化の日 イベント 祭り フェス ステージ 無料",
    "施設 博物館 美術館 公園 図書館 特別イベント 家族",
)

EVENT_WORDS = re.compile(
    r"祭|フェス|イベント|体験|ワークショップ|展示|展覧|子ども|こども|"
    r"キッズ|親子|無料|鉄道|電車|マルシェ|科学|スタンプラリー|"
    r"スポーツ|企画展|音楽|花火|動物|博物館|美術館|文化祭|演奏|ハロウィン"
    r"|festival|event|workshop", re.I
)
MAX_BYTES = 2_000_000
MAX_LINKS = 100
USER_AGENT = "TokyoFamilyEventsEvidence/1.0 (+github.com/toodataa-ai/tokyo-family-events-ai)"


class VisibleLinks(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.links = []
        self.active = None
        self.title = []
        self.in_title = False
        self.skip = 0

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style"):
            self.skip += 1
        if tag == "title":
            self.in_title = True
        if tag == "a":
            self.active = {"href": dict(attrs).get("href", ""), "name": ""}

    def handle_data(self, data):
        if self.in_title:
            self.title.append(data)
        if self.active is not None and not self.skip:
            self.active["name"] += data

    def handle_endtag(self, tag):
        if tag in ("script", "style"):
            self.skip = max(0, self.skip - 1)
        if tag == "title":
            self.in_title = False
        if tag == "a" and self.active is not None:
            self.active["name"] = " ".join(self.active["name"].split())[:150]
            self.links.append(self.active)
            self.active = None


def now():
    return dt.datetime.now(JST).isoformat(timespec="seconds")


def digest(value):
    return hashlib.sha256(value.encode("utf-8")).hexdigest()[:16]


def html_links(body, source_url):
    p = VisibleLinks()
    p.feed(body)
    seen, out = set(), []
    for item in p.links:
        label = item["name"]
        if len(label) < 5 or not EVENT_WORDS.search(label):
            continue
        url = urljoin(source_url, item["href"])
        if urlsplit(url).scheme != "https" or url in seen:
            continue
        seen.add(url)
        out.append({"candidate_id": "link-" + digest(label + "|" + url),
                    "name": label, "discovery_url": url})
        if len(out) >= MAX_LINKS:
            break
    return " ".join(p.title).strip()[:180], out


class TamemapNewArrivalHTML(HTMLParser):
    """Visible new-arrival headings with optional uploader label.

    The event cards may be clickable via JavaScript without usable anchor URLs.
    A new posting is only a lead; its relative posting age is NOT an event date.
    """
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.entries = []
        self.in_heading = False
        self.heading_parts = []
        self.skip = 0
        self.awaiting_poster = False
        self.detail_path = None

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style"):
            self.skip += 1
        if tag == "a" and not self.skip:
            attrs = dict(attrs)
            # Read only the site's literal navigation target; never execute JS.
            clicked = re.fullmatch(r"\s*addCommunityUrlClicked\(['\"](/1311401/event/\d+)['\"]\)\s*;?\s*",
                                   attrs.get("onclick", ""))
            href = attrs.get("href", "")
            self.detail_path = (clicked[1] if clicked else
                                href if re.fullmatch(r"/1311401/event/\d+", href) else None)
        if tag == "h3" and not self.skip:
            self.heading_parts = []
            self.in_heading = True

    def handle_data(self, data):
        if self.skip:
            return
        text = " ".join(data.split())
        if not text:
            return
        if self.in_heading:
            self.heading_parts.append(text)
        elif self.awaiting_poster and self.entries:
            found = re.search(r"(?:投稿者|投稿団体)\s*[:：]\s*(.+)", text)
            if found:
                self.entries[-1]["poster"] = found.group(1).strip()[:110]
                self.awaiting_poster = False

    def handle_endtag(self, tag):
        if tag in ("script", "style"):
            self.skip = max(0, self.skip - 1)
        if tag == "a":
            self.detail_path = None
        if tag == "h3" and self.in_heading:
            name = " ".join(self.heading_parts).strip()
            if name and name not in ("イベントの新着一覧", "イベント情報", "地域イベント情報"):
                self.entries.append({"name": name[:240], "detail_path": self.detail_path})
                self.awaiting_poster = True
            self.in_heading = False
            self.heading_parts = []


def tamemap_new_arrival_leads(body, url):
    """Discover unverified *title* leads; publication requires primary detail."""
    parsed = urlsplit(url)
    if (parsed.scheme != "https" or parsed.hostname != "pc.tamemap.net" or
            parsed.path != "/1311401/new_arrival"):
        raise ValueError("Tamemap newest-post feed URL not allowed")
    if not re.search(r"イベントの新着一覧|イベント新着一覧", body):
        raise ValueError("not a Tamemap new-arrival event listing")
    html = TamemapNewArrivalHTML()
    html.feed(body)
    if not html.entries:
        raise ValueError("Tamemap new-arrival page has no visible event titles")
    # Do not conflate different cards with identical titles but different
    # uploaders; if no uploader is known, distinguish repeated positions.
    counts, candidates = {}, []
    for item in html.entries[:100]:
        name, poster = item["name"], item.get("poster", "")
        identity = name + "|" + poster
        counts[identity] = counts.get(identity, 0) + 1
        suffix = "|" + str(counts[identity]) if counts[identity] > 1 else ""
        detail = "https://pc.tamemap.net" + item["detail_path"] if item.get("detail_path") else None
        candidates.append({
            "candidate_id": "tamemap-newarrival-" + (item["detail_path"].rsplit("/", 1)[1] if detail else digest(identity + suffix)),
            "name": name, "poster": poster, "discovery_url": detail or url,
            "source_page": url, "detail_link_observed": bool(detail),
            "source_id": "tamemap_nakano", "candidate_type": "new_arrival_title_lead",
            "date_unverified": True, "matched_dates": [],
            "primary_source_verified": False, "publication_approved": False,
            "review_required": "投稿本文の詳細・開催日・会場・主催者一次情報を個別に要確認。新着日時を開催日に使用しない。"
        })
    return candidates


def suginami_official_event_links(body, source_url):
    """Extract every official event ID, not just keyword-matched titles.

    The unfiltered daily calendar contains event rows and complete multi-day
    ranges. The monthly view is truncated; a successful HTTP 200 alone does
    not establish completeness.
    """
    if "イベントカレンダー" not in body:
        raise ValueError("not a Suginami event calendar")
    parser = VisibleLinks()
    parser.feed(body)
    events = {}
    for link in parser.links:
        url = urljoin(source_url, link["href"])
        m = re.fullmatch(r"https://www\.city\.suginami\.tokyo\.jp/s\d+/event/(\d+)\.html", url)
        if not m:
            continue
        raw_title = link["name"].replace("\u00a0", " ")
        name = re.split(r"\s+20\d\d年", raw_title, maxsplit=1)[0].strip()
        if not name:
            raise ValueError("official event link missing title: " + url)
        events[m.group(1)] = {
            "candidate_id": "suginami-official-" + m.group(1),
            "name": name, "discovery_url": url, "official_url": url,
            "source_id": "suginami_calendar_all"
        }
    return list(events.values())


def fetch_url(url, fetcher=None, attempts=2):
    """Return real retrieval evidence. A transport success is NOT event verification."""
    evidence = {"url": url, "checked_at": now(), "status": "error"}
    if urlsplit(url).scheme != "https":
        evidence["error"] = "non-HTTPS source not permitted"
        return evidence
    for attempt in range(attempts):
        try:
            if fetcher is not None:
                status, raw, final_url, content_type = fetcher(url)
            else:
                request = Request(url, headers={
                    "User-Agent": USER_AGENT, "Accept-Language": "ja,en;q=0.5"})
                with urlopen(request, timeout=18) as resp:
                    status, raw, final_url, content_type = (
                        resp.status, resp.read(MAX_BYTES + 1),
                        resp.geturl(), resp.headers.get("Content-Type", ""))
            if status != 200 or len(raw) > MAX_BYTES or not raw.strip():
                raise ValueError("empty, truncated or non-200 response")
            if urlsplit(final_url).scheme != "https":
                raise ValueError("redirected to non-HTTPS")
            challenge = diagnostic_for_html_challenge(raw, final_url, status, content_type)
            if challenge is not None:
                return {"url": url, "checked_at": now(), "status": "error",
                        "error": "security challenge response is not source content",
                        **challenge}
            charset = "cp932" if "shift_jis" in content_type.lower() else "utf-8"
            try:
                body = raw.decode(charset)
            except UnicodeDecodeError:
                body = raw.decode("cp932")
            # Never carry error headers from a previously failed retry into a
            # successful 200. Only the final successful body is authoritative.
            return {"url": url, "checked_at": now(), "status": "checked",
                    "http_status": status, "final_url": final_url,
                    "content_type": content_type,
                    "bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest(),
                    "body": body}
        except (HTTPError, URLError, OSError, ValueError, UnicodeError, TimeoutError) as error:
            # Each attempt owns its own status. A final transport/parse failure
            # must not inherit an earlier 404/403 or trigger its fallback path.
            evidence = {"url": url, "checked_at": now(), "status": "error",
                        "error": str(error)[:350]}
            if isinstance(error, HTTPError):
                # Capture at most 4 KiB of *response metadata/signature*;
                # do not retain the untrusted raw error HTML or discard 404s.
                evidence.update(diagnostic_for_http_error(error))
            if attempt + 1 < attempts:
                time.sleep(0.4 * (attempt + 1))
    return evidence


def public_row(record):
    """Do not accidentally ship page contents or unbounded HTML in evidence."""
    return {key: value for key, value in record.items() if key != "body"}


def rss_items(body, audit=None, ward=None):
    """Filter search-engine topic drift before it becomes a candidate lead.

    A transport-successful RSS channel is not evidence that the search engine
    respected the Tokyo/ward query. Nonmatching titles remain counted in the
    audit as filtered, not silently presented as event leads.
    """
    root = ET.fromstring(body)
    if root.tag != "rss" or root.find("channel") is None:
        raise ValueError("Search endpoint did not return a valid RSS channel")
    out = []
    total, rejected = 0, 0
    for item in root.findall("./channel/item"):
        total += 1
        name = (item.findtext("title") or "").strip()[:150]
        url = (item.findtext("link") or "").strip()
        host = (urlsplit(url).hostname or "").lower()
        japanese_title = bool(re.search(r"[\u3040-\u30ff\u3400-\u9fff]", name))
        geographic_marker = bool(re.search(
            "Tokyo|東京|千代田区|中央区|港区|新宿区|文京区|台東区|墨田区|江東区|品川区|目黒区|大田区|"
            "世田谷区|渋谷区|中野区|杉並区|豊島区|北区|荒川区|板橋区|練馬区|足立区|葛飾区|江戸川区|"
            "池袋|上野|浅草|豊洲|お台場|銀座|荻窪|六本木|石神井|光が丘|"
            "小石川|高円寺|阿佐ヶ谷|自由が丘|錦糸町|蒲田|葛西|赤羽", name, re.I))
        matching_ward_host = any(ward == w and host == official_host
                                 for w, official_host in WARDS)
        search_is_relevant = (matching_ward_host or
                              bool(ward and ward in name) or
                              geographic_marker)
        if (len(name) < 5 or not url.startswith("https://")
                or not EVENT_WORDS.search(name)
                or not (search_is_relevant if ward else (
                    japanese_title or host.endswith(".jp") or geographic_marker))):
            rejected += 1
            continue
        out.append({"candidate_id": "rss-" + digest(name + "|" + url),
                    "name": name, "discovery_url": url})
    if audit is not None:
        audit.update(search_results_total=total,
                     search_results_rejected_irrelevant=rejected,
                     search_results_event_leads=len(out))
    return out[:MAX_LINKS]


HOLIDAY_CALENDAR_ENGINES = (
    ("toshima_daily", "豊島区", "https://www.city.toshima.lg.jp/cgi-bin/event_cal/calendar.cgi?day={D}&month={M}&type=3&year={Y}", "daily"),
    ("arakawa_daily", "荒川区", "https://www.city.arakawa.tokyo.jp/cgi-bin/event_cal_multi/calendar.cgi?day={D}&month={M}&type=3&year={Y}", "daily"),
    ("nerima_monthly", "練馬区", "https://www.city.nerima.tokyo.jp/kankomoyoshi/event/calendar/list_calendar{Y}{MM}.html", "monthly"),
    ("nerima_kids_monthly", "練馬区", "https://www.city.nerima.tokyo.jp/nerimakids/event/calendar/list_calendar{Y}{MM}.html", "monthly"),
    ("edogawa_daily", "江戸川区", "https://www.city.edogawa.tokyo.jp/cgi-bin/event_cal_multi/calendar.cgi?day={D}&month={M}&siteid=6&type=3&year={Y}", "daily"),
)

def holiday_calendar_jobs(holiday):
    """Day-scoped official sources, separate from weekend or generic RSS."""
    day = dt.date.fromisoformat(holiday["date"])
    if day.weekday() > 4 or not holiday.get("requires_independent_23_ward_search"):
        return []
    tokens = {"Y": str(day.year), "M": str(day.month), "MM": f"{day.month:02d}", "D": str(day.day)}
    return [{"kind": "holiday_calendar", "source_id": sid, "ward": ward,
             "holiday": holiday["date"], "calendar_mode": mode, "required": False,
             "url": re.sub(r"\{(Y|M|MM|D)\}", lambda m: tokens[m[1]], template)}
            for sid, ward, template, mode in HOLIDAY_CALENDAR_ENGINES]

class CalendarRowLinks(HTMLParser):
    """Retain date and linked event titles from each monthly calendar table row."""
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.rows, self.row, self.cell, self.link = [], None, None, None
    def handle_starttag(self, tag, attrs):
        if tag == "tr":
            self.row = []
        elif tag in ("td", "th") and self.row is not None:
            self.cell = {"text": [], "links": []}
        elif tag == "a" and self.cell is not None:
            self.link = {"name": [], "href": dict(attrs).get("href", "")}
    def handle_data(self, data):
        if self.cell is not None:
            self.cell["text"].append(data)
        if self.link is not None:
            self.link["name"].append(data)
    def handle_endtag(self, tag):
        if tag == "a" and self.link is not None:
            self.link["name"] = " ".join("".join(self.link["name"]).split())
            self.cell["links"].append(self.link)
            self.link = None
        elif tag in ("td", "th") and self.cell is not None:
            self.cell["text"] = " ".join("".join(self.cell["text"]).split())
            self.row.append(self.cell)
            self.cell = None
        elif tag == "tr" and self.row is not None:
            self.rows.append(self.row)
            self.row = None

def holiday_calendar_candidates(body, source_url, day_text, mode):
    """Official listing gives date *candidates*, not publishable event facts."""
    day = dt.date.fromisoformat(day_text)
    host = urlsplit(source_url).hostname
    if mode == "daily":
        parser = VisibleLinks()
        parser.feed(body)
        marks = (f"{day.year}年{day.month}月{day.day}日",
                 f"{day.year}年{day.month:02d}月{day.day:02d}日")
        raw = [link for link in parser.links
               if any(mark in link["name"].replace(" ", "") for mark in marks)]
    elif mode == "monthly":
        parser = CalendarRowLinks()
        parser.feed(body)
        raw = [link for row in parser.rows if len(row) >= 3
               and re.match(r"^" + str(day.day) + r"日(?:\s|$)", row[0]["text"])
               for link in row[-1]["links"]]
    else:
        raise ValueError("unsupported holiday calendar mode")
    out = {}
    for link in raw:
        event_url = urljoin(source_url, link["href"])
        if urlsplit(event_url).hostname != host or len(link["name"]) < 4:
            continue
        uid = digest(link["name"] + "|" + event_url)
        out[uid] = {"candidate_id": "holiday-official-" + uid,
                    "name": link["name"], "discovery_url": event_url,
                    "official_url": event_url, "matched_dates": [day_text],
                    "date_unverified": True, "calendar_date_hint": day_text,
                    "source_kind": "official_calendar_candidate_only"}
    return list(out.values())


def build_jobs(plan):
    """Each ward has independent cross-search, official entry, and holiday queries."""
    jobs = []
    for ward, host in WARDS:
        jobs.append({"kind": "ward_official", "ward": ward, "url": "https://" + host + "/"})
        for week in plan["weekends"]:
            date = week["sat"].replace("-", "年", 1).replace("-", "月", 1) + "日"
            for phrase in PHRASES:
                query = f"{ward} {date} {phrase}"
                jobs.append({"kind": "ai_cross", "ward": ward, "week": week["sat"],
                             "query": query,
                             "url": "https://www.bing.com/search?format=rss&q=" + quote(query)})
        for holiday in plan.get("holiday_targets", []):
            if holiday.get("requires_independent_23_ward_search"):
                for phrase in HOLIDAY_PHRASES:
                    query = f"{ward} {holiday['date']} {phrase}"
                    jobs.append({"kind": "holiday_ai_cross", "ward": ward,
                                 "holiday": holiday["date"], "query": query,
                                 "url": "https://www.bing.com/search?format=rss&q=" + quote(query)})
    for holiday in plan.get("holiday_targets", []):
        jobs.extend(holiday_calendar_jobs(holiday))
    for source in plan["explicit_source_checks"]:
        for url in source["urls"]:
            jobs.append({"kind": "explicit", "source_id": source["id"],
                         "required": source["required"], "url": url,
                         "target_start": plan["target_start"],
                         "target_end": plan["target_end"],
                         "holiday_dates": [h["date"] for h in plan.get("holiday_targets", [])],
                         "annual_listing_url": source.get("annual_listing_url")})
    return jobs



# Two month-suffixed Nerima calendar routes returned HTTP 404 on 2026-11-09.
# The official monthless pages are observed as HTTP 200 and show Nov 2026
# calendar rows. For a DIFFERENT month, reject the monthless page unless its
# own heading matches the requested year/month; do not fabricate date matches.
NERIMA_HOLIDAY_INDEX_FALLBACKS = {
    "nerima_monthly":
        "https://www.city.nerima.tokyo.jp/kankomoyoshi/event/calendar/list_calendar.html",
    "nerima_kids_monthly":
        "https://www.city.nerima.tokyo.jp/nerimakids/event/calendar/list_calendar.html",
}


def nerima_holiday_calendar_fallback(job, previous, fetcher=None):
    """Return unverified calendar leads, preserving original 404 as an error."""
    fallback = NERIMA_HOLIDAY_INDEX_FALLBACKS.get(job.get("source_id"))
    if (job.get("kind") != "holiday_calendar"
            or previous.get("http_status") != 404
            or not fallback):
        return [], None
    observed = fetch_url(fallback, fetcher)
    proof = {
        "fallback_url": fallback,
        "fallback_status": observed["status"],
        "fallback_http_status": observed.get("http_status"),
        "original_source_status_remains": "error",
        "original_http_status": 404,
        "original_source_url": job["url"],
        "calendar_month_matches_target": False,
        "candidate_count": 0,
        "event_details_verified": False,
        "publication_permitted": False,
        "decision_reconciliation": "pending",
    }
    if observed["status"] != "checked":
        proof["fallback_error"] = observed.get("error", "official index unreachable")
        return [], proof
    day = dt.date.fromisoformat(job["holiday"])
    # The monthless index changes with the current month. Reject any page
    # whose heading does not identify the month containing this target holiday.
    month_label = re.compile(
        rf"{day.year}\s*年\s*0?{day.month}\s*月\s*カレンダー")
    if not month_label.search(observed["body"]):
        proof["fallback_error"] = "official index month mismatch; no candidate may be inferred"
        return [], proof
    proof["calendar_month_matches_target"] = True
    proof["fallback_sha256"] = observed["sha256"]
    try:
        candidates = holiday_calendar_candidates(
            observed["body"], fallback, job["holiday"], job["calendar_mode"])
    except (ValueError, ET.ParseError) as error:
        proof["fallback_error"] = "official calendar parse error: " + str(error)
        return [], proof
    proof["candidate_count"] = len(candidates)
    return candidates, proof


def inspect(job, fetcher=None):
    result = {**job, "checked_at": now(), "status": "error",
              "candidates": []}
    evidence = fetch_url(job["url"], fetcher)
    result.update(public_row(evidence))
    if evidence["status"] != "checked":
        leads, fallback_proof = nerima_holiday_calendar_fallback(job, evidence, fetcher)
        if fallback_proof is not None:
            result["official_calendar_index_fallback"] = fallback_proof
            result["candidates"] = leads
            result["calendar_day_candidate_links"] = len(leads)
            result["candidate_link_count"] = len(leads)
            # The original 404 remains error even when an official index was
            # accessible; candidate links require independent event facts.
            result["status"] = "error"
        return result
    try:
        if job["kind"] in ("ai_cross", "holiday_ai_cross"):
            result["candidates"] = rss_items(evidence["body"], result, ward=job.get("ward"))
        elif job["kind"] == "holiday_calendar":
            result["candidates"] = holiday_calendar_candidates(
                evidence["body"], job["url"], job["holiday"], job["calendar_mode"])
            result["calendar_day_candidate_links"] = len(result["candidates"])
        elif (job.get("source_id") == "tamemap_nakano" and
              urlsplit(job["url"]).path == "/1311401/new_arrival"):
            result["candidates"] = tamemap_new_arrival_leads(evidence["body"], job["url"])
            result["page_title"] = "ためまっぷなかの・新着一覧（投稿候補のみ）"
            result["individually_verified_event_count"] = None
            result["candidate_status"] = "unverified_title_leads"
            result["new_arrival_is_partial_not_calendar_replacement"] = True
        elif (job.get("source_id") == "tamemap_nakano" and
              urlsplit(job["url"]).path.startswith("/1311401/calendar/")):
            result["candidates"] = tamemap_calendar_leads(
                evidence["body"], job["url"],
                dt.date.fromisoformat(job["target_start"]) if job.get("target_start") else None,
                dt.date.fromisoformat(job["target_end"]) if job.get("target_end") else None)
            result["page_title"] = "ためまっぷなかの・月別カレンダー"
            result["candidate_status"] = "unverified_calendar_links"
            result["decision_reconciliation"] = "pending"
        elif job.get("source_id") == "shinjuku_sankaku_hiroba":
            result.update(parse_sankaku_listing(
                evidence["body"], dt.date.fromisoformat(job["target_start"]),
                dt.date.fromisoformat(job["target_end"]), job["url"],
                holiday_dates=job.get("holiday_dates", [])))
            result["page_title"] = "新宿住友ビル三角広場 イベント一覧"
            result["candidate_status"] = "unverified_external_organizer_links"
        elif job.get("source_id") == "suginami_calendar_all":
            result["candidates"] = suginami_official_event_links(evidence["body"], job["url"])
            result["page_title"] = "杉並区公式イベントカレンダー"
            result["official_event_link_count"] = len(result["candidates"])
        elif job.get("source_id") == "nerima_forest_festa_2026":
            # Parse ALL dated rows; a successful fetch is not complete discovery.
            forest = parse_nerima_forest_schedule(
                evidence["body"], dt.date.fromisoformat(job["target_start"]),
                dt.date.fromisoformat(job["target_end"]), job["url"])
            result["candidates"] = forest["candidates"]
            result["candidate_ids"] = forest["candidate_ids"]
            result["candidate_count"] = forest["candidate_count"]
            result["official_row_count"] = forest["official_row_count"]
            result["outside_target_count"] = forest["outside_target_count"]
            result["page_title"] = "ねりまの森こどもフェスタ2026（公式日程表）"
            result["decision_reconciliation"] = "pending"
        else:
            title, links = html_links(evidence["body"], job["url"])
            if not title and not links:
                raise ValueError("HTML had no usable title/event links")
            result["page_title"] = title
            result["candidates"] = links
    except (ValueError, ET.ParseError) as error:
        result["status"] = "error"
        result["error"] = "parse: " + str(error)
    result["candidate_link_count"] = len(result["candidates"])
    return result


def annual_report(job, index_record, fetcher=None):
    """Resolve the actual fiscal page and extract *every* in-horizon festival row."""
    if index_record["status"] != "checked":
        return {"status": "error", "source_id": job["source_id"],
                "error": "official annual index unavailable"}
    r = fetch_url(job["url"], fetcher)
    if r["status"] != "checked":
        return {"status": "error", "source_id": job["source_id"],
                "error": r.get("error", "index unavailable")}
    try:
        # Resolve against plan span; the page itself must identify fiscal year.
        start = dt.date.fromisoformat(job["target_start"])
        end = dt.date.fromisoformat(job["target_end"])
        pages = resolve_annual_schedule_urls(r["body"], start, end)
        extracted, resolved = [], []
        for year, url in pages:
            src = fetch_url(url, fetcher)
            if src["status"] != "checked":
                raise ValueError(f"official fiscal page unavailable: {year}: {src.get('error')}")
            entries = extract_candidates(src["body"], start, end,
                                         fiscal_start_year=year, source_url=url)
            extracted.extend(entries)
            resolved.append({"fiscal_year": year, "resolved_url": url,
                             "row_count": len(entries), "checked_at": src["checked_at"],
                             "sha256": src["sha256"]})
        ids = [c["candidate_id"] for c in extracted]
        if len(ids) != len(set(ids)):
            raise ValueError("duplicate official festival candidate ID")
        return {"status": "checked", "source_id": job["source_id"],
                "official_row_count": len(ids), "resolved_pages": resolved,
                "candidate_ids": ids, "candidates": extracted,
                "decision_reconciliation": "pending"}
    except (OSError, ValueError) as error:
        return {"status": "error", "source_id": job["source_id"],
                "error": str(error)}


def collect(plan, fetcher=None, max_workers=12, supplemental_config=None,
            exception_policy=None):
    if plan.get("status") != "eligible":
        raise ValueError("holiday-after plan is not eligible")
    if plan.get("publication_permitted") is not False:
        raise ValueError("plan must be read-only and non-publishable")
    if len(plan.get("weekends", [])) != 6 or not plan.get("base_data_production_sha"):
        raise ValueError("invalid six-week plan/baseline")
    jobs = build_jobs(plan)
    if len({ward for ward, _ in WARDS}) != 23:
        raise ValueError("duplicate ward labels")
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        rows = list(executor.map(lambda job: inspect(job, fetcher), jobs))
    index_jobs = [job for job in jobs if job.get("annual_listing_url")]
    annual = []
    for job in index_jobs:
        annual.append(annual_report({**job, "target_start": plan["target_start"],
                                      "target_end": plan["target_end"]},
                                    next(r for r in rows if r["url"] == job["url"]), fetcher))
    wards = {}
    for ward, _ in WARDS:
        own = [r for r in rows if r.get("ward") == ward]
        wards[ward] = {
            "total_queries": sum(r["kind"] in ("ai_cross", "holiday_ai_cross") for r in own),
            "successful_queries": sum(r["kind"] in ("ai_cross", "holiday_ai_cross") and r["status"] == "checked" for r in own),
            "official_home_checked": any(r["kind"] == "ward_official" and r["status"] == "checked" for r in own),
            "errors": [{"url": r["url"], "error": r.get("error", "")} for r in own if r["status"] != "checked"]
        }
    required_failures = [{"id": r.get("source_id"), "url": r["url"], "error": r.get("error")}
                         for r in rows if r["kind"] == "explicit" and r["required"] and r["status"] != "checked"]
    deferred_issues, outstanding_failures = [], []
    approved = (exception_policy or {}).get("exceptions") or []
    allowed_run = (exception_policy or {}).get("only_for_run") or {}
    for failure in required_failures:
        record = next((row for row in rows if
                       row.get("source_id") == failure["id"] and
                       row.get("url") == failure["url"]), {})
        scoped = allowed_run.get("as_of_jst") == plan.get("as_of_jst") == "2026-10-19"
        rule = next((x for x in approved if
                     x.get("source_id") == failure["id"] == "tamemap_nakano"
                     and x.get("expected_http_status") == record.get("http_status") == 403
                     and x.get("expected_observed_status") == record.get("status") == "error"
                     and x.get("required_source_stays_enabled") is True), None)
        if scoped and rule and record.get("challenge_detected") is True:
            deferred_issues.append({**failure, "status": "error", "http_status": 403,
                                    "exception_ref": rule["id"],
                                    "checked_at": record["checked_at"],
                                    "response_server": record.get("response_server"),
                                    "challenge_detected": True})
        else:
            outstanding_failures.append(failure)
    source_fallbacks = []
    configured = {row["id"]: row for row in plan.get("explicit_source_checks", [])}
    for source_id, cfg in configured.items():
        ids = cfg.get("fallback_source_ids") or []
        if not ids:
            continue
        primary = [x for x in rows if x.get("kind") == "explicit"
                   and x.get("source_id") == source_id]
        alternatives = [x for x in rows if x.get("kind") == "explicit"
                        and x.get("source_id") in ids]
        primary_failed = bool(primary and any(x["status"] != "checked" for x in primary))
        available = sorted({x["source_id"] for x in alternatives if x["status"] == "checked"})
        source_fallbacks.append({
            "source_id": source_id, "primary_failed": primary_failed,
            "primary_source_errors_preserved": True,
            "alternative_source_ids": ids, "verified_accessible_alternatives": available,
            "status": ("official_alternative_checked_not_primary" if primary_failed and available
                       else "no_fallback_needed" if not primary_failed else "no_alternative_verified"),
            "candidate_publication_approved": False,
            "note": "板橋観光協会の障害を成功扱いせず、区公式の独立した証拠で必要なイベントを別途検証する。"
        })
    ward_failures = [{"ward": ward, **stat} for ward, stat in wards.items()
                     if stat["errors"]]
    annual_failures = [row for row in annual if row["status"] != "checked"]
    holiday_calendar_checks = [
        {"source_id": r["source_id"], "ward": r["ward"], "date": r["holiday"],
         "status": r["status"], "url": r["url"],
         "candidate_count": len(r["candidates"]), "error": r.get("error", ""),
         "official_index_fallback": r.get("official_calendar_index_fallback"),
         "original_status_not_masked": r["status"] != "checked"}
        for r in rows if r["kind"] == "holiday_calendar"
    ]
    raw_candidates = []
    for row in rows:
        for candidate in row["candidates"]:
            raw_candidates.append({**candidate, "discovered_via": {
                "channel": "explicit" if row["kind"] == "explicit" else "ai_cross",
                "source_id": row.get("source_id"),
                "ward": row.get("ward"), "query": row.get("query"),
                "search_url": row["url"]}, "status": "unverified"})
    for annual_item in annual:
        for c in annual_item.get("candidates", []):
            raw_candidates.append({**c, "status": "unverified"})
    supplemental = None
    if supplemental_config is not None:
        from nakano_supplemental_discovery import collect_supplemental
        supplemental = collect_supplemental(plan, supplemental_config, fetcher)
        raw_candidates.extend(supplemental["candidates"])
    unique = {}
    for candidate in raw_candidates:
        identity = candidate.get("candidate_id")
        if identity not in unique:
            unique[identity] = candidate
        else:
            unique[identity].setdefault("other_discoveries", []).append(
                candidate.get("discovered_via", candidate.get("discovery_sources")))
    blockers = []
    if outstanding_failures:
        blockers.append("required_explicit_url_errors")
    if ward_failures:
        blockers.append("incomplete_23_ward_search")
    if annual_failures:
        blockers.append("official_annual_schedule_errors")
    if supplemental and supplemental["supplemental_failures"]:
        blockers.append("supplemental_primary_source_errors")
    # HTTP 200 and candidate discovery do not prove published event facts.
    blockers.append("unverified_candidate_decisions_and_official_event_facts")
    return {
        "summary": {"run_type": "holiday_after_update", "as_of_jst": plan["as_of_jst"],
                    "base_data_production_sha": plan["base_data_production_sha"],
                    "prompt_version": "v1.15", "read_only": True,
                    "publishable": False, "request_count": len(rows),
                    "requests_success": sum(r["status"] == "checked" for r in rows),
                    "required_source_failures": required_failures,
                    "required_source_failures_outstanding": outstanding_failures,
                    "approved_deferred_source_errors": deferred_issues,
                    "nonblocking_known_issues": [
                        {"id": "tamemap_nakano", "classification": "temporarily_deferred_not_checked",
                         "deferred_count": len(deferred_issues)}
                    ] if deferred_issues else [],
                    "wards": wards, "ward_failures": ward_failures,
                    "annual_schedule": [{k: v for k, v in r.items() if k != "candidates"} for r in annual],
                    "holiday_calendar_checks": holiday_calendar_checks,
                    "candidate_links_unverified": len(unique),
                    "supplemental_checked": (supplemental or {}).get("supplemental_success", 0),
                    "supplemental_failures": [
                        {"source_id": x["source_id"], "month": x.get("month"), "error": x.get("error")}
                        for x in (supplemental or {}).get("supplemental_failures", [])
                    ],
                    "tamemap_source_still_required": True,
                    "blockers": blockers},
        "source_fallbacks": source_fallbacks,
        "supplemental_sources": (supplemental or {}).get("source_checks", []),
        "requests": [{k: v for k, v in r.items() if k != "candidates"} for r in rows],
        "candidate_pool": list(unique.values())
    }


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--plan", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--workers", type=int, default=12)
    parser.add_argument("--supplemental-config", type=Path,
                        help="Additive, read-only Nakano official and community sources")
    parser.add_argument("--exception-policy", type=Path,
                        help="Explicit one-run user-approved source-error classification; never upgrades checked")
    args = parser.parse_args(argv)
    plan = json.loads(args.plan.read_text(encoding="utf-8"))
    if not 1 <= args.workers <= 20:
        parser.error("--workers must be 1..20")
    supplemental_config = (json.loads(args.supplemental_config.read_text(encoding="utf-8"))
                           if args.supplemental_config else None)
    exception_policy = (json.loads(args.exception_policy.read_text(encoding="utf-8"))
                        if args.exception_policy else None)
    result = collect(plan, max_workers=args.workers,
                     supplemental_config=supplemental_config,
                     exception_policy=exception_policy)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    for name, payload in result.items():
        (args.output_dir / (name + ".json")).write_text(
            json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in result["summary"].items()
                      if k not in ("wards", "ward_failures", "required_source_failures")},
                     ensure_ascii=False))
    if result["summary"]["blockers"]:
        print("FAIL CLOSED: candidate evidence is NOT verified for publication", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
