import copy,json,subprocess,sys,unittest
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'tools'))
from validate_all_remaining_evidence_20261115 import BASE,load_spec,expected_outputs,compare_outputs
class AllRemainingEvidenceTests(unittest.TestCase):
 def test_closed_registration_and_regional_children_are_separate(self):
  rows={r['index']:r for r in load_spec()['assessment_reviews']}
  self.assertEqual(set(rows),{27,29,36,46})
  for i in [36,46]:self.assertEqual(rows[i]['after_family_fit']['axes']['reservation']['grade'],'C')
  self.assertIn('11:30',rows[29]['after_family_fit']['reason'])
  self.assertIn('午前',rows[29]['after_family_fit']['reason'])
  for r in rows.values():self.assertEqual(r['before_family_fit']['overall'],r['after_family_fit']['overall'])
 def test_archived_primary_text_does_not_become_live_http_success(self):
  for r in load_spec()['assessment_reviews']:
   ev=r['after_family_fit']['review']['evidence'][0]
   self.assertIn(ev['capture_method'],['indexed_primary_publication','organizer_poster_republished_photo'])
   self.assertNotIn('http_status',ev)
   self.assertTrue(ev['hash_scope'])
  ledger=json.loads((R/'research/all_remaining_evidence_20261115/review_ledger.json').read_text())
  self.assertFalse(ledger['all_primary_content_verified'])
  self.assertEqual(len(ledger['records']),20)
  held=[r for r in ledger['records']if r['status']=='withheld_insufficient_evidence']
  self.assertEqual(len(held),9)
  self.assertTrue(all(r['decision']=='do_not_add' and r['primary_content_confirmed']is False and r['decision_reason']and r['evidence_urls'] for r in held))
 def test_all_event_facts_history_and_failed_source_checks_retained(self):
  old=lambda n:json.loads(subprocess.check_output(['git','show',BASE+':site/data/'+n],cwd=R))
  spec=load_spec();out=expected_outputs(old,spec,'2026-11-15T04:30:00Z')
  self.assertEqual(out['update_history.json']['history'][:-1],old('update_history.json')['history'])
  for r in spec['assessment_reviews']:
   a=copy.deepcopy(next(e for e in out[r['event_file']]if e['id']==r['id']));b=copy.deepcopy(next(e for e in old(r['event_file'])if e['id']==r['id']));a.pop('family_fit');b.pop('family_fit');self.assertEqual(a,b)
  run=copy.deepcopy(out['2026-11-07-run.json']);run.pop('all_remaining_evidence_20261115');self.assertEqual(run,old('2026-11-07-run.json'))
  bad=copy.deepcopy(out);bad['update_history.json']['history'].pop(0)
  with self.assertRaises(ValueError):compare_outputs(bad,out)
  bad=copy.deepcopy(out);r=spec['assessment_reviews'][0];next(e for e in bad[r['event_file']]if e['id']==r['id'])['venue']='different event'
  with self.assertRaises(ValueError):compare_outputs(bad,out)
if __name__=='__main__':unittest.main()
