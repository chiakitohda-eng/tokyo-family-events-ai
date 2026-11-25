import unittest
from tools.validate_official_schedule_audit import validate, WARDS

SOURCE = 'nerima_district_festivals_2026'


def setup():
    checks = [{"source_id": SOURCE, "status": "checked", "url": "https://www.city.nerima.tokyo.jp/example.html",
               "checked_at": "2026-10-10T10:00:00+09:00", "official_row_count": 1,
               "candidate_ids": ["candidate-A"], "matched_candidate_count": 1, "unmatched_official_rows": []}]
    rows = [{"ward": w, "query_logs": [{"query": w + " 祭り", "status": "checked", "checked_at": "2026-10-10T10:00:00+09:00"}],
             "source_checks": [{"url": "https://example.org/", "status": "checked", "checked_at": "2026-10-10T10:00:00+09:00"}]} for w in WARDS]
    run = {"prompt": {"version": "v1.15"}, "discovery_evidence": {"wards": rows}, "official_schedule_checks": checks}
    week = {"sat": "2026-10-10", "coverage": {"wards": [{"ward": w, "status": "checked", "queries": 1, "sources_checked": 1} for w in WARDS]}}
    decisions = {"decisions": [{"candidate_id": "candidate-A", "decision": "published"}]}
    return run, week, decisions


class AuditTests(unittest.TestCase):
    def test_good_audit(self):
        self.assertEqual(validate(*setup()), [])

    def test_missing_source_candidate_fails(self):
        r, w, d = setup()
        d["decisions"] = []
        self.assertTrue(any("reconciliation" in x for x in validate(r, w, d)))

    def test_fake_counters_and_no_evidence_fail(self):
        r, w, d = setup()
        w["coverage"]["wards"][0]["queries"] = 3
        r["discovery_evidence"]["wards"][1]["source_checks"] = []
        self.assertTrue(any("coverage.queries" in x for x in validate(r, w, d)))
        self.assertTrue(any("missing actual" in x for x in validate(r, w, d)))

    def test_missing_required_official_source_fails(self):
        run, week, decisions = setup()
        config = {"explicit_sources": [{
            "id": "nakano_official_tourism", "enabled": True, "required": True,
            "search_urls": ["https://www.nakano-kanko.com/event/"],
            "event_row_audit_required": True,
        }]}
        errors = validate(run, week, decisions, config)
        self.assertTrue(any("required source not checked" in x for x in errors))

    def test_unmatched_official_event_row_fails(self):
        run, week, decisions = setup()
        config = {"explicit_sources": [{
            "id": "nakano_official_tourism", "enabled": True, "required": True,
            "search_urls": ["https://www.nakano-kanko.com/event/"],
            "event_row_audit_required": True,
        }]}
        run["explicit_source_checks"] = [{
            "source_id": "nakano_official_tourism", "status": "checked",
            "search_url": "https://www.nakano-kanko.com/event/",
            "checked_at": "2026-10-16T23:00:00+09:00",
            "official_row_count": 1, "candidate_count": 1,
            "candidate_ids": ["missing-Komafes"], "unmatched_official_rows": [],
        }]
        errors = validate(run, week, decisions, config)
        self.assertTrue(any("unreconciled official event rows" in x for x in errors))

    def test_known_festivals_must_not_be_absent_from_new_oct17_run(self):
        run, week, decisions = setup()
        week["sat"] = "2026-10-17"
        errors = validate(run, week, decisions)
        self.assertTrue(any("中野区" in x and "missing" in x for x in errors))
        self.assertTrue(any("板橋区" in x and "missing" in x for x in errors))
        decisions["decisions"].extend([
            {"candidate_id": "known-komafes", "ward": "中野区", "name": "KOMAFES2026", "decision": "published"},
            {"candidate_id": "known-itabashi", "ward": "板橋区", "name": "第55回板橋区民まつり", "decision": "published"},
        ])
        self.assertFalse(any("known 2026 official festival missing" in x for x in validate(run, week, decisions)))

    def test_one_run_tamemap_403_can_be_deferred_without_success_fraud(self):
        import json
        from pathlib import Path
        rules = json.loads((Path(__file__).parents[1] /
                            'policy/temporary_source_exceptions.json').read_text())['exceptions']
        run, week, decisions = setup()
        run['holiday_after'] = {'as_of_jst': '2026-10-19',
                                'run_type': 'holiday_after_update'}
        week['sat'] = '2026-11-21'
        config = {'explicit_sources': [{
            'id': 'tamemap_nakano', 'enabled': True, 'required': True,
            'event_row_audit_required': True,
            'search_urls': ['https://pc.tamemap.net/1311401/calendar/{YYYY-MM}?lat=x'],
        }]}
        failure = {'source_id': 'tamemap_nakano', 'status': 'error',
                   'http_status': 403, 'response_server': 'cloudflare',
                   'challenge_detected': True, 'error': 'HTTP Error 403: Forbidden',
                   'search_url': 'https://pc.tamemap.net/1311401/calendar/2026-11?lat=x',
                   'checked_at': '2026-10-20T00:30:00+09:00',
                   'exception_ref': 'tamemap-nakano-cloudflare403-20261019'}
        run['explicit_source_checks'] = [failure]
        self.assertEqual(validate(run, week, decisions, config, rules), [])
        self.assertTrue(any('required source failed' in x
                            for x in validate(run, week, decisions, config)))
        self.assertEqual(failure['status'], 'error')

    def test_deferred_exception_rejects_wrong_run_path_and_status(self):
        import json
        from pathlib import Path
        rules = json.loads((Path(__file__).parents[1] /
                            'policy/temporary_source_exceptions.json').read_text())['exceptions']
        run, week, decisions = setup()
        run['holiday_after'] = {'as_of_jst': '2026-10-19',
                                'run_type': 'holiday_after_update'}
        week['sat'] = '2026-11-21'
        config = {'explicit_sources': [{
            'id': 'tamemap_nakano', 'enabled': True, 'required': True,
            'search_urls': ['https://pc.tamemap.net/1311401/calendar/{YYYY-MM}'],
        }]}
        failure = {'source_id': 'tamemap_nakano', 'status': 'error',
                   'http_status': 403, 'response_server': 'cloudflare',
                   'challenge_detected': True, 'error': 'HTTP Error 403: Forbidden',
                   'search_url': 'https://pc.tamemap.net/1311401/calendar/2026-11',
                   'checked_at': '2026-10-20T00:30:00+09:00',
                   'exception_ref': 'tamemap-nakano-cloudflare403-20261019'}
        run['explicit_source_checks'] = [failure]
        scenarios = [
            {'status': 'checked', 'http_status': 403},
            {'status': 'error', 'http_status': 404},
            {'status': 'error', 'response_server': 'nginx'},
            {'status': 'error', 'challenge_detected': False},
            {'status': 'error', 'error': 'blocked without HTTP evidence'},
            {'status': 'error', 'search_url': 'https://other.net/1311401/calendar/2026-11'},
            {'status': 'error', 'exception_ref': 'unapproved'},
        ]
        for patch in scenarios:
            with self.subTest(patch=patch):
                run['explicit_source_checks'] = [{**failure, **patch}]
                self.assertTrue(validate(run, week, decisions, config, rules))
        run['explicit_source_checks'] = [failure]
        run['holiday_after']['as_of_jst'] = '2026-11-01'
        self.assertTrue(validate(run, week, decisions, config, rules))
        run['holiday_after']['as_of_jst'] = '2026-10-19'
        week['sat'] = '2026-12-05'
        self.assertTrue(validate(run, week, decisions, config, rules))

    def test_unrelated_required_source_cannot_use_tamemap_exception(self):
        import json
        from pathlib import Path
        rules = json.loads((Path(__file__).parents[1] /
                            'policy/temporary_source_exceptions.json').read_text())['exceptions']
        run, week, decisions = setup()
        run['holiday_after'] = {'as_of_jst': '2026-10-19', 'run_type': 'holiday_after_update'}
        week['sat'] = '2026-11-21'
        config = {'explicit_sources': [{
            'id': 'nakano_official_tourism', 'enabled': True, 'required': True,
            'search_urls': ['https://www.nakano-kanko.com/event/'],
        }]}
        run['explicit_source_checks'] = [{
            'source_id': 'nakano_official_tourism', 'status': 'error',
            'http_status': 403, 'error': 'HTTP Error 403',
            'search_url': 'https://www.nakano-kanko.com/event/',
            'checked_at': '2026-10-20T00:30:00+09:00',
            'exception_ref': 'tamemap-nakano-cloudflare403-20261019',
        }]
        self.assertTrue(any('required source failed' in x
                            for x in validate(run, week, decisions, config, rules)))

    def test_historical_runs_not_retroactively_mutated(self):
        r, w, d = setup()
        r["prompt"]["version"] = "v1.5"
        r["discovery_evidence"] = {}
        self.assertEqual(validate(r, w, d), [])


if __name__ == "__main__":
    unittest.main()
