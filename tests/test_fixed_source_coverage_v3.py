import datetime as dt
import json
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from fixed_source_coverage_v3 import expand_urls, source_audit, build_report, validate


def make_registry():
    entries = []
    for i in range(26):
        sid = ("source_" + str(i))
        urls = ["https://www.example.com/calendar?month={YYYY-MM}"] if i == 24 else [
            "https://www.example.com/"+sid]
        entries.append({"id": sid, "label": "固定サイト" + str(i),
                        "origin": "legacy" if i < 18 else "official",
                        "required": i != 25, "enabled": True,
                        "base_url": "https://www.example.com/"+sid, "search_urls": urls})
    return {"explicit_sources": entries,
            "protected_legacy_source_ids": [x["id"] for x in entries[:18]]}


def fake_response(url):
    if "source_5" in url:
        return 503, b"", url, "text/html; charset=utf-8"
    if "month=2026-11" in url:
        return 404, b"", url, "text/html; charset=utf-8"
    html = ('<title>イベント公式サイト</title><h2>地域イベント</h2>'
            '<a href="https://www.example.com/events/child">こども科学体験</a>'
            '<a href="https://www.example.com/events/child">こども科学体験</a>')
    return 200, html.encode(), url, "text/html; charset=utf-8"


class FixedSourcePhase3Tests(unittest.TestCase):
    def setUp(self):
        self.start = dt.date(2026,10,31)
        self.end = dt.date(2026,12,6)
        self.registry = make_registry()

    def test_appended_source_is_audited_without_losing_originals(self):
        registry=make_registry()
        registry['protected_source_ids']=[r['id']for r in registry['explicit_sources']]
        new=dict(registry['explicit_sources'][-1],id='new_venue',label='新しい会場',base_url='https://www.example.com/new',search_urls=['https://www.example.com/new'])
        registry['explicit_sources'].append(new)
        report=build_report(registry,self.start,self.end,fetcher=fake_response,workers=4)
        self.assertTrue(validate(report,registry));self.assertEqual(report['registered_source_count'],27)
        self.assertEqual([r['source_id']for r in report['sources']],[r['id']for r in registry['explicit_sources']])
        registry['explicit_sources']=[r for r in registry['explicit_sources']if r['id']!='source_24']
        with self.assertRaises(ValueError):build_report(registry,self.start,self.end,fetcher=fake_response,workers=4)

    def test_all_26_sources_protected_and_same_registry_order(self):
        r = build_report(self.registry,self.start,self.end,
                         fetcher=fake_response,workers=4,checked_at="2026-10-27T22:00:00+09:00")
        self.assertTrue(validate(r,self.registry))
        self.assertEqual(r["registered_source_count"],26)
        self.assertEqual(r["protected_legacy_source_count"],18)
        self.assertEqual([x["source_id"] for x in r["sources"]],
                         [x["id"] for x in self.registry["explicit_sources"]])
        self.assertEqual(r["summary"]["reachable_all_registered_urls"],24)
        self.assertEqual(r["summary"]["source_errors"],1)
        self.assertEqual(r["summary"]["partial_errors"],1)
        self.assertIsNone(r["summary"]["publication_gaps_confirmed"])
        self.assertEqual(r["summary"]["full_event_row_parity_verified_by_this_report"],0)
        self.assertTrue(all(x["event_candidates_total"] is None for x in r["sources"]))
        self.assertTrue(all(x["candidate_publication_parity"]=="未検証" for x in r["sources"]))
        self.assertTrue(r["read_only"])

    def test_calendar_expands_each_month_once_and_fails_if_one_missing(self):
        s=self.registry["explicit_sources"][24]
        urls=expand_urls(s,self.start,self.end)
        self.assertEqual(len(urls),3)
        self.assertEqual(urls[0].split("=")[-1],"2026-10")
        r=source_audit(s,self.start,self.end,fetcher=fake_response)
        self.assertEqual(r["pages_checked"],2)
        self.assertEqual(r["pages_failed"],1)
        self.assertEqual(r["retrieval_status"],"partial_error")
        self.assertEqual(r["observed_distinct_link_leads"],1)
        self.assertEqual(r["status_label"],"一部取得失敗")
        self.assertEqual(len(r["errors"]),1)
        self.assertIsNone(r["published_count_from_source"])

    def test_broken_required_site_is_error_not_zero_events(self):
        x=source_audit(self.registry["explicit_sources"][5],self.start,self.end,
                       fetcher=fake_response)
        self.assertEqual(x["retrieval_status"],"source_error")
        self.assertEqual(x["pages_checked"],0)
        self.assertEqual(x["pages_failed"],1)
        self.assertTrue(x["required"])
        self.assertIsNone(x["event_candidates_total"])
        self.assertTrue(x["unverified_due_to_source_error"])

    def test_zero_event_links_cannot_be_counted_as_zero_event_candidates(self):
        def bare(url):
            return 200,"<title>公式サイト</title><main>記事一覧</main>".encode("utf-8"),url,"text/html"
        x=source_audit(self.registry["explicit_sources"][0],self.start,self.end,
                       fetcher=bare)
        self.assertEqual(x["retrieval_status"],"checked")
        self.assertEqual(x["observed_distinct_link_leads"],0)
        self.assertIsNone(x["event_candidates_total"])
        self.assertEqual(x["candidate_publication_parity"],"未検証")

    def test_missing_legacy_or_duplicate_id_is_fatal(self):
        bad=json.loads(json.dumps(self.registry))
        bad["protected_legacy_source_ids"].pop()
        with self.assertRaisesRegex(ValueError,"protected"):
            build_report(bad,self.start,self.end,fetcher=fake_response)
        bad=json.loads(json.dumps(self.registry))
        bad["explicit_sources"][-1]["id"]="source_0"
        with self.assertRaisesRegex(ValueError,"duplicate"):
            build_report(bad,self.start,self.end,fetcher=fake_response)

    def test_registry_not_modified_by_source_audit(self):
        before=json.dumps(self.registry,sort_keys=True)
        build_report(self.registry,self.start,self.end,fetcher=fake_response)
        self.assertEqual(json.dumps(self.registry,sort_keys=True),before)

    def test_tamemap_partial_fallback_and_itabashi_official_separate_from_503(self):
        registry = json.loads(json.dumps(self.registry))
        official, tourism, tama = registry["explicit_sources"][19:22]
        official.update(id="itabashi_official_festival",
                        base_url="https://www.city.itabashi.tokyo.jp/bunka/kanko/matsuri/1006858.html",
                        search_urls=["https://www.city.itabashi.tokyo.jp/bunka/kanko/matsuri/1006858.html"])
        tourism.update(id="itabashi_tourism_festival",
                       base_url="https://itabashi-kanko.jp/pickup/detail?id=1799",
                       search_urls=["https://itabashi-kanko.jp/pickup/detail?id=1799"],
                       fallback_source_ids=["itabashi_official_festival"])
        tama.update(id="tamemap_nakano",
                    base_url="https://pc.tamemap.net/1311401",
                    search_urls=[
                      "https://pc.tamemap.net/1311401/calendar/{YYYY-MM}",
                      "https://pc.tamemap.net/1311401/new_arrival?lat=35.7089745"])
        def fake(url):
            if "itabashi-kanko.jp" in url:
                return 503, b"unavailable", url, "text/html"
            if "/calendar/" in url:
                return 403, b"forbidden", url, "text/html"
            if "/new_arrival" in url:
                body = ("<h1>イベントの新着一覧</h1>"
                        "<h3>絵本の読み聞かせの会</h3><p>投稿者 : ポプラ文庫</p>")
                return 200,body.encode(),url,"text/html"
            return 200,'<title>OK</title><a href="/events">地域イベント</a>'.encode(),url,"text/html"
        report = build_report(registry,self.start,self.end,fetcher=fake)
        self.assertTrue(validate(report,registry))
        found = {x["source_id"]:x for x in report["sources"]}
        tama_row = found["tamemap_nakano"]
        self.assertEqual(tama_row["retrieval_status"],"partial_error")
        self.assertEqual(tama_row["pages_expected"],4)
        self.assertEqual(tama_row["pages_checked"],1)
        self.assertEqual(tama_row["new_arrival_post_leads_observed"],1)
        self.assertTrue(tama_row["new_arrival_samples"][0]["date_verified"] is False)
        self.assertIsNone(tama_row["event_candidates_total"])
        tourism_row = found["itabashi_tourism_festival"]
        self.assertEqual(tourism_row["retrieval_status"],"source_error")
        self.assertEqual(tourism_row["official_alternatives"][0]["source_id"],
                         "itabashi_official_festival")
        self.assertEqual(tourism_row["official_alternatives"][0]["retrieval_status"],"checked")
        self.assertTrue(tourism_row["failed_primary_source_stays_failed"])
        self.assertTrue(tourism_row["official_alternative_can_be_used_for_event_verification"])
        self.assertIsNone(tourism_row["published_count_from_source"])

    def test_incorrect_coverage_claim_rejected(self):
        r=build_report(self.registry,self.start,self.end,fetcher=fake_response)
        r["sources"][0]["candidate_publication_parity"]="完全照合"
        with self.assertRaisesRegex(ValueError,"cannot assert"):
            validate(r,self.registry)


if __name__=="__main__":
    unittest.main()
