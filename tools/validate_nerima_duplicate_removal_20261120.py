#!/usr/bin/env python3
"""Gate: exactly the five approved Nerima duplicates leave the published lists, each with a duplicate decision."""
import argparse, json, pathlib, subprocess, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import nerima_duplicate_removal_20261120 as lg

errors = []
def err(m): errors.append(m)

def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--data-dir', required=True); ap.add_argument('--pages-dir'); ap.add_argument('--tools-dir'); ap.add_argument('--base-ref', required=True)
    a = ap.parse_args(); d = pathlib.Path(a.data_dir)
    if a.base_ref != lg.BASE: err('base-ref is not the pinned data-production sha')
    def show(p): return json.loads(subprocess.check_output(['git', 'show', f'{a.base_ref}:{p}'], text=True))
    load = lambda p: json.loads(pathlib.Path(p).read_text(encoding='utf-8'))
    names = [pathlib.Path(b).name for b in subprocess.check_output(['git', 'ls-tree', '-r', '--name-only', a.base_ref, 'site/data'], text=True).split()]
    names = [n for n in names if n.endswith('.json') and (n.startswith('2026-') or n in ('manifest.json', 'update_history.json'))]
    exp = set()
    for wk, shards in lg.REMOVALS.items():
        exp |= {f'{wk}.json', f'{wk}-verification.json', f'{wk}-decisions.json', f'{wk}-run.json'} | set(shards)
    exp |= {'manifest.json', 'update_history.json'}
    changed = {n for n in names if load(d / n) != show('site/data/' + n)}
    if changed != exp: err(f'changed files differ: extra={sorted(changed-exp)} missing={sorted(exp-changed)}')
    for wk, shards in lg.REMOVALS.items():
        k = sum(len(v) for v in shards.values())
        for sh, pairs in shards.items():
            cur, base = load(d / sh), show('site/data/' + sh)
            gone = {r for r, _ in pairs}
            if [r for r in base if r['id'] not in gone] != cur: err(f'{sh}: not exactly the base minus the approved removals')
            if {r['id'] for r in base} & gone != gone: err(f'{sh}: removal ids not in base')
        w, bw = load(d / f'{wk}.json'), show(f'site/data/{wk}.json')
        if w['coverage']['published_count'] != bw['coverage']['published_count'] - k or w['coverage']['duplicate_removed'] != (bw['coverage'].get('duplicate_removed') or 0) + k or w['coverage']['candidate_count'] != bw['coverage']['candidate_count']:
            err(f'{wk}: coverage counts wrong')
        dec, bdec = load(d / f'{wk}-decisions.json'), show(f'site/data/{wk}-decisions.json')
        if len(dec['decisions']) != len(bdec['decisions']): err(f'{wk}: decision rows count changed')
        kept = {r: kk for s in shards.values() for r, kk in s}
        allids = set()
        for sh in w['event_files']:
            allids |= {r['id'] for r in load(d / sh)}
        for row in dec['decisions']:
            if row['candidate_id'] in kept:
                if row.get('decision') != 'duplicate' or row.get('duplicate_of') != kept[row['candidate_id']] or not row.get('reasons') or not str((row.get('evidence') or [{}])[0].get('url', '')).startswith('https://'):
                    err(f'{wk}: duplicate decision incomplete for {row["candidate_id"]}')
                if kept[row['candidate_id']] not in allids: err(f'{wk}: kept record {kept[row["candidate_id"]]} not published')
        if dec['summary']['duplicate'] != (bdec['summary'].get('duplicate', 0)) + k or dec['summary']['published'] != bdec['summary']['published'] - k: err(f'{wk}: decision summary wrong')
    h, bh = load(d / 'update_history.json'), show('site/data/update_history.json')
    if h['history'][:len(bh['history'])] != bh['history'] or len(h['history']) != len(bh['history']) + 1: err('history not exactly one append')
    elif sorted(h['history'][-1].get('duplicate_decisions_recorded') or []) != lg.REMOVED_IDS: err('history entry ids wrong')
    if errors:
        for x in errors: print('ERROR:', x)
        print('NERIMA DUPLICATE REMOVAL FAILED'); return 1
    print('NERIMA DUPLICATE REMOVAL PASS: 5 approved duplicates recorded and removed; nothing else changed.'); return 0
sys.exit(main())
