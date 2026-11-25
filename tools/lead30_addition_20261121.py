#!/usr/bin/env python3
"""1 weekly record (Tama expansion: Tachikawa x1) from committed official pages (2026-11-21).

Raw official pages are committed unchanged under research/2026-11-20-thin-wards/pages/. The gate validator re-derives every record and requires exact equality.
"""
import argparse, hashlib, json, pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import suginami_addition_20261118 as S

BASE = '15b18aa7e38622c8ffe1917b3ae5f147964495de'   # data-production after lead27 (751 active week records)
CHECKED = '2026-11-21'
AXES = S.AXES
NOTE_AUDIT = '週別全源照合は未完（ためまっぷ403等）。この1件は多摩各市の公式ページの個別確認に基づく。'
S.CHECKED = CHECKED


def _page_text(path):
    """Like suginami page_text, but falls back to the whole document when a page has no early <h1>."""
    raw = pathlib.Path(path).read_text(encoding='utf-8', errors='ignore')
    i = raw.find('<h1')
    raw = raw[i:] if 0 <= i < 20000 else raw   # SPA pages (event site) put the only <h1> after the body; use the whole document
    raw = S.re.sub(r'<(script|style).*?</\1>', '', raw, flags=S.re.S)
    raw = S.re.sub(r'<br\s*/?>|</(p|li|tr|dt|dd|h\d|div|th|td)>', '\n', raw)
    return S.re.sub(r'\s+', '', S.html.unescape(S.re.sub(r'<[^>]+>', '', raw)))



def _ax(ct, it, af, st, bu, co, re_, fv):
    return {'child_target': ct, 'interactivity': it, 'age_fit': af, 'stay_flexibility': st, 'burden': bu, 'cost': co, 'reservation': re_, 'family_value': fv}


_TAMA = 'https://www.city.tama.lg.jp/kosodate/1008019/1008033'

SPECS_RAW = [
    {'id': 'verified-20261205-tachikawa-xmas-takamatsuri-eigakai', 'week': '2026-12-05', 'ward': '立川市', 'page': 'tachikawa_xmas_takamatsuri_20261205.html',
     'name': 'クリスマスたかまつり クリスマス映画会「パンダコパンダ」（高松学習館）', 'url': 'https://www.city.tachikawa.lg.jp/event/e-kodomo/1028344.html', 'date': '2026-12-05', 'period': '12/5(土)', 'time': '11:00〜11:35／13:30〜14:05（2回上映）',
     'venue': '高松学習館（立川市高松町3-22-5）', 'price': '無料（費用なし）',
     'description': '12月5日に高松学習館で開くクリスマス映画会。上映作品は「パンダコパンダ」で、午前11時と午後1時30分の2回（各約35分）。対象はどなたでも。事前申込が必要で、定員は各回30人。',
     'cats': ['舞台・音楽', 'まつり・イベント'], 'io': '屋内',
     'res': {'required': True, 'note': '申込必要。11/10 9:00から電子申請または電話（高松学習館）。各回30人。受付状況は公式ページに記載なし。'},
     'quotes': ['開催日 2026年12月5日（土曜日） 開催時間 上映時間（2回上映） 第1回目 午前11時から11時35分 第2回目 午後1時30分から2時5分',
                '開催場所 高松学習館 所在地 立川市高松町3-22-5',
                '対象 どなたでも ハッシュタグ #人気、#無料',
                '上映作品は「パンダコパンダ」です。',
                '申込み 必要 11月10日（火曜日）午前9時より電子申請またはお電話で高松学習館（042-527-0014）にお申し込みください。',
                '費用 なし 定員 各回30人'],
     'overall': 'B', 'basis': 'all_ages', 'child': True,
     'reason': '子ども向けのアニメ「パンダコパンダ」を無料で上映するクリスマス映画会（約35分×2回）。事前申込が必要で、定員は各回30人。',
     'axes': _ax(['B', '対象はどなたでも。「子ども・子育て」カテゴリの映画会'], ['C', '映画の鑑賞が中心'], ['B', '年齢の限定はなく、約35分と短い'], ['B', '午前と午後の2回から選べる（各約35分）'], ['B', '事前申込が必要で、定員は各回30人'], ['A', '費用はなし'], ['B', '申込必要（11/10から受付、受付状況は未記載）'], ['B', '短いアニメを無料で見られる']),
     'strengths': ['無料で、約35分と短く、小さな子にも見やすい', '午前・午後の2回から選べる'], 'limitations': ['事前申込が必要で、定員は各回30人', '受付状況は公式ページに記載がなく、満席の場合がある'],
     'comparison': '総合B：無料の短いアニメ映画会。事前申込が必要で、定員が少ない。',
     'pf': 'pass', 'pos': ['official_date_confirmed', 'child_activity_confirmed']},
]
RAW = SPECS_RAW
SPECS = []
for _r in RAW:
    _s = dict(_r)
    _s['categories'] = _s.pop('cats'); _s['indoor_outdoor'] = _s.pop('io'); _s['reservation'] = _s.pop('res')
    _s['child_activity'] = _s.pop('child'); _s['price_field'] = _s.pop('pf'); _s['positive'] = _s.pop('pos')
    SPECS.append(_s)
NEW_IDS = [s['id'] for s in SPECS]
SHARDS = {w: f'{w}-events-lead30-20261121.json' for w in ('2026-11-21', '2026-11-28', '2026-12-05', '2026-12-12', '2026-12-19', '2026-12-26')}
HELD = {
    'tachikawa-moruku-20261128': '立川市 第3回モルック大会（11/28）：市内在住・在勤・在学が条件で、申込も終了しているため保留。',
    'tachikawa-tamagawa-cleanup-20261128': '立川市 美しい多摩川クリーンアップ作戦（11/28）：費用の記載がなく、清掃活動のため保留。',
    'tachikawa-kamui-no-uta-20261212': '立川市 平和人権ロードショー『カムイのうた』（12/12）：子ども向けの記載がなく保留。',
    'tachikawa-barbarian-20261212': '立川市 多文化共生映画上映会「バーバリアン狂騒曲」（12/12）：大人向けの内容で保留。',
    'tachikawa-kurashi-festa-pre-20261212': '立川市 くらしフェスタ立川プレ企画映画会（12/12）：青年・成人向けで保留。',
    'remaining-cities': '小金井・小平・国分寺・西東京・日野・狛江・町田・国立の週末の個別イベントは、公式根拠（日付・場所・費用）を引き続き調査中。',
}


def evidence(spec, pages_dir):
    text = _page_text(pathlib.Path(pages_dir) / spec['page'])
    out = []
    for q in spec['quotes']:
        if S._strip(q) not in text:
            raise ValueError(f"{spec['id']}: quote not found verbatim in the committed official page: {q}")
        out.append({'url': spec['url'], 'quote': q, 'checked_at': CHECKED,
                    'sha256': hashlib.sha256(q.encode('utf-8')).hexdigest(),
                    'hash_scope': 'quoted_text_only_not_HTTP_response_hash',
                    'description': f"公式ページ（2026-11-21にHTTP200で取得、research/2026-11-20-thin-wards/pages/に不変保存）の本文引用。引用文字列だけのUTF-8 SHA-256。"})
    for x in spec.get('extra', []):
        t2 = _page_text(pathlib.Path(pages_dir) / x['page'])
        if S._strip(x['q']) not in t2:
            raise ValueError(f"{spec['id']}: calendar quote not found verbatim in the committed official calendar page: {x['q']}")
        out.append({'url': x['url'], 'quote': x['q'], 'checked_at': CHECKED,
                    'sha256': hashlib.sha256(x['q'].encode('utf-8')).hexdigest(),
                    'hash_scope': 'quoted_text_only_not_HTTP_response_hash',
                    'description': f"公式ページ（2026-11-21にHTTP200で取得、research/2026-11-20-thin-wards/pages/に不変保存）の本文引用。"})
    return out


def derive(pages_dir):
    out = {}
    for s in SPECS:
        ev = evidence(s, pages_dir)
        if s.get('image'):
            _raw = (pathlib.Path(pages_dir) / s['page']).read_text(encoding='utf-8', errors='ignore')
            if s['image'] not in _raw and S.re.sub(r'^https?://[^/]+', '', s['image']) not in _raw:
                raise ValueError(f"{s['id']}: image URL is not declared on the committed official page")
        fit = S.family_fit(s, ev)
        event = {
            'id': s['id'], 'ward': s['ward'], 'name': s['name'], 'url': s['url'], 'official_url': s['url'], 'source': s['url'],
            'image': s.get('image', ''), 'period': s['period'], 'date_start': s['date'], 'date_end': s.get('end', s['date']), 'time': s['time'],
            'venue': s['venue'], 'price': s['price'], 'description': s['description'], 'categories': s['categories'],
            'indoor_outdoor': s['indoor_outdoor'], 'reservation': s['reservation'], 'family_fit': fit,
            'audit': {'checked_on': CHECKED, 'calendar_index_url': None, 'source_claim': 'verified',
                      'global_23_ward_source_audit_complete': False},
        }
        ver = {'id': s['id'], 'status': 'verified', 'source': s['url'], 'source_kind': 'public_official', 'verified_on': CHECKED,
               'fields': {'name': 'pass', 'date': 'pass', 'venue': 'pass', 'time': 'pass', 'price': s['price_field'],
                          'reservation': 'pass' if s['reservation']['required'] is not None else 'unknown', 'official_url': 'pass'},
               'corrections': {}, 'note': NOTE_AUDIT, 'evidence': ev}
        dec = {'candidate_id': s['id'], 'name': s['name'], 'ward': s['ward'], 'decision': 'published', 'family_fit': fit,
               'positive_signals': s['positive'], 'negative_signals': ['global_source_audit_pending'],
               'hard_exclusion': None, 'exclusion_type': None, 'primary_reason_code': 'family_value_high',
               'reason_codes': ['family_value_high'], 'reasons': [s['reason']],
               'evidence': [{'url': s['url'], 'basis': '2026-11-21 official individual event page (HTTP200); 23 ward completeness not asserted'}],
               'override_reason': '',
               'discovery_sources': [{'channel': 'ai_cross', 'kind': 'ai_cross_search', 'url': s['url']}]}
        out.setdefault(s['week'], []).append((event, ver, dec))
    return out


def build(data_dir, pages_dir):
    d = pathlib.Path(data_dir)
    derived = derive(pages_dir)
    m = S.jload(d / 'manifest.json')
    for week, items in derived.items():
        n = len(items)
        S.jdump(d / SHARDS[week], [i[0] for i in items])
        w = S.jload(d / f'{week}.json')
        w['event_files'] = list(w['event_files']) + [SHARDS[week]]
        cov = w['coverage']
        cov['candidate_count'] += n
        cov['published_count'] += n
        munis = cov.setdefault('municipalities', [])
        for ward in sorted({i[0]['ward'] for i in items}):
            k = sum(1 for i in items if i[0]['ward'] == ward)
            row = next((r for r in munis if r['ward'] == ward), None)
            if row is None:
                row = {'ward': ward, 'candidate_count': 0, 'published_count': 0, 'note': '多摩拡張（v1.41）の初回。'}
                munis.append(row)
            row['candidate_count'] += k
            row['published_count'] += k
            row['note'] += f' 2026-11-21 公式個別ページ確認済み{k}件を非破壊追加。'
        S.jdump(d / f'{week}.json', w)
        v = S.jload(d / f'{week}-verification.json')
        v['events'] += [i[1] for i in items]
        v['summary'] = dict(v['summary'], total=v['summary']['total'] + n, verified=v['summary']['verified'] + n)
        S.jdump(d / f'{week}-verification.json', v)
        dec = S.jload(d / f'{week}-decisions.json')
        dec['decisions'] += [i[2] for i in items]
        dec['summary'] = dict(dec['summary'], candidate_total=dec['summary']['candidate_total'] + n,
                              published=dec['summary']['published'] + n)
        S.jdump(d / f'{week}-decisions.json', dec)
        run = S.jload(d / f'{week}-run.json')
        run['summary'] = dict(run['summary'], candidates=run['summary']['candidates'] + n,
                              published=run['summary']['published'] + n, verified=run['summary']['verified'] + n)
        run['lead30_addition_20261121'] = {
            'kind': 'individually_verified_official_events_from_lead_triage', 'added_ids': [i[0]['id'] for i in items],
            'held_not_published': sorted(HELD), 'pages_committed_at': 'research/2026-11-20-thin-wards/pages/',
            'base_data_production_sha': BASE, 'global_source_audit_complete': False}
        S.jdump(d / f'{week}-run.json', run)
        for x in m['weekends']:
            if x['sat'] == week:
                x['count'] += n
    m['generated'] = '2026-11-21T20:00:00+09:00'
    S.jdump(d / 'manifest.json', m)
    h = S.jload(d / 'update_history.json')
    h['history'].append({
        'run_id': 'lead30-addition-20261121', 'run_type': 'manual_verified_lead30_addition',
        'status': 'verified_subset_publication', 'as_of_jst': '2026-11-21', 'executed_at': m['generated'],
        'base_data_production_sha': BASE, 'target_weekends': sorted(derived),
        'prior_active_week_records': 751, 'candidate_active_week_records': 752, 'added_weekly_records': 1,
        'new_event_ids': NEW_IDS, 'held_not_published': sorted(HELD),
        'existing_event_records_physically_deleted': 0, 'image_only_updates': 0,
        'source_failures_remain_unverified': True, 'global_source_audit_complete': False,
        'full_23_ward_25_source_audit_complete': False,
        'note': '多摩拡張の第6弾として、立川市（クリスマスたかまつり・クリスマス映画会）を公式の個別ページで確認して追加。'
    })
    S.jdump(d / 'update_history.json', h)


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--data-dir', required=True)
    ap.add_argument('--pages-dir', default='research/2026-11-20-thin-wards/pages')
    a = ap.parse_args()
    try:
        build(a.data_dir, a.pages_dir)
    except ValueError as exc:
        print('ERROR:', exc, file=sys.stderr)
        sys.exit(1)
