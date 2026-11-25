#!/usr/bin/env python3
"""2 weekly records (Kasai Rinkai Park events, Edogawa, 11/21 and 12/5) from committed official park pages (2026-11-21).

Raw official pages are committed unchanged under research/2026-11-20-thin-wards/pages/. The gate validator re-derives every record and requires exact equality.
"""
import argparse, hashlib, json, pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import suginami_addition_20261118 as S

BASE = '04a0c93d19b732504d32cce21a6dcf8dd0f9216b'   # data-production after lead22 (718 active week records)
CHECKED = '2026-11-21'
AXES = S.AXES
NOTE_AUDIT = '週別全源照合は未完（ためまっぷ403等）。この4件は各公式ページの個別確認に基づく。'
S.CHECKED = CHECKED


def _page_text(path):
    """Like suginami page_text, but falls back to the whole document when a page has no early <h1>."""
    raw = pathlib.Path(path).read_text(encoding='utf-8', errors='ignore')
    i = raw.find('<h1')
    raw = raw[i:] if 0 <= i < 20000 else raw   # SPA pages (event site) put the only <h1> after the body; use the whole document
    raw = S.re.sub(r'<(script|style).*?</\1>', '', raw, flags=S.re.S)
    raw = S.re.sub(r'<br\s*/?>|</(p|li|tr|dt|dd|h\d|div|th|td)>', '\n', raw)
    return S.re.sub(r'\s+', '', S.html.unescape(S.re.sub(r'<[^>]+>', '', raw)))


SPECS_RAW = [
    {'id': 'verified-20261121-edogawa-kasai-micro-daisakusen', 'week': '2026-11-21', 'ward': '江戸川区', 'page': 'kasai_micro_daisakusen_20261121.html',
     'name': 'マイクロ大作戦 〜ミライの海を守ろう〜（葛西海浜公園）', 'url': 'https://kasaikaihinpark.com/event/%e5%b8%b0%e3%81%a3%e3%81%a6%e3%81%8d%e3%81%9f%ef%bc%81%e3%83%9e%e3%82%a4%e3%83%97%e3%83%a9%e6%8e%a2%e6%a4%9c%e9%9a%8a%ef%bc%81/',
     'date': '2026-11-21', 'period': '11/21(土)', 'time': '11:00〜15:00',
     'venue': '都立葛西海浜公園 西なぎさ（江戸川区臨海町）', 'price': '無料',
     'description': '砂浜でごみを探すプラごみビンゴ（全年齢、各回20組）と、海に見立てたプールで魚の形の網を使う「すくえ！海ゴミバスターズ」（3歳以上、予約不要）で、海洋プラスチックごみを遊びながら学ぶ体験型イベント。専門学校の学生が運営し、参加無料・当日参加。',
     'cats': ['自然・公園', '体験・ワークショップ'], 'io': '屋外',
     'res': {'required': False, 'note': '当日参加。海ゴミバスターズは予約・受付不要で随時参加。プラごみビンゴは各回20組（原則2名1組）。'},
     'quotes': ['2026 年 11 月 15 日（日）・11 月 21 日（土） 各日11時～15時', '小さなお子様から大人の方まで、 ご家族でお楽しみいただけます。', '場所 都立葛西海浜公園 西なぎさ', '実施時間： 11:00〜14:30(予約・受付不要で随時参加できます。)', '対象：3 歳以上 定員：制限なし', '参加費 無料 持ち物 持ち物 タオル、飲料水'],
     'overall': 'A', 'basis': 'child_program', 'child': True,
     'reason': '小さな子どもから大人まで家族で参加でき、3歳以上が遊びながら海のごみ問題を学べる無料の体験。当日参加で、プラごみビンゴは各回20組の定員制。',
     'axes': {'child_target': ['A', '「小さなお子様から大人の方まで、ご家族で」と明記され、3歳以上が遊べるゲームがある'], 'interactivity': ['A', 'ビンゴ・網ですくうゲームなど参加型'],
              'age_fit': ['A', '海ゴミバスターズは3歳以上、ビンゴは全年齢と明記'], 'stay_flexibility': ['A', '海ゴミバスターズは11:00〜14:30に随時参加できる'],
              'burden': ['B', '屋外開催で小雨決行・荒天中止。ビンゴは回ごとの定員制'], 'cost': ['A', '参加費無料'],
              'reservation': ['A', '当日参加で、予約・受付は不要'], 'family_value': ['A', '無料で家族が遊びながら海の環境を学べる']},
     'strengths': ['無料・当日参加で3歳以上が遊べる', '家族で参加できる'], 'limitations': ['屋外で荒天中止', 'プラごみビンゴは各回20組の定員制'],
     'comparison': '総合A：家族向けの無料の体験で当日参加できる。屋外・荒天中止とビンゴの定員制が条件。',
     'pf': 'pass', 'pos': ['official_date_confirmed', 'child_activity_confirmed']},
    {'id': 'verified-20261205-edogawa-kasai-beachclean-rugby', 'week': '2026-12-05', 'ward': '江戸川区', 'page': 'kasai_beachclean_rugby_20261205.html',
     'name': 'ビーチクリーン＆ラグビー体験・選手交流会（葛西海浜公園）', 'url': 'https://kasaikaihinpark.com/event/%e3%80%90%e5%8b%9f%e9%9b%86%e4%b8%ad%e3%80%91%e3%83%93%e3%83%bc%e3%83%81%e3%82%af%e3%83%aa%e3%83%bc%e3%83%b3%ef%bc%86%e3%83%a9%e3%82%b0%e3%83%93%e3%83%bc%e4%bd%93%e9%a8%93%e3%83%bb%e9%81%b8%e6%89%8b/',
     'date': '2026-12-05', 'period': '12/5(土)', 'time': '10:00〜（第1部ビーチクリーン）／11:00〜（第2部ラグビー体験・選手交流会）',
     'venue': '葛西海浜公園 西なぎさ（江戸川区臨海町）', 'price': '第1部：無料／第2部：1人1,000円（税込）',
     'image': 'https://kasaikaihinpark.com/wp-content/uploads/2026/11/ビーチクリーン＆ラグビー体験・選手交流会-1.jpg',
     'description': '浦安D-Rocksの選手と、第1部はビーチクリーン（どなたでも、無料）、第2部はラグビー体験・選手交流会（小学生20名、1,000円）。どちらもPeatixで申込が必要だが、第1部は当日参加もできる。',
     'cats': ['自然・公園', 'スポーツ', '体験・ワークショップ'], 'io': '屋外',
     'res': {'required': True, 'note': 'どちらもPeatixで申込。第1部は当日参加も可能。第2部は定員（小学生20名）に達した時点で締切。'},
     'quotes': ['【募集中】ビーチクリーン＆ラグビー体験・選手交流会', '１０時からの１部はビーチクリーン １１時からの２部はラグビー体験・選手交流会を開催します。', '場所 葛西海浜公園 西なぎさ', '１部：どなたでも／２部：小学生のお子さま２０名', '参加費 １部：無料 ／ ２部：お一人 1,000円（税込み）', 'どちらもPeatixにてお申込みが必要ですが １部については当日参加も可能です。'],
     'overall': 'B', 'basis': 'all_ages', 'child': True,
     'reason': '第1部は誰でも参加できる無料のビーチクリーン、第2部は小学生20名のラグビー体験・選手交流会（1,000円）で、家族で参加を呼びかけている。申込はPeatix。',
     'axes': {'child_target': ['B', '第2部は小学生向けだが、第1部は誰でも参加できる'], 'interactivity': ['A', 'ビーチクリーンとラグビー体験・選手との交流に参加する'],
              'age_fit': ['B', '第2部は小学生と明記、第1部は年齢制限なし'], 'stay_flexibility': ['B', '第1部と第2部が時間で分かれている'],
              'burden': ['B', '屋外で、動きやすい服装・軍手などの持ち物と、第2部は事前申込が必要'], 'cost': ['B', '第1部は無料、第2部は1人1,000円'],
              'reservation': ['B', 'Peatixで申込（第1部は当日参加も可、第2部は先着20名で締切）'], 'family_value': ['B', '家族でビーチクリーンに参加でき、小学生はラグビー体験もできる']},
     'strengths': ['第1部は無料で当日参加もできる', '小学生はラグビー選手と体験・交流できる'], 'limitations': ['第2部は1,000円・事前申込・小学生20名の定員', '屋外で防寒の備えが必要'],
     'comparison': '総合B：第1部は無料で気軽に参加できるが、小学生向けの第2部は有料・事前申込・少人数。',
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
SHARDS = {w: f'{w}-events-lead23-20261121.json' for w in ('2026-11-21', '2026-11-28', '2026-12-05', '2026-12-12', '2026-12-19', '2026-12-26')}
HELD = {
    'tokyo-park-event-search-dynamic': '東京都公園協会（都立公園）のイベント検索ページ（event_search）はJavaScriptで表示され、取得できた本文にイベントが含まれないため、都立公園（陸の公園）の一覧は未確認。',
    'ariake-nordic-walking-20261206': 'ノルディックウォーキング体験会（江東区、12/6）：小学生以上だが運動目的の企画で、子ども向けの体験とは言えないため見送り。',
    'odaiba-fishing-bbq-20261129': 'お台場釣り教室＆BBQ（港区、11/29）：予定人数に達し募集終了。',
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
        for ward in sorted({i[0]['ward'] for i in items}):
            k = sum(1 for i in items if i[0]['ward'] == ward)
            for row in cov['wards']:
                if row['ward'] == ward:
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
        run['lead23_addition_20261121'] = {
            'kind': 'individually_verified_official_events_from_lead_triage', 'added_ids': [i[0]['id'] for i in items],
            'held_not_published': sorted(HELD), 'pages_committed_at': 'research/2026-11-20-thin-wards/pages/',
            'base_data_production_sha': BASE, 'global_source_audit_complete': False}
        S.jdump(d / f'{week}-run.json', run)
        for x in m['weekends']:
            if x['sat'] == week:
                x['count'] += n
    m['generated'] = '2026-11-21T18:00:00+09:00'
    S.jdump(d / 'manifest.json', m)
    h = S.jload(d / 'update_history.json')
    h['history'].append({
        'run_id': 'lead23-addition-20261121', 'run_type': 'manual_verified_lead23_addition',
        'status': 'verified_subset_publication', 'as_of_jst': '2026-11-21', 'executed_at': m['generated'],
        'base_data_production_sha': BASE, 'target_weekends': sorted(derived),
        'prior_active_week_records': 718, 'candidate_active_week_records': 720, 'added_weekly_records': 2,
        'new_event_ids': NEW_IDS, 'held_not_published': sorted(HELD),
        'existing_event_records_physically_deleted': 0, 'image_only_updates': 0,
        'source_failures_remain_unverified': True, 'global_source_audit_complete': False,
        'full_23_ward_25_source_audit_complete': False,
        'note': '葛西海浜公園（江戸川区）のマイクロ大作戦（11/21）とビーチクリーン＆ラグビー体験・選手交流会（12/5）を公式ページで確認し、2件を追加。',
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
