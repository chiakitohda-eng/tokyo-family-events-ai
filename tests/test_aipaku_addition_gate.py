import copy,json,subprocess,sys,unittest
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'tools'))
from validate_aipaku_addition_20261115 import BASE,load_spec,expected_outputs,compare_outputs
class AipakuAdditionTests(unittest.TestCase):
 def test_current_november_prices_and_parent_workshops(self):
  rows=load_spec();self.assertEqual(len(rows),1);e=rows[0]['event'];self.assertEqual(e['date_start'],'2026-11-15');self.assertEqual(e['date_end'],'2026-11-15');self.assertIn('小学生以上900円',e['price']);self.assertIn('未就学児無料',e['price']);self.assertIn('別料金',e['price']);self.assertIn('キャッシュレス',e['reservation']['note']);self.assertIn('11/9',e['reservation']['note']);self.assertEqual(e['family_fit']['grade'],'A');self.assertEqual(len(e['family_fit']['axes']),8);self.assertIn('11/15',e['family_fit']['reason']);self.assertTrue(e['image'].startswith('https://www.sumitomo-sankakuhiroba.jp/'))
 def test_previous_602_stage_records_and_all_source_errors_unchanged(self):
  old=lambda n:json.loads(subprocess.check_output(['git','show',BASE+':site/data/'+n],cwd=R));out=expected_outputs(old,load_spec(),'2026-11-15T01:00:00Z');w='2026-11-14'
  self.assertEqual(out[w+'.json']['events'],old(w+'.json')['events']);self.assertEqual(out[w+'-verification.json']['events'][:-1],old(w+'-verification.json')['events']);self.assertEqual(out[w+'-decisions.json']['decisions'][:-1],old(w+'-decisions.json')['decisions']);self.assertEqual(out['update_history.json']['history'][:-1],old('update_history.json')['history'])
  before=old(w+'-run.json');after=copy.deepcopy(out[w+'-run.json']);after.pop('aipaku_review_20261115');after['summary']=before['summary'];self.assertEqual(after,before)
  bad=copy.deepcopy(out);bad[w+'-events-aipaku-20261115.json'][0]['price']='小学生無料'
  with self.assertRaises(ValueError):compare_outputs(bad,out)
 def test_no_existing_alias_readded(self):
  rows=load_spec();w=rows[0]['week'];old=lambda n:json.loads(subprocess.check_output(['git','show',BASE+':site/data/'+n],cwd=R));d=old(w+'.json');es=list(d['events'])
  for n in d['event_files']:es.extend(old(n))
  self.assertFalse(any('あいぱく'in e['name']or'i-89.jp'in e.get('official_url','')for e in es))
if __name__=='__main__':unittest.main()
