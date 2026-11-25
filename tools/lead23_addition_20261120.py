#!/usr/bin/env python3
"""1 weekly record (12/26 Nerima forest festival) from the committed official Nerima page (2026-11-20).

Raw official pages are committed unchanged under research/2026-11-20-thin-wards/pages/
(fetched by read-only workflows, HTTP 200). Quotes must occur verbatim in those pages.
The gate validator re-derives every record from this module and requires exact equality.
"""
import argparse, hashlib, json, pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import suginami_addition_20261118 as S

BASE = 'a279cf9b7b9b576122f51257b705ad9633b3d040'   # data-production after the Nerima duplicate removal (658 active week records)
CHECKED = '2026-11-20'
AXES = S.AXES
NOTE_AUDIT = '週別全源照合は未完（ためまっぷ403等）。この追加分は主催者公式の案内ページの確認に基づく。'
S.CHECKED = CHECKED


def _page_text(path):
    """Like suginami page_text, but falls back to the whole document when a page has no <h1>."""
    raw = pathlib.Path(path).read_text(encoding='utf-8', errors='ignore')
    i = raw.find('<h1')
    raw = raw[i:] if i >= 0 else raw
    raw = S.re.sub(r'<(script|style).*?</\1>', '', raw, flags=S.re.S)
    raw = S.re.sub(r'<br\s*/?>|</(p|li|tr|dt|dd|h\d|div|th|td)>', '\n', raw)
    return S.re.sub(r'\s+', '', S.html.unescape(S.re.sub(r'<[^>]+>', '', raw)))


SPECS_RAW = [{'id': 'verified-20261219-toshima-hinemos-concert', 'week': '2026-12-19', 'ward': '豊島区', 'page': 'toshima_hinemos_1219.html', 'name': 'ヒネモスが贈る、音楽のクリスマスプレゼント！（としま区民センター）', 'url': 'https://www.toshima-mirai.or.jp/tabid216.html?pdid1=3603', 'date': '2026-12-19', 'period': '12/19(土)', 'time': '14:00開演（13:30開場／15:30終演予定）', 'venue': 'としま区民センター 8F 多目的ホール（豊島区東池袋1-20-10）', 'price': 'おとな1,800円／こども（3歳〜小学生）500円（2歳以下無料）', 'description': '奇想天外おもちゃの楽隊「ヒネモス」による、0歳から楽しめるクリスマスコンサート。各回200名。チケットは発売中。', 'cats': ['音楽', 'クリスマス', 'コンサート'], 'io': '屋内', 'res': {'required': True, 'note': 'チケット制（としまチケットセンター等で発売中）。各回200名。'}, 'quotes': ['日程2026年12月19日(土曜)・20日(日曜)各日14時開演(13時30分開場／15時30分終演予定)', '対象0歳からおとなまで定員各', '定員各回200名場所としま区', '場所としま区民センター8F多目的ホール', 'こども（3歳から小学生）※2歳以下は無料500円'], 'basis': 'all_ages', 'reason': '12/19(土)開催。おもちゃや楽器、ガラクタで奏でるヒネモスのクリスマスコンサートで、0歳から入場できる。こどもは500円、2歳以下は無料。', 'axes': {'child_target': ['B', '0歳から入場でき、こどもの料金も設定された公演（こども専用の公演ではない）'], 'interactivity': ['B', '音楽公演を鑑賞して楽しむのが中心'], 'age_fit': ['A', '対象が0歳からおとなまでと明記'], 'stay_flexibility': ['B', '14:00開演で、終演は15:30ごろ'], 'burden': ['B', 'チケットが必要で、各回200名'], 'cost': ['B', 'おとな1,800円、こども500円'], 'reservation': ['B', 'チケット制'], 'family_value': ['A', '0歳から家族そろってクリスマスの音楽を楽しめる']}, 'strengths': ['0歳から入場できる', 'こどもは500円と手頃'], 'limitations': ['チケットの購入が必要', '鑑賞が中心の公演'], 'comparison': '総合B（12/19(土)）：0歳から家族で楽しめるクリスマス公演だが、チケット制で鑑賞が中心。', 'pos': ['official_date_confirmed', 'child_activity_confirmed'], 'override': '', 'pf': 'pass', 'overall': 'B', 'child': True}, {'id': 'verified-20261220-toshima-hinemos-concert', 'week': '2026-12-19', 'ward': '豊島区', 'page': 'toshima_hinemos_1219.html', 'name': 'ヒネモスが贈る、音楽のクリスマスプレゼント！（としま区民センター）', 'url': 'https://www.toshima-mirai.or.jp/tabid216.html?pdid1=3603', 'date': '2026-12-20', 'period': '12/20(日)', 'time': '14:00開演（13:30開場／15:30終演予定）', 'venue': 'としま区民センター 8F 多目的ホール（豊島区東池袋1-20-10）', 'price': 'おとな1,800円／こども（3歳〜小学生）500円（2歳以下無料）', 'description': '奇想天外おもちゃの楽隊「ヒネモス」による、0歳から楽しめるクリスマスコンサート。各回200名。チケットは発売中。', 'cats': ['音楽', 'クリスマス', 'コンサート'], 'io': '屋内', 'res': {'required': True, 'note': 'チケット制（としまチケットセンター等で発売中）。各回200名。'}, 'quotes': ['日程2026年12月19日(土曜)・20日(日曜)各日14時開演(13時30分開場／15時30分終演予定)', '対象0歳からおとなまで定員各', '定員各回200名場所としま区', '場所としま区民センター8F多目的ホール', 'こども（3歳から小学生）※2歳以下は無料500円'], 'basis': 'all_ages', 'reason': '12/20(日)開催。おもちゃや楽器、ガラクタで奏でるヒネモスのクリスマスコンサートで、0歳から入場できる。こどもは500円、2歳以下は無料。', 'axes': {'child_target': ['B', '0歳から入場でき、こどもの料金も設定された公演（こども専用の公演ではない）'], 'interactivity': ['B', '音楽公演を鑑賞して楽しむのが中心'], 'age_fit': ['A', '対象が0歳からおとなまでと明記'], 'stay_flexibility': ['B', '14:00開演で、終演は15:30ごろ'], 'burden': ['B', 'チケットが必要で、各回200名'], 'cost': ['B', 'おとな1,800円、こども500円'], 'reservation': ['B', 'チケット制'], 'family_value': ['A', '0歳から家族そろってクリスマスの音楽を楽しめる']}, 'strengths': ['0歳から入場できる', 'こどもは500円と手頃'], 'limitations': ['チケットの購入が必要', '鑑賞が中心の公演'], 'comparison': '総合B（12/20(日)）：0歳から家族で楽しめるクリスマス公演だが、チケット制で鑑賞が中心。', 'pos': ['official_date_confirmed', 'child_activity_confirmed'], 'override': '', 'pf': 'pass', 'overall': 'B', 'child': True}, {'id': 'verified-20261219-edogawa-kodomomirai-shimenawa', 'week': '2026-12-19', 'ward': '江戸川区', 'page': 'edogawa_kodomomirai_shimenawa_1219.html', 'name': '親子でしめ縄づくり（江戸川区子ども未来館）', 'url': 'https://www.city.edogawa.tokyo.jp/event/2612shimenawa.html', 'date': '2026-12-19', 'period': '12/19(土)', 'time': '10:00〜12:00', 'venue': '江戸川区子ども未来館（江戸川区篠崎町3-12-10）', 'price': '無料', 'description': '稲わらを使って、お正月に歳神様を迎えるしめ縄の作り方を親子で学んで作る。小学3〜6年生とその保護者が対象で、定員8組の抽選。申込期間は11/13〜12/8。', 'cats': ['工作', '伝統文化', '体験・ワークショップ'], 'io': '屋内', 'res': {'required': True, 'note': '事前申込制（11/13〜12/8）。定員8組の抽選。'}, 'quotes': ['開催日時2026年12月19日（土曜日）10時00分から12時00分', '申し込み期間2026年11月13日（金曜日）から2026年12月8日（火曜日）', '小学校3年生から6年生までとその保護者', '定員8組（抽選）費用無料問合', '費用無料問合せ子ども未来館（', '江戸川区篠崎町三丁目12番10号'], 'basis': 'child_program', 'reason': '小学3〜6年生とその保護者が、稲わらでお正月用のしめ縄を作る体験。参加費は無料だが、定員8組の抽選制。', 'axes': {'child_target': ['A', '小学3〜6年生とその保護者を対象にした親子向けの講座'], 'interactivity': ['A', '稲わらでしめ縄を実際に作る体験'], 'age_fit': ['A', '対象が小学3〜6年生と明記'], 'stay_flexibility': ['B', '10:00〜12:00の2時間で、時間が決まっている'], 'burden': ['B', '定員8組の抽選で、事前申込が必要'], 'cost': ['A', '参加費無料'], 'reservation': ['C', '事前申込で定員8組の抽選'], 'family_value': ['A', '親子で日本の正月飾りの作り方を学び、持ち帰れる']}, 'strengths': ['小学生と保護者向けで無料', 'しめ縄を作って持ち帰れる'], 'limitations': ['定員8組の抽選', '対象が小学3〜6年生に限られる'], 'comparison': '総合B：小学生と保護者向けの無料の体験だが、定員8組の抽選制で申込が必要。', 'pos': ['official_date_confirmed', 'child_activity_confirmed'], 'override': '', 'pf': 'pass', 'overall': 'B', 'child': True}, {'id': 'verified-20261205-minato-monodukuri-fair', 'week': '2026-12-05', 'ward': '港区', 'page': 'minato_monodukuri_1205.html', 'name': 'みつかるみらいMINATO 第11回港区ものづくり・商業観光フェア（札の辻スクエア）', 'url': 'https://minato-monodukuri2026.jp', 'date': '2026-12-05', 'period': '12/5(土)', 'time': '10:00〜17:30', 'venue': '札の辻スクエア（港区芝5-36-4）', 'price': '入場無料（一部の体験は有料）', 'description': 'ものづくりや商業の体験ブースが並ぶ港区のフェア。ミニ四駆や万華鏡づくり、サイエンスワークショップなどの体験コンテンツがある。事前申込の受付は終了しており、事前申込不要の企画ブースに当日参加できる。', 'cats': ['ものづくり', '体験', '地域イベント'], 'io': '屋内', 'res': {'required': None, 'note': '事前申込コンテンツの受付は終了。事前申込不要の企画ブースは当日参加できる。'}, 'quotes': ['開催日時令和8年(2026年)12月5日（土）', '場所札の辻スクエア住所東京都', '時間10:00～17:30', '事前申込受付終了のお知らせ', '事前申込不要！企画ブース', 'ミニ四駆『組み立て・走行』体験会'], 'basis': 'all_ages', 'overall': 'C', 'override': 'ものづくり体験が並ぶ区のフェアで、子どもが参加できる体験があるが、公式ページでは子ども向けの対象年齢が示されず、事前申込のコンテンツは受付が終了しているため、条件つきの総合Cとして掲載する。', 'reason': '港区のものづくり・商業観光フェアで、ミニ四駆の組み立て、万華鏡づくり、サイエンスワークショップなどの体験がある。事前申込分の受付は終了し、事前申込不要の企画ブースが当日参加できる。', 'axes': {'child_target': ['B', 'ミニ四駆や万華鏡づくりなど、子どもが参加できる体験コンテンツがある'], 'interactivity': ['A', 'ものづくり体験が中心'], 'age_fit': ['unknown', '対象年齢の目安が明記されていない'], 'stay_flexibility': ['A', '10:00〜17:30の間に出入りできる'], 'burden': ['B', '公共交通機関での来場が必要で、混雑の可能性がある'], 'cost': ['A', '入場無料（一部の体験は有料）'], 'reservation': ['C', '事前申込コンテンツは受付終了。事前申込不要の企画ブースのみ当日参加'], 'family_value': ['B', '親子でものづくりを体験できる']}, 'strengths': ['入場無料', 'ものづくり体験が多い'], 'limitations': ['事前申込コンテンツは受付終了', '対象年齢の目安がない'], 'comparison': '総合C：入場無料でものづくり体験が楽しめるが、事前申込分は受付終了で、対象年齢の目安もない。', 'pos': ['official_date_confirmed', 'child_activity_confirmed'], 'pf': 'pass', 'child': True}]
RAW = SPECS_RAW
SPECS = []
for _r in RAW:
    _s = dict(_r)
    _s['categories'] = _s.pop('cats'); _s['indoor_outdoor'] = _s.pop('io'); _s['reservation'] = _s.pop('res')
    _s['child_activity'] = _s.pop('child'); _s['price_field'] = _s.pop('pf'); _s['positive'] = _s.pop('pos')
    SPECS.append(_s)
NEW_IDS = [s['id'] for s in SPECS]
SHARDS = {w: f'{w}-events-lead23-20261120.json' for w in ('2026-12-05', '2026-12-19')}
HELD = {}


def evidence(spec, pages_dir):
    text = _page_text(pathlib.Path(pages_dir) / spec['page'])
    out = []
    for q in spec['quotes']:
        if S._strip(q) not in text:
            raise ValueError(f"{spec['id']}: quote not found verbatim in the committed official page: {q}")
        out.append({'url': spec['url'], 'quote': q, 'checked_at': CHECKED,
                    'sha256': hashlib.sha256(q.encode('utf-8')).hexdigest(),
                    'hash_scope': 'quoted_text_only_not_HTTP_response_hash',
                    'description': f"主催者公式ページ（2026-11-20にHTTP200で取得、research/2026-11-20-thin-wards/pages/に不変保存）の本文引用。引用文字列だけのUTF-8 SHA-256。"})
    for x in spec.get('extra', []):
        t2 = _page_text(pathlib.Path(pages_dir) / x['page'])
        if S._strip(x['q']) not in t2:
            raise ValueError(f"{spec['id']}: calendar quote not found verbatim in the committed official calendar page: {x['q']}")
        out.append({'url': x['url'], 'quote': x['q'], 'checked_at': CHECKED,
                    'sha256': hashlib.sha256(x['q'].encode('utf-8')).hexdigest(),
                    'hash_scope': 'quoted_text_only_not_HTTP_response_hash',
                    'description': f"主催者公式ページ（2026-11-20にHTTP200で取得、research/2026-11-20-thin-wards/pages/に不変保存）の本文引用。"})
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
               'evidence': [{'url': s['url'], 'basis': '2026-11-20 official individual event page (HTTP200); 23 ward completeness not asserted'}],
               'override_reason': s.get('override', '')}
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
                    row['note'] += f' 2026-11-20 公式個別ページ確認済み{k}件を非破壊追加。'
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
        run['lead23_addition_20261120'] = {
            'kind': 'individually_verified_official_events_from_lead_triage', 'added_ids': [i[0]['id'] for i in items],
            'held_not_published': sorted(HELD), 'pages_committed_at': 'research/2026-11-20-thin-wards/pages/',
            'base_data_production_sha': BASE, 'global_source_audit_complete': False}
        S.jdump(d / f'{week}-run.json', run)
        for x in m['weekends']:
            if x['sat'] == week:
                x['count'] += n
    m['generated'] = '2026-11-20T19:00:00+09:00'
    S.jdump(d / 'manifest.json', m)
    h = S.jload(d / 'update_history.json')
    h['history'].append({
        'run_id': 'lead23-addition-20261120', 'run_type': 'manual_verified_lead23_addition',
        'status': 'verified_subset_publication', 'as_of_jst': '2026-11-20', 'executed_at': m['generated'],
        'base_data_production_sha': BASE, 'target_weekends': sorted(derived),
        'prior_active_week_records': 658, 'candidate_active_week_records': 662, 'added_weekly_records': 4,
        'new_event_ids': NEW_IDS, 'held_not_published': sorted(HELD),
        'existing_event_records_physically_deleted': 0, 'image_only_updates': 0,
        'source_failures_remain_unverified': True, 'global_source_audit_complete': False,
        'full_23_ward_25_source_audit_complete': False,
        'note': '東京都の公園管理者・としま未来文化財団・江戸川区子ども未来館・港区ものづくりフェア実行委員会の公式ページで日付・時間・会場・条件を確認できた4件のみ追加。',
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
