import copy
import json
from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from validate_non_tamemap_next_addition import load_spec,expected_outputs,compare_outputs,WEEKS,COUNTS


class NonTamemapNextGateTests(unittest.TestCase):
    def fixture(self):
        docs={'manifest.json':{'generated':'2026-11-01','weekends':[{'sat':w,'count':4} for w in WEEKS],'holidays':['2026-11-23']},'update_history.json':{'history':[{'run_id':'protected'}]}}
        for w in WEEKS:
            docs[w+'.json']={'generated':'2026-11-01','events':[{'id':'old','price':'old'}],'event_files':['old-shard.json'],'coverage':{'published_count':4,'candidate_count':9,'sources_checked':17,'wards':[{'ward':ward,'published_count':1,'candidate_count':2,'status':'error'} for ward in ('中野区','杉並区','練馬区','板橋区','目黒区','北区','荒川区','江戸川区','品川区','台東区','墨田区','江東区','豊島区','足立区','港区','千代田区')]}}
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
            lambda x:x[WEEKS[0]+'-events-non-tamemap-next-20261114.json'][0].update(price='9999円'),
        ):
            actual=copy.deepcopy(expected);mutate(actual)
            with self.assertRaises(ValueError):compare_outputs(actual,expected)

    def test_program_conditions_and_individual_assessments(self):
        rows=load_spec();self.assertEqual(len(rows),31)
        bykey={r['review_key']:r['event'] for r in rows}
        self.assertIn('11/16',bykey['minato-coffee-craft']['reservation']['note'])
        self.assertIn('小学1〜6',bykey['minato-coffee-craft']['description'])
        self.assertEqual(bykey['minato-coffee-craft']['price'],'')
        self.assertIn('110cm未満',bykey['chiyoda-bosai-horse']['description'])
        self.assertIn('同乗不可',bykey['chiyoda-bosai-horse']['description'])
        self.assertNotIn('区内在住',bykey['chiyoda-bosai-attraction']['description'])
        self.assertEqual(bykey['chiyoda-bosai-baby']['family_fit']['grade'],'B')
        self.assertIn('乳幼児自身の遊び',bykey['chiyoda-bosai-baby']['family_fit']['reason'])
        self.assertIn('19:00',bykey['nakano-hee-haw-meal']['time'])
        self.assertEqual(bykey['nakano-hee-haw-meal']['family_fit']['grade'],'B')
        self.assertEqual(bykey['meguro-math-19']['family_fit']['grade'],'C')
        self.assertTrue(next(r for r in rows if r['review_key']=='meguro-math-19')['decision']['override_reason'])
        self.assertEqual(bykey['adachi-reading-bingo']['date_start'],'2026-11-21')
        self.assertFalse(any('tamemap.net' in r['event']['official_url']for r in rows))
        for r in rows:
            self.assertGreaterEqual(r['event']['date_start'],'2026-11-15')
            self.assertEqual(r['event']['family_fit']['review']['method'],'individual_evidence_review')
            self.assertTrue(r['event']['family_fit']['review']['evidence'])
        turner=[r['event'] for r in rows if r['review_key']=='turner-exhibition' and r['week']=='2026-11-21'][0]
        self.assertEqual(turner['date_end'],'2026-11-23')
        self.assertIn('中学生以下無料',turner['price'])

if __name__=='__main__':unittest.main()
