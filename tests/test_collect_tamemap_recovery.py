"""Separate-environment source recovery remains unverified, including failures."""
import datetime as dt
from email.message import Message
import io
from pathlib import Path
import sys
import unittest
from unittest.mock import patch
from urllib.error import HTTPError
from urllib.parse import urlsplit

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from collect_tamemap_recovery import collect, ENVIRONMENT_KIND


def manifest():
    start = dt.date(2026, 11, 7)
    return {"weekends": [{"sat": str(start + dt.timedelta(days=7*i)),
                          "sun": str(start + dt.timedelta(days=7*i+1))} for i in range(6)]}


def body(url):
    if urlsplit(url).path.endswith("/new_arrival"):
        return '''<h1>イベントの新着一覧</h1>
        <a onclick="addCommunityUrlClicked('/1311401/event/333')">
        <h3>新着のおもちゃDAY</h3><p>投稿者 : 主催者</p></a>'''
    month = urlsplit(url).path.rsplit("/", 1)[1]
    year, number = month.split("-")
    return ('<p class="date">%s年%s月</p><table><tr id="list_date_%s-7"><td>'
            '<a href="/1311401/event/%s/%s-07">健康茶房</a></td></tr></table>' %
            (year, int(number), int(number), int(number), month))


def success(url):
    return 200, body(url).encode(), url, "text/html"


class TamemapRecoveryTests(unittest.TestCase):
    def test_collects_canonical_months_and_newarrival_with_separate_provenance(self):
        result = collect(manifest(), success)
        audit = result["source_checks"]
        self.assertEqual(audit["summary"], {"pages_requested": 3, "pages_checked": 3,
                                          "pages_failed": 0, "unverified_candidates": 3})
        self.assertEqual(audit["environment_kind"], ENVIRONMENT_KIND)
        self.assertFalse(audit["required_github_actions_check_satisfied"])
        self.assertFalse(audit["publication_permitted"])
        for check in audit["checks"]:
            self.assertEqual(check["status"], "checked")
            self.assertIn("checked_at", check)
            self.assertEqual(len(check["sha256"]), 64)
            self.assertNotIn("body", check)
        rows = result["candidate_pool"]["candidates"]
        self.assertTrue(all(r["status"] == "unverified" and r["date_unverified"] and
                            not r["publication_permitted"] and not r["primary_source_verified"] for r in rows))
        newest = next(r for r in rows if r["candidate_type"] == "new_arrival_title_lead")
        self.assertEqual(newest["matched_dates"], [])
        self.assertEqual(newest["discovery_url"], "https://pc.tamemap.net/1311401/event/333")

    def test_403_stays_failed_and_accessible_newarrival_cannot_replace_calendars(self):
        def transport(url):
            if "/calendar/" in url:
                headers = Message(); headers["Server"] = "cloudflare"
                raise HTTPError(url, 403, "Forbidden", headers,
                                io.BytesIO(b"<title>Just a moment...</title>challenge-platform"))
            return success(url)
        with patch("holiday_after_collect.time.sleep"):
            result = collect(manifest(), transport)
        audit = result["source_checks"]
        self.assertEqual(audit["summary"]["pages_failed"], 2)
        self.assertEqual(audit["summary"]["unverified_candidates"], 1)
        failed = [c for c in audit["checks"] if c["status"] == "error"]
        self.assertTrue(all(c["http_status"] == 403 and c["challenge_detected"] for c in failed))
        self.assertFalse(audit["required_github_actions_check_satisfied"])

    def test_empty_shell_and_wrong_calendar_month_do_not_become_zero_event_success(self):
        for payload in ("<title>Empty shell</title>",
                        body("https://pc.tamemap.net/1311401/calendar/2026-10")):
            def transport(url):
                return (200, payload.encode(), url, "text/html") if "/calendar/" in url else success(url)
            with self.subTest(payload=payload):
                result = collect(manifest(), transport)
                audit = result["source_checks"]
                self.assertEqual(audit["summary"]["pages_failed"], 2)
                self.assertEqual(audit["summary"]["unverified_candidates"], 1)
                self.assertTrue(all(c["status"] == "error" for c in audit["checks"] if "/calendar/" in c["url"]))


if __name__ == "__main__":
    unittest.main()
