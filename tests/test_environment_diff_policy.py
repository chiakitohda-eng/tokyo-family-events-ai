"""Unit tests for environment diff classification, safe without GitHub/network."""
import importlib.util
import unittest
from pathlib import Path

PATH = Path(__file__).resolve().parents[1] / "tools" / "audit_environment_diff.py"
spec = importlib.util.spec_from_file_location("audit_environment_diff", PATH)
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)


def fixture():
    return {
        "allowed_differences": [
            {
                "path": ".github/release-trigger.txt", "kind": "different",
                "disposition": "intentional_staging_only", "reason": "main control",
            },
            {
                "path": "research/history.json", "kind": "staging_only",
                "disposition": "intentional_staging_only", "reason": "audit trail",
            },
        ]
    }


class DiffGovernanceTests(unittest.TestCase):
    def test_matching_intentional_differences(self):
        actual = {".github/release-trigger.txt": "different",
                  "research/history.json": "staging_only"}
        result = audit.classify(actual, fixture())
        self.assertEqual(result["approved_count"], 2)
        self.assertEqual(result["unclassified"], [])
        self.assertEqual(result["wrong_kind"], [])
        self.assertEqual(result["resolved_allowlist"], [])
        self.assertEqual(result["site_or_prompt_differences"], [])

    def test_new_site_change_is_not_auto_approved(self):
        result = audit.classify({".github/release-trigger.txt": "different",
                                  "research/history.json": "staging_only",
                                  "site/app.js": "different"}, fixture())
        self.assertEqual(result["unclassified"], ["site/app.js"])
        self.assertEqual(result["site_or_prompt_differences"], ["site/app.js"])

    def test_reviewed_staging_ui_is_reported_as_unreleased(self):
        inventory=fixture()
        inventory['allowed_differences'].append({'path':'site/staged-ui.js','kind':'staging_only','disposition':'intentional_staging_only','reason':'isolated staging feature','release_state':'pending_release'})
        actual={'.github/release-trigger.txt':'different','research/history.json':'staging_only','site/staged-ui.js':'staging_only'}
        result=audit.classify(actual,inventory)
        self.assertEqual(result['pending_release_paths'],['site/staged-ui.js'])
        self.assertEqual(result['unclassified'],[])
        self.assertEqual(result['site_or_prompt_differences'],['site/staged-ui.js'])

    def test_kind_changed_requires_review(self):
        result = audit.classify({
            ".github/release-trigger.txt": "staging_only",
            "research/history.json": "staging_only",
        }, fixture())
        self.assertEqual(result["wrong_kind"], [".github/release-trigger.txt"])

    def test_disappeared_exception_requires_inventory_reconciliation(self):
        result = audit.classify({".github/release-trigger.txt": "different"},
                                fixture())
        self.assertEqual(result["resolved_allowlist"], ["research/history.json"])

    def test_blob_comparison_is_not_commit_history_comparison(self):
        actual = audit.differences({"site/a.js": "same", "research/a": "new"},
                                   {"site/a.js": "same", "site/b.js": "old"})
        self.assertEqual(actual, {"research/a": "staging_only",
                                  "site/b.js": "production_only"})

    def test_missing_explanation_rejected(self):
        data = fixture()
        data["allowed_differences"][0]["reason"] = ""
        with self.assertRaises(ValueError):
            audit.classify({}, data)


if __name__ == "__main__":
    unittest.main()
