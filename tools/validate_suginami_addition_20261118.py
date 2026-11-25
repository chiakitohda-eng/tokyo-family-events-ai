#!/usr/bin/env python3
"""Gate for operation `verified-suginami-addition-20261118`.

Exactly four Suginami official events are added to the 2026-12-19 week. All four
records are re-derived from tools/suginami_addition_20261118.py and the unchanged
official pages committed under research/2026-11-18-suginami-pages/, and must be
identical to the candidate. Every other record, week and file stays untouched; the
history is append-only with exactly one new entry.
"""
import argparse
import importlib.util
import json
import pathlib
import re
import subprocess
import sys

BASE = '06888a9239c86436c4a499b4268847fa34f4dd2c'
WEEK = '2026-12-19'
ALLOWED = {
    'site/data/manifest.json', 'site/data/update_history.json',
    f'site/data/{WEEK}.json', f'site/data/{WEEK}-verification.json', f'site/data/{WEEK}-decisions.json',
    f'site/data/{WEEK}-run.json', 'site/data/2026-12-19-events-suginami-official-20261118.json',
}


def load(p):
    return json.loads(pathlib.Path(p).read_text(encoding='utf-8'))


def show(ref, p):
    return json.loads(subprocess.check_output(['git', 'show', f'{ref}:{p}'], text=True))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--data-dir', default='site/data')
    ap.add_argument('--pages-dir', required=True)
    ap.add_argument('--base-ref', required=True)
    ap.add_argument('--tools-dir', default=str(pathlib.Path(__file__).resolve().parent))
    a = ap.parse_args()
    errors = []
    err = errors.append
    d = pathlib.Path(a.data_dir)
    spec = importlib.util.spec_from_file_location('suginami_addition_20261118',
                                                  pathlib.Path(a.tools_dir) / 'suginami_addition_20261118.py')
    sg = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(sg)
    if a.base_ref != BASE or sg.BASE != BASE:
        err(f'unexpected base ref {a.base_ref}')

    diff = set(subprocess.check_output(['git', 'diff', '--name-only', a.base_ref, 'HEAD'], text=True).splitlines())
    runtime = {p for p in diff if p.startswith('site/data/') and (
        pathlib.Path(p).name in {'manifest.json', 'update_history.json'} or
        re.fullmatch(r'20\d{2}-\d{2}-\d{2}.*\.json', pathlib.Path(p).name))}
    if runtime != ALLOWED:
        err(f'changed paths differ: extra={sorted(runtime - ALLOWED)} missing={sorted(ALLOWED - runtime)}')
    if any(not p.startswith('site/data/') for p in diff):
        err('candidate changes files outside site/data')

    try:
        events, verification, decisions = sg.derive(a.pages_dir)
    except (ValueError, OSError) as exc:
        err(f'official page evidence: {exc}')
        events = verification = decisions = None

    shard = load(d / sg.SHARD)
    if events is not None and shard != events:
        err('new event shard differs from records re-derived from the committed official pages')
    base_week = show(a.base_ref, f'site/data/{WEEK}.json')
    week = load(d / f'{WEEK}.json')
    if week.get('event_files') != base_week.get('event_files') + [sg.SHARD]:
        err('week event_files must be the base list plus exactly the new shard')
    for k in set(base_week) | set(week):
        if k not in ('event_files', 'coverage') and base_week.get(k) != week.get(k):
            err(f'week field changed unexpectedly: {k}')
    bc, wc = base_week['coverage'], week['coverage']
    if wc['published_count'] != bc['published_count'] + 4 or wc['candidate_count'] != bc['candidate_count'] + 4:
        err('coverage counts not +4')
    for b, w in zip(bc['wards'], wc['wards']):
        if b['ward'] != '杉並区' and b != w:
            err(f"coverage row changed for {b['ward']}")

    # Previously published records are unchanged and unrelated weeks identical.
    for sat in ('2026-11-21', '2026-11-28', '2026-12-05', '2026-12-12', '2026-12-26'):
        if load(d / f'{sat}.json') != show(a.base_ref, f'site/data/{sat}.json'):
            err(f'{sat}: week file changed')
    for eid in ('confirmed-20261219-nakano-rock-experience', 'tamemap-20261220-nakano-forest-choir'):
        base_events = {e['id']: e for e in show(a.base_ref, 'site/data/2026-12-19-events-non-ng-verified-only-20261117.json')}
        cur = {e['id']: e for e in load(d / '2026-12-19-events-non-ng-verified-only-20261117.json')}
        if base_events != cur:
            err('previously published 12/19 events changed')
        break

    ver, base_ver = load(d / f'{WEEK}-verification.json'), show(a.base_ref, f'site/data/{WEEK}-verification.json')
    if verification is not None and ver['events'] != base_ver['events'] + verification:
        err('verification entries differ from re-derived records (or base entries changed)')
    if ver['summary'].get('total') != len(ver['events']) or ver['summary'].get('verified', 0) != base_ver['summary']['verified'] + 4:
        err('verification summary not consistent')
    dec, base_dec = load(d / f'{WEEK}-decisions.json'), show(a.base_ref, f'site/data/{WEEK}-decisions.json')
    if decisions is not None and dec['decisions'] != base_dec['decisions'] + decisions:
        err('decision rows differ from re-derived records (or base rows changed)')
    if dec['summary'].get('candidate_total') != len(dec['decisions']) or dec['summary'].get('published') != len(dec['decisions']):
        err('decision summary not consistent')

    run, base_run = load(d / f'{WEEK}-run.json'), show(a.base_ref, f'site/data/{WEEK}-run.json')
    if run.get('rollover_evidence_20261118') != base_run.get('rollover_evidence_20261118'):
        err('receipt-backed evidence block changed')
    if run.get('summary', {}).get('source_audit_complete') is not False:
        err('run must not claim a complete source audit')
    held = (run.get('suginami_addition_20261118') or {}).get('held_not_published')
    if held != sorted(sg.HELD):
        err('held list differs from the recorded dispositions')

    manifest, base_manifest = load(d / 'manifest.json'), show(a.base_ref, 'site/data/manifest.json')
    expected_weeks = [dict(w, count=w['count'] + 4) if w['sat'] == WEEK else w for w in base_manifest['weekends']]
    if manifest['weekends'] != expected_weeks:
        err('manifest weekends differ from base with only the 12/19 count +4')
    rest = {k: v for k, v in manifest.items() if k not in ('weekends', 'generated')}
    if rest != {k: v for k, v in base_manifest.items() if k not in ('weekends', 'generated')}:
        err('manifest fields other than weekends/generated changed')

    hist, base_hist = load(d / 'update_history.json'), show(a.base_ref, 'site/data/update_history.json')
    if hist['history'][:len(base_hist['history'])] != base_hist['history']:
        err('history is not append-only')
    if len(hist['history']) != len(base_hist['history']) + 1:
        err('expected exactly one history append')
    else:
        last = hist['history'][-1]
        if (last.get('run_type') != 'manual_verified_suginami_december_addition' or
                last.get('base_data_production_sha') != BASE or set(last.get('new_event_ids') or []) != set(sg.NEW_IDS) or
                last.get('existing_event_records_physically_deleted') != 0 or
                last.get('global_source_audit_complete') is not False or
                last.get('source_failures_remain_unverified') is not True):
            err('history entry fields wrong')

    if errors:
        for x in errors:
            print('ERROR:', x)
        return 1
    print('SUGINAMI ADDITION 20261118 PASS: 4 individually verified official events added to 2026-12-19; '
          'all earlier records, weeks and history preserved; source debt unchanged.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
