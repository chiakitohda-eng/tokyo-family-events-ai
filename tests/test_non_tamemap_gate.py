import copy
import json
from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from validate_non_tamemap_addition import load_spec,expected_outputs,compare_outputs,WEEKS,COUNTS


class NonTamemapGateTests(unittest.TestCase):
    def fixture(self):
        docs={'manifest.json':{'generated':'2026-11-01','weekends':[{'sat':w,'count':4} for w in WEEKS],'holidays':['2026-11-23']},'update_history.json':{'history':[{'run_id':'protected'}]}}
        for w in WEEKS:
            docs[w+'.json']={'generated':'2026-11-01','events':[{'id':'old','price':'old'}],'event_files':['old-shard.json'],'coverage':{'published_count':4,'candidate_count':9,'sources_checked':17,'wards':[{'ward':ward,'published_count':1,'candidate_count':2,'status':'error'} for ward in ('中野区','杉並区','練馬区','板橋区','目黒区','北区','荒川区','江戸川区','品川区','台東区','墨田区','江東区','豊島区','足立区')]}}
            docs[w+'-verification.json']={'events':[{'id':'old','status':'verified'}],'summary':{'total':4,'verified':4}}
            docs[w+'-decisions.json']={'rubric_version':'family-fit-v1' if w==WEEKS[0] else 'family-fit-v2','decisions':[{'candidate_id':'old'}],'summary':{'candidate_total':9,'published':4}}
            docs[w+'-run.json']={'summary':{'published':4,'verified':4},'discovery_evidence':{'status':'error','http_status':403}}
        return docs

    def test_old_events_source_debt_holidays_and_history_remain_exactly(self):
        old=self.fixture();unchanged=copy.deepcopy(old);out=expected_outputs(old.__getitem__,load_spec(),'2026-11-14T00:00:00Z')
        self.assertEqual(old,unchanged)
        self.assertEqual(len(out),27)
        self.assertEqual(out['manifest.json']['holidays'],old['manifest.json']['holidays'])
        self.assertEqual(out['update_history.json']['history'][0],old['update_history.json']['history'][0])
        for w in WEEKS:
            self.assertEqual(out[w+'.json']['events'],old[w+'.json']['events'])
            self.assertEqual(out[w+'-run.json']['discovery_evidence'],old[w+'-run.json']['discovery_evidence'])
            self.assertEqual(out[w+'.json']['coverage']['sources_checked'],17)
            self.assertEqual(out[w+'-verification.json']['events'][0],old[w+'-verification.json']['events'][0])
        first=out[WEEKS[0]+'-decisions.json']['decisions'][-1]
        self.assertEqual(first['family_fit']['rubric_version'],'family-fit-v1')
        self.assertEqual(first['canonical_family_fit_v2']['rubric_version'],'family-fit-v2')

    def test_event_old_evidence_history_and_extra_paths_cannot_be_mutated(self):
        expected=expected_outputs(self.fixture().__getitem__,load_spec(),'2026-11-14T00:00:00Z')
        for mutate in (
            lambda x:x[WEEKS[0]+'.json']['events'].clear(),
            lambda x:x[WEEKS[1]+'-run.json']['discovery_evidence'].update(status='checked'),
            lambda x:x['update_history.json']['history'].pop(0),
            lambda x:x.update({'discovery_sources.json':{}}),
            lambda x:x[WEEKS[0]+'-events-non-tamemap-20261114.json'][0].update(price='9999円'),
        ):
            actual=copy.deepcopy(expected);mutate(actual)
            with self.assertRaises(ValueError):compare_outputs(actual,expected)

    def test_new_program_audiences_costs_and_closed_subprograms(self):
        rows=load_spec();self.assertEqual(len(rows),40)
        self.assertFalse(any('tamemap.net' in r['event']['official_url'] for r in rows))
        english=next(r['event'] for r in rows if r['review_key']=='adachi-lfesta-english')
        self.assertEqual(english['price'],'')
        self.assertEqual(english['family_fit']['axes']['cost']['grade'],'unknown')
        self.assertIn('就学前',english['description'])
        self.assertFalse(any('ピックルボール' in r['event']['name'] for r in rows))
        self.assertFalse(any('赤ちゃんから楽しめる' in r['event']['name'] for r in rows))
        for r in rows:
            self.assertGreaterEqual(r['event']['date_start'],'2026-11-15')
            self.assertEqual(r['event']['family_fit']['review']['method'],'individual_evidence_review')
        matsuri=next(r['event'] for r in rows if r['review_key']=='what-matsuri-art')
        self.assertIn('17:00',matsuri['time'])
        for r in rows:
            if r['review_key'] in ('toshima-4koma-museum','toshima-4koma-retro','toshima-tsunoda','edogawa-chrysanthemum') and r['week']=='2026-11-21':
                self.assertEqual(r['event']['date_end'],'2026-11-23')

if __name__=='__main__':unittest.main()
