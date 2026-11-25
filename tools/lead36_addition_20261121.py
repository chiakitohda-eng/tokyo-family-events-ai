#!/usr/bin/env python3
"""2 weekly records (Sunshine City x1, Koganei Park x1) from committed official pages (2026-11-21).

Raw official pages are committed unchanged under research/2026-11-20-thin-wards/pages/. The gate validator re-derives every record and requires exact equality.
"""
import argparse, hashlib, json, pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import suginami_addition_20261118 as S

BASE = 'fb4999cedea142e5bac21c0a3670cfef3f3c1573'   # data-production after lead35 (766 active week records)
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
    {'id': 'verified-20261121-toshima-sunshine60-candle-workshop-2026', 'week': '2026-11-21', 'ward': '豊島区', 'page': 'sunshine_candle_workshop_2026.html',
     'name': 'クリスマスキャンドルワークショップ（サンシャイン60展望台 てんぼうパーク）', 'url': 'https://sunshinecity.jp/observatory/event/entry-39310.html', 'date': '2026-11-21', 'end': '2026-11-29',
     'period': '11/21(土)・23(月・祝)・28(土)・29(日)（12月分の日程は後日公開）', 'time': '11:00〜16:00（最終受付16:00）',
     'venue': 'サンシャイン60展望台 てんぼうパーク（池袋・サンシャインシティ）', 'price': '参加費2,530円（税込）〜（別途展望台入場料が必要）',
     'description': 'サンシャイン60展望台のてんぼうパークで開く、クリスマスのキャンドルづくり体験。グラスに色鮮やかな砂を敷き、好きなガラス細工を置いて、世界に一つだけのキャンドルを作る。対象は3歳以上で、体験は20分ほど。お渡しまで別に約40〜60分かかる。',
     'cats': ['体験・ワークショップ', 'まつり・イベント'], 'io': '屋内',
     'res': {'required': False, 'note': '予約の記載なし。各日11:00から受付、最終受付16:00。'},
     'quotes': ['クリスマスキャンドルワークショップ開催！', '開催場所サンシャイン60展望台てんぼうパーク', '11月21日（土）、23日（月・祝）', '11月28日（土）、29日（日）', '【対象年齢】3歳以上【参加費】2,530円（税込）~', '※別途展望台入場料が必要です。', '各日11:00～（最終受付16:00）'],
     'overall': 'B', 'basis': 'age_eligible', 'child': True,
     'reason': '3歳以上から参加できる、クリスマスのキャンドルづくり体験。参加費は2,530円（税込）から。展望台の入場料が別にかかり、出来上がりのお渡しまで約40〜60分待つ。',
     'axes': _ax(['B', '3歳以上が対象。子どもも楽しめる体験'], ['A', '砂とガラス細工を選んで、自分でキャンドルを作る'], ['B', '3歳以上が対象'], ['B', '開催日が限られ、受付は16:00まで'], ['B', '体験20分に加え、お渡しまで約40〜60分かかる'], ['C', '参加費2,530円〜に加え、展望台入場料が必要'], ['A', '予約の記載なし'], ['B', '展望台で過ごしながら、クリスマスの工作を楽しめる']),
     'strengths': ['3歳から参加でき、自分だけのキャンドルを作れる', '屋内で、天候に左右されない'], 'limitations': ['参加費に加えて展望台の入場料が必要', '出来上がりまでの待ち時間が長い', 'お支払いは現金のみ'],
     'comparison': '総合B：3歳から参加できる屋内の工作体験。費用は参加費と展望台入場料の両方がかかる。',
     'pf': 'pass', 'pos': ['official_date_confirmed']},
    {'id': 'verified-20261205-koganei-park-bousai-festa-2026', 'week': '2026-12-05', 'ward': '小金井市', 'page': 'koganei_bousai_festa_2026.html',
     'name': '小金井公園 防災フェスタ2026', 'url': 'https://www.tokyo-park.or.jp/park/koganei/news/2026/12_6_2026.html', 'date': '2026-12-06', 'end': '2026-12-06',
     'period': '12/6(日)', 'time': '10:00〜14:00（雨天中止）',
     'venue': '小金井公園 いこいの広場（小金井市桜町）', 'price': '入園料は無料（一部有料施設あり）。フェスタの参加費の記載なし',
     'description': '地域の人が楽しみながら防災を学べる、小金井公園の防災フェスタ。市役所・消防署・警察署・自衛隊などが出展し、新企画のインクルーシブウォークラリーと、消火器やAEDの使い方などを体験する恒例の三助スタンプラリーがある。全ブースを回ると防災グッズをもらえる。キッチンカーも出る。',
     'cats': ['まつり・イベント', '体験・ワークショップ'], 'io': '屋外',
     'res': {'required': False, 'note': '予約の記載なし。雨天中止。'},
     'quotes': ['小金井公園防災フェスタが開催決定', '【日時】12/6（日）10：00～14：00（雨天中止）', '【場所】小金井公園いこいの広場', 'インクルーシブウォークラリー', '三助スタンプラリー自助・共助の知識と経験を身に着けるための毎年恒例スタンプラリーです。'],
     'extra': [{'page': 'koganei_park_top_2026.html', 'url': 'https://www.tokyo-park.or.jp/park/koganei/', 'q': '入園料無料（一部有料施設あり）'}],
     'overall': 'B', 'basis': 'all_ages', 'child': True,
     'reason': 'ウォークラリーやスタンプラリーで、防災を体験しながら学べる公園のイベント。入園料は無料で、全ブースを回るとグッズがもらえる。雨天中止。',
     'axes': _ax(['B', '対象は地域の皆様。親子で楽しめるラリーがある'], ['A', 'ウォークラリーやスタンプラリーで体験しながら学べる'], ['B', '年齢の限定はない'], ['B', '10:00〜14:00の開催'], ['B', '屋外で、雨天中止'], ['A', '入園料は無料（一部有料施設あり）'], ['A', '予約の記載なし'], ['B', '公園で遊びながら、防災を家族で学べる']),
     'strengths': ['入園料が無料', 'スタンプラリーを回ると防災グッズをもらえる'], 'limitations': ['屋外で、雨天中止', '開催は4時間のみ'],
     'comparison': '総合B：無料で参加できる、公園での防災体験イベント。雨天中止。',
     'pf': 'pass', 'pos': ['official_date_confirmed']},
]
RAW = SPECS_RAW
SPECS = []
for _r in RAW:
    _s = dict(_r)
    _s['categories'] = _s.pop('cats'); _s['indoor_outdoor'] = _s.pop('io'); _s['reservation'] = _s.pop('res')
    _s['child_activity'] = _s.pop('child'); _s['price_field'] = _s.pop('pf'); _s['positive'] = _s.pop('pos')
    SPECS.append(_s)
NEW_IDS = [s['id'] for s in SPECS]
SHARDS = {w: f'{w}-events-lead36-20261121.json' for w in ('2026-11-21', '2026-11-28', '2026-12-05', '2026-12-12', '2026-12-19', '2026-12-26')}
HELD = {
    'urayasu-tokyo-disney-resort': '浦安市 東京ディズニーリゾート（ディズニー・クリスマス）：公式サイトがGitHub Actionsから取得できず（タイムアウト・リダイレクトのループ）、本文の引用と入園料の確認ができず保留。入園料は日・券種で変わる。',
    'taito-hanayashiki-events': '台東区 浅草花やしき：イベントカレンダーが画面表示（JavaScript）で、取得できた本文に含まれず保留。',
    'toshima-sunshine-aquarium-abydos': '豊島区 サンシャイン水族館×ブルーアーカイブ（12/11〜）：ファン向けのコラボで、子ども向けではなく保留。',
    'toshima-sunshine-pawfes': '豊島区 パウフェクト フェスティバル（12/30〜1/11）：今回の6週間の範囲外。次回以降に再確認。',
    'tokyo-zoo-association-events': '上野・井の頭・葛西の動物園・水族園：イベントカレンダーが画面表示で、取得できた本文に含まれず保留。',
    'chofu-jindai-stamp-rally': '調布市 神代植物公園の紅葉スタンプラリー：子ども向けの記載と参加費の記載がなく保留。',
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
        run['lead36_addition_20261121'] = {
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
        'run_id': 'lead36-addition-20261121', 'run_type': 'manual_verified_lead36_addition',
        'status': 'verified_subset_publication', 'as_of_jst': '2026-11-21', 'executed_at': m['generated'],
        'base_data_production_sha': BASE, 'target_weekends': sorted(derived),
        'prior_active_week_records': 766, 'candidate_active_week_records': 768, 'added_weekly_records': 2,
        'new_event_ids': NEW_IDS, 'held_not_published': sorted(HELD),
        'existing_event_records_physically_deleted': 0, 'image_only_updates': 0,
        'source_failures_remain_unverified': True, 'global_source_audit_complete': False,
        'full_23_ward_25_source_audit_complete': False,
        'note': 'サンシャインシティのキャンドルワークショップ（豊島区）と小金井公園の防災フェスタ（小金井市）を公式ページで個別に確認して追加。東京ディズニーリゾートは公式サイトが取得できず保留。',
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
