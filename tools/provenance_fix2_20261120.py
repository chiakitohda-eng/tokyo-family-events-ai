#!/usr/bin/env python3
"""Revert the Nerima Kanko rows to ai_cross: they were not clearly taken mechanically from the fixed source (route unproven). Only discovery_sources of those rows change."""
import argparse, pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import suginami_addition_20261118 as S

BASE = 'd08af64d1378b75e847983ee184b97de5b498fea'   # data-production after provenance-fix-20261120
RUN_ID = 'provenance-fix2-20261120'


def fixed_entry(ds):
    if len(ds) == 1 and ds[0].get('channel') == 'explicit' and ds[0].get('kind') == 'registered_source' and ds[0].get('source_id') == 'nerimakanko':
        return [{'channel': 'ai_cross', 'kind': 'ai_cross_search', 'url': ds[0]['url']}]
    return None


def build(data_dir):
    d = pathlib.Path(data_dir); changed = []
    for f in sorted(d.glob('2026-*-decisions.json')):
        data = S.jload(f); touched = False
        for x in data['decisions']:
            new = fixed_entry(x.get('discovery_sources') or [])
            if new: x['discovery_sources'] = new; changed.append((x.get('published_event_id') or x.get('candidate_id')) + '@' + f.name[:10]); touched = True
        if touched: S.jdump(f, data)
    if not changed: raise ValueError('nothing to fix')
    h = S.jload(d / 'update_history.json')
    h['history'].append({
        'run_id': RUN_ID, 'run_type': 'manual_provenance_fix2', 'status': 'metadata_only_update', 'as_of_jst': '2026-11-20',
        'executed_at': '2026-11-20T23:40:00+09:00', 'base_data_production_sha': BASE, 'target_weekends': sorted({c.split('@')[1] for c in changed}),
        'prior_active_week_records': 704, 'candidate_active_week_records': 704, 'added_weekly_records': 0,
        'new_event_ids': [], 'provenance_updated_count': len(changed), 'existing_event_records_physically_deleted': 0,
        'image_only_updates': 0, 'global_source_audit_complete': False,
        'note': '練馬観光協会の2件は、固定サイトから機械的に取得した経路を確認できないため、取得元をAI探索に戻した（三角広場は固定サイトのまま）。イベント本体は変更なし。'})
    S.jdump(d / 'update_history.json', h)


if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('--data-dir', required=True); a = ap.parse_args()
    try: build(a.data_dir)
    except ValueError as e: print('ERROR:', e, file=sys.stderr); sys.exit(1)
