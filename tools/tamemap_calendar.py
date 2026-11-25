"""Read the public Nakano calendar's dated event links, never infer event facts."""
from datetime import date
from html.parser import HTMLParser
import re
from urllib.parse import urljoin, urlsplit


class CalendarHTML(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.links = []
        self.anchor = None
        self.months = []
        self.month_text = None
        self.has_day_rows = False
        self.skip = 0

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag in ("script", "style"):
            self.skip += 1
        if self.skip:
            return
        if tag == "p" and "date" in attrs.get("class", "").split():
            self.month_text = []
        if tag == "tr" and re.fullmatch(r"list_date_\d{1,2}-\d{1,2}", attrs.get("id", "")):
            self.has_day_rows = True
        if tag == "a":
            self.anchor = {"href": attrs.get("href", ""), "text": []}

    def handle_data(self, data):
        if self.skip:
            return
        if self.month_text is not None:
            self.month_text.append(data)
        if self.anchor is not None:
            self.anchor["text"].append(data)

    def handle_endtag(self, tag):
        if tag in ("script", "style"):
            self.skip = max(0, self.skip - 1)
        if self.skip:
            return
        if tag == "p" and self.month_text is not None:
            self.months.append("".join(self.month_text).strip())
            self.month_text = None
        if tag == "a" and self.anchor is not None:
            self.links.append(self.anchor)
            self.anchor = None


def calendar_leads(body, source_url, start=None, end=None):
    """All dated links, including names without generic event keywords.

    The date in a calendar link is a discovery hint until the detail's actual
    schedule and venue are checked. Do not cap at the generic 100-link limit.
    """
    source = urlsplit(source_url)
    month = re.fullmatch(r"/1311401/calendar/(\d{4}-\d{2})", source.path)
    if (source.scheme != "https" or source.netloc != "pc.tamemap.net" or not month):
        raise ValueError("not a Nakano monthly calendar URL")
    expected = date.fromisoformat(month[1] + "-01")
    parser = CalendarHTML()
    parser.feed(body)
    marker = re.compile(r"%d\s*年\s*0?%d\s*月" % (expected.year, expected.month))
    if not any(marker.fullmatch(text) for text in parser.months):
        raise ValueError("calendar body does not show requested year-month")
    if not parser.has_day_rows:
        raise ValueError("calendar has no dated list rows")
    found = {}
    for link in parser.links:
        url = urljoin(source_url, link["href"])
        parsed = urlsplit(url)
        event = re.fullmatch(r"/1311401/event/(\d+)/(\d{4}-\d{2}-\d{2})", parsed.path)
        if parsed.scheme != "https" or parsed.netloc != "pc.tamemap.net" or not event:
            continue
        day = date.fromisoformat(event[2])
        if (day.year, day.month) != (expected.year, expected.month):
            raise ValueError("event date does not match calendar month")
        if (start and day < start) or (end and day > end):
            continue
        name = " ".join("".join(link["text"]).split())
        if not name:
            raise ValueError("calendar event link missing title")
        canonical = "https://pc.tamemap.net" + parsed.path
        found[canonical] = {
            "candidate_id": "tamemap-calendar-" + event[1] + "-" + day.strftime("%Y%m%d"),
            "name": name, "ward": "中野区", "discovery_url": canonical,
            "source_page": source_url, "source_id": "tamemap_nakano",
            "candidate_type": "calendar_dated_link", "matched_dates": [day.isoformat()],
            "date_from_calendar": day.isoformat(), "date_unverified": True,
            "primary_source_verified": False, "publication_approved": False,
            "review_required": "詳細本文の開催日・会場・対象・主催者情報を個別に確認する。",
        }
    return list(found.values())
