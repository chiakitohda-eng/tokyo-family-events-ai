#!/usr/bin/env python3
"""Fill event-specific thumbnails (image) for records added this week whose image was empty.
Each URL is declared on the record's own official page (og:image or an image attached to that page); generic site logos/shared images are excluded.
Image-only: no record added/removed, no other field changed."""
import argparse, pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import suginami_addition_20261118 as S

BASE = 'd550d33d3c02189794284edbe0f4878234771112'   # data-production after image-fill2-20261120 (704 active week records)
RUN_ID = 'image-fill3-20261120'
TARGETS = ['2026-11-21-events-lead10-20261119.json']
IMAGES = {
    'verified-20261121-katsushika-nishikameari-plarail': 'https://www.city.katsushika.lg.jp/_res/projects/default_project/_page_/001/043/520/nisikamearimonn.jpg',
    'verified-20261122-katsushika-otanoshimi-trainday': 'https://www.city.katsushika.lg.jp/_res/projects/default_project/_page_/001/000/586/wakuwakutorein.jpg',
}


def build(data_dir):
    d = pathlib.Path(data_dir); changed = []
    for fn in TARGETS:
        data = S.jload(d / fn); rows = data if isinstance(data, list) else data['events']
        for r in rows:
            if r.get('id') in IMAGES and r.get('image') in (None, ''):
                r['image'] = IMAGES[r['id']]; changed.append(r['id'] + '@' + fn[:10])
        S.jdump(d / fn, data)
    if len(changed) != len(IMAGES) or len(set(changed)) != len(changed):
        raise ValueError(f'expected {len(IMAGES)} image fills, got {len(changed)}')
    h = S.jload(d / 'update_history.json')
    h['history'].append({
        'run_id': RUN_ID, 'run_type': 'manual_image_alignment', 'status': 'image_only_update', 'as_of_jst': '2026-11-20',
        'executed_at': '2026-11-20T22:40:00+09:00', 'base_data_production_sha': BASE, 'target_weekends': ['2026-11-21'],
        'prior_active_week_records': 704, 'candidate_active_week_records': 704, 'added_weekly_records': 0,
        'new_event_ids': [], 'image_updated': changed, 'existing_event_records_physically_deleted': 0,
        'image_only_updates': len(changed), 'global_source_audit_complete': False,
        'note': '今週追加した公式ページ由来の記録のうち、公式ページに掲載された行事固有の画像があるものだけサムネイルを設定。サイト共通ロゴ・共有画像は対象外。画像以外は変更なし。'})
    S.jdump(d / 'update_history.json', h)


if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('--data-dir', required=True); a = ap.parse_args()
    try: build(a.data_dir)
    except ValueError as e: print('ERROR:', e, file=sys.stderr); sys.exit(1)
