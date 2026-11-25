#!/usr/bin/env python3
"""Align the image URL of partial-20261129-nakano-precure-rally in the 12/5 week with the identical
record already published in the 11/28 week (image was empty there, the only field that differed).
No other field changes, no records added or removed. Source of the URL: the already published sibling records."""
import argparse, pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import suginami_addition_20261118 as S

BASE = '2e8c6f87c025b07f6b7b9f8c60544e6e40973b58'   # data-production after the Sumida image alignment (629 active week records)
EID = 'partial-20261129-nakano-precure-rally'
IMAGE = 'https://www.city.tokyo-nakano.lg.jp/kanko/city-promotion/animemangafest2026.images/animecomicfes.jpg'
TARGETS = {'2026-12-05': '2026-12-05-events-preserved-carryover.json'}
RUN_ID = 'nakano-image-alignment-20261120'


def build(data_dir):
    d = pathlib.Path(data_dir)
    changed = []
    for week, fn in TARGETS.items():
        data = S.jload(d / fn)
        rows = data if isinstance(data, list) else data['events']
        hit = [r for r in rows if r.get('id') == EID]
        if len(hit) != 1 or hit[0].get('image') not in (None, ''):
            raise ValueError(f'{fn}: expected exactly one {EID} record with empty image')
        hit[0]['image'] = IMAGE
        S.jdump(d / fn, data)
        changed.append(EID + '@' + week)
    h = S.jload(d / 'update_history.json')
    h['history'].append({
        'run_id': RUN_ID, 'run_type': 'manual_image_alignment', 'status': 'image_only_update', 'as_of_jst': '2026-11-20',
        'executed_at': '2026-11-20T17:30:00+09:00', 'base_data_production_sha': BASE, 'target_weekends': sorted(TARGETS),
        'prior_active_week_records': 629, 'candidate_active_week_records': 629, 'added_weekly_records': 0,
        'new_event_ids': [], 'image_updated': changed, 'existing_event_records_physically_deleted': 0,
        'image_only_updates': 1, 'global_source_audit_complete': False,
        'note': '同一IDの中野「プリキュアラリー」で、11/28週は画像あり、12/5週は画像が空だった食い違いを、公開済みの同じ画像URLで揃えた。画像以外は変更なし。'})
    S.jdump(d / 'update_history.json', h)


if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('--data-dir', required=True); a = ap.parse_args()
    try: build(a.data_dir)
    except ValueError as e: print('ERROR:', e, file=sys.stderr); sys.exit(1)
