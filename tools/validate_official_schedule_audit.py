#!/usr/bin/env python3
"""Validate v1.15+ real discovery evidence and official multi-event schedule parity.

Historical v1.5 runs are intentionally not rewritten with invented provenance.
"""
import argparse
import json
from pathlib import Path
import re
import sys

WARDS = ['千代田区','中央区','港区','新宿区','文京区','台東区','墨田区','江東区','品川区','目黒区','大田区','世田谷区','渋谷区','中野区','杉並区','豊島区','北区','荒川区','板橋区','練馬区','足立区','葛飾区','江戸川区']
SOURCE = 'nerima_district_festivals_2026'


def active_version(run):
    version = (run.get('prompt') or {}).get('version', '')
    found = re.fullmatch(r'v1\.(\d+)', version)
    return bool(found and int(found.group(1)) >= 15)


def valid_temporary_exception(run, week, check, source_id, rules):
    """Only the measured Cloudflare error for this exact one-time run can defer."""
    from urllib.parse import urlsplit
    run_meta = run.get("holiday_after") or {}
    if (run_meta.get("as_of_jst") != "2026-10-19" or
            run_meta.get("run_type") != "holiday_after_update" or
            week.get("sat") not in {
                "2026-10-24", "2026-10-31", "2026-11-07",
                "2026-11-14", "2026-11-21", "2026-11-28"}):
        return False
    for rule in rules:
        if (source_id != rule.get("source_id") or
                check.get("exception_ref") != rule.get("id") or
                check.get("status") != rule.get("expected_observed_status") or
                check.get("http_status") != rule.get("expected_http_status") or
                check.get("response_server", "").casefold() != "cloudflare" or
                check.get("challenge_detected") is not True or
                rule.get("required_source_stays_enabled") is not True):
            continue
        url = check.get("search_url") or check.get("url") or ""
        parsed = urlsplit(url)
        if (parsed.scheme != "https" or parsed.hostname != rule.get("expected_host") or
                not parsed.path.startswith("/1311401/calendar/") or
                not check.get("checked_at") or
                "403" not in str(check.get("error") or "")):
            return False
        # A real 403 does not become status='checked'; only its scoped blocker
        # is deferred. The original HTTP error stays in source audit evidence.
        return True
    return False


def validate(run, week, decisions, source_config=None, temporary_rules=()):
    if not active_version(run):
        return []
    errors = []
    label = week.get('sat', '?')
    evidence = run.get('discovery_evidence') or {}
    ward_rows = evidence.get('wards') or []
    mapping = {row.get('ward'): row for row in ward_rows}
    if set(mapping) != set(WARDS) or len(ward_rows) != 23:
        errors.append(f'{label}: discovery_evidence.wards must cover all 23 wards exactly once')
    coverage = {row.get('ward'): row for row in (week.get('coverage') or {}).get('wards', [])}
    for name in WARDS:
        actual = mapping.get(name) or {}
        logs = actual.get('query_logs') or []
        sources = actual.get('source_checks') or []
        if not logs or not sources:
            errors.append(f'{label}/{name}: missing actual per-query and per-source evidence')
            continue
        if any(not r.get('query') or not r.get('checked_at') or r.get('status') not in ('checked', 'error') for r in logs):
            errors.append(f'{label}/{name}: invalid query evidence')
        if any(not r.get('url') or not r.get('checked_at') or r.get('status') not in ('checked', 'error') for r in sources):
            errors.append(f'{label}/{name}: invalid source evidence')
        c = coverage.get(name) or {}
        if c.get('queries') != len(logs):
            errors.append(f'{label}/{name}: coverage.queries differs from real query log count')
        if c.get('sources_checked') != sum(r.get('status') == 'checked' for r in sources):
            errors.append(f'{label}/{name}: coverage.sources_checked differs from successful URL checks')
        if c.get('status') == 'checked' and (any(r.get('status') == 'error' for r in sources) or any(r.get('status') == 'error' for r in logs)):
            errors.append(f'{label}/{name}: checked is forbidden when required exploration failed')
    official = [r for r in run.get('official_schedule_checks', []) if r.get('source_id') == SOURCE]
    if len(official) != 1:
        errors.append(f'{label}: expected one official_schedule_checks record for {SOURCE}')
        return errors
    item = official[0]
    for field in ('url', 'checked_at'):
        if not item.get(field):
            errors.append(f'{label}: official schedule missing {field}')
    if item.get('status') != 'checked':
        errors.append(f'{label}: official schedule not successfully checked')
    count = item.get('official_row_count')
    ids = item.get('candidate_ids')
    if not isinstance(count, int) or count < 0 or not isinstance(ids, list) or len(ids) != count or len(set(ids)) != len(ids):
        errors.append(f'{label}: official row count must equal unique candidate IDs')
        return errors
    known = {d.get('candidate_id') for d in decisions.get('decisions', []) if d.get('decision') in ('published', 'excluded', 'duplicate')}
    missing = [cid for cid in ids if cid not in known]
    if item.get('unmatched_official_rows') or missing or item.get('matched_candidate_count') != count:
        errors.append(f'{label}: incomplete official-row-to-decision reconciliation ({len(missing)} candidate IDs absent)')
    # Annual official schedules must resolve the fiscal year from the stable
    # listing, not silently accept a stale 2026 schedule in later years.
    annual = next((s for s in (source_config or {}).get('explicit_sources', [])
                   if s.get('id') == SOURCE), None)
    if annual and annual.get('annual_listing_url'):
        pages = item.get('resolved_pages') or []
        from datetime import date
        saturday = date.fromisoformat(week['sat'])
        sunday = date.fromisoformat(week.get('sun') or week['sat'])
        needed = set(range(
            saturday.year if saturday.month >= 4 else saturday.year - 1,
            (sunday.year if sunday.month >= 4 else sunday.year - 1) + 1
        ))
        resolved = {p.get('fiscal_year') for p in pages if isinstance(p, dict)}
        if resolved != needed:
            errors.append(f'{label}: annual schedule resolution missing actual fiscal-year pages')
        for page in pages:
            url = page.get('resolved_url', '') if isinstance(page, dict) else ''
            if (not isinstance(url, str) or not url.startswith(
                    'https://www.city.nerima.tokyo.jp/kankomoyoshi/annai/omatsuri/chikusai/')
                    or not url.endswith('.html') or url == annual.get('annual_listing_url')):
                errors.append(f'{label}: invalid resolved annual schedule URL')
    # Concrete regressions: both festivals have independently verified official
    # pages, so a newly generated Oct 17 run must not report an empty candidate
    # set for Nakano/Itabashi. This check is date-specific, not a synthetic
    # assertion about historic v1.5 search logs.
    if week.get('sat') == '2026-10-17':
        records = [x for x in decisions.get('decisions', [])
                   if x.get('decision') in ('published', 'excluded', 'duplicate')]
        for ward, pattern in (('中野区', r'(?i)KOMAFES|コマフェス'),
                              ('板橋区', r'板橋区民まつり')):
            if not any(r.get('ward') == ward and re.search(pattern, r.get('name') or '')
                       for r in records):
                errors.append(f'{label}/{ward}: known 2026 official festival missing from candidate decisions')
    # Validate *actual* required-source checks for v1.15+ runs. An HTTP status
    # alone is not event discovery; required official indexes must reconcile
    # every discovered row with a candidate-level publication decision.
    if source_config is not None:
        source_checks = run.get('explicit_source_checks') or []
        known_decisions = {d.get('candidate_id') for d in decisions.get('decisions', [])
                           if d.get('decision') in ('published', 'excluded', 'duplicate')}
        for source in source_config.get('explicit_sources', []):
            if not (source.get('enabled') and source.get('required')):
                continue
            source_id = source.get('id')
            checks = [c for c in source_checks if c.get('source_id', c.get('id')) == source_id]
            annual_listing = source.get('annual_listing_url')
            templates = [annual_listing] if annual_listing else source.get('search_urls', [])
            for template in templates:
                prefix = template.split('{', 1)[0]
                matches = [c for c in checks if (c.get('search_url') or c.get('url') or '').startswith(prefix)]
                if not matches:
                    errors.append(f'{label}: required source not checked: {source_id}, {template}')
                    continue
                for c in matches:
                    if valid_temporary_exception(run, week, c, source_id, temporary_rules):
                        continue
                    if c.get('status') != 'checked' or not c.get('checked_at'):
                        errors.append(f'{label}: required source failed: {source_id}')
                    ids = c.get('candidate_ids')
                    if not isinstance(ids, list) or len(set(ids)) != len(ids):
                        errors.append(f'{label}: source candidate IDs missing/duplicated: {source_id}')
                        continue
                    if c.get('candidate_count') != len(ids):
                        errors.append(f'{label}: candidate count not supported by IDs: {source_id}')
                    if source.get('event_row_audit_required'):
                        count = c.get('official_row_count')
                        if not isinstance(count, int) or count < 0 or count != len(ids):
                            errors.append(f'{label}: official event row parity mismatch: {source_id}')
                        if c.get('unmatched_official_rows') or any(cid not in known_decisions for cid in ids):
                            errors.append(f'{label}: unreconciled official event rows: {source_id}')
    return errors


def allow_only_preexisting_suginami_gaps(errors, baseline, directory):
    """Fail closed: suppress only immutable known gaps in untouched historical weeks.

    Scoped to one independently audited Nov 3 addendum; no source is upgraded
    to 'checked', and the complete missing-check list remains in warnings.
    """
    import subprocess
    if not re.fullmatch(r'[0-9a-f]{40}', baseline or ''):
        raise ValueError('real 40-char baseline SHA required for historical-gap audit')
    touched = set(subprocess.check_output(
        ['git', 'diff', '--name-only', baseline, 'HEAD'],
        text=True).splitlines())
    expected = {
        'site/data/manifest.json', 'site/data/2026-10-31.json',
        'site/data/2026-10-31-verification.json',
        'site/data/2026-10-31-decisions.json', 'site/data/2026-10-31-run.json',
        'site/data/update_history.json',
        'site/data/2026-10-31-events-holiday-2026-11-03.json'
    }
    if touched != expected:
        raise ValueError('manual holiday exception is restricted to seven reviewed 11/3 files')
    for sat in ('2026-11-21', '2026-11-28'):
        for suffix in ('.json','-run.json','-decisions.json','-verification.json'):
            file=f'{sat}{suffix}'
            before=subprocess.check_output(['git', 'show', f'{baseline}:site/data/{file}'])
            if (directory/file).read_bytes()!=before:
                raise ValueError('pre-existing holiday exception cannot alter '+file)
    allowed = {
        f'{sat}: required source not checked: suginami_calendar_all, '
        'https://www.city.suginami.tokyo.jp/cgi-bin/event_cal_multi/calendar.cgi?type=2&year={YYYY}&month={MM}'
        for sat in ('2026-11-21','2026-11-28')
    }
    remainder = []
    for error in errors:
        if error in allowed:
            print('KNOWN_PREEXISTING_UNCHECKED_REQUIRED_SOURCE (not verified): '+error)
        else:
            remainder.append(error)
    return remainder


def main():
    p = argparse.ArgumentParser()
    p.add_argument('directory', type=Path)
    p.add_argument('--allow-unchanged-historical-gaps-base', default='')
    args = p.parse_args()
    errors = []
    manifest = json.loads((args.directory/'manifest.json').read_text(encoding='utf-8'))
    source_config = json.loads((args.directory/'discovery_sources.json').read_text(encoding='utf-8'))
    # Read the exception authorization from main/staging audit policy, never
    # from data-staging itself. Unapproved candidate data cannot self-waive.
    exception_file = Path(__file__).resolve().parents[1] / 'policy' / 'temporary_source_exceptions.json'
    temporary_rules = []
    if exception_file.exists():
        policy = json.loads(exception_file.read_text(encoding='utf-8'))
        if policy.get('schema_version') != 1 or policy.get('policy') != 'temporary_known_issue_deferral':
            raise ValueError('invalid approved temporary source exception ledger')
        temporary_rules = policy.get('exceptions') or []
    for period in manifest.get('weekends', []):
        week = json.loads((args.directory/period['file']).read_text(encoding='utf-8'))
        run = json.loads((args.directory/week['run_file']).read_text(encoding='utf-8'))
        decisions_path = args.directory/(run.get('source_data') or {}).get('decision_file', period['sat']+'-decisions.json')
        decisions = json.loads(decisions_path.read_text(encoding='utf-8'))
        errors.extend(validate(run, week, decisions, source_config, temporary_rules))
    if args.allow_unchanged_historical_gaps_base:
        try:
            errors = allow_only_preexisting_suginami_gaps(
                errors, args.allow_unchanged_historical_gaps_base, args.directory)
        except (ValueError, OSError, __import__('subprocess').CalledProcessError) as exc:
            errors.append('historical baseline scope verification failed: '+str(exc))
    for error in errors:
        print('ERROR', error, file=sys.stderr)
    print(f'official schedule discovery audit: {"FAIL" if errors else "PASS"}')
    return 1 if errors else 0


if __name__ == '__main__':
    sys.exit(main())
