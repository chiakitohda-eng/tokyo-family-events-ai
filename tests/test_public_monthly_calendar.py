import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from review_public_monthly_calendar import monthly_dates


class CalendarEvidenceTests(unittest.TestCase):
    MASTER = 'BEGIN:VEVENT\nUID:kitchen\nDTSTART;VALUE=DATE:20250713\nRRULE:FREQ=MONTHLY;BYDAY=2SU\n{}END:VEVENT\n'

    def test_explicit_ongoing_rule_does_not_reuse_past_year(self):
        self.assertEqual(monthly_dates(self.MASTER.format(''), 'kitchen', '2026-11-15', '2026-12-13'), ['2026-12-13'])

    def test_excluded_and_cancelled_dates_are_not_published(self):
        self.assertEqual(monthly_dates(self.MASTER.format('EXDATE;VALUE=DATE:20261213\n'), 'kitchen', '2026-11-15', '2026-12-13'), [])
        self.assertEqual(monthly_dates(self.MASTER.format('STATUS:CANCELLED\n'), 'kitchen', '2026-11-15', '2026-12-13'), [])

    def test_moved_and_cancelled_instances_override_the_regular_day(self):
        override = 'BEGIN:VEVENT\nUID:kitchen\nRECURRENCE-ID;VALUE=DATE:20261213\nDTSTART;VALUE=DATE:20261206\n{}END:VEVENT'
        self.assertEqual(monthly_dates(self.MASTER.format('')+override.format(''), 'kitchen', '2026-11-15', '2026-12-13'), ['2026-12-06'])
        self.assertEqual(monthly_dates(self.MASTER.format('')+override.format('STATUS:CANCELLED\n'), 'kitchen', '2026-11-15', '2026-12-13'), [])

    def test_unsupported_rules_and_duplicate_masters_require_review(self):
        for text in [self.MASTER.format('').replace('FREQ=MONTHLY', 'FREQ=WEEKLY'), self.MASTER.format('')*2]:
            with self.assertRaises(ValueError):
                monthly_dates(text, 'kitchen', '2026-11-15', '2026-12-13')

    def test_actual_public_calendar_exceptions_are_applied(self):
        root = Path(__file__).resolve().parents[1] / 'research/remaining_evidence_review_20261115'
        text = (root / 'kitchen-calendar-extract.ics').read_text()
        uid = '4ldksf95p78qva310jfgp5n0g6@google.com'
        self.assertEqual(monthly_dates(text, uid, '2025-09-01', '2025-09-30'), ['2025-09-21'])
        self.assertEqual(monthly_dates(text, uid, '2026-02-01', '2026-02-28'), [])
        self.assertEqual(monthly_dates(text, uid, '2026-11-15', '2026-12-13'), ['2026-12-13'])


if __name__ == '__main__':
    unittest.main()
