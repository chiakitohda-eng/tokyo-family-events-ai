import copy
import json
from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from validate_final_backlog_addition import load_spec,expected_outputs,compare_outputs,WEEKS,COUNTS


class FinalBacklogGateTests(unittest.TestCase):
    def fixture(self):
        docs={'manifest.json':{'generated':'2026-11-01','weekends':[{'sat':w,'count':4} for w in WEEKS],'holidays':['2026-11-23']},'update_history.json':{'history':[{'run_id':'protected'}]}}
        for w in WEEKS:
            docs[w+'.json']={'generated':'2026-11-01','events':[{'id':'old','price':'old'}],'event_files':['old-shard.json'],'coverage':{'published_count':4,'candidate_count':9,'sources_checked':17,'wards':[{'ward':ward,'published_count':1,'candidate_count':2,'status':'error'} for ward in ('中野区','杉並区','練馬区','板橋区')]}}
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
            lambda x:x[WEEKS[0]+'-events-reviewed-backlog-20261114.json'][0].update(price='9999円'),
        ):
            actual=copy.deepcopy(expected);mutate(actual)
            with self.assertRaises(ValueError):compare_outputs(actual,expected)

    def test_closures_sold_out_previous_year_times_and_booking_are_not_guessed(self):
        rows=load_spec()
        self.assertEqual(len(rows),sum(COUNTS.values()))
        for r in rows:
            e=r['event']
            if r['review_key'] in ('nakano-162738','nakano-163067'):
                self.assertNotEqual(e['date_end'],'2026-11-15')
                self.assertNotEqual(e['date_end'],'2026-11-23')
            if r['review_key'].startswith('park-') and e['date_start']>='2026-12-01' and e['reservation']['required']:
                self.assertIn('11/15 9:00',e['reservation']['note'])
            if r['review_key']=='itabashi-johoku':self.assertEqual(e['time'],'')
            if r['verification']['source_kind']=='organizer_provided_partner':
                self.assertIn('pc.tamemap.net',e['official_url'])
        cafe=next(r['event'] for r in rows if r['review_key']=='nakano-160639')
        self.assertTrue(cafe['reservation']['required']);self.assertIn('前日',cafe['reservation']['note'])
        self.assertFalse(any(r['review_key'] in ('nakano-160665','nakano-162435','nakano-143271') for r in rows))
        play=next(r['event'] for r in rows if r['review_key']=='suginami-28661-play')
        self.assertFalse(play['reservation']['required'])
        self.assertEqual(sum(r['review_key']=='nakano-161828' for r in rows),1)


if __name__=='__main__':unittest.main()
