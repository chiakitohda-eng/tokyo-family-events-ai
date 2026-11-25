import copy,json,subprocess,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
from validate_evidence_recovery_20261115 import BASE,load_spec,expected_outputs,compare_outputs
class EvidenceRecoveryTests(unittest.TestCase):
 def test_general_admission_and_separate_programme_conditions(self):
  spec=load_spec();events={r['review_key']:r['event']for r in spec['records']}
  self.assertNotIn('magokoro-marche',events) # already published from the same official source
  m=events['mucha-weekend'];self.assertEqual((m['date_start'],m['date_end']),('2026-11-21','2026-11-22'));self.assertIn('18:00',m['time']);self.assertIn('途中',m['family_fit']['axes']['stay_flexibility']['reason']);self.assertIn('11/23',m['reservation']['note'])
  m=events['meguro-dance-view'];self.assertIn('幼児',m['description']);self.assertIn('定員',m['reservation']['note']);self.assertIn('1200',m['price']);self.assertIn('11/13',m['reservation']['note'])
  m=events['kita-iwate-fair'];self.assertIn('店舗',m['time']);self.assertIn('日曜休業',m['family_fit']['reason'])
  for r in spec['records']:
   self.assertGreaterEqual(r['event']['date_start'],'2026-11-21');self.assertNotIn('tamemap',r['event']['official_url'])
  for r in spec['assessment_reviews']:
   self.assertEqual(r['before_family_fit']['overall'],r['after_family_fit']['overall']);self.assertEqual(len(r['after_family_fit']['axes']),8)
 def test_no_new_official_url_duplicates_existing_week(self):
  old=lambda n:json.loads(subprocess.check_output(['git','show',BASE+':site/data/'+n],cwd=ROOT))
  for r in load_spec()['records']:
   doc=old(r['week']+'.json');es=list(doc.get('events',[]))
   for n in doc.get('event_files',[]):es.extend(old(n))
   urls={e.get('official_url','').split('?')[0].rstrip('/') for e in es}
   self.assertNotIn(r['event']['official_url'].split('?')[0].rstrip('/'),urls)
 def test_all_old_facts_history_and_source_checks_preserved(self):
  old=lambda n:json.loads(subprocess.check_output(['git','show',BASE+':site/data/'+n],cwd=ROOT));spec=load_spec();out=expected_outputs(old,spec,'2026-11-14T22:00:00Z')
  self.assertEqual(out['update_history.json']['history'][:-1],old('update_history.json')['history'])
  for w in ['2026-11-07','2026-11-14','2026-11-21','2026-11-28']:
   a,b=copy.deepcopy(out[w+'-run.json']),copy.deepcopy(old(w+'-run.json'));a.pop('evidence_recovery_20261115');sa,sb=a.pop('summary'),b.pop('summary');self.assertEqual(a,b);self.assertEqual(sa.get('announced'),sb.get('announced'))
  for r in spec['assessment_reviews']:
   a=copy.deepcopy(next(e for e in out[r['event_file']]if e['id']==r['id']));b=copy.deepcopy(next(e for e in old(r['event_file'])if e['id']==r['id']));a.pop('family_fit');b.pop('family_fit');self.assertEqual(a,b)
  bad=copy.deepcopy(out);r=spec['assessment_reviews'][0];next(e for e in bad[r['event_file']]if e['id']==r['id'])['venue']='unapproved venue'
  with self.assertRaises(ValueError):compare_outputs(bad,out)
  bad=copy.deepcopy(out);bad['update_history.json']['history'].pop(0)
  with self.assertRaises(ValueError):compare_outputs(bad,out)
 def test_every_original_hold_and_failed_source_remain_accountable(self):
  rows=json.loads((ROOT/'research/evidence_recovery_20261115/review_ledger.json').read_text())['records'];self.assertEqual(len(rows),36)
  cand=[r for r in rows if r['scope']=='original_candidate'];self.assertEqual(len(cand),24);self.assertEqual(sum(r['status']=='needs_primary_evidence'for r in cand),17)
  self.assertTrue(all(r['original_retrieval_unchanged']for r in cand));self.assertEqual(sum(r['status']=='assessment_reconfirmed'for r in rows),6)
if __name__=='__main__':unittest.main()
