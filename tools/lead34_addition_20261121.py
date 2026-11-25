#!/usr/bin/env python3
"""4 weekly records (Theme parks: Tama x1, Bunkyo x2, Hino x1) from committed official pages (2026-11-21).

Raw official pages are committed unchanged under research/2026-11-20-thin-wards/pages/. The gate validator re-derives every record and requires exact equality.
"""
import argparse, hashlib, json, pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import suginami_addition_20261118 as S

BASE = '0f84cff8a5ec34592502d0b130e1a5bf301834eb'   # data-production after lead27 (760 active week records)
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
    {'id': 'verified-20261121-tama-puroland-illumination-xmas-2026', 'week': '2026-11-21', 'ward': '多摩市', 'page': 'puroland_illumination_xmas_2026.html',
     'name': 'Puroland Illumination Christmas（サンリオピューロランド）', 'url': 'https://www.puroland.jp/event-campaign/2026_christmas/', 'date': '2026-11-21', 'end': '2026-12-25', 'period': '11/6(金)〜12/25(金)（開催中）', 'time': 'パスポートの営業時間内（営業時間・休館日は公式サイトで確認）',
     'venue': 'サンリオピューロランド（多摩市落合1-31）館内', 'price': '入館にはパスポートが必要。デイパスポートは大人3,900円〜・小人（3〜17歳）・シニア2,800円〜（来場日により変わる。2歳以下は無料）',
     'description': 'サンリオキャラクターのテーマパークで開く、クリスマスのイルミネーション期間。ハローキティ、キキ＆ララと一緒にサンタさんのおてつだいをするイルミネーション、「くまのがっこう」とのコラボ、スタンプラリー、絵本の読み聞かせ、クリスマスのダンスなどがある。',
     'cats': ['まつり・イベント', 'テーマパーク・遊園地'], 'io': '屋内',
     'res': {'required': False, 'note': '来場予約と、パスポートの購入が必要（公式サイトで事前に購入・予約する）。'},
     'quotes': ['開催期間2026/11/06～2026/12/25', 'ピューロランドのみんなが、サンタさんのおてつだいをしているみたい…！', 'スタンプを押して、クリスマスツリーをかざりつけるおてつだいをしよう★'],
     'extra': [{'page': 'puroland_passport_list_2026.html', 'url': 'https://www.puroland.jp/passport/list/', 'q': 'パスポートチケット料金は、ご来場日により異なります'},
               {'page': 'puroland_passport_list_2026.html', 'url': 'https://www.puroland.jp/passport/list/', 'q': 'デイパスポート(開館〜閉館)アフタヌーンパスポート14時からの入場大人3,900円〜2,800円〜小人・シニア2,800円〜2,500円〜'}],
     'overall': 'B', 'basis': 'all_ages', 'child': False,
     'reason': 'サンリオのキャラクターに会える、屋内のクリスマスのイルミネーション期間。パスポートが必要で、来場日により料金が変わる。',
     'axes': _ax(['B', '子ども向けの人気キャラクターの施設で、対象はどなたでも'], ['A', 'スタンプラリーやダンスなど、参加できる内容が多い'], ['B', '3歳以上は小人料金で、2歳以下は無料'], ['B', '期間が長く、好きな日に行ける'], ['B', '来場予約が必要で、混む日がある'], ['C', 'パスポートが必要（小人2,800円〜、大人3,900円〜）'], ['C', '来場予約とパスポートの購入が必要'], ['A', '屋内で、天候に関係なく家族で楽しめる']),
     'strengths': ['屋内で、雨や寒さを気にせず楽しめる', 'スタンプラリーやダンスなど、子どもが参加できる内容が多い'], 'limitations': ['パスポートが必要で、家族だと費用がかさむ', '来場予約が必要で、日によって料金が変わる'],
     'comparison': '総合B：屋内で天候に左右されないが、パスポートと来場予約が必要で費用がかかる。',
     'pf': 'pass', 'pos': ['official_date_confirmed']},
    {'id': 'verified-20261121-bunkyo-dome-cinema-christmas-20261219', 'week': '2026-12-19', 'ward': '文京区', 'page': 'dome_cinema_christmas_20261219.html',
     'name': 'Tokyo Dome City Cinema Christmas 2026（東京ドームシティ）', 'url': 'https://www.tokyo-dome.co.jp/illumination/event/christmas', 'date': '2026-12-19', 'end': '2026-12-20', 'period': '12/19(土)・20(日)', 'time': 'サンタグリーティング12:30・15:30・18:00（各日3回）、焚き火演出とマシュマロ焼き17:00〜21:00',
     'venue': '東京ドームシティ ラクーアガーデン（芝生広場）（文京区後楽1-3-61）', 'price': '無料（サンタグリーティングは、東京ドームシティの店舗で税込2,500円以上の購入が条件）',
     'description': '芝生広場で楽しむ、クリスマスの屋外シネマイベント。『キャット・イン・ザ・ハット』のフォトスポットや関連映像の上映のほか、名作映画（パディントンなど）を上映する。サンタグリーティング（各回先着60組）と、焚き火を囲むマシュマロ焼き体験もある。雨天決行・荒天中止。',
     'cats': ['まつり・イベント', '舞台・音楽'], 'io': '屋外',
     'res': {'required': False, 'note': '観覧は予約の記載なし。サンタグリーティングは、各回30分前に会場で整理券を配布（店舗で2,500円以上の購入が条件）。'},
     'quotes': ['2026年12月19日(土)・20日(日)無料ラクーアガーデン（芝生広場）', 'ラクーアガーデンの芝生広場にて、屋外で映画を楽しめるシネマイベントを開催します。', 'クリスマスの特別な夜を彩る焚火台を設置。'],
     'overall': 'B', 'basis': 'all_ages', 'child': False,
     'reason': '無料の屋外映画とサンタグリーティングなどがある、東京ドームシティのクリスマスイベント。冬の夜の屋外で、寒さに注意。',
     'axes': _ax(['B', '家族向けの映画（パディントンなど）を上映。対象はどなたでも'], ['B', '映画を見たり、焚き火やマシュマロ焼きを楽しんだりできる'], ['B', '年齢の限定はない'], ['A', '2日間、好きな時間に立ち寄れる'], ['B', '冬の夜の屋外で、寒さと混雑に注意'], ['A', '観覧は無料（サンタグリーティングは店舗で2,500円以上の購入が条件）'], ['A', '観覧に予約は不要'], ['B', '遊園地やショッピングと合わせて、クリスマスの雰囲気を楽しめる']),
     'strengths': ['映画やフォトスポットを無料で楽しめる', '焚き火とマシュマロ焼きなど、冬ならではの体験がある'], 'limitations': ['屋外で冬の夜は寒い', 'サンタグリーティングは購入条件と整理券が必要'],
     'comparison': '総合B：無料で楽しめる屋外のクリスマス映画イベント。寒さ対策が必要。',
     'pf': 'pass', 'pos': ['official_date_confirmed']},
    {'id': 'verified-20261121-bunkyo-asobono-ahiru-taicho-20261110', 'week': '2026-11-21', 'ward': '文京区', 'page': 'asobono_ahiru_taicho_20261110.html',
     'name': 'アヒル隊長×アソボ～ノ！（東京ドームシティ アソボ～ノ！）', 'url': 'https://www.tokyo-dome.co.jp/asobono/event/7854', 'date': '2026-11-21', 'end': '2026-12-18', 'period': '11/10(火)〜12/18(金)（アヒル隊長グリーティングは11/23(月・祝)・26(木)）', 'time': 'グリーティング11:45〜・12:45〜（各20〜30分）',
     'venue': '東京ドームシティ アソボ～ノ！（文京区後楽1-3-61）', 'price': '入館料が必要。こども（6か月〜小学生）60分950〜1,300円、おとな（中学生以上）入館料950〜1,300円（日により料金区分が変わる）',
     'description': '子ども向けの遊び場「アソボ～ノ！」で、アヒル隊長25周年のコラボ。アヒル隊長のグリーティングと撮影、限定のぬりえ、館内に隠れたアヒル隊長を探すゲームがある。グリーティングは11/23と11/26の各2回。',
     'cats': ['体験・ワークショップ', 'まつり・イベント'], 'io': '屋内',
     'res': {'required': False, 'note': '予約の記載なし。入館料が必要（料金区分は日により異なる）。'},
     'quotes': ['2026年11月10日(火)～2026年12月18日(金)', '①11月15日(日)②11月23日(月・祝)③11月26日(木)', '館内５カ所にアヒル隊長が隠れているよ！'],
     'extra': [{'page': 'asobono_schedule_price_2026.html', 'url': 'https://www.tokyo-dome.co.jp/asobono/schedule-price', 'q': '種別ABCDこども60分950円1,100円1,200円1,300円'},
               {'page': 'asobono_schedule_price_2026.html', 'url': 'https://www.tokyo-dome.co.jp/asobono/schedule-price', 'q': 'おとな入館料950円1,100円1,200円1,300円'}],
     'overall': 'A', 'basis': 'child_program', 'child': True,
     'reason': '子ども向けの屋内の遊び場で、アヒル隊長のグリーティングや、ぬりえ・探しゲームを楽しめる。入館料が必要。',
     'axes': _ax(['A', '子ども向けの屋内の遊び場（6か月〜小学生）'], ['A', 'グリーティングの撮影、ぬりえ、探しゲームに参加できる'], ['A', '6か月から小学生までが対象の遊び場'], ['B', '60分から利用でき、延長もできる'], ['A', '屋内で、天候に左右されない'], ['C', '入館料が必要（こども60分950〜1,300円など）'], ['A', '予約の記載なし'], ['A', '雨の日でも、子どもが体を動かして遊べる']),
     'strengths': ['子ども向けの屋内の遊び場で、天候に左右されない', 'グリーティングやぬりえ、探しゲームなどコラボ企画が多い'], 'limitations': ['入館料が必要で、おとなも料金がかかる', 'グリーティングは11/23と11/26のみ（各日2回）'],
     'comparison': '総合A：子ども向けの屋内の遊び場でのコラボ企画。入館料は日により変わる。',
     'pf': 'pass', 'pos': ['official_date_confirmed']},
    {'id': 'verified-20261121-hino-tamazoo-africa-fair-20261122', 'week': '2026-11-21', 'ward': '日野市', 'page': 'tamazoo_africa_fair_20261122.html',
     'name': '第12回都立動物園アフリカフェア（多摩動物公園）', 'url': 'https://www.tokyo-zoo.net/tama/news/12878/index.html', 'date': '2026-11-22', 'end': '2026-11-23', 'period': '11/22(日)・23(月・祝)', 'time': 'アフリカ各国紹介ブース 11/22は11:30〜16:00・11/23は9:30〜16:00。アフリカ音楽・ダンスの公演は日により異なる',
     'venue': '多摩動物公園（日野市程久保7-1-1）', 'price': '参加は無料（入園料が必要：一般600円、中学生200円、65歳以上300円。小学生以下と都内在住・在学の中学生は無料）',
     'description': 'アフリカ各国の大使館や団体が出展する紹介ブース、アフリカ音楽・ダンスの公演（11/23は小さな子どもも一緒に踊れる参加型）、園内のスタンプラリー（各日先着800名に記念品）などがある、動物園のアフリカフェア。',
     'cats': ['まつり・イベント', '自然・公園'], 'io': '屋内・屋外',
     'res': {'required': False, 'note': '予約の記載なし。入園料が必要（小学生以下は無料）。'},
     'quotes': ['2026年11月22日（日）、23日（月・祝）', 'アフリカ各国紹介ブース「アフリカン・ディスカバリー」', '小さなお子様から大人まで、手拍子やダンスでいっしょに盛り上がれる参加型のステージです。'],
     'extra': [{'page': 'tamazoo_tickets_2026.html', 'url': 'https://www.tokyo-zoo.net/tama/visitor-info/tickets/index.html', 'q': '通常入園料は600円（65歳以上300円、中学生200円）。'},
               {'page': 'tamazoo_tickets_2026.html', 'url': 'https://www.tokyo-zoo.net/tama/visitor-info/tickets/index.html', 'q': '小学生以下および「都内在住・在学の中学生」は無料。'}],
     'overall': 'A', 'basis': 'all_ages', 'child': False,
     'reason': '動物園で開く、アフリカの音楽・ダンス・スタンプラリーなどのイベント。小学生以下は入園無料で、11/23は子どもも一緒に踊れる公演がある。',
     'axes': _ax(['B', '動物園のイベントで対象はどなたでも。子どもも参加できる内容が多い'], ['A', '音楽やダンスに参加でき、スタンプラリーもある'], ['A', '小さな子どもも楽しめる（小学生以下は入園無料）'], ['A', '2日間、好きな時間に回れる'], ['B', '広い園内を歩くため、体力が必要'], ['A', '小学生以下は無料、一般600円で費用が低い'], ['A', '予約の記載なし'], ['A', '動物を見ながら、アフリカの文化も体験できる']),
     'strengths': ['小学生以下は入園無料で、費用が低い', '音楽・ダンス・スタンプラリーと、動物の見学を一緒に楽しめる'], 'limitations': ['広い園内を歩くため、小さな子どもは疲れやすい', '11/22は開催当日（日曜）で、公演の一部は終了している場合がある'],
     'comparison': '総合A：小学生以下は入園無料の動物園で、アフリカの音楽・ダンス・スタンプラリーを楽しめる。',
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
SHARDS = {w: f'{w}-events-lead34-20261121.json' for w in ('2026-11-21', '2026-11-28', '2026-12-05', '2026-12-12', '2026-12-19', '2026-12-26')}
HELD = {
    'bunkyo-dome-winter-illumination-2026': '文京区 東京ドームシティ ウィンターイルミネーション2026（〜2027/2/28）：公式ページに開始日と観覧の費用の記載が確認できず保留。',
    'nerima-wb-studio-tour': '練馬区 ワーナー ブラザース スタジオツアー東京：常設の施設でイベントとしての期間がなく、料金は来場日により変わるため保留。',
    'tokyo-sunshine-solamachi-hanayashiki-joypolis': 'サンシャインシティ・東京ソラマチ・浅草花やしき・東京ジョイポリス・葛西臨海公園：公式の個別ページ（日付・場所・費用）を引き続き調査中。',
    'tokyo-legoland-discovery-center': 'レゴランド・ディスカバリー・センター東京：公式ページのURLが取得できず（404）、調査中。',
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
        run['lead34_addition_20261121'] = {
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
        'run_id': 'lead34-addition-20261121', 'run_type': 'manual_verified_lead34_addition',
        'status': 'verified_subset_publication', 'as_of_jst': '2026-11-21', 'executed_at': m['generated'],
        'base_data_production_sha': BASE, 'target_weekends': sorted(derived),
        'prior_active_week_records': 760, 'candidate_active_week_records': 764, 'added_weekly_records': 4,
        'new_event_ids': NEW_IDS, 'held_not_published': sorted(HELD),
        'existing_event_records_physically_deleted': 0, 'image_only_updates': 0,
        'source_failures_remain_unverified': True, 'global_source_audit_complete': False,
        'full_23_ward_25_source_audit_complete': False,
        'note': 'テーマパーク・大型施設の第1弾として、サンリオピューロランド、東京ドームシティ（シネマクリスマス・アソボ～ノ！）、多摩動物公園（アフリカフェア）を公式サイトの個別ページと料金ページで確認して追加。'
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
