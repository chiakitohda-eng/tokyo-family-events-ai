import copy,sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from validate_rail_family_fit_correction import load_spec,expected_outputs,compare_outputs
class RailAssessmentTests(unittest.TestCase):
 def fixture(self):
  s=load_spec();w=s['week'];eid=s['event_id'];fit=copy.deepcopy(s['before_family_fit'])
  return {'manifest.json':{'generated':'2026-11-14T00:00:00Z','weekends':[{'sat':w,'count':94}],'holidays':['2026-11-23']},w+'.json':{'generated':'old','events':[],'event_files':[s['event_file']],'coverage':{'published_count':94}},s['event_file']:[{'id':'keep','name':'other','family_fit':{'grade':'B'}},{'id':eid,'name':'rail','time':'','family_fit':fit}],w+'-decisions.json':{'rubric_version':'family-fit-v1','decisions':[{'candidate_id':eid,'family_fit':fit,'canonical_family_fit_v2':fit,'reasons':['old'],'evidence':[],'positive_signals':[]}]},w+'-verification.json':{'events':[{'id':eid,'fields':{'time':'unknown'},'corrections':{},'evidence':[]}]},w+'-run.json':{'discovery_evidence':{'status':'error','http_status':403},'summary':{'published':94}},'update_history.json':{'history':[{'run_id':'old'}]}}
 def test_only_selected_assessment_and_review_metadata_change(self):
  old=self.fixture();before=copy.deepcopy(old);s=load_spec();out=expected_outputs(old.__getitem__,s,'2026-11-14T05:00:00Z');self.assertEqual(old,before)
  oldevent=old[s['event_file']][1];newevent=out[s['event_file']][1];self.assertEqual({k:v for k,v in oldevent.items() if k!='family_fit'},{k:v for k,v in newevent.items() if k!='family_fit'})
  self.assertEqual(out[s['event_file']][0],old[s['event_file']][0]);self.assertEqual(out[s['week']+'-run.json']['discovery_evidence'],old[s['week']+'-run.json']['discovery_evidence']);self.assertEqual(out['update_history.json']['history'][0],old['update_history.json']['history'][0]);self.assertEqual(out['manifest.json']['weekends'],old['manifest.json']['weekends'])
 def test_no_blanket_promotion_or_unknown_assumptions(self):
  f=load_spec()['after_family_fit'];self.assertEqual(f['overall'],'A');self.assertEqual(f['axes']['age_fit']['grade'],'B');self.assertEqual(f['axes']['burden']['grade'],'unknown');self.assertIn('子ども向け',f['reason'])
 def test_facts_other_ratings_history_and_extra_files_are_rejected(self):
  s=load_spec();expected=expected_outputs(self.fixture().__getitem__,s,'2026-11-14T05:00:00Z')
  for mutate in [lambda x:x[s['event_file']][1].update(time='10:00'),lambda x:x[s['event_file']][0]['family_fit'].update(grade='A'),lambda x:x['update_history.json']['history'].pop(0),lambda x:x.update({'discovery_sources.json':{}})]:
   actual=copy.deepcopy(expected);mutate(actual)
   with self.assertRaises(ValueError):compare_outputs(actual,expected)
if __name__=='__main__':unittest.main()
