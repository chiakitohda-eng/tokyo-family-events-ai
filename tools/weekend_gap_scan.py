#!/usr/bin/env python3
"""Read-only weekend gap scanner.

Fetches the seed pages in policy/weekend_gap_sources.json, follows event-looking
links (bounded depth/count), and keeps only pages whose text mentions one of the
target dates. Output is a *candidate worklist* (hits.tsv / hits.json /
summary.json / benchmark.tsv). It never writes event data and never publishes.
Every hit still needs a human/Claude read of the official page before use.
"""
import argparse
import concurrent.futures
import datetime as dt
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import sys
import time
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin, urlsplit, urldefrag
from urllib.request import Request, urlopen

JST = dt.timezone(dt.timedelta(hours=9))
UA = "TokyoFamilyEventsGapScan/1.0 (read-only; github.com/chiakitohda-eng/tokyo-family-events-ai)"
MAX_BYTES = 1_500_000
EVENT_WORDS = re.compile(
    r"祭|フェス|イベント|体験|ワークショップ|展示|展覧|子ども|こども|キッズ|親子|無料|"
    r"マルシェ|科学|スタンプラリー|防災|消防|コンサート|公演|上映|ツアー|周年|お知らせ|"
    r"event|festival|news|calendar", re.I)
SKIP_EXT = re.compile(r"\.(pdf|jpe?g|png|gif|zip|docx?|xlsx?|pptx?|mp4|svg)(\?|$)", re.I)
RANGE_SEP = r"[～~〜\-ー–—‐]|から"


def target_dates(start, days=2):
    s = dt.date.fromisoformat(start)
    return [s + dt.timedelta(days=i) for i in range(days)]


def norm(text):
    text = text.translate(str.maketrans("０１２３４５６７８９／", "0123456789/"))
    return re.sub(r"\s+", " ", text)


def page_matches(text, targets):
    """Return sorted ISO dates from `targets` that the text mentions (single day,
    'M月D日・D日', or a range 'M月D日～M月D日'/'M月D日～D日')."""
    text = norm(text)
    found = set()
    for t in targets:
        m, d, y = t.month, t.day, t.year
        pats = [rf"(?<!\d){m}月\s*{d}日", rf"(?<!\d){m}/{d}(?!\d)", rf"{y}-0?{m}-0?{d}(?!\d)",
                rf"{y}/0?{m}/0?{d}(?!\d)"]
        if any(re.search(p, text) for p in pats):
            found.add(t.isoformat())
    # "7日(土)・8日(日)" right after "M月D日"
    for mt in re.finditer(r"(\d{1,2})月\s*(\d{1,2})日(?:[（(][^）)]{1,3}[）)])?\s*[・、,]\s*(\d{1,2})日", text):
        mo, d1, d2 = int(mt.group(1)), int(mt.group(2)), int(mt.group(3))
        for t in targets:
            if t.month == mo and t.day in (d1, d2):
                found.add(t.isoformat())
    # ranges
    rng = re.compile(
        rf"(?:(\d{{4}})年)?\s*(\d{{1,2}})月\s*(\d{{1,2}})日(?:[（(][^）)]{{1,3}}[）)])?\s*(?:{RANGE_SEP})\s*"
        rf"(?:(?:(\d{{4}})年)?\s*(\d{{1,2}})月)?\s*(\d{{1,2}})日")
    for mt in rng.finditer(text):
        y1, m1, d1, y2, m2, d2 = mt.groups()
        y1 = int(y1) if y1 else targets[0].year
        m1, d1, d2 = int(m1), int(d1), int(d2)
        m2 = int(m2) if m2 else m1
        y2 = int(y2) if y2 else (y1 + 1 if m2 < m1 else y1)
        try:
            a, b = dt.date(y1, m1, d1), dt.date(y2, m2, d2)
        except ValueError:
            continue
        if b < a or (b - a).days > 400:
            continue
        for t in targets:
            if a <= t <= b:
                found.add(t.isoformat())
    return sorted(found)


class Page(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.links, self.text, self.title = [], [], []
        self._a = None
        self._skip = 0
        self._title = False

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style", "noscript"):
            self._skip += 1
        elif tag == "title":
            self._title = True
        elif tag == "a":
            self._a = {"href": dict(attrs).get("href") or "", "text": ""}

    def handle_endtag(self, tag):
        if tag in ("script", "style", "noscript") and self._skip:
            self._skip -= 1
        elif tag == "title":
            self._title = False
        elif tag == "a" and self._a is not None:
            self.links.append(self._a)
            self._a = None

    def handle_data(self, data):
        if self._skip:
            return
        if self._title:
            self.title.append(data)
        self.text.append(data)
        if self._a is not None:
            self._a["text"] += data


def decode(raw, content_type):
    cands = []
    m = re.search(r"charset=([\w-]+)", content_type or "", re.I)
    if m:
        cands.append(m.group(1))
    m = re.search(rb"<meta[^>]+charset=[\"']?([\w-]+)", raw[:3000], re.I)
    if m:
        cands.append(m.group(1).decode("ascii", "ignore"))
    cands += ["utf-8", "cp932", "euc-jp"]
    for enc in cands:
        try:
            return raw.decode(enc)
        except (UnicodeDecodeError, LookupError):
            continue
    return raw.decode("utf-8", "replace")


def fetch(url, timeout=25):
    rec = {"url": url, "checked_at": dt.datetime.now(JST).isoformat(timespec="seconds")}
    try:
        req = Request(url, headers={"User-Agent": UA, "Accept-Language": "ja"})
        with urlopen(req, timeout=timeout) as r:
            ctype = r.headers.get("Content-Type", "")
            rec.update(http_status=r.status, final_url=r.geturl(), content_type=ctype)
            if "html" not in ctype.lower() and "text" not in ctype.lower():
                rec["status"] = "skipped_non_text"
                return rec, ""
            raw = r.read(MAX_BYTES)
            rec["status"] = "checked"
            return rec, decode(raw, ctype)
    except HTTPError as e:
        rec.update(status="error", http_status=e.code, error=f"HTTP {e.code}")
    except (URLError, TimeoutError, OSError) as e:
        rec.update(status="error", error=str(e)[:160])
    return rec, ""


def expand(url, targets):
    out = []
    for t in targets:
        out.append(url.replace("{YYYY}", str(t.year)).replace("{M}", str(t.month)).replace("{D}", str(t.day))
                   .replace("{MM}", f"{t.month:02d}").replace("{DD}", f"{t.day:02d}"))
        if "{" not in url:
            break
    return list(dict.fromkeys(out))


def snippet(text, targets, width=70):
    t = norm(text)
    for d in targets:
        for p in (rf"{d.month}月\s*{d.day}日", rf"{d.month}/{d.day}(?!\d)"):
            m = re.search(p, t)
            if m:
                a = max(0, m.start() - width)
                return t[a:m.end() + width]
    return t[:120]


def process(url, targets):
    rec, html = fetch(url)
    if not html:
        return rec, None, []
    p = Page()
    try:
        p.feed(html)
    except Exception as e:  # malformed HTML must not kill the run
        rec["parse_error"] = str(e)[:100]
    text = " ".join(p.text)
    title = norm("".join(p.title)).strip()
    hit = page_matches(text, targets)
    page = {"url": url, "final_url": rec.get("final_url", url), "title": title[:120],
            "dates": hit, "snippet": snippet(text, targets) if hit else "", "text": text}
    return rec, page, p.links


def run(cfg, targets, workers, max_total):
    log, pages, seen = [], [], set()
    budget = {}
    frontier = []
    for s in cfg["sources"]:
        for u in s["urls"]:
            for e in expand(u, targets):
                frontier.append((s, e, 0))
    total = 0
    while frontier and total < max_total:
        batch = []
        for s, u, depth in frontier:
            u = urldefrag(u)[0]
            key = (s["id"], u)
            host = urlsplit(u).netloc
            if key in seen or total + len(batch) >= max_total:
                continue
            cap = s.get("max_pages", 40)
            if budget.get(s["id"], 0) >= cap:
                continue
            seen.add(key)
            budget[s["id"]] = budget.get(s["id"], 0) + 1
            batch.append((s, u, depth))
        frontier = []
        if not batch:
            break
        with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as ex:
            futs = {ex.submit(process, u, targets): (s, u, d) for s, u, d in batch}
            for f in concurrent.futures.as_completed(futs):
                s, u, depth = futs[f]
                rec, page, links = f.result()
                rec.update(source_id=s["id"], depth=depth)
                log.append(rec)
                total += 1
                if not page:
                    continue
                page.update(source_id=s["id"], source_name=s.get("name", s["id"]), depth=depth,
                            secondary=bool(s.get("secondary")))
                pages.append(page)
                if depth < s.get("depth", 1):
                    hosts = set(s.get("follow_hosts") or [urlsplit(u).netloc])
                    pat = re.compile(s["follow_pattern"]) if s.get("follow_pattern") else None
                    for l in links:
                        href = urljoin(page["final_url"], l["href"])
                        sp = urlsplit(href)
                        if sp.scheme not in ("http", "https") or sp.netloc not in hosts or SKIP_EXT.search(href):
                            continue
                        if (pat and pat.search(href)) or EVENT_WORDS.search(l["text"]) or EVENT_WORDS.search(href):
                            frontier.append((s, href, depth + 1))
        time.sleep(0.2)
    return log, pages


def benchmark(pages, path):
    rows = []
    if not path or not Path(path).exists():
        return rows
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        if not line.strip() or line.startswith("#"):
            continue
        label, _, rx = line.partition("\t")
        rx = rx or label
        hits = [p for p in pages if re.search(rx, p["title"] + " " + p["text"])]
        dated = [p for p in hits if p["dates"]]
        rows.append({"label": label, "pages_mentioning": len(hits), "pages_with_target_date": len(dated),
                     "example_url": (dated or hits or [{"url": ""}])[0]["url"]})
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default="policy/weekend_gap_sources.json")
    ap.add_argument("--start", help="first target date YYYY-MM-DD (default: next Saturday JST)")
    ap.add_argument("--days", type=int, default=2)
    ap.add_argument("--benchmark", default="policy/weekend_gap_benchmark.tsv")
    ap.add_argument("--output-dir", required=True)
    ap.add_argument("--workers", type=int, default=12)
    ap.add_argument("--max-total", type=int, default=1500)
    a = ap.parse_args()
    today = dt.datetime.now(JST).date()
    start = a.start or (today + dt.timedelta(days=(5 - today.weekday()) % 7 or 7)).isoformat()
    targets = target_dates(start, a.days)
    cfg = json.loads(Path(a.config).read_text(encoding="utf-8"))
    log, pages = run(cfg, targets, a.workers, a.max_total)
    out = Path(a.output_dir)
    out.mkdir(parents=True, exist_ok=True)
    hits = sorted((p for p in pages if p["dates"]), key=lambda p: (p["secondary"], p["source_id"], p["url"]))
    (out / "requests.json").write_text(json.dumps(log, ensure_ascii=False, indent=1), encoding="utf-8")
    slim = [{k: v for k, v in p.items() if k != "text"} for p in hits]
    (out / "hits.json").write_text(json.dumps(slim, ensure_ascii=False, indent=1), encoding="utf-8")
    with (out / "hits.tsv").open("w", encoding="utf-8") as f:
        f.write("source\tsecondary\tdates\ttitle\turl\tsnippet\n")
        for p in slim:
            f.write("\t".join([p["source_name"], str(p["secondary"]), ",".join(p["dates"]),
                               p["title"].replace("\t", " "), p["url"], p["snippet"].replace("\t", " ")]) + "\n")
    bench = benchmark(pages, a.benchmark)
    with (out / "benchmark.tsv").open("w", encoding="utf-8") as f:
        f.write("label\tpages_mentioning\tpages_with_target_date\texample_url\n")
        for r in bench:
            f.write(f"{r['label']}\t{r['pages_mentioning']}\t{r['pages_with_target_date']}\t{r['example_url']}\n")
    errors = [r for r in log if r.get("status") == "error"]
    summary = {"targets": [t.isoformat() for t in targets], "requests": len(log),
               "ok": sum(r.get("status") == "checked" for r in log), "errors": len(errors),
               "pages_read": len(pages), "pages_with_target_date": len(hits),
               "benchmark_found": sum(1 for r in bench if r["pages_with_target_date"]),
               "benchmark_total": len(bench), "publishable": False,
               "note": "Candidate worklist only. Each hit must be read on its official page before use."}
    (out / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
