#!/usr/bin/env python3
"""2 weekly records (Komae city x2) from committed official pages (2026-11-21).

Raw official pages are committed unchanged under research/2026-11-20-thin-wards/pages/. The gate validator re-derives every record and requires exact equality.
"""
import argparse, hashlib, json, pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import suginami_addition_20261118 as S

BASE = 'a2be701d53d8072eacc22daaa299f2c499bfb2be'   # data-production after image-fill4 (783 active week records)
CHECKED = '2026-11-22'
AXES = S.AXES
NOTE_AUDIT = '週別全源照合は未完（ためまっぷ403等）。この1件はGREEN SPRINGSの公式ページの個別確認に基づく。'
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
    {'id': 'verified-20261121-tachikawa-greensprings-illumination-2026', 'week': '2026-11-21', 'ward': '立川市', 'page': 'greensprings_illumination_20261122.html',
     'name': 'GREEN SPRINGS ILLUMINATION／2026 たちかわイルミネーション（GREEN SPRINGS）', 'url': 'https://greensprings.jp/event/10991/', 'date': '2026-11-21', 'end': '2027-02-14',
     'period': '〜2/14(日)の毎日（11/1から開催中）', 'time': '点灯時間は公式ページに記載なし',
     'venue': 'GREEN SPRINGS 2F 街区内（立川市緑町3-1）', 'price': '公式ページに観覧料の記載なし（要確認）',
     'image': 'https://greensprings.jp/wp/wp-content/uploads/2024/11/mk_20240105_2136_rs-scaled.jpg',
     'description': '立川のGREEN SPRINGSで、エントランスから芝生広場まで木々や空中のカラフルな光でライトアップする冬のイルミネーション。会期は2027年2月14日まで（芝生広場のみ11/3から）。隣接するサンサンロードの「2026 たちかわイルミネーション」（約60万球、〜2027/1/17）と連携している。',
     'categories': ['まつり・イベント', '自然・散歩'], 'indoor_outdoor': '屋外',
     'reservation': {'required': False, 'note': '申込・予約の記載なし。'},
     'quotes': ['GREEN SPRINGS ILLUMINATION／2026 たちかわイルミネーション',
                'エントランスから芝生広場まで、鮮やかにライトアップされた木々や空中で輝くカラフルな光が華やかに彩ります。',
                '会期：2026年11月1日(日)〜 2027年2月14日(日)※芝生広場のみ11月3日(火)～',
                '場所：GREEN SPRINGS 2F 街区内'],
     'overall': 'B', 'basis': 'all_ages', 'child_activity': False,
     'reason': '立川のGREEN SPRINGSで2027年2月14日まで続く冬のイルミネーション。エントランスから芝生広場まで光で彩られ、家族で夜の散歩ができる。点灯時間と観覧料は公式ページに記載がない。',
     'axes': {
         'child_target': ('B', '対象の限定はなく、家族で見て歩ける'),
         'interactivity': ('C', '見て歩く内容が中心'),
         'age_fit': ('B', '年齢の限定はない'),
         'stay_flexibility': ('A', '期間が長く、好きな時間に立ち寄れる'),
         'burden': ('B', '屋外のため、夜間の寒さと帰りの時間に注意'),
         'cost': ('unknown', '公式ページに観覧料の記載がない'),
         'reservation': ('A', '申込・予約の記載なし'),
         'family_value': ('B', '冬の夜に家族でイルミネーションを楽しめる'),
     },
     'strengths': ['期間が長く、好きな時間に立ち寄れる', '隣の「たちかわイルミネーション」と合わせて回れる'], 'limitations': ['点灯時間と観覧料が公式ページに記載がない', '屋外で夜間のため、防寒と帰りの時間に注意'],
     'comparison': '総合B：長期間開催の冬のイルミネーション。体験型ではなく、点灯時間と料金は要確認。',
     'status': 'verified', 'price_field': 'unknown', 'positive': ['official_date_confirmed']},
]
SPECS = [dict(_r) for _r in SPECS_RAW]
NEW_IDS = [s['id'] for s in SPECS]
SHARDS = {w: f'{w}-events-lead41-20261122.json' for w in ('2026-11-21', '2026-11-28', '2026-12-05', '2026-12-12', '2026-12-19', '2026-12-26')}
HELD = {
    'greensprings-tachikawa-toukiichi-20261127': 'GREEN SPRINGS たちかわ陶器市（11/27〜29）：陶器・日本茶の即売会で、子ども・家族向けの記載がなく、参加費・申込の記載もないため保留。',
    'greensprings-yaon-20261101': 'GREEN SPRINGS yaon（11月、17:00〜22:00）：DJ・生演奏の夜の音楽イベントで、子ども・家族向けの記載がないため保留。',
    'greensprings-kawatani-shirt-popup-20261120': 'GREEN SPRINGS 河谷シャツ POPUP SHOP（11/20〜30）：衣料品の販売で、子連れの催しではないため対象外。',
    'greensprings-green-grown-marche': 'GREEN SPRINGS GREEN GROWN MARCHE!（毎週火曜）：平日開催のため週末対象外。',
    'greensprings-street-piano-20261111': 'GREEN SPRINGS STREET PIANO：公式ページの実施日が11/11のみ（終了）のため対象外。',
    'greensprings-photomatic': 'GREEN SPRINGS Photomatic：期間未定のセルフフォト設置（常設に近い）のため対象外。',
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
                    'description': f"公式ページ（2026-11-22にHTTP200で取得、research/2026-11-20-thin-wards/pages/に不変保存）の本文引用。引用文字列だけのUTF-8 SHA-256。"})
    for x in spec.get('extra', []):
        t2 = _page_text(pathlib.Path(pages_dir) / x['page'])
        if S._strip(x['q']) not in t2:
            raise ValueError(f"{spec['id']}: calendar quote not found verbatim in the committed official calendar page: {x['q']}")
        out.append({'url': x['url'], 'quote': x['q'], 'checked_at': CHECKED,
                    'sha256': hashlib.sha256(x['q'].encode('utf-8')).hexdigest(),
                    'hash_scope': 'quoted_text_only_not_HTTP_response_hash',
                    'description': f"公式ページ（2026-11-22にHTTP200で取得、research/2026-11-20-thin-wards/pages/に不変保存）の本文引用。"})
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
               'evidence': [{'url': s['url'], 'basis': '2026-11-22 official individual event page (HTTP200); 23 ward completeness not asserted'}],
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
            is_ward = ward.endswith('区')
            row = next((r for r in (cov['wards'] if is_ward else munis) if r['ward'] == ward), None)
            if row is None and is_ward:
                raise SystemExit(f'ward row missing: {ward}')
            if row is None:
                row = {'ward': ward, 'candidate_count': 0, 'published_count': 0, 'note': '多摩拡張（v1.41）の初回。'}
                munis.append(row)
            row['candidate_count'] += k
            row['published_count'] += k
            row['note'] += f' 2026-11-22 公式個別ページ確認済み{k}件を非破壊追加。'
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
        run['lead41_addition_20261122'] = {
            'kind': 'individually_verified_official_events_from_lead_triage', 'added_ids': [i[0]['id'] for i in items],
            'held_not_published': sorted(HELD), 'pages_committed_at': 'research/2026-11-20-thin-wards/pages/',
            'base_data_production_sha': BASE, 'global_source_audit_complete': False}
        S.jdump(d / f'{week}-run.json', run)
        for x in m['weekends']:
            if x['sat'] == week:
                x['count'] += n
    m['generated'] = '2026-11-22T15:00:00+09:00'
    S.jdump(d / 'manifest.json', m)
    h = S.jload(d / 'update_history.json')
    h['history'].append({
        'run_id': 'lead41-addition-20261122', 'run_type': 'manual_verified_lead41_addition',
        'status': 'verified_subset_publication', 'as_of_jst': '2026-11-22', 'executed_at': m['generated'],
        'base_data_production_sha': BASE, 'target_weekends': sorted(derived),
        'prior_active_week_records': 783, 'candidate_active_week_records': 784, 'added_weekly_records': 1,
        'new_event_ids': NEW_IDS, 'held_not_published': sorted(HELD),
        'existing_event_records_physically_deleted': 0, 'image_only_updates': 0,
        'source_failures_remain_unverified': True, 'global_source_audit_complete': False,
        'full_23_ward_25_source_audit_complete': False,
        'note': 'GREEN SPRINGS（立川）の公式ページから、冬のイルミネーション（〜2027/2/14）を個別に確認して追加。点灯時間と観覧料は公式ページに記載がない。陶器市・yaonなどは子ども・家族向けの記載がなく保留。'
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
