#!/usr/bin/env python3
"""Correct the provenance of decision rows whose official page is hosted by a registered fixed source
(Sankaku Hiroba, Nerima Kanko): channel explicit instead of ai_cross. Only discovery_sources of those rows change."""
import argparse, pathlib, sys
from urllib.parse import urlparse
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import suginami_addition_20261118 as S

BASE = '9124a74fc7c312838f4a3618d3824230e30a573f'   # data-production after provenance-fill-20261120
RUN_ID = 'provenance-fix-20261120'
HOSTS = {'sumitomo-sankakuhiroba.jp': 'shinjuku_sankaku_hiroba', 'nerimakanko.jp': 'nerimakanko'}
host = lambda u: urlparse(u).netloc.replace('www.', '')


def fixed_entry(ds):
    if len(ds) == 1 and ds[0].get('kind') == 'ai_cross_search' and host(ds[0].get('url', '')) in HOSTS:
        return [{'channel': 'explicit', 'kind': 'registered_source', 'source_id': HOSTS[host(ds[0]['url'])], 'url': ds[0]['url']}]
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
        'run_id': RUN_ID, 'run_type': 'manual_provenance_fix', 'status': 'metadata_only_update', 'as_of_jst': '2026-11-20',
        'executed_at': '2026-11-20T23:40:00+09:00', 'base_data_production_sha': BASE, 'target_weekends': sorted({c.split('@')[1] for c in changed}),
        'prior_active_week_records': 704, 'candidate_active_week_records': 704, 'added_weekly_records': 0,
        'new_event_ids': [], 'provenance_updated_count': len(changed), 'existing_event_records_physically_deleted': 0,
        'image_only_updates': 0, 'global_source_audit_complete': False,
        'note': '三角広場・練馬観光協会など登録済みの固定サイトに載っている公式ページの記録は、取得元を「固定サイト」に訂正。イベント本体は変更なし。'})
    S.jdump(d / 'update_history.json', h)


if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('--data-dir', required=True); a = ap.parse_args()
    try: build(a.data_dir)
    except ValueError as e: print('ERROR:', e, file=sys.stderr); sys.exit(1)
