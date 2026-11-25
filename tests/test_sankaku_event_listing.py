import datetime as dt
import json
from pathlib import Path
import unittest
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"tools"))
from tools.sankaku_event_listing import parse_listing, period_dates
from tools.holiday_after_collect import html_links, inspect

def card(name='冬のあいぱく', period='2026/11/10(火)〜11/17(火)', url='https://www.i-89.jp/', cls='event_now'):
    return f'<article class="{cls}"><div class="event-period">{period}</div><h4>{name}</h4><div class="text"><p>説明</p></div><div class="detail-link-btn"><a href="{url}">詳しくはこちら</a></div></article>'

class SankakuListingTests(unittest.TestCase):
    def parse(self, body, **kw):
        return parse_listing(body,dt.date(2026,11,14),dt.date(2026,12,13),**kw)
    def test_generic_external_link_inherits_own_heading_and_period(self):
        body=card();self.assertFalse(any('i-89' in str(r) for r in html_links(body,'https://www.sumitomo-sankakuhiroba.jp/event/')[1]))
        r=self.parse(body)['candidates'][0]
        self.assertEqual(r['name'],'冬のあいぱく');self.assertEqual(r['official_url'],'https://www.i-89.jp/')
        self.assertEqual(r['matched_dates'],['2026-11-14','2026-11-15']);self.assertTrue(r['date_unverified'])
    def test_duplicate_cards_and_unrelated_event_do_not_merge(self):
        r=self.parse(card()+card(cls='event_list')+card('別の催事','2026/12/02(水)〜12/06(日)','https://example.org/other/'))
        self.assertEqual(r['official_card_count'],3);self.assertEqual(r['candidate_count'],2)
        self.assertEqual(r['candidates'][1]['matched_dates'],['2026-12-05','2026-12-06'])
    def test_past_year_missing_markup_and_bad_dates_fail_closed(self):
        self.assertEqual(self.parse(card(period='2025/11/10(月)〜11/17(月)'))['candidate_count'],0)
        for body in ['<h4>JS only</h4>',card(period='11/10〜11/17'),card(period='2026/02/30〜03/01')]:
            with self.assertRaises(ValueError):self.parse(body)
    def test_year_rollover_and_explicit_holiday(self):
        self.assertEqual(period_dates('2026/12/25(金)〜01/25(月)'),(dt.date(2026,12,25),dt.date(2027,1,25)))
        self.assertEqual(self.parse(card(period='2026/11/23(月)〜11/23(月)'))['candidate_count'],0)
        r=self.parse(card(period='2026/11/23(月)〜11/23(月)'),holiday_dates=['2026-11-23'])
        self.assertEqual(r['candidates'][0]['matched_dates'],['2026-11-23'])
    def test_collector_integration_never_treats_candidates_as_verified(self):
        url='https://www.sumitomo-sankakuhiroba.jp/event/'
        job={'kind':'explicit','source_id':'shinjuku_sankaku_hiroba','url':url,'target_start':'2026-11-14','target_end':'2026-12-13'}
        result=inspect(job,fetcher=lambda u:(200,card().encode(),u,'text/html'))
        self.assertEqual(result['status'],'checked');self.assertEqual(result['candidate_count'],1)
        self.assertEqual(result['candidate_status'],'unverified_external_organizer_links');self.assertTrue(result['candidates'][0]['date_unverified'])
        result=inspect(job,fetcher=lambda u:(200,b'<title>empty event page</title>',u,'text/html'))
        self.assertEqual(result['status'],'error');self.assertFalse(result['candidates'])
    def test_source_registered_without_mutating_legacy_sources(self):
        s=json.loads((Path(__file__).resolve().parents[1]/'site/data/discovery_sources.json').read_text());r=next(r for r in s['explicit_sources']if r['id']=='shinjuku_sankaku_hiroba')
        self.assertTrue(r['enabled']);self.assertEqual(r['search_urls'],['https://www.sumitomo-sankakuhiroba.jp/event/']);self.assertEqual(len(s['protected_legacy_source_ids']),18)

if __name__=='__main__':unittest.main()
