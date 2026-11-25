import copy,json,os,subprocess,sys,tempfile,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from validate_family_fit_quality import inspect_assessment,check,decision_index
ROOT=Path(__file__).resolve().parents[1]
def reviewed(grade='A'):
 rows=json.loads((ROOT/'research/weekly_family_fit_review_20261114/review.json').read_text())['records']
 return copy.deepcopy(next(r['after_family_fit'] for r in rows if r['after_family_fit']['overall']==grade))
class QualityTests(unittest.TestCase):
 def test_a_may_include_b_and_unknown_without_average_or_blanket_upgrade(self):
  f=reviewed();self.assertFalse(inspect_assessment(f));f['axes']['burden']={'grade':'unknown','reason':'混雑は未記載'};f['review']['unsupported_axes']=['burden'];self.assertFalse(inspect_assessment(f))
  self.assertFalse(inspect_assessment(reviewed('B')))
 def test_verified_transport_reason_is_not_a_rating_reason(self):
  f=reviewed();f['reason']='公式または主催者提供の詳細本文で日付・会場・参加条件を確認。';self.assertTrue(any('overall reason' in e for e in inspect_assessment(f)))
 def test_default_grade_missing_review_and_evidence_are_blocked(self):
  for mutate in [lambda x:x.pop('review'),lambda x:x['review'].update(evidence=[]),lambda x:x['review'].update(grade_comparison='総合評価はB。')]:
   f=reviewed();mutate(f);self.assertTrue(inspect_assessment(f))
 def test_admission_accompaniment_and_performers_are_not_child_target(self):
  for basis in ['all_ages','age_eligible','accompaniment_only','performers_are_children']:
   f=reviewed();f['review']['audience_basis']=basis;f['axes']['child_target']['grade']='A';self.assertTrue(any('child-targeted' in e for e in inspect_assessment(f)))
 def test_adult_activity_and_unconfirmed_safety_cannot_be_scored_as_child_benefits(self):
  f=reviewed();f['review'].update(audience_basis='accompaniment_only',child_activity_confirmed=False);f['axes']['child_target']['grade']='B';f['axes']['interactivity']['grade']='A';self.assertTrue(any('adult activity' in e for e in inspect_assessment(f)))
  f=reviewed();f['review']['unsupported_axes']=['burden'];f['axes']['burden']['grade']='A';self.assertTrue(any('unknown' in e for e in inspect_assessment(f)))
 def test_explicit_legacy_alias_is_unique_and_candidate_id_is_preserved(self):
  row={'candidate_id':'historical-candidate','published_event_id':'published-id','name':'same'}
  result=decision_index([row]);self.assertIs(result['published-id'],row);self.assertIs(result['historical-candidate'],row)
  with self.assertRaisesRegex(ValueError,'ambiguous'):
   decision_index([row,{'candidate_id':'other','published_event_id':'published-id'}])
 def test_delta_gate_preserves_legacy_but_rejects_new_unreviewed_or_mismatched_ratings(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d);(root/'site/data').mkdir(parents=True);w='2026-11-14';legacy=reviewed('B');legacy.pop('review');event={'id':'old','name':'legacy','official_url':'https://example.org/old','venue':'hall','family_fit':legacy}
   def write(n,v):(root/'site/data'/n).write_text(json.dumps(v,ensure_ascii=False))
   write('manifest.json',{'weekends':[{'sat':w,'file':w+'.json'}]});write(w+'.json',{'events':[event],'run_file':w+'-run.json'});write(w+'-run.json',{'source_data':{'decision_file':w+'-decisions.json'}});write(w+'-decisions.json',{'decisions':[{'candidate_id':'old','family_fit':legacy}]})
   subprocess.run(['git','init','-q',d],check=True);subprocess.run(['git','-C',d,'add','.'],check=True);subprocess.run(['git','-C',d,'-c','user.name=Test','-c','user.email=test@example.org','commit','-qm','base'],check=True);base=subprocess.check_output(['git','-C',d,'rev-parse','HEAD'],text=True).strip();previous=os.getcwd()
   try:
    os.chdir(d);self.assertEqual(check(base,'site/data'),0)
    new=copy.deepcopy(event);new['id']='new';write(w+'.json',{'events':[event,new],'run_file':w+'-run.json'})
    with self.assertRaisesRegex(ValueError,'individual evidence review'):check(base,'site/data')
    new['family_fit']=reviewed();write(w+'.json',{'events':[event,new],'run_file':w+'-run.json'});write(w+'-decisions.json',{'decisions':[{'candidate_id':'old','family_fit':legacy},{'candidate_id':'new','family_fit':new['family_fit']}]});self.assertEqual(check(base,'site/data'),1)
    alias={'candidate_id':'historical-new','published_event_id':'new','name':new['name'],'family_fit':new['family_fit']}
    write(w+'-decisions.json',{'decisions':[{'candidate_id':'old','family_fit':legacy},alias]});self.assertEqual(check(base,'site/data'),1)
    alias['name']='different';write(w+'-decisions.json',{'decisions':[{'candidate_id':'old','family_fit':legacy},alias]})
    with self.assertRaisesRegex(ValueError,'does not match'):check(base,'site/data')
    bad=copy.deepcopy(new['family_fit']);bad['overall']='B';write(w+'-decisions.json',{'decisions':[{'candidate_id':'old','family_fit':legacy},{'candidate_id':'new','family_fit':bad}]})
    with self.assertRaisesRegex(ValueError,'disagree'):check(base,'site/data')
   finally:os.chdir(previous)
if __name__=='__main__':unittest.main()
