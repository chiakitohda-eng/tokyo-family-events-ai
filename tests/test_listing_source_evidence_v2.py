import copy
import datetime as dt
import unittest
from tools.listing_source_evidence_v2 import Page, extract_articles, next_pages, SOURCES, crawl_source
from tools.audit_phase2_listing_parity import reconcile_source


NAKANO = "https://www.nakano-kanko.com/event/"
ITABASHI = "https://itabashi-times.com/category/event"
NERIMA = "https://www.nerimakanko.jp/event/"


def anchor(url, label):
    return f'<a href="{url}">{label}</a>'


def heading_event(name, url):
    return f'<article><h3>{name}</h3>{anchor(url, "イベントの詳細へ")}</article>'


def snapshot():
    official = "https://www.city.itabashi.tokyo.jp/official/9876.html"
    event = {"id": "official-itabashi-event", "name": "キッズ体験",
             "date_start": "2026-11-08", "date_end": "2026-11-08",
             "official_url": official,
             "source": "https://itabashi-times.com/archives/kids202611.html"}
    return {"start": "2026-10-31", "end": "2026-12-06",
            "target_dates": {"2026-11-08"},
            "events": [{"event": event, "owned_dates": {"2026-11-08"}, "week": "2026-11-07"}],
            "decisions": [{"decision": {"candidate_id": "official-itabashi-event",
                                       "decision": "published",
                                       "evidence": [{"url": official}]},
                           "owned_dates": {"2026-11-08"}, "week": "2026-11-07"}]}


class Phase2Tests(unittest.TestCase):
    def test_itabashi_nested_object_category_keeps_article_and_pagination(self):
        p = Page()
        p.feed('''<article><a href="/archives/kayaku-koukai2026.html"
          title="火薬製造所跡 秋の一般公開 2026年11月22日">
          <h3>火薬製造所跡 秋の一般公開</h3>
          <object><a href="/category/event">イベント情報</a></object>
          </a></article><a href="/category/event/page/2">2</a>''')
        articles = extract_articles(p, ITABASHI, SOURCES["itabashi_times_event"])
        self.assertEqual(len(articles), 1)
        self.assertEqual(articles[0][0], "https://itabashi-times.com/archives/kayaku-koukai2026.html")
        self.assertEqual(articles[0][1], "火薬製造所跡 秋の一般公開 2026年11月22日")
        self.assertEqual(next_pages(p, ITABASHI, SOURCES["itabashi_times_event"]), [ITABASHI + "/page/2"])
        self.assertTrue(any(a["label"] == "イベント情報" for a in p.links))

    def test_nakano_event_heading_and_generic_more_link(self):
        p = Page()
        p.feed(heading_event("MIYA SONIC 2026", "/event-info/event-3846/"))
        r = extract_articles(p, NAKANO, SOURCES["nakano_official_tourism"])
        self.assertEqual(len(r), 1)
        self.assertEqual(r[0][1], "MIYA SONIC 2026")

    def test_itabashi_roundup_expands_child_without_creating_festival_card(self):
        idx = ITABASHI
        page2 = idx + "/page/2"
        roundurl = "https://itabashi-times.com/archives/event202611.html"
        childurl = "https://itabashi-times.com/archives/kids202611.html"
        pages = {
            idx: anchor("/archives/event202611.html", "2026年11月の板橋区イベントまとめ") +
                 anchor("/archives/kids202611.html", "子ども科学体験 2026年11月8日（日）") +
                 anchor("/category/event/page/2", "2"),
            page2: anchor("/archives/event202611.html", "2026年11月の板橋区イベントまとめ"),
            roundurl: "<article>" + anchor("/archives/kids202611.html",
                                           "子ども科学体験 11月8日") + "</article>",
            childurl: "<h1>子ども科学体験</h1><p>2026年11月8日（日）開催</p>"
        }
        out = crawl_source("itabashi_times_event", dt.date(2026, 10, 31), dt.date(2026, 12, 6),
                           fetcher=lambda url: (200, pages[url]))
        self.assertEqual(out["status"], "checked")
        self.assertEqual(len(out["candidates"]), 2)
        parents = [x for x in out["candidates"] if x["candidate_type"] == "collection_index"]
        self.assertEqual(len(parents), 1)
        self.assertEqual(parents[0]["roundup_child_urls"], [childurl])
        child = next(x for x in out["candidates"] if x["discovery_url"] == childurl)
        self.assertEqual(child["candidate_type"], "event_lead")
        self.assertFalse(child["publication_approved"])
        self.assertEqual(child["date_hints"], ["2026-11-08"])
        self.assertEqual(len(out["listing_pages_checked"]), 2)

    def test_itabashi_www_absolute_article_link(self):
        p = Page()
        p.feed(anchor(
            "https://www.itabashi-times.com/archives/ryokuchi202610.html",
            "高島平緑地で子どもイベント 2026年10月31日"))
        links = extract_articles(p, ITABASHI, SOURCES["itabashi_times_event"])
        self.assertEqual(len(links), 1)
        self.assertIn("ryokuchi202610.html", links[0][0])

    def test_nerima_generic_past_events_heading_does_not_become_event_name(self):
        p = Page()
        p.feed("<h3>過去のイベント</h3>" +
               anchor("/event/detail.php?event_id=e12345", "もっと見る arrow_right"))
        links = extract_articles(p, NERIMA, SOURCES["nerimakanko"])
        self.assertEqual(len(links), 1)
        self.assertEqual(links[0][1], "記事名未確定（要確認）")

    def test_missing_page_two_fail_closed_not_zero(self):
        idx = ITABASHI
        out = crawl_source("itabashi_times_event", dt.date(2026, 10, 31), dt.date(2026, 12, 6),
                           fetcher=lambda url: (503, "") if "/page/2" in url else (
                               200, anchor("/archives/hello2026.html", "お祭り 2026年11月1日"))
                           )
        self.assertEqual(out["status"], "source_error")
        self.assertGreater(out["candidate_count"], 0)
        self.assertTrue(any("/page/2" in x["url"] for x in out["failures"]))
        self.assertFalse(out["retrieval_complete"])

    def test_itabashi_rss_is_partial_recovery_never_a_false_success(self):
        root = "https://itabashi-times.com/category/event/feed/"
        pages = {
            ITABASHI: anchor("/category/event", "イベント情報"),
            ITABASHI + "/page/2": anchor("/category/event", "イベント情報"),
            root: """ \n\ufeff<?xml version="1.0"?><rss version="2.0"><channel>
            <item><title>板橋の子どもイベント2026年11月8日</title>
            <link>https://itabashi-times.com/archives/kids202611.html</link></item>
            </channel></rss>""",
            root + "?paged=2": """<?xml version="1.0"?><rss version="2.0"><channel>
            <item><title>2026年10月31日・地域のお祭り</title>
            <link>https://itabashi-times.com/archives/festival202610.html</link></item>
            </channel></rss>""",
            "https://itabashi-times.com/archives/kids202611.html": "<h1>子どもイベント</h1>",
            "https://itabashi-times.com/archives/festival202610.html": "<h1>地域のお祭り</h1>",
        }
        result = crawl_source(
            "itabashi_times_event", dt.date(2026, 10, 31), dt.date(2026, 12, 6),
            fetcher=lambda url: (200, pages[url]))
        self.assertEqual(result["status"], "source_error")
        self.assertEqual(result["candidate_count"], 2)
        self.assertFalse(result["retrieval_complete"])
        self.assertTrue(any("partial" in x["error"] for x in result["failures"]))
        self.assertTrue(all(not x["publication_approved"] for x in result["candidates"]))

    def test_nerima_month_pages_and_repeated_rows_are_deduplicated(self):
        detail = "https://www.nerimakanko.jp/event/detail.php?event_id=e000002998"
        listing = '<h3>江古田ハロウィンパーティー2026</h3>' + anchor(
            "/event/detail.php?event_id=e000002998", "もっと見る")
        pages = [NERIMA] + [f"https://www.nerimakanko.jp/event/search.php?month=2026-{m}"
                             for m in ("10", "11", "12")]
        material = {url: listing for url in pages}
        material[detail] = "<h1>江古田ハロウィンパーティー2026</h1><p>2026年10月31日</p>"
        out = crawl_source("nerimakanko", dt.date(2026, 10, 31), dt.date(2026, 12, 6),
                           fetcher=lambda url: (200, material[url]))
        self.assertEqual(out["status"], "checked")
        self.assertEqual(out["candidate_count"], 1)
        self.assertEqual(len(out["listing_pages_checked"]), 4)
        self.assertEqual(len(out["candidates"][0]["source_pages"]), 4)
        self.assertFalse(out["candidates"][0]["primary_source_verified"])

    def test_host_restriction_blocks_outside_author_urls(self):
        p = Page()
        p.feed('<h3>Fake</h3>' + anchor("https://malicious.example/event-info/event-111/", "イベントの詳細へ"))
        self.assertEqual(extract_articles(p, NAKANO, SOURCES["nakano_official_tourism"]), [])

    def test_pagination_not_generic_site_navigation(self):
        p = Page()
        p.feed(anchor("/event/", "もっと見る") + anchor("/event/page/2/", "次へ") +
               anchor("https://example.net/event/page/2/", "次へ"))
        self.assertEqual(next_pages(p, NAKANO, SOURCES["nakano_official_tourism"]),
                         ["https://www.nakano-kanko.com/event/page/2"])

    def test_article_proof_only_links_existing_publication(self):
        original = snapshot()
        data = copy.deepcopy(original)
        article = "https://itabashi-times.com/archives/kids202611.html"
        evidence = {"source_id": "itabashi_times_event", "status": "checked", "failures": [],
                    "candidates": [{
                        "candidate_id": "itabashi-article-1", "name": "キッズ体験2026",
                        "candidate_type": "event_lead", "discovery_url": article,
                        "date_hints": ["2026-11-08"], "date_verified": False}]}
        r = reconcile_source(evidence, data)
        self.assertEqual(r["breakdown"]["existing_publication"], 1)
        self.assertEqual(data, original, "no mutation to production snapshot")

        data["decisions"] = []
        r = reconcile_source(evidence, data)
        self.assertEqual(r["breakdown"]["existing_link_needs_proof"], 1)

    def test_same_logical_programme_across_week_shards_is_not_an_ambiguity(self):
        base = snapshot()
        source = base["events"][0]["event"]["source"]
        another = copy.deepcopy(base["events"][0]["event"])
        another["id"] = "other-week-copy"
        another["date_start"] = "2026-11-15"
        another["date_end"] = "2026-11-15"
        base["events"].append({"event": another, "owned_dates": {"2026-11-15"}, "week": "2026-11-14"})
        base["decisions"].append({"decision": {
            "candidate_id": "other-week-copy", "decision": "published",
            "evidence": [{"url": another["official_url"]}]},
            "owned_dates": {"2026-11-15"}, "week": "2026-11-14"})
        candidate = {"source_id": "itabashi_times_event", "status": "checked", "failures": [],
            "candidates": [{"candidate_id": "same-story", "name": "キッズ体験",
                            "candidate_type": "event_lead",
                            "discovery_url": source, "date_hints": []}]}
        report = reconcile_source(candidate, base)
        self.assertEqual(report["breakdown"]["existing_multiweek_publication"], 1)
        self.assertEqual(report["unresolved_count"], 0)

        # A different event sharing the article link cannot be hidden by this exemption.
        base["events"][-1]["event"]["venue"] = "全然違う会場"
        report = reconcile_source(candidate, base)
        self.assertEqual(report["breakdown"]["ambiguous_existing_links"], 1)

    def test_roundup_parent_never_counts_as_missing_individual_event(self):
        evidence = {"source_id": "itabashi_times_event", "status": "checked", "failures": [],
                    "candidates": [{"candidate_id": "parent-1", "name": "11月まとめ",
                                    "candidate_type": "collection_index",
                                    "discovery_url": "https://itabashi-times.com/archives/event202611.html"},
                                   {"candidate_id": "child-1", "name": "子ども体験",
                                    "candidate_type": "roundup_child_lead", "date_hints": [],
                                    "discovery_url": "https://itabashi-times.com/archives/child.html"}]}
        r = reconcile_source(evidence, snapshot())
        self.assertEqual(r["breakdown"]["index_only"], 1)
        self.assertEqual(r["breakdown"]["roundup_child_unverified"], 1)

    def test_source_failure_keeps_observed_candidates_but_denies_completed_audit(self):
        e = {"source_id": "nakano_official_tourism", "status": "source_error",
             "failures": [{"url": NAKANO, "error": "403"}],
             "candidates": [{"candidate_id": "x", "candidate_type": "event_lead",
                             "name": "test", "discovery_url": "https://www.nakano-kanko.com/event-info/event-2/"}]}
        r = reconcile_source(e, snapshot())
        self.assertEqual(r["status"], "source_error")
        self.assertIsNone(r["candidate_count"])
        self.assertEqual(r["observed_candidate_count"], 1)


if __name__ == "__main__":
    unittest.main()
