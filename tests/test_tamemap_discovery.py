import datetime as dt
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from holiday_after_collect import inspect, tamemap_new_arrival_leads
from fixed_source_coverage_v3 import probe
from tamemap_calendar import calendar_leads

URL = "https://pc.tamemap.net/1311401/calendar/2026-11?locale=ja"


def calendar(links, month="2026年11月"):
    return ('<p class="date">' + month + '</p><table class="list">'
            '<tr id="list_date_11-14"><td>' + links + '</td></tr></table>')


class TamemapDiscoveryTests(unittest.TestCase):
    def test_all_dated_links_survive_without_keyword_filter_or_100_link_cap(self):
        links = ''.join('<a href="/1311401/event/%d/2026-11-14">おもちゃDAY %d</a>' % (i, i)
                        for i in range(125))
        rows = calendar_leads(calendar(links), URL)
        self.assertEqual(len(rows), 125)
        self.assertEqual(rows[-1]["name"], "おもちゃDAY 124")
        self.assertTrue(all(r["matched_dates"] == ["2026-11-14"] and
                            r["date_unverified"] and not r["publication_approved"] and
                            not r["primary_source_verified"] for r in rows))

    def test_duplicate_rendering_is_removed_but_distinct_days_and_ids_survive(self):
        link = '<a href="/1311401/event/123/2026-11-14">同名の会</a>'
        body = calendar(link * 2 + link.replace("11-14", "11-15") + link.replace("/123/", "/456/"))
        rows = calendar_leads(body, URL)
        self.assertEqual(len(rows), 3)
        self.assertEqual(len({r["candidate_id"] for r in rows}), 3)
        self.assertEqual(len(calendar_leads(body, URL, dt.date(2026, 11, 15), dt.date(2026, 11, 15))), 1)

    def test_month_mismatch_empty_shell_and_invalid_date_fail_closed(self):
        link = '<a href="/1311401/event/123/2026-11-14">会</a>'
        for body in (calendar(link, "2026年12月"),
                     '<p class="date">2026年11月</p>',
                     calendar(link.replace("11-14", "12-14")),
                     calendar(link.replace("11-14", "11-31")),
                     '<script>"2026年11月"</script>' + calendar(link, "2026年12月")):
            with self.subTest(body=body), self.assertRaises(ValueError):
                calendar_leads(body, URL)

    def test_outside_community_navigation_and_script_links_are_ignored(self):
        body = calendar('<a href="https://evil.example/1311401/event/1/2026-11-14">外部</a>'
                        '<a href="/1310901/event/2/2026-11-14">別地域</a>'
                        '<a href="/1311401/calendar/2026-12">翌月</a>'
                        '<script><a href="/1311401/event/3/2026-11-14">偽</a></script>')
        self.assertEqual(calendar_leads(body, URL), [])
        with self.assertRaises(ValueError):
            calendar_leads(body, URL.replace("pc.tamemap.net", "evil.example"))

    def test_collector_and_status_probe_use_full_calendar_adapter(self):
        body = calendar('<a href="/1311401/event/123/2026-11-14">健康茶房</a>')
        fetcher = lambda u: (200, body.encode(), u, "text/html")
        row = inspect({"kind": "explicit", "source_id": "tamemap_nakano", "url": URL,
                       "target_start": "2026-11-14", "target_end": "2026-12-20"}, fetcher)
        self.assertEqual(row["status"], "checked")
        self.assertEqual(row["candidate_link_count"], 1)
        self.assertFalse(row["candidates"][0]["publication_approved"])
        check, links = probe(URL, fetcher)
        self.assertEqual(check["observed_event_link_leads"], 1)
        self.assertEqual(links[0]["discovery_url"], "https://pc.tamemap.net/1311401/event/123/2026-11-14")
        bad, _ = probe(URL, lambda u: (200, b'<title>Just an empty shell</title>', u, "text/html"))
        self.assertEqual(bad["status"], "error")

    def test_new_arrival_reads_literal_detail_target_without_running_javascript(self):
        body = '''<h1>イベントの新着一覧</h1>
        <a href="javascript:void(0)" onclick="addCommunityUrlClicked('/1311401/event/123')">
        <h3>同名の会</h3><p>投稿者 : 主催者</p><span>2時間前</span></a>
        <a href="/1311401/event/456"><h3>同名の会</h3></a>
        <a onclick="addCommunityUrlClicked('https://evil.example/1311401/event/7')"><h3>外部の会</h3></a>
        <a onclick="addCommunityUrlClicked('/1311401/event/8'); alert(1)"><h3>追加命令</h3></a>'''
        rows = tamemap_new_arrival_leads(body, "https://pc.tamemap.net/1311401/new_arrival")
        self.assertEqual(rows[0]["discovery_url"], "https://pc.tamemap.net/1311401/event/123")
        self.assertEqual(rows[0]["poster"], "主催者")
        self.assertNotEqual(rows[0]["candidate_id"], rows[1]["candidate_id"])
        self.assertTrue(all(r["matched_dates"] == [] and r["date_unverified"] for r in rows))
        self.assertTrue(all(not r["detail_link_observed"] for r in rows[2:]))


if __name__ == "__main__":
    unittest.main()
