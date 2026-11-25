import copy,json,sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from validate_weekly_family_fit_correction import load_spec,expected_outputs,compare_outputs
class WeeklyGateTests(unittest.TestCase):
 def fixture(self):
  rows=load_spec()['records'];weeks=sorted({r['week'] for r in rows});docs={'manifest.json':{'generated':'old','weekends':[{'sat':w,'count':99} for w in weeks],'holidays':['2026-11-23']},'update_history.json':{'history':[{'id':'protected-history'}]}}
  for w in weeks:
   docs[w+'.json']={'generated':'old','events':[{'id':'protected'}]};docs[w+'-decisions.json']={'rubric_version':'family-fit-v1' if w=='2026-11-14' else 'family-fit-v2','decisions':[]};docs[w+'-verification.json']={'events':[]};docs[w+'-run.json']={'summary':{'published':99},'source_debt':{'status':'error','http_status':403}}
  for r in rows:
   docs.setdefault(r['event_file'],[]).append({'id':r['id'],'name':r['name'],'time':'original','family_fit':copy.deepcopy(r['before_family_fit'])});docs[r['week']+'-decisions.json']['decisions'].append({'candidate_id':r['id'],'family_fit':r['before_family_fit'],'positive_signals':[],'negative_signals':[],'reasons':['old'],'evidence':[]});docs[r['week']+'-verification.json']['events'].append({'id':r['id']})
  return docs
 def test_scope_counts_and_no_fact_history_or_source_changes(self):
  s=load_spec();self.assertEqual(len(s['records']),200);self.assertEqual(s['program_count'],139);old=self.fixture();before=copy.deepcopy(old);out=expected_outputs(old.__getitem__,s,'new');self.assertEqual(old,before)
  self.assertEqual(out['manifest.json']['weekends'],old['manifest.json']['weekends']);self.assertEqual(out['update_history.json']['history'][0],old['update_history.json']['history'][0])
  for r in s['records']:
   after=next(e for e in out[r['event_file']] if e['id']==r['id']);prior=next(e for e in old[r['event_file']] if e['id']==r['id']);self.assertEqual({k:v for k,v in after.items() if k!='family_fit'},{k:v for k,v in prior.items() if k!='family_fit'})
  for w in {r['week'] for r in s['records']}:self.assertEqual(out[w+'-run.json']['source_debt'],old[w+'-run.json']['source_debt'])
 def test_every_frozen_quote_matches_its_captured_source(self):
  programs=json.loads((Path(__file__).resolve().parents[1]/'research/weekly_family_fit_review_20261114/source_evidence.json').read_text())['programs']
  by_hash={p['primary_capture']['sha256']:p['body'] for p in programs}
  for r in load_spec()['records']:
   for evidence in r['after_family_fit']['review']['evidence']:
    self.assertIn(evidence['quote'],by_hash[evidence['sha256']])
 def test_unreviewed_mutations_cannot_be_hidden_in_rating_update(self):
  s=load_spec();expected=expected_outputs(self.fixture().__getitem__,s,'new');p=s['records'][0]['event_file']
  for change in [lambda a:a[p][0].update(time='new'),lambda a:a['update_history.json']['history'].pop(0),lambda a:a.update({'discovery_sources.json':{}})]:
   actual=copy.deepcopy(expected);change(actual)
   with self.assertRaises(ValueError):compare_outputs(actual,expected)
if __name__=='__main__':unittest.main()
