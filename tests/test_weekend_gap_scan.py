import datetime as dt
import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "tools"))
import weekend_gap_scan as w  # noqa: E402

T = w.target_dates("2026-11-07")


class MatchTests(unittest.TestCase):
    def test_single_dates(self):
        self.assertEqual(w.page_matches("開催日 11月8日（日）10時", T), ["2026-11-08"])
        self.assertEqual(w.page_matches("2026-11-07 開催", T), ["2026-11-07"])
        self.assertEqual(w.page_matches("１１月７日", T), ["2026-11-07"])  # full-width digits are normalized

    def test_no_false_positive_on_prefix_digits(self):
        self.assertEqual(w.page_matches("11月17日 開催", T), [])
        self.assertEqual(w.page_matches("11月27日", T), [])

    def test_pair_and_range(self):
        self.assertEqual(w.page_matches("11月7日（土）・8日（日）", T), ["2026-11-07", "2026-11-08"])
        self.assertEqual(w.page_matches("2026年10月1日～12月25日", T), ["2026-11-07", "2026-11-08"])
        self.assertEqual(w.page_matches("11月5日〜11月7日", T), ["2026-11-07"])
        self.assertEqual(w.page_matches("11月9日～12月1日", T), [])

    def test_expand_templates(self):
        urls = w.expand("https://x/c?y={YYYY}&m={M}&d={D}", T)
        self.assertEqual(urls, ["https://x/c?y=2026&m=11&d=7", "https://x/c?y=2026&m=11&d=8"])
        self.assertEqual(w.expand("https://x/", T), ["https://x/"])

    def test_config_is_valid(self):
        cfg = json.loads((Path(__file__).parents[1] / "policy/weekend_gap_sources.json").read_text(encoding="utf-8"))
        ids = [s["id"] for s in cfg["sources"]]
        self.assertEqual(len(ids), len(set(ids)))
        for s in cfg["sources"]:
            self.assertTrue(s["urls"])
            self.assertTrue(all(u.startswith("https://") for u in s["urls"]))

    def test_default_start_is_a_saturday(self):
        today = dt.date(2026, 11, 3)
        start = today + dt.timedelta(days=(5 - today.weekday()) % 7 or 7)
        self.assertEqual(start, dt.date(2026, 11, 7))


if __name__ == "__main__":
    unittest.main()
