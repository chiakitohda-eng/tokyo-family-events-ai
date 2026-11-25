import copy, json, sys, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
import rollover_evidence_20261118 as ev

ROOT = Path(__file__).resolve().parents[1]
DIR = ROOT / 'research' / '2026-11-18-source-evidence'


class RolloverEvidenceGate(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.requests = json.loads((DIR / 'requests.json').read_text(encoding='utf-8'))

    def test_committed_receipts_match_the_audited_artifact(self):
        ev.check_pins(DIR)

    def test_failure_ledger_is_closed(self):
        ev.check_failure_ledger(self.requests)
        flipped = copy.deepcopy(self.requests)
        for r in flipped:
            if r.get('source_id') == 'tamemap_nakano':
                r['status'] = 'checked'
        with self.assertRaises(ValueError):
            ev.check_failure_ledger(flipped)

    def test_new_unlisted_failure_is_rejected(self):
        broken = copy.deepcopy(self.requests)
        next(r for r in broken if r['kind'] == 'ai_cross')['status'] = 'error'
        with self.assertRaises(ValueError):
            ev.check_failure_ledger(broken)

    def test_every_ward_week_has_three_checked_queries_and_a_home_check(self):
        for sat in ev.SATS:
            rows = ev.derive_wards(self.requests, sat)
            self.assertEqual(len(rows), 23)
            for row in rows:
                self.assertEqual(len(row['query_logs']), 3)
                self.assertEqual(len(row['source_checks']), 1)

    def test_missing_ward_receipt_is_refused_not_invented(self):
        thin = [r for r in self.requests if not (r['kind'] == 'ai_cross' and r['ward'] == '港区' and r['week'] == '2026-12-19')]
        with self.assertRaises(ValueError):
            ev.derive_wards(thin, '2026-12-19')


if __name__ == '__main__':
    unittest.main()
