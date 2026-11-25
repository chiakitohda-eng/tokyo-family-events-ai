#!/usr/bin/env python3
"""Gate for operation `verified-sankaku-addition-20261119`.

Exactly four weekend records of the user-approved 三角広場のクリスマス (hours not published; Instagram reference) are added (one each in the 11/21, 11/28, 12/5, 12/12 weeks). Records are re-derived from tools/sankaku_addition_20261119.py
and the unchanged official pages under research/2026-11-19-audit/pages/ and must
be identical to the candidate. All other records, weeks and files stay untouched; history
is append-only with exactly one new entry.
"""
import argparse
import importlib.util
import json
import pathlib
import re
import subprocess
import sys

BASE = 'd32b8dbe18b04e41791cf88801bec57d5ace0aaa'
WEEKS = {'2026-11-21': 1, '2026-11-28': 1, '2026-12-05': 1, '2026-12-12': 1}
ALLOWED = {'site/data/manifest.json', 'site/data/update_history.json'}
for _w in WEEKS:
    ALLOWED |= {f'site/data/{_w}.json', f'site/data/{_w}-verification.json', f'site/data/{_w}-decisions.json',
                f'site/data/{_w}-run.json', f'site/data/{_w}-events-sankaku-20261119.json'}


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
    sys.path.insert(0, a.tools_dir)
    spec = importlib.util.spec_from_file_location('sankaku_addition_20261119', pathlib.Path(a.tools_dir) / 'sankaku_addition_20261119.py')
    lg = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(lg)
    if a.base_ref != BASE or lg.BASE != BASE:
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
        derived = lg.derive(a.pages_dir)
    except (ValueError, OSError) as exc:
        err(f'official page evidence: {exc}')
        derived = None

    for week, n in WEEKS.items():
        items = derived.get(week) if derived else None
        shard = load(d / lg.SHARDS[week])
        if items is not None and shard != [i[0] for i in items]:
            err(f'{week}: new event shard differs from records re-derived from committed official pages')
        base_week = show(a.base_ref, f'site/data/{week}.json')
        w = load(d / f'{week}.json')
        if w.get('event_files') != base_week.get('event_files') + [lg.SHARDS[week]]:
            err(f'{week}: event_files must be the base list plus exactly the new shard')
        for k in set(base_week) | set(w):
            if k not in ('event_files', 'coverage') and base_week.get(k) != w.get(k):
                err(f'{week}: week field changed unexpectedly: {k}')
        bc, wc = base_week['coverage'], w['coverage']
        if wc['published_count'] != bc['published_count'] + n or wc['candidate_count'] != bc['candidate_count'] + n:
            err(f'{week}: coverage counts not +{n}')
        wards = {i[0]['ward'] for i in items} if items else set()
        for b, r in zip(bc['wards'], wc['wards']):
            if b['ward'] not in wards and b != r:
                err(f"{week}: coverage row changed for {b['ward']}")
        ver, base_ver = load(d / f'{week}-verification.json'), show(a.base_ref, f'site/data/{week}-verification.json')
        if items is not None and ver['events'] != base_ver['events'] + [i[1] for i in items]:
            err(f'{week}: verification entries differ from re-derived records (or base entries changed)')
        if ver['summary'].get('total') != len(ver['events']) or ver['summary'].get('verified', 0) != base_ver['summary']['verified'] + n:
            err(f'{week}: verification summary not consistent')
        dec, base_dec = load(d / f'{week}-decisions.json'), show(a.base_ref, f'site/data/{week}-decisions.json')
        if items is not None and dec['decisions'] != base_dec['decisions'] + [i[2] for i in items]:
            err(f'{week}: decision rows differ from re-derived records (or base rows changed)')
        if dec['summary'].get('candidate_total') != len(dec['decisions']) or dec['summary'].get('published') != base_dec['summary']['published'] + n:
            err(f'{week}: decision summary not consistent')
        run, base_run = load(d / f'{week}-run.json'), show(a.base_ref, f'site/data/{week}-run.json')
        if run.get('rollover_evidence_20261118') != base_run.get('rollover_evidence_20261118'):
            err(f'{week}: receipt-backed evidence block changed')
        if run.get('summary', {}).get('source_audit_complete') is True:
            err(f'{week}: run must not claim a complete source audit')
        if (run.get('sankaku_addition_20261119') or {}).get('held_not_published') != sorted(lg.HELD):
            err(f'{week}: held list differs from the recorded dispositions')

    # Untouched weeks identical to base.
    base_manifest = show(a.base_ref, 'site/data/manifest.json')
    for wk in base_manifest['weekends']:
        if wk['sat'] not in WEEKS and load(d / wk['file']) != show(a.base_ref, f"site/data/{wk['file']}"):
            err(f"{wk['sat']}: untouched week changed")

    manifest = load(d / 'manifest.json')
    expected = [dict(x, count=x['count'] + WEEKS.get(x['sat'], 0)) for x in base_manifest['weekends']]
    if manifest['weekends'] != expected:
        err('manifest weekends differ from base with only the two week counts changed')
    if {k: v for k, v in manifest.items() if k not in ('weekends', 'generated')} != {k: v for k, v in base_manifest.items() if k not in ('weekends', 'generated')}:
        err('manifest fields other than weekends/generated changed')

    hist, base_hist = load(d / 'update_history.json'), show(a.base_ref, 'site/data/update_history.json')
    if hist['history'][:len(base_hist['history'])] != base_hist['history']:
        err('history is not append-only')
    if len(hist['history']) != len(base_hist['history']) + 1:
        err('expected exactly one history append')
    else:
        last = hist['history'][-1]
        if (last.get('run_type') != 'manual_verified_sankaku_addition' or last.get('base_data_production_sha') != BASE or
                set(last.get('new_event_ids') or []) != set(lg.NEW_IDS) or
                last.get('existing_event_records_physically_deleted') != 0 or
                last.get('global_source_audit_complete') is not False or
                last.get('source_failures_remain_unverified') is not True):
            err('history entry fields wrong')

    if errors:
        for x in errors:
            print('ERROR:', x)
        return 1
    print('SANKAKU ADDITION 20261119 PASS: 4 weekend records added (one per week 11/21, 11/28, 12/5, 12/12); '
          'all earlier records, weeks and history preserved; source debt unchanged.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
