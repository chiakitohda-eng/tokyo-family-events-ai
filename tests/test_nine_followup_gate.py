import unittest,sys,json
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'tools'))
from validate_nine_followup_addition_20261115 import load_spec
class NineFollowupTests(unittest.TestCase):
 def test_official_conflict_is_not_resolved_by_choosing_one_time(self):
  rows=load_spec();self.assertEqual(len(rows),1);r=rows[0];e=r['event'];self.assertEqual((e['date_start'],e['date_end']),('2026-11-21','2026-11-22'));self.assertIn('18:00',e['time']);self.assertIn('19:00',e['time']);self.assertEqual(r['verification']['fields']['time'],'unknown');self.assertIn('入場無料',e['price']);self.assertIsNone(e['reservation']['required']);self.assertEqual(e['family_fit']['axes']['child_target']['grade'],'unknown')
 def test_outbound_drafts_are_not_sent_and_nine_issues_remain_open(self):
  root=R/'research/nine_followup_20261115';follow=json.loads((root/'followup.json').read_text());self.assertEqual(follow['unresolved_units'],9);self.assertTrue(all(r['resolution_status']=='unresolved'for r in follow['records']))
  drafts=json.loads((root/'contact_drafts.json').read_text());self.assertEqual(len(drafts['records']),9);self.assertTrue(all(r['sent']is False for r in drafts['records']))
if __name__=='__main__':unittest.main()
