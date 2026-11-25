import copy,json,hashlib,subprocess,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
from validate_all_non_tamemap_addition import load_spec,expected_outputs,compare_outputs,BASE
O=ROOT/'research/all_non_tamemap_review_20261114'
class AllReviewTests(unittest.TestCase):
 def test_all_851_adjudicated_and_failed_bodies_kept(self):
  rows=json.loads((O/'candidate_ledger.json').read_text());summary=json.loads((O/'review_summary.json').read_text())
  self.assertEqual([r['index'] for r in rows],list(range(851)))
  self.assertEqual(hashlib.sha256('\n'.join(r['url'] for r in rows).encode()).hexdigest(),summary['corpus_url_sha256'])
  self.assertTrue(summary['all_candidates_adjudicated']);self.assertFalse(summary['all_source_bodies_verified'])
  self.assertEqual(summary['unreviewed_candidates'],0)
  for r in rows:self.assertTrue(r['reason']);self.assertFalse(any(x in r['status']for x in ['needs_review','future_primary','future_official','retrieval_failed']))
  self.assertEqual(sum(r['retrieval']['status']!='checked' for r in rows),46)
  self.assertEqual(rows[396]['status'],'weekday_registration_closed')
  self.assertEqual(rows[530]['status'],'blocked_event_year')
 def test_separate_programme_conditions(self):
  rows=load_spec();self.assertEqual(len(rows),118);d={r['review_key']:r['event'] for r in rows}
  self.assertTrue(d['sugi-731']['reservation']['required']);self.assertFalse(d['sugi-731-walkin']['reservation']['required'])
  self.assertIn('小学1年',d['sugi-731-walkin']['description']);self.assertIn('小学校5年',d['sugi-731']['description'])
  self.assertFalse(d['sugi-803-korczak']['reservation']['required']);self.assertTrue(d['sugi-803-dialogue']['reservation']['required'])
  self.assertIn('各20人',d['shibuya-tennis-family']['reservation']['note'])
  self.assertTrue(d['playground-gym']['reservation']['required']);self.assertFalse(d['playground-walk']['reservation']['required'])
  for r in rows:
   e=r['event'];self.assertNotIn('sunshinecity.jp/archives',e['image']);self.assertGreaterEqual(e['date_start'],'2026-11-15');self.assertNotIn('tamemap',e['official_url'])
   self.assertEqual(len(e['family_fit']['axes']),8);self.assertEqual(e['family_fit']['review']['method'],'individual_evidence_review')
   if e['family_fit']['grade']in ['C','D']:self.assertTrue(r['decision']['override_reason'])
   if r['review_key']=='meguro-free-space':self.assertFalse(e['date_start']<='2026-11-22'<=e['date_end']);self.assertFalse(e['date_start']<='2026-11-23'<=e['date_end'])
  self.assertEqual(d['sugi-825']['date_start'],'2026-11-15');self.assertEqual(d['sugi-825']['date_end'],'2026-11-15')
  self.assertIn('自宅',d['tachiuo-base']['family_fit']['reason']);self.assertIn('20歳',d['world-drinks2026']['reservation']['note'])
 def test_old_records_history_and_frozen_facts(self):
  old=lambda n:json.loads(subprocess.check_output(['git','show',BASE+':site/data/'+n]))
  out=expected_outputs(old,load_spec(),'2026-11-14T12:00:00Z')
  self.assertEqual(out['update_history.json']['history'][:-1],old('update_history.json')['history'])
  for week in ['2026-11-14','2026-11-21','2026-11-28','2026-12-05','2026-12-12']:
   self.assertEqual(out[week+'.json']['events'],old(week+'.json')['events'])
   self.assertEqual(out[week+'-run.json'].get('discovery_evidence'),old(week+'-run.json').get('discovery_evidence'))
  x=copy.deepcopy(out);x['2026-11-14-events-all-non-tamemap-20261114.json'][0]['price']='推測の無料'
  with self.assertRaises(ValueError):compare_outputs(x,out)
if __name__=='__main__':unittest.main()
