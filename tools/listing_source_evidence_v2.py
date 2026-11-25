#!/usr/bin/env python3
"""Read-only, bounded listing/pagination/article evidence collector (phase 2).

Discovery is not publication. Keep article/index evidence even when event date
or primary organizer proof is unknown. A failed required page never means zero.
"""
import argparse
import datetime as dt
import hashlib
from html.parser import HTMLParser
import json
import re
from pathlib import Path
from urllib.parse import urljoin, urlsplit, urlunsplit, parse_qs
from urllib.request import urlopen, Request
import xml.etree.ElementTree as ET

SOURCES = {
    "nakano_official_tourism": {
        "start": ["https://www.nakano-kanko.com/event/"],
        "hostname": "www.nakano-kanko.com", "article_pattern": r"^/event-info/event-\d+/?$",
        "listing_path": "/event/", "page_limit": 4, "max_articles": 90, "ward": "中野区",
    },
    "itabashi_times_event": {
        "start": ["https://itabashi-times.com/category/event",
                  "https://itabashi-times.com/category/event/page/2"],
        "hostname": "itabashi-times.com", "article_pattern": r"^/archives/[^/]+\.html$",
        "listing_path": "/category/event", "page_limit": 3, "max_articles": 100, "ward": "板橋区",
        "roundups": True,
    },
    "nerimakanko": {
        "start": ["https://www.nerimakanko.jp/event/"],
        "hostname": "www.nerimakanko.jp", "article_pattern": r"^/event/detail\.php$",
        "listing_path": "/event/search.php", "page_limit": 6, "max_articles": 140, "ward": "練馬区",
        "monthly": True,
    },
}
ROUNDUP = re.compile(r"(?:今週|今月|月の|まとめ|一覧|総まとめ|特集)", re.I)
YM_D = re.compile(r"(?<!\d)(20\d{2})\s*[年/.-]\s*(\d{1,2})\s*[月/.-]\s*(\d{1,2})\s*日?")
MD = re.compile(r"(?<!\d)(\d{1,2})\s*月\s*(\d{1,2})\s*日")
M_ABBR = re.compile(r"(?<!\d)(\d{1,2})\s*/\s*(\d{1,2})(?!\d)")


def canonical(url):
    p = urlsplit(url)
    return urlunsplit((p.scheme.lower(), p.netloc.lower(), p.path.rstrip("/") or "/", p.query, ""))


def sha(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:18]


class Page(HTMLParser):
    """Visible links with nearby preceding heading; excludes script/style text."""
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.links, self.headings, self.texts = [], [], []
        self.anchors, self.heading, self.skip = [], None, 0
        self.rel_next = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag in ("script", "style", "noscript"):
            self.skip += 1
        if self.skip:
            return
        if tag in ("h1", "h2", "h3", "h4"):
            self.heading = []
        if tag == "a":
            # Itabashi cards contain a category link inside an <object> in
            # the outer article anchor. A single current-anchor slot loses
            # every article URL when that nested link starts.
            self.anchors.append({"href": attrs.get("href", ""), "text": [],
                           "heading": self.headings[-1] if self.headings else "",
                           "rel": attrs.get("rel", ""), "title": attrs.get("title", "")})
        if tag == "link" and "next" in attrs.get("rel", "").lower():
            self.rel_next.append(attrs.get("href", ""))

    def handle_data(self, value):
        if self.skip:
            return
        value = " ".join(value.split())
        if not value:
            return
        if self.anchors:
            self.anchors[-1]["text"].append(value)
        if self.heading is not None:
            self.heading.append(value)
        self.texts.append(value)

    def handle_endtag(self, tag):
        if tag in ("script", "style", "noscript"):
            self.skip = max(0, self.skip - 1)
            return
        if self.skip:
            return
        if tag in ("h1", "h2", "h3", "h4") and self.heading is not None:
            title = " ".join(self.heading)
            if title:
                self.headings.append(title)
            self.heading = None
        if tag == "a" and self.anchors:
            a = self.anchors.pop()
            a["label"] = a["title"] or " ".join(a["text"])
            a["nearby_text"] = " ".join(self.texts[-12:])[:900]
            self.links.append(a)


def fetch(url, fetcher=None):
    try:
        if not url.startswith("https://"):
            raise ValueError("non-HTTPS URL")
        if fetcher:
            response = fetcher(url)
            if isinstance(response, tuple):
                status, body = response
            else:
                status, body = 200, response
        else:
            req = Request(url, headers={"User-Agent": "TokyoFamilyEventsAI/phase2-readonly"})
            with urlopen(req, timeout=18) as r:
                status, body = r.status, r.read(3_000_000).decode("utf-8", "replace")
        if status != 200 or not str(body).strip():
            raise ValueError("HTTP/empty response: " + str(status))
        if len(body) > 3_000_000:
            raise ValueError("too large page")
        return {"url": url, "status": "checked", "body": body}
    except Exception as e:
        return {"url": url, "status": "error", "error": str(e)[:180]}


def same_host_link(base, href, cfg):
    url = canonical(urljoin(base, href))
    p = urlsplit(url)
    if p.scheme != "https" or not p.hostname or p.hostname.removeprefix("www.") != cfg["hostname"].removeprefix("www."):
        return None
    return url


def article_title(a):
    label = a["label"]
    if not label or label in ("イベントの詳細へ", "もっと見る", "詳細", "arrow_right"):
        label = a.get("heading", "")
    if label.startswith("もっと見る"):
        label = a.get("heading", "")
    if label in ("過去のイベント", "イベント", "イベント検索", "詳細", "イベント一覧"):
        # Preserve actual event detail URL as an *unverified* lead, rather
        # than using a menu heading as if it were the event name.
        label = "記事名未確定（要確認）"

    return " ".join(label.split())[:240]


def date_hints(text, horizon_year):
    """Conservative date hints, not definitive event dates.

    Without a unique date, manual review is required. Never infer a date from
    crawler time or publication timestamp alone.
    """
    dates = []
    for y, m, d in YM_D.findall(text):
        try:
            day = dt.date(int(y), int(m), int(d)).isoformat()
            if day not in dates:
                dates.append(day)
        except ValueError:
            continue
    if not dates:
        for m, d in MD.findall(text):
            try:
                day = dt.date(horizon_year, int(m), int(d)).isoformat()
                if day not in dates:
                    dates.append(day)
            except ValueError:
                continue
    if not dates:
        for m, d in M_ABBR.findall(text):
            try:
                day = dt.date(horizon_year, int(m), int(d)).isoformat()
                if day not in dates:
                    dates.append(day)
            except ValueError:
                continue
    return dates[:40]


def month_urls(cfg, start, end):
    if not cfg.get("monthly"):
        return []
    month = start.replace(day=1)
    out = []
    while month <= end:
        out.append(f"https://www.nerimakanko.jp/event/search.php?month={month:%Y-%m}")
        month = (month.replace(day=28) + dt.timedelta(days=4)).replace(day=1)
    return out


def next_pages(page, base, cfg):
    """Only explicit pagination controls, never arbitrary /page/N guessing."""
    items = []
    current = urlsplit(base)
    for a in page.links:
        u = same_host_link(base, a["href"], cfg)
        if not u:
            continue
        p = urlsplit(u)
        label = a["label"].lower()
        explicit = ("next" in a["rel"].lower() or label in ("次へ", "次のページ", "次", ">", "»", "2", "3", "4", "5", "もっと見る") or "次へ" in label)
        if not explicit:
            continue
        if cfg["hostname"] == "itabashi-times.com":
            if re.fullmatch(r"/category/event/page/\d+", p.path):
                items.append(u)
        elif cfg["hostname"] == "www.nakano-kanko.com":
            if p.path.startswith("/event/page/") or (p.path == "/event/" and "paged=" in p.query):
                items.append(u)
        elif cfg["hostname"] == "www.nerimakanko.jp":
            if p.path.endswith("search.php") and parse_qs(p.query).get("month") == parse_qs(current.query).get("month"):
                if any(x in parse_qs(p.query) for x in ("page", "p", "offset")):
                    items.append(u)
    for href in page.rel_next:
        u = same_host_link(base, href, cfg)
        if u:
            items.append(u)
    return list(dict.fromkeys(items))


def extract_articles(page, base, cfg):
    results = []
    for a in page.links:
        u = same_host_link(base, a["href"], cfg)
        if not u or not re.fullmatch(cfg["article_pattern"], urlsplit(u).path):
            continue
        title = article_title(a)
        if not title or len(title) < 5:
            continue
        results.append((u, title, a["nearby_text"]))
    return results


def rss_article_fallback(source_id, *, fetcher=None):
    """Supplemental candidate discovery when Itabashi HTML has no usable article links.

    RSS is incomplete historical coverage. Never upgrades a broken listing
    into an audited success; the original failure must remain visible.
    """
    if source_id != "itabashi_times_event":
        return [], []
    root = "https://itabashi-times.com/category/event/feed/"
    records, failures, seen = [], [], set()
    for url in (root, root + "?paged=2"):
        r = fetch(url, fetcher=fetcher)
        if r["status"] != "checked":
            failures.append({"url": url, "error": "supplemental RSS unavailable: " + r["error"]})
            continue
        try:
            # Some WordPress RSS endpoints prepend a BOM or blank line to
            # the XML declaration. Ignore only leading whitespace, never
            # repair malformed XML or waive missing feed items.
            tree = ET.fromstring(r["body"].lstrip("\ufeff \t\r\n"))
            items = tree.findall("./channel/item")
            if not items:
                raise ValueError("RSS channel has no event entries")
            for item in items:
                link = (item.findtext("link") or "").strip()
                title = " ".join((item.findtext("title") or "").split())
                link = same_host_link(url, link, SOURCES[source_id])
                if not link or not re.fullmatch(SOURCES[source_id]["article_pattern"], urlsplit(link).path):
                    continue
                if not title or link in seen:
                    continue
                records.append((link, title, title))
                seen.add(link)
        except (ET.ParseError, ValueError) as e:
            failures.append({"url": url, "error": "invalid or empty RSS: " + str(e)})
    return records, failures


def crawl_source(source_id, start, end, *, fetcher=None):
    cfg = SOURCES[source_id]
    queue = [(u, True) for u in cfg["start"] + month_urls(cfg, start, end)]
    seen_pages, links, failures, pages = set(), {}, [], []
    max_pages = cfg["page_limit"] * max(1, len(queue))
    while queue:
        url, required = queue.pop(0)
        if url in seen_pages:
            continue
        if len(seen_pages) >= max_pages:
            failures.append({"url": url, "error": "pagination exceeds audited page limit"})
            break
        seen_pages.add(url)
        result = fetch(url, fetcher)
        pages.append({"url": url, "status": result["status"], "required": required})
        if result["status"] != "checked":
            failures.append({"url": url, "error": result["error"]})
            continue
        p = Page()
        p.feed(result["body"])
        entries = extract_articles(p, url, cfg)
        # A 200 response with navigation but zero articles can be bot blocking,
        # wrong-domain absolute links or a changed template, never an empty success.
        pages[-1]["links_seen"] = len(p.links)
        pages[-1]["article_links_seen"] = len(entries)
        pages[-1]["event_like_href_examples"] = [a.get("href", "")[:190] for a in p.links
                              if "archive" in a.get("href", "") or "event" in a.get("href", "")][:6]
        if not entries:
            failures.append({"url": url, "error": "no event article links: template or selector changed",
                             "links_seen": len(p.links),
                             "event_like_href_examples": pages[-1]["event_like_href_examples"]})
        for article_url, name, nearby in entries:
            if article_url not in links:
                links[article_url] = {"name": name, "snippet": nearby, "listed_on": [url]}
            elif url not in links[article_url]["listed_on"]:
                links[article_url]["listed_on"].append(url)
        for nxt in next_pages(p, url, cfg):
            if nxt not in seen_pages and nxt not in [x[0] for x in queue]:
                queue.append((nxt, True))
    # A valid HTML listing with no recognized article links is not zero
    # events. Use RSS as *additional discovery evidence* while keeping
    # HTML selector/pagination failures and non-exhaustive scope explicit.
    if source_id == "itabashi_times_event" and not links:
        extras, rss_failures = rss_article_fallback(source_id, fetcher=fetcher)
        failures.extend(rss_failures)
        for article_url, name, nearby in extras:
            links[article_url] = {"name": name, "snippet": nearby,
                                  "listed_on": ["https://itabashi-times.com/category/event/feed/"]}
        if extras:
            failures.append({"url": cfg["start"][0],
                             "error": "RSS recovery is partial evidence, not complete HTML listing coverage"})
    if len(links) > cfg["max_articles"]:
        failures.append({"url": cfg["start"][0], "error": "article quota exceeded (unreviewed pages)"})
    articles, candidates, child_urls, detail_errors = [], [], {}, []
    for u, item in list(links.items())[:cfg["max_articles"]]:
        document = fetch(u, fetcher)
        evidence = {"url": u, "status": document["status"], "source_pages": item["listed_on"]}
        if document["status"] != "checked":
            detail_errors.append({"url": u, "error": document["error"]})
            article = None
        else:
            article = Page()
            article.feed(document["body"])
            evidence["title"] = item["name"]
            evidence["links_checked"] = len(article.links)
            if not item["name"] or item["name"] in ("過去のイベント", "イベント検索", "記事名未確定（要確認）"):
                item["name"] = next((h for h in article.headings if len(h) >= 5 and
                                     h not in ("イベント", "過去のイベント", "イベント検索")),
                                    "記事名未確定（要確認）")
            evidence["title"] = item["name"]
        articles.append(evidence)
        is_index = bool(cfg.get("roundups") and ROUNDUP.search(item["name"]))
        # Use only event heading/listing title for date leads; article dates can
        # include registration deadlines and publication dates.
        dates = date_hints(item["name"], start.year)
        if not dates and cfg["hostname"] == "www.nerimakanko.jp":
            dates = date_hints(item["snippet"].split("日時")[-1][:160], start.year) if "日時" in item["snippet"] else []
        if not dates and article and cfg["hostname"] == "www.nakano-kanko.com":
            text = " ".join(article.texts)
            match = re.search(r"(?:イベント期間|開催日)\s*((?:20\d{2}\s*年\s*)?\d{1,2}\s*月\s*\d{1,2}\s*日(?:.{0,18}?\d{1,2}\s*月\s*\d{1,2}\s*日)?)", text)
            dates = date_hints(match.group(1), start.year) if match else []
        entry = {
            "candidate_id": source_id + "-" + sha(u), "source_id": source_id,
            "name": item["name"], "ward": cfg["ward"],
            "discovery_url": u, "source_pages": item["listed_on"],
            "candidate_type": "collection_index" if is_index else "event_lead",
            "date_hints": dates, "date_verified": False,
            "detail_status": document["status"],
            "primary_source_verified": False,
            "publication_approved": False,
        }
        if is_index and article:
            child = []
            for x, name, _ in extract_articles(article, u, cfg):
                if x != u and x not in child:
                    child.append(x)
                if len(child) > cfg["max_articles"]:
                    detail_errors.append({"url": u, "error": "roundup expansion exceeded bound"})
                    break
            entry["roundup_child_urls"] = child
            child_urls[u] = child
        candidates.append(entry)
    # Collection articles are indexes, not independent festival subprogram cards.
    # Linked child articles found only in roundups must be indexed separately.
    indexed = {x["discovery_url"] for x in candidates}
    for parent, children in child_urls.items():
        for u in children:
            if u in indexed:
                continue
            candidates.append({"candidate_id": source_id + "-" + sha(u),
                               "source_id": source_id, "name": "まとめ記事内の候補（詳細未検証）",
                               "ward": cfg["ward"], "discovery_url": u, "source_pages": [parent],
                               "candidate_type": "roundup_child_lead", "date_hints": [],
                               "date_verified": False, "detail_status": "unreviewed",
                               "primary_source_verified": False,
                               "publication_approved": False})
            indexed.add(u)
    return {
        "schema_version": 1, "source_id": source_id,
        "status": "checked" if not failures and not detail_errors else "source_error",
        "horizon": [str(start), str(end)],
        "candidate_count": len(candidates),
        "listing_pages_checked": pages,
        "detail_pages_checked": articles,
        "candidates": candidates, "failures": failures + detail_errors,
        "retrieval_complete": not failures and not detail_errors,
        "all_candidates_unapproved": True, "read_only": True,
        "note": "Only indexed pages; no claim to all historical articles or page combinations.",
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--published-dir", type=Path, required=True)
    ap.add_argument("--source", choices=list(SOURCES) + ["all"], default="all")
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()
    try:
        try:
            from .source_coverage_reconcile import load_published
        except ImportError:
            from source_coverage_reconcile import load_published
        s = load_published(args.published_dir)
        start, end = dt.date.fromisoformat(s["start"]), dt.date.fromisoformat(s["end"])
        sources = list(SOURCES) if args.source == "all" else [args.source]
        result = {"schema_version": 1, "horizon": [str(start), str(end)], "read_only": True,
                  "sources": [crawl_source(sid, start, end) for sid in sources]}
    except (ValueError, OSError, KeyError) as exc:
        result = {"schema_version": 1, "read_only": True, "status": "error", "error": str(exc)}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({s["source_id"]: {"status": s["status"], "candidates": s["candidate_count"],
          "failures": len(s["failures"])} for s in result.get("sources", [])}, ensure_ascii=False))
    return 0 if result.get("sources") and all(s["status"] == "checked" for s in result["sources"]) else 1


if __name__ == "__main__":
    raise SystemExit(main())
