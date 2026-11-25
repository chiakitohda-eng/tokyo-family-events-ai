import copy
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from validate_nakano_review_addition import expected_outputs, compare_outputs, load_spec, WEEKS


class ReviewGateTests(unittest.TestCase):
    def fixture(self):
        docs = {
            "manifest.json": {"generated": "2026-11-01", "weekends": [
                {"sat": w, "count": 1} for w in WEEKS], "holidays": ["unchanged"]},
            "update_history.json": {"history": [{"run_id": "protected", "new_event_ids": ["old"]}]},
        }
        for week in WEEKS:
            docs[week + ".json"] = {"generated": "2026-11-01", "events": [{"id": "old"}],
                "event_files": [week + "-old.json"],
                "coverage": {"sources_checked": 17, "candidate_count": 4, "published_count": 1,
                    "wards": [{"ward": "中野区", "candidate_count": 2, "published_count": 1,
                               "status": "error", "queries": 0}]}}
            docs[week + "-verification.json"] = {"events": [{"id": "old", "note": "protected"}],
                                                   "summary": {"total": 1, "verified": 1}}
            docs[week + "-decisions.json"] = {"decisions": [{"candidate_id": "old", "evidence": ["old"]}],
                                               "summary": {"candidate_total": 4, "published": 1, "excluded": 3}}
            if week == WEEKS[0]:
                docs[week + "-decisions.json"]["rubric_version"] = "family-fit-v1"
            docs[week + "-run.json"] = {"summary": {"published": 1, "verified": 1},
                "discovery_evidence": {"status": "error", "http_status": 403}}
        return docs

    def test_preserves_old_records_crawl_failures_holidays_and_history(self):
        before = self.fixture()
        untouched = copy.deepcopy(before)
        out = expected_outputs(before.__getitem__, load_spec(), "2026-11-13T00:00:00Z")
        self.assertEqual(before, untouched)
        self.assertEqual(len(out), 12)
        self.assertEqual(out["manifest.json"]["holidays"], ["unchanged"])
        self.assertEqual(out["update_history.json"]["history"][0], before["update_history.json"]["history"][0])
        for week in WEEKS:
            self.assertEqual(out[week + ".json"]["events"], [{"id": "old"}])
            self.assertEqual(out[week + ".json"]["coverage"]["sources_checked"], 17)
            self.assertEqual(out[week + ".json"]["coverage"]["wards"][0]["status"], "error")
            self.assertEqual(out[week + "-run.json"]["discovery_evidence"], {"status": "error", "http_status": 403})
        self.assertFalse(out["update_history.json"]["history"][-1]["content_review_complete"])
        exported = out[WEEKS[0] + "-decisions.json"]["decisions"][-1]
        self.assertEqual(exported["family_fit"]["rubric_version"], "family-fit-v1")
        self.assertEqual(exported["canonical_family_fit_v2"]["rubric_version"], "family-fit-v2")
        public = out[WEEKS[0] + "-events-reviewed-nakano-20261113.json"][-1]
        self.assertEqual(public["family_fit"]["rubric_version"], "family-fit-v2")

    def test_unapproved_event_fact_old_status_history_and_extra_file_fail(self):
        expected = expected_outputs(self.fixture().__getitem__, load_spec(), "2026-11-13T00:00:00Z")
        shard = WEEKS[0] + "-events-reviewed-nakano-20261113.json"
        for mutate in (
            lambda x: x[shard][0].update(price="999円"),
            lambda x: x[WEEKS[0] + ".json"]["events"].clear(),
            lambda x: x[WEEKS[0] + "-run.json"]["discovery_evidence"].update(status="checked"),
            lambda x: x["update_history.json"]["history"].pop(0),
            lambda x: x.update({"discovery_sources.json": {"required": False}}),
        ):
            actual = copy.deepcopy(expected)
            mutate(actual)
            with self.assertRaises(ValueError):
                compare_outputs(actual, expected)

    def test_unknown_time_is_retained_and_partner_posts_are_not_official_badges(self):
        for row in load_spec():
            if not row["event"]["time"]:
                self.assertEqual(row["verification"]["fields"]["time"], "unknown")
            if "pc.tamemap.net" in row["event"]["official_url"]:
                self.assertEqual(row["verification"]["source_kind"], "organizer_provided_partner")
        self.assertFalse(next(r for r in load_spec() if r["tamemap_event_id"] == "161805")["event"]["reservation"]["required"])


if __name__ == "__main__":
    unittest.main()
