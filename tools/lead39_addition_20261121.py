#!/usr/bin/env python3
"""2 weekly records (Inokashira Park Zoo x2) from committed official pages (2026-11-21).

Raw official pages are committed unchanged under research/2026-11-20-thin-wards/pages/. The gate validator re-derives every record and requires exact equality.
"""
import argparse, hashlib, json, pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import suginami_addition_20261118 as S

BASE = '13168b41aac713ca69ed6d2f6453412919ca2027'   # data-production after lead38 (779 active week records)
CHECKED = '2026-11-21'
AXES = S.AXES
NOTE_AUDIT = '週別全源照合は未完（ためまっぷ403等）。この4件は多摩各市の公式ページの個別確認に基づく。'
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
    {'id': 'verified-20261121-musashino-inokashira-zoo-stamp-rally-shinka-2026', 'week': '2026-11-21', 'ward': '武蔵野市', 'page': 'inokashira_stamp_rally_2026.html',
     'name': '秋のスタンプラリー「続・しんかのふしぎ」（井の頭自然文化園）', 'url': 'https://www.tokyo-zoo.net/inokashira/news/13386/index.html', 'date': '2026-11-21', 'end': '2026-12-06',
     'period': '10/10(土)〜12/6(日)（開催中）', 'time': '9:30〜17:00（水生物館は16:45まで）',
     'venue': '井の頭自然文化園 動物園（本園）・水生物園（分園）（武蔵野市御殿山1-17-6）', 'price': '公式ページに金額の明記なし（来園前に要確認）',
     'description': 'クイズを解きながら園内の生きものや植物12か所をめぐり、「進化の系統樹」を完成させるスタンプラリー。台紙は動物園正門先広場と水生物園の七井門先で配る。台紙は各日先着（平日150部・土日祝800部）。',
     'categories': ['体験・ワークショップ', '公園・自然'], 'indoor_outdoor': '屋内・屋外',
     'reservation': {'required': False, 'note': '申込の記載なし。台紙は各日先着で配布し、なくなり次第終了。'},
     'quotes': ['2026年10月10日（土）～12月6日（日）', '井の頭自然文化園・動物園（本園）正門先広場', 'クイズを解きながら園内の生きものや植物をめぐり、進化の系統樹を完成させましょう。', '各日先着150部（平日）/800部（土日祝）'],
     'overall': 'B', 'basis': 'all_ages', 'child_activity': True,
     'reason': 'クイズを解きながら園内の生きものをめぐるスタンプラリー。年齢の限定はなく、子どもが楽しみやすい。台紙は各日先着で、料金は公式ページに金額の記載がない。',
     'axes': {
         'child_target': ('B', '年齢の限定はなく、子どもも参加しやすいクイズ形式'),
         'interactivity': ('A', 'クイズを解きながらスタンプを集めて園内をめぐる'),
         'age_fit': ('B', '年齢の限定はない'),
         'stay_flexibility': ('A', '約2か月と長く、開園時間内で好きな時間に回れる'),
         'burden': ('B', '本園と分園の間は徒歩約5分で、屋外を歩く'),
         'cost': ('unknown', '公式ページに金額の記載がない'),
         'reservation': ('A', '申込の記載なし（台紙は先着配布）'),
         'family_value': ('B', '動物を見ながら進化や生きもののことを学べる'),
     },
     'strengths': ['約2か月と長く、好きな日に回れる', 'クイズで生きものについて学べる'], 'limitations': ['台紙は各日先着で、なくなり次第終了', '料金は公式ページに記載がなく、来園前の確認が必要'],
     'comparison': '総合B：動物園で楽しみながら学べるスタンプラリー。台紙は先着で、料金は要確認。',
     'status': 'verified', 'price_field': 'unknown', 'positive': ['official_date_confirmed']},
    {'id': 'verified-20261128-musashino-inokashira-zoo-ochiba-oekaki-2026', 'week': '2026-11-28', 'ward': '武蔵野市', 'page': 'inokashira_nov_events_2026.html',
     'name': '植物担当職員による「落ち葉でお絵描き」（井の頭自然文化園）', 'url': 'https://www.tokyo-zoo.net/inokashira/news/13683/index.html', 'date': '2026-11-28', 'end': '2026-11-28',
     'period': '11/28(土)', 'time': '14:00〜14:30',
     'venue': '井の頭自然文化園 動物園（本園）資料館2階 集会室（武蔵野市御殿山1-17-6）', 'price': '公式ページに金額の明記なし（来園前に要確認）',
     'description': '色とりどりの落ち葉を使って絵を描く、植物担当職員によるイベント。未就学児から小学校低学年のお子さんでも楽しめる。定員は25組程度。',
     'categories': ['体験・ワークショップ', '公園・自然'], 'indoor_outdoor': '屋内',
     'reservation': {'required': False, 'note': '申込の記載なし。定員は25組程度。'},
     'quotes': ['色とりどりの落ち葉を使って、お絵描きをするイベントです。', '未就学児から小学校低学年のお子さんでも楽しめます。', '2026年11月28日（土）14時〜14時30分', '動物園（本園）資料館2階集会室'],
     'overall': 'B', 'basis': 'child_program', 'child_activity': True,
     'reason': '未就学児から小学校低学年でも楽しめる、落ち葉を使ったお絵描き。30分で終わり、屋内で行う。定員は25組程度で、料金は公式ページに金額の記載がない。',
     'axes': {
         'child_target': ('A', '未就学児から小学校低学年が楽しめる内容'),
         'interactivity': ('A', '落ち葉を使って自分で絵を描く'),
         'age_fit': ('A', '未就学児から小学校低学年と、対象がはっきりしている'),
         'stay_flexibility': ('C', '14:00〜14:30の30分だけ'),
         'burden': ('B', '屋内で30分と短いが、定員は25組程度'),
         'cost': ('unknown', '公式ページに金額の記載がない'),
         'reservation': ('B', '申込の記載はないが、定員は25組程度'),
         'family_value': ('B', '自然の材料で、動物園の資料館で絵を楽しめる'),
     },
     'strengths': ['未就学児から小学校低学年が楽しめる', '屋内で、落ち葉を使って自由に描ける'], 'limitations': ['14:00〜14:30の30分だけで、定員は25組程度', '料金は公式ページに記載がなく、来園前の確認が必要'],
     'comparison': '総合B：幼児から低学年向けの短い自然工作。時間が短く、定員があり、料金は要確認。',
     'status': 'verified', 'price_field': 'unknown', 'positive': ['official_date_confirmed']},
]
SPECS = [dict(_r) for _r in SPECS_RAW]
NEW_IDS = [s['id'] for s in SPECS]
SHARDS = {w: f'{w}-events-lead39-20261121.json' for w in ('2026-11-21', '2026-11-28', '2026-12-05', '2026-12-12', '2026-12-19', '2026-12-26')}
HELD = {
    'inokashira-zoo-volunteer-programs': '井の頭自然文化園のボランティア企画（ボトルウォッチング11/21・糸つむぎ11/22・紙芝居11/28など）：対象年齢の記載がなく、子ども向けか判断できず保留。',
    'ueno-kasai-zoo-events': '上野・葛西：期間内の子ども向けイベントなし（葛西の海鳥イベントは中学生以上向け）。',
    'urayasu-tokyo-disney-resort': '浦安市 東京ディズニーリゾート：公式サイトを取得できず保留。',
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
            is_ward = ward.endswith('区')
            row = next((r for r in (cov['wards'] if is_ward else munis) if r['ward'] == ward), None)
            if row is None and is_ward:
                raise SystemExit(f'ward row missing: {ward}')
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
        run['lead39_addition_20261121'] = {
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
        'run_id': 'lead39-addition-20261121', 'run_type': 'manual_verified_lead39_addition',
        'status': 'verified_subset_publication', 'as_of_jst': '2026-11-21', 'executed_at': m['generated'],
        'base_data_production_sha': BASE, 'target_weekends': sorted(derived),
        'prior_active_week_records': 779, 'candidate_active_week_records': 781, 'added_weekly_records': 2,
        'new_event_ids': NEW_IDS, 'held_not_published': sorted(HELD),
        'existing_event_records_physically_deleted': 0, 'image_only_updates': 0,
        'source_failures_remain_unverified': True, 'global_source_audit_complete': False,
        'full_23_ward_25_source_audit_complete': False,
        'note': '井の頭自然文化園（武蔵野市）の秋のスタンプラリーと落ち葉でお絵描きを、東京ズーネットの公式ページで個別に確認して追加。料金は公式ページに金額の記載がないため「料金要確認」で掲載。',
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
