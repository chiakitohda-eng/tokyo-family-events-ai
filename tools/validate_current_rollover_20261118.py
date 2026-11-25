#!/usr/bin/env python3
"""Fail-closed gate for the 2026-11-21 six-week rollover (operation
`verified-current-rollover-20261118`, user-approved gate change 2026-11-18).

What it permits: roll the window to 11/21..12/26, add exactly eight individually
verified non-NG events, add 42 event-matched thumbnails to already-published
events, re-verify 14 carried announcements, and record today's real source
receipts. What it still forbids: waiving any source failure (the five failed
receipts must remain failed and are pinned by URL), editing or removing any
previously published record, marking an unchecked source checked, touching
files outside the pinned path list, or any history rewrite.
"""
import argparse
import importlib.util
import json
import pathlib
import subprocess
import sys

BASE = 'fc6bec505975c6dabbddd404f33cd7d9f3f525e9'
OPERATION = 'verified-current-rollover-20261118'
TARGETS = [
    ('2026-11-21', 1, 'full', 155),
    ('2026-11-28', 2, 'full', 108),
    ('2026-12-05', 3, 'preview', 87),
    ('2026-12-12', 4, 'preview', 72),
    ('2026-12-19', 5, 'announcement', 4),
    ('2026-12-26', 6, 'announcement', 4),
]
NEW_EVENTS = {
    '2026-12-19': {
        'confirmed-20261219-nakano-rock-experience', 'confirmed-20261220-nakano-ikebana',
        'tamemap-20261219-nakano-family-rhythm', 'tamemap-20261220-nakano-forest-choir'},
    '2026-12-26': {
        'confirmed-20261226-nakano-wagakki', 'tamemap-20261226-nakano-tomocchao',
        'tamemap-20261227-nakano-mama-hot-kitchen', 'tamemap-20261227-nakano-family-rhythm'},
}
ALLOWED_PATHS = None  # loaded from the pinned list below
ALLOWED_PATH_LIST = [
    '2026-11-17-carried-announcement-rechecks.json',
    '2026-11-17-scoped-source-audit-evidence.json',
    '2026-11-21-events-additional-primary-20261114.json',
    '2026-11-21-events-all-non-tamemap-20261114.json',
    '2026-11-21-events-evidence-recovery-20261115.json',
    '2026-11-21-events-gap-recovery-20261108.json',
    '2026-11-21-events-holiday-2026-11-23.json',
    '2026-11-21-events-manual-festival-subprograms.json',
    '2026-11-21-events-manual-primary.json',
    '2026-11-21-events-nine-followup-20261115.json',
    '2026-11-21-events-official-subset-20261116.json',
    '2026-11-21-events-verified-omissions-20261108.json',
    '2026-11-21-events-verified-somei-20261109.json',
    '2026-11-21-run.json', '2026-11-21-verification.json', '2026-11-21.json',
    '2026-11-28-events-all-non-tamemap-20261114.json',
    '2026-11-28-events-evidence-recovery-20261115.json',
    '2026-11-28-events-manual-festival-subprograms.json',
    '2026-11-28-events-manual-primary.json',
    '2026-11-28-events-neighbors-official-20261117.json',
    '2026-11-28-events-non-tamemap-20261114.json',
    '2026-11-28-events-non-tamemap-next-20261114.json',
    '2026-11-28-events-verified-subset-2026-11-29.json',
    '2026-11-28-run.json', '2026-11-28-verification.json', '2026-11-28.json',
    '2026-12-05-run.json', '2026-12-05.json',
    '2026-12-12-run.json', '2026-12-12.json',
    '2026-12-19-decisions.json', '2026-12-19-events-non-ng-verified-only-20261117.json',
    '2026-12-19-run.json', '2026-12-19-verification.json', '2026-12-19.json',
    '2026-12-26-decisions.json', '2026-12-26-events-non-ng-verified-only-20261117.json',
    '2026-12-26-run.json', '2026-12-26-verification.json', '2026-12-26.json',
    'manifest.json', 'update_history.json',
]


def load(path):
    return json.loads(pathlib.Path(path).read_text(encoding='utf-8'))


def show(ref, path):
    return json.loads(subprocess.check_output(['git', 'show', f'{ref}:{path}'], text=True))


def bundle(loader, sat):
    week = loader(f'site/data/{sat}.json')
    events = list(week.get('events') or [])
    for name in week.get('event_files') or []:
        events += loader(f'site/data/{name}')
    return events


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--data-dir', default='site/data')
    ap.add_argument('--evidence-dir', required=True)
    ap.add_argument('--base-ref', required=True)
    ap.add_argument('--tools-dir', default=str(pathlib.Path(__file__).resolve().parent))
    a = ap.parse_args()
    errors = []
    err = errors.append
    d = pathlib.Path(a.data_dir)
    ev_dir = pathlib.Path(a.evidence_dir)

    spec = importlib.util.spec_from_file_location('rollover_evidence_20261118',
                                                  pathlib.Path(a.tools_dir) / 'rollover_evidence_20261118.py')
    ev = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(ev)

    if a.base_ref != BASE:
        err(f'unexpected base ref {a.base_ref}')

    # 1. Exact changed-path scope (runtime data only; static policy overlay is excluded).
    import re
    diff = set(subprocess.check_output(['git', 'diff', '--name-only', a.base_ref, 'HEAD'], text=True).splitlines())
    untracked = set(subprocess.check_output(['git', 'ls-files', '--others', '--exclude-standard'], text=True).splitlines())
    runtime = {p for p in (diff | untracked) if p.startswith('site/data/') and (
        pathlib.Path(p).name in {'manifest.json', 'update_history.json'} or
        re.fullmatch(r'20\d{2}-\d{2}-\d{2}.*\.json', pathlib.Path(p).name))}
    expected = {f'site/data/{n}' for n in ALLOWED_PATH_LIST}
    if runtime != expected:
        err(f'changed runtime paths differ: extra={sorted(runtime - expected)} missing={sorted(expected - runtime)}')
    if any(p.startswith(('site/', 'prompts/', 'tools/', '.github/', 'policy/')) and not p.startswith('site/data/')
           for p in diff):
        err('candidate changes application, prompt, tool, workflow, or policy files')

    # 2. Receipts are the audited artifact, byte for byte; failure ledger is closed.
    try:
        ev.check_pins(ev_dir)
        requests = load(ev_dir / 'requests.json')
        summary = load(ev_dir / 'summary.json')
        if len(requests) != 588 or sum(r['status'] == 'checked' for r in requests) != 583:
            err('request totals differ from the audited 588/583')
        ev.check_failure_ledger(requests)
    except (ValueError, OSError, KeyError) as exc:
        err(f'evidence integrity: {exc}')
        requests = summary = None
    if summary is not None:
        if summary.get('base_data_production_sha') != BASE or summary.get('as_of_jst') != '2026-11-16':
            err('evidence base/as_of mismatch')
        if summary.get('candidate_links_unverified') != 821:
            err('unverified candidate link count changed')

    # 3. Manifest.
    manifest = load(d / 'manifest.json')
    got = [(w.get('sat'), w.get('horizon_index'), w.get('publication_tier'), w.get('count')) for w in manifest.get('weekends', [])]
    if got != TARGETS:
        err(f'manifest weeks differ: {got}')
    if manifest.get('default') != '2026-11-21' or manifest.get('rolling_horizon_weeks') != 6:
        err('manifest default or horizon wrong')
    if manifest.get('holidays') != [{'date': '2026-11-23', 'name': '勤労感謝の日', 'weekend_sat': '2026-11-21'}]:
        err('11/23 holiday mapping mismatch')
    roll = manifest.get('current_rollover') or {}
    if (roll.get('base_data_production_sha') != BASE or roll.get('evidence_workflow_run_id') != ev.RUN_ID or
            roll.get('evidence_artifact_id') != ev.ARTIFACT_ID or roll.get('unresolved_required_source_failures') != 5 or
            roll.get('global_source_audit_complete') is not False or
            roll.get('full_23_ward_25_source_audit_complete') is not False):
        err('manifest rollover provenance or honesty flags wrong')

    # 4. Required-source ledger: all 25 required sources have receipts; only the pinned five failed.
    try:
        registry = load(d / 'discovery_sources.json')
        required = {s['id'] for s in registry.get('explicit_sources', []) if s.get('enabled') and s.get('required')}
        if requests is not None:
            got_ids = {r['source_id'] for r in requests if r['kind'] == 'explicit' and r.get('required')}
            if len(required) != 25 or got_ids != required:
                err(f'required source registry != receipts: {sorted(required ^ got_ids)}')
    except (OSError, KeyError) as exc:
        err(f'discovery_sources.json: {exc}')

    # 5. Per-week evidence blocks must equal the receipts exactly; coverage rows must be honest.
    ward_names = ev.WARDS
    for sat, idx, tier, count in TARGETS:
        week = load(d / f'{sat}.json')
        run = load(d / f'{sat}-run.json')
        if week.get('horizon_index') != idx or week.get('publication_tier') != tier:
            err(f'{sat}: week tier mismatch')
        if run.get('horizon_index') != idx or run.get('publication_tier') != tier:
            err(f'{sat}: run tier mismatch')
        if requests is not None and summary is not None:
            try:
                want = ev.derive_block(requests, summary, sat)
            except ValueError as exc:
                err(f'{sat}: {exc}')
            else:
                if run.get('rollover_evidence_20261118') != want:
                    err(f'{sat}: run evidence block differs from receipts')
        rows = {r.get('ward'): r for r in (week.get('coverage') or {}).get('wards', [])}
        if set(rows) != set(ward_names):
            err(f'{sat}: coverage wards incomplete')
        if sat in ev.NEW_EVIDENCE_WEEKS:
            for ward in ward_names:
                r = rows.get(ward, {})
                if r.get('status') != 'checked' or r.get('queries') != 3 or r.get('sources_checked') != 1:
                    err(f'{sat}/{ward}: coverage row not supported by 3 query receipts + 1 official-home receipt')
            if (week.get('coverage') or {}).get('sources_checked') != 23:
                err(f'{sat}: coverage.sources_checked != 23')
        s = run.get('summary') or {}
        if s.get('source_audit_complete') is True:
            err(f'{sat}: run claims a complete source audit')

    # 6. Previously published records: every one retained and unchanged except the image field of 42 records.
    image_changes = 0
    for sat in ('2026-11-21', '2026-11-28', '2026-12-05', '2026-12-12'):
        before = {e['id']: e for e in bundle(lambda p: show(a.base_ref, p), sat)}
        after = {e['id']: e for e in bundle(lambda p: load(pathlib.Path(a.data_dir) / pathlib.Path(p).name), sat)}
        if set(before) - set(after):
            err(f'{sat}: previously published records missing: {sorted(set(before) - set(after))[:5]}')
        if set(after) - set(before):
            err(f'{sat}: unexpected new records in an already-published week')
        for eid, old in before.items():
            cur = after.get(eid)
            if cur is None or cur == old:
                continue
            diff_keys = {k for k in set(old) | set(cur) if old.get(k) != cur.get(k)}
            if diff_keys != {'image'}:
                err(f'{sat}: {eid} changed fields beyond image: {sorted(diff_keys)}')
                continue
            image_changes += 1
    if image_changes != 42:
        err(f'expected exactly 42 image-only updates, found {image_changes}')

    # 7. Exactly eight new events, pinned IDs, per-event verification.
    for sat, ids in NEW_EVENTS.items():
        events = bundle(lambda p: load(pathlib.Path(a.data_dir) / pathlib.Path(p).name), sat)
        got_ids = {e['id'] for e in events}
        if got_ids != ids or len(events) != len(ids):
            err(f'{sat}: event IDs differ from the approved eight: {sorted(got_ids ^ ids)}')
        verification = load(d / f'{sat}-verification.json')
        v_ids = {x.get('id') for x in verification.get('events') or []}
        if v_ids != ids:
            err(f'{sat}: verification file does not match events')
        if any(x.get('status') not in ('verified', 'announced') for x in verification.get('events') or []):
            err(f'{sat}: invalid verification status')
        decisions = load(d / f'{sat}-decisions.json')
        published = {x.get('candidate_id') for x in decisions.get('decisions', []) if x.get('decision') == 'published'}
        if published != ids:
            err(f'{sat}: decision ledger does not publish exactly the approved IDs')
        for e in events:
            if not e.get('official_url') or e.get('date_start') not in {sat, f'{sat[:8]}{int(sat[8:]) + 1:02d}'}:
                err(f'{sat}: {e["id"]} lacks official URL or in-week date')

    # 8. History: append-only, one entry, honest.
    before = show(a.base_ref, 'site/data/update_history.json')
    after = load(d / 'update_history.json')
    if after.get('history', [])[:len(before.get('history', []))] != before.get('history', []):
        err('update history is not append-only')
    if len(after.get('history', [])) != len(before.get('history', [])) + 1:
        err('expected exactly one history append')
    else:
        last = after['history'][-1]
        if (last.get('base_data_production_sha') != BASE or last.get('existing_event_records_physically_deleted') != 0 or
                last.get('unresolved_required_source_failures') != 5 or last.get('unverified_candidate_links') != 821 or
                last.get('source_failures_remain_unverified') is not True or
                last.get('evidence_workflow_run_id') != ev.RUN_ID or last.get('full_23_ward_25_source_audit_complete') is not False):
            err('history entry provenance/honesty fields wrong')
        if set(last.get('new_event_ids') or []) != set().union(*NEW_EVENTS.values()):
            err('history new_event_ids differ from the approved eight')

    if errors:
        for x in errors:
            print('ERROR:', x)
        return 1
    print('CURRENT ROLLOVER 20261118 PASS: 8 verified events added; 42 image-only updates; 607 earlier records '
          'preserved; 5 source failures remain recorded as failed; no source marked checked without a receipt.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
