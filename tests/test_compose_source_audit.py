"""Source status can refresh without changing released apps or event data."""
import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from compose_source_audit import compose_source_audit, validate_snapshot
from source_fallback_policy import apply_fallback_overlay


class SourceAuditCompositionTests(unittest.TestCase):
    def setUp(self):
        self.registry_path = ROOT / "site/data/discovery_sources.json"
        self.registry = apply_fallback_overlay(json.loads(
            self.registry_path.read_text(encoding="utf-8")))
        self.report = json.loads((ROOT / "site/audit/fixed_sources.json").read_text(
            encoding="utf-8"))

    def seed_pages(self, root):
        files = {
            "index.html": b"released production app",
            "app.js": b"released production code",
            "data/manifest.json": b"production event manifest",
            "data/2026-11-14.json": b"protected production event records",
            "audit/pending_issues_catalog.json": b"released production catalog",
            "audit/fixed_sources.json": b"previous source-status report",
            "staging/index.html": b"separate staging app",
            "staging/audit/fixed_sources.json": b"separate staging source report",
        }
        for relative, raw in files.items():
            path = root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(raw)
        return files

    def test_only_exact_audit_json_changes_and_bytes_preserved(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            pages = root / "pages"
            before = self.seed_pages(pages)
            snapshot = root / "snapshot.json"
            raw = (json.dumps(self.report, ensure_ascii=False, indent=2) + "\n").encode()
            snapshot.write_bytes(raw)
            result = compose_source_audit(snapshot, self.registry_path, pages)
            self.assertEqual(result, pages / "audit/fixed_sources.json")
            self.assertEqual(result.read_bytes(), raw)
            after = {str(p.relative_to(pages)): p.read_bytes()
                     for p in pages.rglob("*") if p.is_file()}
            self.assertEqual(set(after), set(before))
            self.assertEqual([p for p in before if before[p] != after[p]],
                             ["audit/fixed_sources.json"])

    def test_invalid_reports_leave_entire_pages_tree_unchanged(self):
        def bad_digest(report):
            report["source_registry_digest"] = "0" * 64
        def false_success(report):
            report["sources"][0]["pages_checked"] += 1
        def missing_route(report):
            report["sources"][0]["source_checks"].pop()
        def publication_claim(report):
            report["summary"]["publication_gaps_confirmed"] = 0
        def raw_html(report):
            report["sources"][0]["source_checks"][0]["body"] = "<html>page</html>"
        for mutate in (bad_digest, false_success, missing_route, publication_claim, raw_html):
            with self.subTest(mutation=mutate.__name__), tempfile.TemporaryDirectory() as tmp:
                pages = Path(tmp) / "pages"
                before = self.seed_pages(pages)
                report = copy.deepcopy(self.report)
                mutate(report)
                snapshot = Path(tmp) / "snapshot.json"
                snapshot.write_text(json.dumps(report), encoding="utf-8")
                with self.assertRaises(ValueError):
                    compose_source_audit(snapshot, self.registry_path, pages)
                after = {str(p.relative_to(pages)): p.read_bytes()
                         for p in pages.rglob("*") if p.is_file()}
                self.assertEqual(after, before)

    def test_new_staging_registry_uses_only_validated_previous_production_report(self):
        old_registry=copy.deepcopy(self.registry)
        old_registry['explicit_sources']=[r for r in old_registry['explicit_sources']if r['id'] not in ('shinjuku_sankaku_hiroba','greensprings_tachikawa','futako_tamagawa_rise','chuosen_rr_suginami','hachilabo_shibuya')]
        raw=(ROOT/'research/aipaku_review_20261115/fixed_sources_before_addition.json').read_bytes()
        with tempfile.TemporaryDirectory()as tmp:
            root=Path(tmp);pages=root/'pages';self.seed_pages(pages)
            registry_path=root/'registry.json';registry_path.write_text(json.dumps(old_registry))
            candidate=root/'new-snapshot.json';candidate.write_text(json.dumps(self.report))
            fallback=root/'previous.json';fallback.write_bytes(raw)
            result=compose_source_audit(candidate,registry_path,pages,fallback)
            self.assertEqual(result.read_bytes(),raw)
            bad=json.loads(raw);bad['sources'][0]['pages_checked']+=1;fallback.write_text(json.dumps(bad))
            before=result.read_bytes()
            with self.assertRaises(ValueError):compose_source_audit(candidate,registry_path,pages,fallback)
            self.assertEqual(result.read_bytes(),before)

    def test_snapshot_and_registry_are_not_modified(self):
        before_report = copy.deepcopy(self.report)
        before_registry = copy.deepcopy(self.registry)
        self.assertTrue(validate_snapshot(self.report, self.registry))
        self.assertEqual(self.report, before_report)
        self.assertEqual(self.registry, before_registry)


if __name__ == "__main__":
    unittest.main()
