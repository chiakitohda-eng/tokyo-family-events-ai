#!/usr/bin/env python3
"""Gate: only discovery_sources of ai_cross rows on registered fixed-source hosts changed to explicit, plus one history append."""
import argparse, json, pathlib, subprocess, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import provenance_fix_20261120 as lg

errors = []
def err(m): errors.append(m)

def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--data-dir', required=True); ap.add_argument('--pages-dir'); ap.add_argument('--tools-dir'); ap.add_argument('--base-ref', required=True)
    a = ap.parse_args(); d = pathlib.Path(a.data_dir)
    if a.base_ref != lg.BASE: err('base-ref is not the pinned data-production sha')
    def show(p): return json.loads(subprocess.check_output(['git', 'show', f'{a.base_ref}:{p}'], text=True))
    load = lambda p: json.loads(pathlib.Path(p).read_text(encoding='utf-8'))
    base_files = subprocess.check_output(['git', 'ls-tree', '-r', '--name-only', a.base_ref, 'site/data'], text=True).split()
    base_files = [b for b in base_files if b.endswith('.json') and (pathlib.Path(b).name.startswith('2026-') or pathlib.Path(b).name in ('manifest.json', 'update_history.json'))]
    changed = []
    for bf in base_files:
        cur = d / pathlib.Path(bf).name
        if not cur.exists(): err(f'missing file {bf}'); continue
        if load(cur) != show(bf): changed.append(pathlib.Path(bf).name)
    bad = [c for c in changed if not (c.endswith('-decisions.json') or c == 'update_history.json')]
    if bad: err(f'unexpected changed files {bad}')
    new = {p.name for p in d.glob('*') if p.is_file() and p.suffix == '.json' and p.name.startswith('2026-')} - {pathlib.Path(b).name for b in base_files}
    if new: err(f'unexpected new files {sorted(new)}')
    bh = show('site/data/update_history.json'); n = 0
    for fn in changed:
        if fn == 'update_history.json': continue
        cur = load(d / fn); base = show('site/data/' + fn)
        if {k: v for k, v in cur.items() if k != 'decisions'} != {k: v for k, v in base.items() if k != 'decisions'}: err(f'{fn}: header changed')
        if len(cur['decisions']) != len(base['decisions']): err(f'{fn}: row count changed'); continue
        for c, b in zip(cur['decisions'], base['decisions']):
            if c == b: continue
            exp = lg.fixed_entry(b.get('discovery_sources') or [])
            if exp is None or c.get('discovery_sources') != exp or {k: v for k, v in c.items() if k != 'discovery_sources'} != {k: v for k, v in b.items() if k != 'discovery_sources'}: err(f'{fn}: unexpected change {c.get("candidate_id")}')
            n += 1
    h = load(d / 'update_history.json')
    if h['history'][:len(bh['history'])] != bh['history'] or len(h['history']) != len(bh['history']) + 1: err('history not exactly one append')
    elif h['history'][-1].get('run_type') != 'manual_provenance_fix' or h['history'][-1].get('provenance_updated_count') != n: err('history entry wrong')
    if n == 0: err('nothing updated')
    if errors:
        for x in errors: print('ERROR:', x)
        print('PROVENANCE FIX FAILED'); return 1
    print(f'PROVENANCE FIX PASS: {n} decision rows corrected to explicit; nothing else changed; history appended.'); return 0
sys.exit(main())
