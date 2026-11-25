import copy,sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from validate_non_tamemap_last_addition import load_spec,expected_outputs,compare_outputs,BASE
class LastGateTests(unittest.TestCase):
 def test_exam_facts_and_review(self):
  rows=load_spec();self.assertEqual(len(rows),1);e=rows[0]['event']
  self.assertEqual(e['date_start'],'2026-11-29');self.assertIn('11/16',e['reservation']['note'])
  self.assertIn('小中学生500円',e['price']);self.assertEqual(e['family_fit']['grade'],'B')
  self.assertIn('60分',e['family_fit']['review']['limitations'][0])
 def test_history_source_errors_and_old_events_are_preserved(self):
  import json,subprocess
  old=lambda n:json.loads(subprocess.check_output(['git','show',BASE+':site/data/'+n]))
  out=expected_outputs(old,load_spec(),'2026-11-14T10:00:00Z');self.assertEqual(len(out),7)
  self.assertEqual(out['update_history.json']['history'][:-1],old('update_history.json')['history'])
  self.assertEqual(out['2026-11-28.json']['events'],old('2026-11-28.json')['events'])
  self.assertEqual(out['2026-11-28-run.json']['discovery_evidence'],old('2026-11-28-run.json')['discovery_evidence'])
  for mutate in [lambda x:x['update_history.json']['history'].pop(0),lambda x:x['2026-11-28-events-non-tamemap-last-20261114.json'][0].update(price='無料'),lambda x:x.update({'app.js':{}})]:
   changed=copy.deepcopy(out);mutate(changed)
   with self.assertRaises(ValueError):compare_outputs(changed,out)
if __name__=='__main__':unittest.main()
