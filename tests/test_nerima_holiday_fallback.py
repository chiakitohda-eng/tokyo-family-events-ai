"""Tests safe original-404 preserving Nerima holiday-calendar index fallback."""
import io
import sys
from email.message import Message
from pathlib import Path
import unittest
from urllib.error import HTTPError

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/"tools"))
from holiday_after_collect import inspect

HTML = """<html><head><title>2026年11月カレンダー</title></head>
<h1>2026年11月カレンダー</h1><table>
<tr><th>日</th><th>曜日</th><th>イベント</th></tr>
<tr><td>22日</td><td>日曜日</td><td><a href="/event/other.html">親子遊び教室</a></td></tr>
<tr><td>23日</td><td>月曜日</td><td><a href="/kankomoyoshi/event/forest.html">ねりまの森こどもフェスタ2026</a></td></tr>
</table></html>""".encode("utf-8")

def job(id, day="2026-11-23"):
    prefix=("/kankomoyoshi" if id=="nerima_monthly" else "/nerimakids")
    return {
        "kind":"holiday_calendar", "source_id":id, "ward":"練馬区",
        "url":"https://www.city.nerima.tokyo.jp"+prefix+"/event/calendar/list_calendar202611.html",
        "holiday":day,"calendar_mode":"monthly","required":False,
    }

def transport(original, html=HTML):
    def read(url):
        if url==original:
            raise HTTPError(url,404,"Not Found",Message(),io.BytesIO(b"Not Found"))
        return 200,html,url,"text/html"
    return read

class NerimaFallbackTests(unittest.TestCase):
    def test_main_monthly_fallback_retains_failed_original_with_unverified_candidate(self):
        j=job("nerima_monthly")
        out=inspect(j,transport(j["url"]))
        self.assertEqual(out["status"],"error")
        self.assertEqual(out["http_status"],404)
        proof=out["official_calendar_index_fallback"]
        self.assertEqual(proof["original_source_status_remains"],"error")
        self.assertTrue(proof["calendar_month_matches_target"])
        self.assertEqual(proof["fallback_http_status"],200)
        self.assertFalse(proof["event_details_verified"])
        self.assertFalse(proof["publication_permitted"])
        self.assertEqual(proof["candidate_count"],1)
        self.assertEqual(len(out["candidates"]),1)
        lead=out["candidates"][0]
        self.assertEqual(lead["matched_dates"],["2026-11-23"])
        self.assertTrue(lead["date_unverified"])
        self.assertEqual(lead["source_kind"],"official_calendar_candidate_only")

    def test_kids_monthly_404_can_use_only_approved_index(self):
        j=job("nerima_kids_monthly")
        out=inspect(j,transport(j["url"]))
        self.assertEqual(out["official_calendar_index_fallback"]["fallback_url"],
            "https://www.city.nerima.tokyo.jp/nerimakids/event/calendar/list_calendar.html")
        self.assertEqual(out["status"],"error")
        self.assertEqual(len(out["candidates"]),1)

    def test_wrong_month_fails_closed_no_fake_december_event(self):
        j=job("nerima_monthly","2026-12-23")
        out=inspect(j,transport(j["url"]))
        p=out["official_calendar_index_fallback"]
        self.assertFalse(p["calendar_month_matches_target"])
        self.assertEqual(p["candidate_count"],0)
        self.assertEqual(out["candidates"],[])
        self.assertEqual(out["status"],"error")
        self.assertIn("month mismatch",p["fallback_error"])

    def test_security_challenge_403_does_not_fallback(self):
        j=job("nerima_monthly")
        def denied(u):
            h=Message();h["Server"]="cloudflare"
            raise HTTPError(u,403,"Forbidden",h,io.BytesIO(
                b"<html><title>Just a moment...</title>challenge-platform</html>"))
        out=inspect(j,denied)
        self.assertEqual(out["status"],"error")
        self.assertEqual(out["http_status"],403)
        self.assertNotIn("official_calendar_index_fallback",out)
        self.assertEqual(out["candidates"],[])

if __name__=="__main__":
    unittest.main()
