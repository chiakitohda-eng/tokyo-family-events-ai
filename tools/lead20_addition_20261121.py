#!/usr/bin/env python3
"""7 weekly records (4 Arakawa events: Nippori Holiday Park x2, choir workshop x3, Don-to-yarou kids festival, choir concert) from the committed official Arakawa pages (2026-11-21).

Raw official pages are committed unchanged under research/2026-11-20-thin-wards/pages/
(fetched by read-only workflows, HTTP 200). Quotes must occur verbatim in those pages.
The gate validator re-derives every record from this module and requires exact equality.
"""
import argparse, hashlib, json, pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import suginami_addition_20261118 as S

BASE = 'cf93083b984aacd9b8f5258d4bd8b623a9a65e5f'   # data-production before lead20 (704 active week records)
CHECKED = '2026-11-21'
AXES = S.AXES
NOTE_AUDIT = '週別全源照合は未完（ためまっぷ403等）。この7件は荒川区公式の個別ページの確認に基づく。'
S.CHECKED = CHECKED


def _page_text(path):
    """Like suginami page_text, but falls back to the whole document when a page has no <h1>."""
    raw = pathlib.Path(path).read_text(encoding='utf-8', errors='ignore')
    i = raw.find('<h1')
    raw = raw[i:] if i >= 0 else raw
    raw = S.re.sub(r'<(script|style).*?</\1>', '', raw, flags=S.re.S)
    raw = S.re.sub(r'<br\s*/?>|</(p|li|tr|dt|dd|h\d|div|th|td)>', '\n', raw)
    return S.re.sub(r'\s+', '', S.html.unescape(S.re.sub(r'<[^>]+>', '', raw)))


def _spec(**k):
    return k

_NIPPORI_URL = 'https://www.city.arakawa.tokyo.jp/a022/event/eventkouenmeigi/nipporiholidayparkr8112122.html'
_DON_URL = 'https://www.city.arakawa.tokyo.jp/a009/chiikikatsudou/kodomomaturi/r8kodomomatsuri/r8kodomomatsuri_arakawa.html'
_WS_URL = 'https://www.city.arakawa.tokyo.jp/a015/event/workshop_gassyotai.html'
_CON_URL = 'https://www.city.arakawa.tokyo.jp/a015/event/teikiensoukai164.html'


def _nippori(date, period, week, md):
    return {'id': f'verified-{date.replace("-", "")}-arakawa-nippori-holiday-park', 'week': week, 'ward': '荒川区',
        'page': 'arakawa_nippori_holiday_park_1121.html',
        'name': 'にっぽり・ホリデー・パーク（日暮里駅前イベント広場）', 'url': _NIPPORI_URL, 'date': date, 'period': period,
        'time': '10:00〜17:00', 'venue': '日暮里駅前イベント広場（荒川区西日暮里二丁目24番）',
        'price': '入場の可否は公式ページに記載なし。ゲーム・アトラクション、飲食ブースなど費用が掛かるものがある',
        'description': '日暮里駅前イベント広場で、子どもから大人まで遊べるゲーム・アトラクション、飲食ブース、屋外ステージを開催する。荒天の場合は中止になることがある。',
        'cats': ['まつり・イベント', '親子・地域体験'], 'io': '屋外',
        'res': {'required': None, 'note': '公式ページに事前申込の記載なし。荒天時は主催のバイタル・プロジェクトのInstagramで確認。'},
        'quotes': ['子どもから大人まで遊べるゲーム・アトラクション', '日暮里駅前イベント広場（荒川区西日暮里二丁目24番）', '両日　午前10時から午後5時まで', 'ゲーム・アトラクション、飲食ブースなど費用が掛かるものがあります'],
        'overall': 'B', 'basis': 'all_ages', 'child': True,
        'reason': f'公式ページに子どもから大人まで遊べるゲーム・アトラクションと記載があり、{md}の10〜17時に駅前広場で遊べる。',
        'axes': {'child_target': ['B', '公式ページに「子どもから大人まで遊べる」とある'], 'interactivity': ['B', 'ゲーム・アトラクションと屋外ステージがある'],
                 'age_fit': ['unknown', '対象年齢の目安は明記がない'], 'stay_flexibility': ['A', '10〜17時の間に出入りして遊べる'],
                 'burden': ['B', '屋外開催で荒天時は中止になることがある'], 'cost': ['unknown', '費用が掛かるものがあるとだけ記載され、金額は不明'],
                 'reservation': ['unknown', '事前申込の記載がない'], 'family_value': ['B', '駅前広場で子どもが遊べる体験と飲食が一か所にある']},
        'strengths': ['ゲーム・アトラクションが複数ある', '10〜17時で出入り自由に近い'], 'limitations': ['屋外で荒天時は中止', '有料のブースがあり金額は不明'],
        'comparison': f'総合B：{md}の日暮里駅前で10〜17時に遊べるが、屋外で天候の影響があり、費用の金額は公式ページにない。',
        'pf': 'unknown', 'pos': ['official_date_confirmed', 'child_activity_confirmed']}


def _ws(date, period, week, md, venue_note):
    return {'id': f'verified-{date.replace("-", "")}-arakawa-gassyotai-workshop', 'week': week, 'ward': '荒川区',
        'page': 'arakawa_gassyotai_workshop_winter.html',
        'name': '東京荒川少年少女合唱隊 合唱ワークショップ（冬）', 'url': _WS_URL, 'image': 'https://www.city.arakawa.tokyo.jp/images/46863/akt_workshop_2026.jpg', 'date': date, 'period': period,
        'time': '11:00〜11:30', 'venue': '夕やけこやけふれあい館、生涯学習センター（公式ページは両施設を併記し、日ごとの会場の区別は記載なし）',
        'price': '無料', 'description': '東京荒川少年少女合唱隊のワークショップに参加し、定期演奏会の舞台で一緒に歌う。対象は年長・小学生・中学生。',
        'cats': ['音楽', '体験・ワークショップ'], 'io': '屋内',
        'res': {'required': None, 'note': '申込方法は東京荒川少年少女合唱隊のホームページで確認するよう公式ページに記載（詳細は不明）。'},
        'quotes': ['東京荒川少年少女合唱隊のワークショップに参加し、定期演奏会の舞台で一緒に歌いませんか？', '対象者　年長、小学生、中学生', '午前11時00分から午前11時30分', '夕やけこやけふれあい館、生涯学習センター'],
        'overall': 'B', 'basis': 'child_program', 'child': True,
        'reason': f'対象が年長・小学生・中学生で、{md}の11時から30分、合唱隊と一緒に歌う子ども向けの体験で、費用は無料と公式ページに記載がある。',
        'axes': {'child_target': ['A', '公式ページの対象者が年長・小学生・中学生'], 'interactivity': ['A', '合唱隊と一緒に歌う参加型の体験'],
                 'age_fit': ['B', '年長から中学生までと幅がある'], 'stay_flexibility': ['C', '30分の短い枠で時間は固定'],
                 'burden': ['B', '会場が2施設併記で当日の会場は申込先で確認が要る'], 'cost': ['A', '費用は無料と記載'],
                 'reservation': ['unknown', '申込方法は合唱隊のホームページで確認とあり、締切などは不明'], 'family_value': ['B', '子どもが演奏会の舞台に向けて歌える機会']},
        'strengths': ['対象が年長から中学生と明記', '費用無料'], 'limitations': ['30分の短い枠', '会場と申込の詳細が公式ページにない'],
        'comparison': f'総合B：{md}11時の30分、年長〜中学生向けで無料だが、会場の区別と申込の詳細は公式ページにない。',
        'pf': 'pass', 'pos': ['official_date_confirmed', 'child_activity_confirmed']}


SPECS_RAW = [
    _nippori('2026-11-21', '11/21(土)', '2026-11-21', '11/21'),
    _nippori('2026-11-22', '11/22(日)', '2026-11-21', '11/22'),
    _ws('2026-11-22', '11/22(日)', '2026-11-21', '11/22', ''),
    _ws('2026-12-06', '12/6(日)', '2026-12-05', '12/6', ''),
    _ws('2026-12-13', '12/13(日)', '2026-12-12', '12/13', ''),
    {'id': 'verified-20261206-arakawa-dontoyarou-taikai', 'week': '2026-12-05', 'ward': '荒川区', 'page': 'arakawa_dontoyarou_1206.html',
     'name': 'ドンとやろう大会（地域のこどもまつり）', 'url': _DON_URL, 'date': '2026-12-06', 'period': '12/6(日)', 'time': '10:30〜13:30',
     'venue': '第三峡田小学校（雨天時は体育館）', 'price': '参加費の記載なし（模擬店あり）',
     'description': '町会・自治会や青少年育成地区委員会等が協力して開く地域のこどもまつり。ステージやゲーム、創作コーナー、手作りコーナー、あそびコーナー、クイズラリー、模擬店などが楽しめる。車・バイク・自転車での来場は不可。',
     'cats': ['まつり・イベント', '親子・地域体験'], 'io': '屋内・屋外',
     'res': {'required': None, 'note': '公式ページに事前申込の記載なし。雨天時は体育館で実施（室内用運動靴を持参）。'},
     'quotes': ['遊びに行こう！地域のこどもまつり', 'ステージやゲーム・創作コーナー等が楽しめます。', '手作りコーナー、あそびコーナー、クイズラリー、模擬店等', '車・バイク・自転車での来場は不可'],
     'overall': 'B', 'basis': 'child_program', 'child': True,
     'reason': '公式ページが地域のこどもまつりと明記し、12/6の10:30〜13:30に手作り・あそび・クイズラリーなどの子ども向けコーナーがある。',
     'axes': {'child_target': ['A', '公式ページに「地域のこどもまつり」とある'], 'interactivity': ['A', '手作りコーナー、あそびコーナー、クイズラリーがある'],
              'age_fit': ['unknown', '対象年齢の目安は明記がない'], 'stay_flexibility': ['B', '10:30〜13:30の間に好きなコーナーを回れる'],
              'burden': ['B', '車・バイク・自転車での来場不可。雨天は体育館で室内履きが要る'], 'cost': ['unknown', '参加費の記載がない'],
              'reservation': ['unknown', '事前申込の記載がない'], 'family_value': ['B', '小学校を会場に地域の子ども向けコーナーを巡れる']},
     'strengths': ['子ども向けのこどもまつり', '手作り・あそび・クイズラリー'], 'limitations': ['車・自転車での来場不可', '参加費の記載がない'],
     'comparison': '総合B：12/6の小学校会場で10:30〜13:30に体験を回れるが、来場手段に制限があり、参加費は公式ページにない。',
     'pf': 'unknown', 'pos': ['official_date_confirmed', 'child_activity_confirmed']},
    {'id': 'verified-20261220-arakawa-gassyotai-teiki164', 'week': '2026-12-19', 'ward': '荒川区', 'page': 'arakawa_gassyotai_teiki164.html',
     'name': '東京荒川少年少女合唱隊 第164回定期演奏会', 'url': _CON_URL, 'image': 'https://www.city.arakawa.tokyo.jp/images/46619/akt_concert_20261220_omote.jpg', 'date': '2026-12-20', 'period': '12/20(日)', 'time': '開演14:00（開場13:30）',
     'venue': 'サンパール荒川 大ホール', 'price': '大人1,000円、小中学生500円（ACC友の会会員は各1割引）',
     'description': '東京荒川少年少女合唱隊の定期演奏会。「風の谷のナウシカ」「君をのせて」「もののけ姫」「トトロメドレー」「クリスマスソング集」などを歌う。チケットは町屋文化センター、サンパール荒川で販売。',
     'cats': ['コンサート', '音楽・ステージ'], 'io': '屋内',
     'res': {'required': True, 'note': 'チケット販売は町屋文化センターとサンパール荒川。'},
     'quotes': ['サンパール荒川　大ホール', '大人　1,000円　小中学生　500円', 'トトロメドレー　クリスマスソング集', 'チケット販売：町屋文化センター、サンパール荒川'],
     'overall': 'B', 'basis': 'performers_are_children', 'child': True,
     'reason': '少年少女合唱隊が出演し、ジブリ作品やクリスマスソングを歌う12/20の演奏会で、小中学生の料金が公式ページにある。',
     'axes': {'child_target': ['C', '子どもが出演する演奏会で、観客の対象年齢は明記がない'], 'interactivity': ['C', '観賞中心の演奏会'],
              'age_fit': ['unknown', '観客の対象年齢の目安は明記がない'], 'stay_flexibility': ['C', '開演14時からの座席制の公演で時間は固定'],
              'burden': ['B', '大ホールの座席制でチケットの事前購入が要る'], 'cost': ['B', '小中学生500円、大人1,000円'],
              'reservation': ['B', 'チケットの事前購入が必要'], 'family_value': ['B', '親しみのある曲を子どもの合唱で家族で聴ける']},
     'strengths': ['小中学生500円の料金設定', 'ジブリ曲とクリスマスソング'], 'limitations': ['観賞中心で参加型ではない', 'チケットの事前購入が必要'],
     'comparison': '総合B：12/20の座席制の演奏会で、小中学生500円。観賞中心で対象年齢の明記はなく、チケットの事前購入が要る。',
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
SHARDS = {w: f'{w}-events-lead20-20261121.json' for w in ('2026-11-21', '2026-11-28', '2026-12-05', '2026-12-12', '2026-12-19', '2026-12-26')}
HELD = {
    'bunkyo-futsal-1128-1219': '区内在住・在勤・在学が条件で、申込は11/1に終了（抽選）',
    'bunkyo-flyingdisc-1129': '区内在住・在学・在勤の限定で、申込は11/1に終了',
    'bunkyo-furoshiki-1213': '区内在住・在学の限定（抽選・申込は11/25まで）',
    'chuo-hinohara-tour-1212': '区内在住・在学の小学生と保護者に限定。申込は11/16に終了',
    'chuo-bunkazai-meguri-1128': '区内在住・在勤・在学の中学生以上で、申込は11/1に終了',
    'chuo-dads-swag-1205': '区内在住限定で、定員に達して募集終了',
    'arakawa-hananoki-shokudo-1121': '申込期間が11/19で終了（ひろば館利用児童の先着）',
    'arakawa-recycle-center-1128-1205-1212': '区内在住・在勤・在学の限定',
    'arakawa-fureaikan-1121-1128-1129': '公式ページに時間・内容・参加費の記載がなく内容を確認できない',
    'arakawa-kirakira-parade-1128-1220': '公式ページに子ども向けの記載がなく、あらかわ遊園の入園料が別にかかる',
    'arakawa-araboccia-1206': 'チームでの事前申込が必要で、会場・締切が公式ページにない',
    'arakawa-tougei-1129': '申込期限があり詳細が別ページ。子ども向けの記載なし',
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
                    'description': f"荒川区公式ページ（2026-11-21にHTTP200で取得、research/2026-11-20-thin-wards/pages/に不変保存）の本文引用。引用文字列だけのUTF-8 SHA-256。"})
    for x in spec.get('extra', []):
        t2 = _page_text(pathlib.Path(pages_dir) / x['page'])
        if S._strip(x['q']) not in t2:
            raise ValueError(f"{spec['id']}: calendar quote not found verbatim in the committed official calendar page: {x['q']}")
        out.append({'url': x['url'], 'quote': x['q'], 'checked_at': CHECKED,
                    'sha256': hashlib.sha256(x['q'].encode('utf-8')).hexdigest(),
                    'hash_scope': 'quoted_text_only_not_HTTP_response_hash',
                    'description': f"荒川区公式ページ（2026-11-21にHTTP200で取得、research/2026-11-20-thin-wards/pages/に不変保存）の本文引用。"})
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
        run['lead20_addition_20261121'] = {
            'kind': 'individually_verified_official_events_from_lead_triage', 'added_ids': [i[0]['id'] for i in items],
            'held_not_published': sorted(HELD), 'pages_committed_at': 'research/2026-11-20-thin-wards/pages/',
            'base_data_production_sha': BASE, 'global_source_audit_complete': False}
        S.jdump(d / f'{week}-run.json', run)
        for x in m['weekends']:
            if x['sat'] == week:
                x['count'] += n
    m['generated'] = '2026-11-21T13:00:00+09:00'
    S.jdump(d / 'manifest.json', m)
    h = S.jload(d / 'update_history.json')
    h['history'].append({
        'run_id': 'lead20-addition-20261121', 'run_type': 'manual_verified_lead20_addition',
        'status': 'verified_subset_publication', 'as_of_jst': '2026-11-21', 'executed_at': m['generated'],
        'base_data_production_sha': BASE, 'target_weekends': sorted(derived),
        'prior_active_week_records': 704, 'candidate_active_week_records': 711, 'added_weekly_records': 7,
        'new_event_ids': NEW_IDS, 'held_not_published': sorted(HELD),
        'existing_event_records_physically_deleted': 0, 'image_only_updates': 0,
        'source_failures_remain_unverified': True, 'global_source_audit_complete': False,
        'full_23_ward_25_source_audit_complete': False,
        'note': '荒川区公式の個別ページで日付・時間・会場・内容を確認できた4イベント7件（11/21週3・12/5週2・12/12週1・12/19週1）を追加。',
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
