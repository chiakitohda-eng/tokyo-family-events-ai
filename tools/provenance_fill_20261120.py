#!/usr/bin/env python3
"""Add the discovery provenance (channel) to the decision rows of records added since 2026-11-18.
All of them were found by AI cross search (web search) and confirmed on the official page, so the channel is ai_cross.
Only the decision rows' discovery_sources field changes; no event record, no other field."""
import argparse, pathlib, re, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import suginami_addition_20261118 as S

BASE = 'b2e210da009baa911b94a90e74c53d2dca83a4ec'   # data-production after image-fill3-20261120
RUN_ID = 'provenance-fill-20261120'
AUX = re.compile(r'-(decisions|verification|run|v16-rereview|events-\d+|events-parity)\.json$')


def new_ids(history):
    out = set()
    for r in history:
        if r.get('as_of_jst', '') >= '2026-11-18': out |= set(r.get('new_event_ids') or [])
    return out


def event_urls(d):
    urls = {}
    for f in sorted(d.glob('2026-*.json')):
        if AUX.search(f.name): continue
        data = S.jload(f); rows = data if isinstance(data, list) else data.get('events', [])
        for e in rows:
            if isinstance(e, dict) and e.get('id'): urls.setdefault(e['id'], e.get('official_url') or e.get('url') or '')
    return urls


def decision_files(d):
    return sorted(f for f in d.glob('2026-*-decisions.json'))


def build(data_dir):
    d = pathlib.Path(data_dir); h = S.jload(d / 'update_history.json')
    ids = new_ids(h['history']); urls = event_urls(d); changed = []
    for f in decision_files(d):
        data = S.jload(f); touched = False
        for x in data['decisions']:
            eid = x.get('published_event_id') or x.get('candidate_id') or ''
            if (eid in ids or x.get('candidate_id') in ids) and not x.get('discovery_sources'):
                url = urls.get(eid) or urls.get(x.get('candidate_id') or '') or ''
                if not url: continue
                x['discovery_sources'] = [{'channel': 'ai_cross', 'kind': 'ai_cross_search', 'url': url}]
                changed.append(eid + '@' + f.name[:10]); touched = True
        if touched: S.jdump(f, data)
    if not changed: raise ValueError('no decision rows to update')
    h['history'].append({
        'run_id': RUN_ID, 'run_type': 'manual_provenance_fill', 'status': 'metadata_only_update', 'as_of_jst': '2026-11-20',
        'executed_at': '2026-11-20T23:30:00+09:00', 'base_data_production_sha': BASE, 'target_weekends': sorted({c.split('@')[1] for c in changed}),
        'prior_active_week_records': 704, 'candidate_active_week_records': 704, 'added_weekly_records': 0,
        'new_event_ids': [], 'provenance_updated_count': len(changed), 'existing_event_records_physically_deleted': 0,
        'image_only_updates': 0, 'global_source_audit_complete': False,
        'note': '2026-11-18以降に追加した記録の判断記録に、取得経路（AI横断探索で見つけ、公式ページで確認）を追記。イベント本体・他の項目は変更なし。過去分は推測で付けず不明のまま。'})
    S.jdump(d / 'update_history.json', h)


if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('--data-dir', required=True); a = ap.parse_args()
    try: build(a.data_dir)
    except ValueError as e: print('ERROR:', e, file=sys.stderr); sys.exit(1)
