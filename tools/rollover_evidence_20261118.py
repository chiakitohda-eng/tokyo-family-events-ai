#!/usr/bin/env python3
"""Derive per-week, per-ward source evidence for the 2026-11-21 six-week rollover.

The ONLY input is the immutable copy of the real crawl receipts committed under
research/2026-11-18-source-evidence (GitHub Actions run 44187635448, artifact
14375267058). Nothing is invented: every query and source record is copied from
a receipt; failed receipts stay failed. The same `derive_*` functions are used
by the builder (to write data) and by the gate validator (to re-derive and
require byte-for-field equality), so data cannot drift from the receipts.
"""
import argparse
import hashlib
import json
import pathlib
import sys

WARDS = ['千代田区', '中央区', '港区', '新宿区', '文京区', '台東区', '墨田区', '江東区', '品川区', '目黒区', '大田区',
         '世田谷区', '渋谷区', '中野区', '杉並区', '豊島区', '北区', '荒川区', '板橋区', '練馬区', '足立区', '葛飾区', '江戸川区']
SATS = ['2026-11-21', '2026-11-28', '2026-12-05', '2026-12-12', '2026-12-19', '2026-12-26']
NEW_EVIDENCE_WEEKS = ('2026-12-19', '2026-12-26')   # weeks whose coverage rows were still pending
RUN_ID = 44187635448
ARTIFACT_ID = 14375267058
BASE = 'fc6bec505975c6dabbddd404f33cd7d9f3f525e9'
PINNED_SHA256 = {
    'requests.json': '3459409ad644d4e6b3b387312098583a63c69eda2aee073ff65644fee08e502a',
    'summary.json': '1bd9df863e4fe9c568a604106a20118bebe57dbf79ac4cb6bcb5806c6d4431cf',
    'plan.json': 'aa408365b651cbc03a3602f51658e5aab69b61a89a1cc3a3606039e9b468b0f8',
}
# The complete, closed list of failed receipts. Anything else failing is a hard error.
KNOWN_FAILURES = [
    ('explicit', 'tamemap_nakano', 'https://pc.tamemap.net/1311401/calendar/2026-11?lat=35.7089745&lng=139.6630981&level=5000&locale=ja', 'HTTP Error 403: Forbidden'),
    ('explicit', 'tamemap_nakano', 'https://pc.tamemap.net/1311401/calendar/2026-12?lat=35.7089745&lng=139.6630981&level=5000&locale=ja', 'HTTP Error 403: Forbidden'),
    ('explicit', 'tamemap_nakano', 'https://pc.tamemap.net/1311401/new_arrival?lat=35.7089745&lng=139.6630981&level=5000&locale=ja', 'HTTP Error 403: Forbidden'),
    ('holiday_calendar', 'nerima_monthly', 'https://www.city.nerima.tokyo.jp/kankomoyoshi/event/calendar/list_calendar202611.html', 'HTTP Error 404: Not Found'),
    ('holiday_calendar', 'nerima_kids_monthly', 'https://www.city.nerima.tokyo.jp/nerimakids/event/calendar/list_calendar202611.html', 'HTTP Error 404: Not Found'),
]


def load_json(path):
    return json.loads(pathlib.Path(path).read_text(encoding='utf-8'))


def sha256_file(path):
    return hashlib.sha256(pathlib.Path(path).read_bytes()).hexdigest()


def check_pins(evidence_dir):
    """Raise ValueError unless the committed receipts are byte-identical to the audited artifact."""
    evidence_dir = pathlib.Path(evidence_dir)
    for name, want in PINNED_SHA256.items():
        got = sha256_file(evidence_dir / name)
        if got != want:
            raise ValueError(f'evidence file {name} sha256 {got} != pinned {want}')


def _q(rec):
    return {k: rec.get(k) for k in ('query', 'url', 'checked_at', 'status', 'http_status', 'sha256',
                                    'search_results_total', 'search_results_event_leads')}


def _s(rec):
    return {k: rec.get(k) for k in ('url', 'checked_at', 'status', 'http_status', 'sha256')}


def failures(requests):
    return [r for r in requests if r.get('status') != 'checked']


def check_failure_ledger(requests):
    got = sorted((r['kind'], r.get('source_id'), r['url'], str(r.get('error'))) for r in failures(requests))
    want = sorted(KNOWN_FAILURES)
    if got != want:
        raise ValueError(f'failed-receipt ledger changed: {got!r}')


def derive_wards(requests, sat):
    rows = []
    for ward in WARDS:
        qs = [r for r in requests if r['kind'] == 'ai_cross' and r['ward'] == ward and r['week'] == sat]
        home = [r for r in requests if r['kind'] == 'ward_official' and r['ward'] == ward]
        if len(qs) != 3 or len(home) != 1:
            raise ValueError(f'{sat}/{ward}: expected 3 query receipts and 1 official-home receipt, got {len(qs)}/{len(home)}')
        if any(r['status'] != 'checked' for r in qs + home):
            raise ValueError(f'{sat}/{ward}: failed ward receipt would have to be recorded as error, not checked')
        rows.append({'ward': ward, 'query_logs': [_q(r) for r in qs], 'source_checks': [_s(r) for r in home]})
    return rows


def derive_required_sources(requests):
    out = []
    for r in requests:
        if r['kind'] != 'explicit':
            continue
        row = {k: r.get(k) for k in ('source_id', 'required', 'url', 'checked_at', 'status', 'http_status', 'sha256')}
        if r['status'] != 'checked':
            row['error'] = r.get('error')
        out.append(row)
    return out


def derive_holiday(requests):
    return {
        'holiday': '2026-11-23',
        'ward_queries': [dict(_q(r), ward=r['ward']) for r in requests if r['kind'] == 'holiday_ai_cross'],
        'calendar_checks': [
            dict({k: r.get(k) for k in ('source_id', 'ward', 'calendar_mode', 'url', 'checked_at', 'status',
                                        'http_status', 'sha256')},
                 **({'error': r.get('error')} if r['status'] != 'checked' else {}))
            for r in requests if r['kind'] == 'holiday_calendar'],
    }


def derive_block(requests, summary, sat):
    block = {
        'source': {'workflow_run_id': RUN_ID, 'artifact_id': ARTIFACT_ID,
                   'requests_sha256': PINNED_SHA256['requests.json'],
                   'committed_copy': 'research/2026-11-18-source-evidence/'},
        'as_of_jst': summary['as_of_jst'],
        'base_data_production_sha': BASE,
        'request_count': summary['request_count'],
        'requests_success': summary['requests_success'],
        'wards': derive_wards(requests, sat),
        'required_sources': derive_required_sources(requests),
        'known_unresolved_failures': [
            {'kind': k, 'source_id': s, 'url': u, 'error': e, 'recorded_as': 'error', 'never_marked_checked': True}
            for k, s, u, e in KNOWN_FAILURES],
        'unverified_candidate_links': summary['candidate_links_unverified'],
        'full_23_ward_25_source_audit_complete': False,
    }
    if sat == SATS[0]:
        block['holiday_2026_11_23'] = derive_holiday(requests)
    return block


def ward_note(ward):
    base = '2026-11-18実測: 週別検索3件と区公式トップの取得に成功。個別の掲載はイベント単位の公式確認済みのみ。'
    if ward == '中野区':
        return base + ' ただし必須参照元 tamemap_nakano の3URLはHTTP403で取得不能（checkedにはしない）。'
    if ward == '練馬区':
        return base + ' ただし月別の旧公式カレンダー2URLはHTTP404（失敗のまま記録）。'
    return base


def build(data_dir, evidence_dir):
    data_dir = pathlib.Path(data_dir)
    evidence_dir = pathlib.Path(evidence_dir)
    check_pins(evidence_dir)
    requests = load_json(evidence_dir / 'requests.json')
    summary = load_json(evidence_dir / 'summary.json')
    if len(requests) != 588 or sum(r['status'] == 'checked' for r in requests) != 583:
        raise ValueError('request totals changed')
    check_failure_ledger(requests)
    for sat in SATS:
        run_path = data_dir / f'{sat}-run.json'
        run = load_json(run_path)
        run['rollover_evidence_20261118'] = derive_block(requests, summary, sat)
        if sat in NEW_EVIDENCE_WEEKS:
            run['discovery_evidence'] = dict(run.get('discovery_evidence') or {},
                                             wards_total=23, wards_fully_checked_this_run=23,
                                             required_sources_total=25,
                                             required_sources_fully_checked_this_run=24,
                                             evidence_ref='rollover_evidence_20261118')
            run.setdefault('summary', {})['wards_checked'] = 23
            for stage in run.get('stages') or []:
                if stage.get('name') == 'discover_23_wards':
                    stage['status'] = 'passed'
                if stage.get('name') == 'mandatory_explicit_source_crawl':
                    stage['status'] = 'partial'
            run['mode'] = 'verified_current_rollover_20261118'
        run_path.write_text(json.dumps(run, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        if sat in NEW_EVIDENCE_WEEKS:
            week_path = data_dir / f'{sat}.json'
            week = load_json(week_path)
            cov = week['coverage']
            cov['sources_checked'] = 23
            for row in cov['wards']:
                row['status'] = 'checked'
                row['queries'] = 3
                row['sources_checked'] = 1
                row['note'] = ward_note(row['ward'])
            week_path.write_text(json.dumps(week, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    # Provenance in the manifest and the single new history entry.
    manifest_path = data_dir / 'manifest.json'
    manifest = load_json(manifest_path)
    roll = manifest.setdefault('current_rollover', {})
    roll.update(provenance_fields(summary))
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    hist_path = data_dir / 'update_history.json'
    hist = load_json(hist_path)
    hist['history'][-1].update(provenance_fields(summary))
    hist_path.write_text(json.dumps(hist, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    return 0


def provenance_fields(summary):
    return {
        'evidence_workflow_run_id': RUN_ID,
        'evidence_artifact_id': ARTIFACT_ID,
        'evidence_requests_sha256': PINNED_SHA256['requests.json'],
        'evidence_committed_copy': 'research/2026-11-18-source-evidence/',
        'required_source_failures_observed': len(KNOWN_FAILURES),
        'unresolved_required_source_failures': len(KNOWN_FAILURES),
        'unverified_candidate_links': summary['candidate_links_unverified'],
        'source_failures_remain_unverified': True,
        'global_source_audit_complete': False,
        'full_23_ward_25_source_audit_complete': False,
        'ward_week_search_receipts_checked': 414,
    }


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--data-dir', default='site/data')
    ap.add_argument('--evidence-dir', default='research/2026-11-18-source-evidence')
    a = ap.parse_args()
    try:
        sys.exit(build(a.data_dir, a.evidence_dir))
    except ValueError as exc:
        print('ERROR:', exc, file=sys.stderr)
        sys.exit(1)
