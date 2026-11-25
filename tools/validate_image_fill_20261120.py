#!/usr/bin/env python3
"""Gate: only the image field of the pinned records changed (empty -> pinned URL), plus exactly one append-only history entry."""
import argparse, json, pathlib, subprocess, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import image_fill_20261120 as lg

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
    exp = sorted(list(lg.TARGETS) + ['update_history.json'])
    if sorted(changed) != exp: err(f'changed files {sorted(changed)} != {exp}')
    new = {p.name for p in d.glob('*') if p.is_file() and p.suffix == '.json' and p.name.startswith('2026-')} - {pathlib.Path(b).name for b in base_files}
    if new: err(f'unexpected new files {sorted(new)}')
    n = 0
    for fn in lg.TARGETS:
        cur = load(d / fn); base = show('site/data/' + fn)
        cr = cur if isinstance(cur, list) else cur['events']; br = base if isinstance(base, list) else base['events']
        if len(cr) != len(br): err(f'{fn}: record count changed'); continue
        for c, b in zip(cr, br):
            if c.get('id') in lg.IMAGES and b.get('image') in (None, ''):
                n += 1
                if c.get('image') != lg.IMAGES[c['id']] or {k: v for k, v in c.items() if k != 'image'} != {k: v for k, v in b.items() if k != 'image'}:
                    err(f'{fn}: more than the image changed {c.get("id")}')
            elif c != b: err(f'{fn}: other record changed {c.get("id")}')
    if n != len(lg.IMAGES): err(f'filled {n} != {len(lg.IMAGES)}')
    h, bh = load(d / 'update_history.json'), show('site/data/update_history.json')
    if h['history'][:len(bh['history'])] != bh['history'] or len(h['history']) != len(bh['history']) + 1: err('history not exactly one append')
    elif h['history'][-1].get('run_type') != 'manual_image_alignment' or h['history'][-1].get('existing_event_records_physically_deleted') != 0: err('history entry wrong')
    if errors:
        for x in errors: print('ERROR:', x)
        print('IMAGE FILL FAILED'); return 1
    print(f'IMAGE FILL PASS: {n} image fields filled; nothing else changed; history appended.'); return 0
sys.exit(main())
