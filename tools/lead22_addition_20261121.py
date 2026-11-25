#!/usr/bin/env python3
"""5 weekly records (Itabashi mystery-solving workshop 11/23, Tokyo kids-smile Ogi-mama workshop 12/5, Human Rights Festa Tokyo 12/5-12/6) from committed official pages (2026-11-21).

Raw official pages are committed unchanged under research/2026-11-20-thin-wards/pages/
(fetched by read-only workflows, HTTP 200). Quotes must occur verbatim in those pages.
The gate validator re-derives every record from this module and requires exact equality.
"""
import argparse, hashlib, json, pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import suginami_addition_20261118 as S

BASE = 'ff8091da2d87d9a0ec7c4d5990c297c24c199693'   # data-production after lead21 (713 active week records)
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


_HRF = 'https://www.hrf-tokyo-2026.metro.tokyo.lg.jp/'


def _hrf(date, md, time, q):
    return {'id': f'verified-{date.replace("-", "")}-chiyoda-human-rights-festa', 'week': '2026-12-05', 'ward': '千代田区',
        'page': 'hrf_tokyo_2026_site.html', 'name': 'ヒューマンライツ・フェスタ東京2026（東京国際フォーラム）', 'url': _HRF, 'date': date, 'period': md, 'time': time,
        'venue': '東京国際フォーラム（JR有楽町駅国際フォーラム口改札から徒歩1分）', 'price': '参加費無料',
        'image': 'https://www.hrf-tokyo-2026.metro.tokyo.lg.jp/assets/img/ogp.png',
        'description': '東京都が開く人権啓発イベント。トークショー、お笑い・音楽ライブ、車いすバスケや点字などの体験コーナーなどがあり、東京国際フォーラム会場は1歳以上の未就学児の無料託児（7名・先着順、事務局へ連絡）もある。日ごとの出演者・体験内容は公式サイトで確認。',
        'cats': ['まつり・イベント', '体験・ワークショップ'], 'io': '屋内',
        'res': {'required': None, 'note': '一部プログラムは事前抽選（申込締切11/23）だが、当日席もある。入場自体の事前申込の記載なし。'},
        'quotes': [q, '主 催 東京都 参加費 無 料 PDFダウンロード', 'おとなから子どもまで、 楽しみながら', '東京国際フォーラム会場は託児を受け付けております。', '※当日席もご用意しております。'],
        'overall': 'B', 'basis': 'all_ages', 'child': True,
        'reason': '公式サイトに「おとなから子どもまで」とあり、体験コーナーや無料託児（1歳以上の未就学児）があるが、全体は幅広い年代向けの人権啓発イベント。',
        'axes': {'child_target': ['B', '「おとなから子どもまで」と案内されるが、子ども専用の企画ではない'], 'interactivity': ['B', '車いすバスケ体験・点字体験など体験コーナーがあるが、ステージ鑑賞も多い'],
                 'age_fit': ['B', '託児は1歳以上の未就学児が対象で、年齢別の案内は限られる'], 'stay_flexibility': ['B', '10:00から終日開催で、プログラムを選んで参加できる'],
                 'burden': ['B', '一部プログラムは事前抽選が優先で、当日席もある'], 'cost': ['A', '参加費無料'],
                 'reservation': ['B', '事前抽選のプログラムがあるが、当日席もある'], 'family_value': ['B', '無料で体験とステージを家族で楽しめ、託児もある']},
        'strengths': ['参加費無料で、体験コーナーと無料託児がある'], 'limitations': ['一部は事前抽選が優先で、日ごとの内容は公式サイトで要確認', '子ども専用のイベントではない'],
        'comparison': f'総合B：{md}は東京国際フォーラムで無料で参加でき、体験コーナーや託児があるが、幅広い年代向けで一部は事前抽選。',
        'pf': 'pass', 'pos': ['official_date_confirmed', 'child_activity_confirmed']}


SPECS_RAW = [
    {'id': 'verified-20261123-itabashi-hase-nazotoki', 'week': '2026-11-21', 'ward': '板橋区', 'page': 'itabashi_nazotoki_20261123.html',
     'name': '機械工学×謎解きプログラム「機械のからくりを学んで、ふっかちゃんを探せ！」（板橋区立教育科学館）',
     'url': 'https://www.mech.kanagawa-u.ac.jp/lab/hase_lab/HaseLab-Nazotoki-Itabashi2026.html', 'date': '2026-11-23', 'period': '11/23(月・祝)', 'time': '13:30〜16:00',
     'venue': '板橋区立教育科学館 研修室', 'price': '受講料無料（教材費500円を当日会場で徴収）',
     'description': '神奈川大学の研究室が開く、機械のしくみを学びながら謎解きとペーパークラフト製作に挑戦する体験学習。小学4年生〜中学生が対象で、定員40名・事前申込制（先着順）。保護者の付添い・見学も可。',
     'cats': ['体験・ワークショップ', '科学・学び'], 'io': '屋内',
     'res': {'required': True, 'note': '事前申込制（Googleフォーム）。申込多数の場合は先着順。'},
     'quotes': ['2026年11月23日（月・祝）13:30-16:00', '板橋区立教育科学館 研修室', '（定員40名，小学4年生～中学生対象，受講料無料/別途，教材費が必要，事前申込制）', '教材費：500円（当日会場にて徴収）', '※保護者の付添い・見学可 ★タイムスケジュール★', '参加申込み受付中！ 参加申込みフォームURL'],
     'overall': 'A', 'basis': 'child_program', 'child': True,
     'reason': '小学4年生〜中学生が謎解きとペーパークラフトで機械のしくみを学ぶ体験学習で、受講料無料。事前申込制（先着順）で定員40名。',
     'axes': {'child_target': ['A', '小学4年生〜中学生が対象の子ども向けプログラム'], 'interactivity': ['A', '謎解きとペーパークラフト製作に参加して体験する内容'],
              'age_fit': ['A', '小学4年生〜中学生と対象学年が明記され、保護者の付添い・見学も可'], 'stay_flexibility': ['B', '13:30〜16:00のタイムスケジュールに沿って進む'],
              'burden': ['B', '事前申込制で、はさみ・のりなどの持参品と教材費500円が必要'], 'cost': ['A', '受講料無料（教材費500円は別途）'],
              'reservation': ['B', '事前申込制（先着順）で定員40名'], 'family_value': ['A', '機械のしくみを謎解きで学べる無料の体験学習で、保護者の見学もできる']},
     'strengths': ['受講料無料で、謎解きとペーパークラフトを体験できる', '保護者の付添い・見学が可能'], 'limitations': ['事前申込制・先着順で定員40名', '教材費500円と文房具などの持参が必要'],
     'comparison': '総合A：小学4年生〜中学生向けの体験学習で受講料無料。事前申込制（先着順）と教材費・持参品が条件。',
     'pf': 'pass', 'pos': ['official_date_confirmed', 'child_activity_confirmed']},
    {'id': 'verified-20261123-edogawa-kasai-ramsar-pr', 'week': '2026-11-21', 'ward': '江戸川区', 'page': 'kasai_ramsar_pr_20261123.html',
     'name': '葛西海浜公園 ラムサール条約湿地PRイベント', 'url': 'https://www.kouwan.metro.tokyo.lg.jp/kanko/park/kasaikaihin',
     'date': '2026-11-23', 'period': '11/23(月・祝)', 'time': '10:00〜15:00',
     'venue': '葛西海浜公園 西なぎさ（雨天時はいきものステーションで規模を縮小）', 'price': '無料（親子で楽しめるプログラム・自然観察会とも）',
     'description': '東京都港湾局が開く、ラムサール条約湿地の葛西海浜公園を学ぶイベント。パネル展示のほか、親子で楽しめるスタンプラリーとクラフト体験（申込不要・無料）と、野鳥・干潟の生きもの観察会（事前申込制・無料、小学3年生以上、各回20名先着）がある。',
     'cats': ['自然・公園', '体験・ワークショップ'], 'io': '屋外',
     'res': {'required': None, 'note': '親子プログラム（スタンプラリー・クラフト体験）は申込不要。自然観察会は事前申込制（各回20名先着）。'},
     'quotes': ['令和８年11月23日（月･祝）10:00～15:00', '場所 葛西海浜公園 西なぎさ', '親子でたのしめるプログラム（申込不要、無料）', 'スタンプラリー、クラフト体験 など', '自然観察会（事前申込制、無料）', '募集人数 各回20名（先着順） 対象 小学３年生以上（小学生以下は保護者同伴）'],
     'overall': 'A', 'basis': 'child_program', 'child': True,
     'reason': '親子で楽しめるスタンプラリー・クラフト体験が無料・申込不要で、小学3年生以上は無料の自然観察会（事前申込制）にも参加できる。',
     'axes': {'child_target': ['A', '「親子でたのしめるプログラム」と自然観察会（小学3年生以上）が設けられている'], 'interactivity': ['A', 'スタンプラリー・クラフト体験・干潟の生きもの観察など参加型'],
              'age_fit': ['B', '観察会は小学3年生以上（小学生以下は保護者同伴）で、未就学児向けは親子プログラム中心'], 'stay_flexibility': ['A', '10:00〜15:00の間に親子プログラムを自由に体験できる'],
              'burden': ['B', '屋外開催で、自然観察会は事前申込と開始時刻への集合が必要'], 'cost': ['A', '親子プログラム・自然観察会とも無料'],
              'reservation': ['B', '親子プログラムは申込不要、観察会は事前申込制（各回20名先着）'], 'family_value': ['A', '無料で干潟の自然を体験でき、親子で参加できる']},
     'strengths': ['親子プログラムが無料・申込不要', '干潟の生きもの観察会も無料'], 'limitations': ['観察会は事前申込制で小学3年生以上、各回20名先着', '屋外で雨天時は規模を縮小'],
     'comparison': '総合A：親子で楽しめる無料プログラムが申込不要で、観察会は申込制・小学3年生以上という条件が付く。',
     'pf': 'pass', 'pos': ['official_date_confirmed', 'child_activity_confirmed']},
    {'id': 'verified-20261205-minato-ogimama-book-christmas', 'week': '2026-12-05', 'ward': '港区', 'page': 'kodomo_smile_ogi_christmas_20261205.html',
     'name': '尾木ママと親子で楽しむ 本と出会うクリスマス', 'url': 'https://kodomo-smile.metro.tokyo.lg.jp/stp/kodomo_ambassador/r8_ogisan_event.html',
     'date': '2026-12-05', 'period': '12/5(土)', 'time': '第1部13:00〜14:00／第2部15:00〜16:00',
     'venue': 'BUNKITSU TOKYO Gallery B（港区高輪2-21-2 NEWoMan高輪 South 5F）', 'price': '参加費無料',
     'description': '東京都こどもスマイルムーブメントの親子ワークショップ。第1部は未就学児（3〜6歳）と保護者で絵本の読み聞かせとクリスマスカード作り、第2部は小学1〜3年生（4〜6年生も可）と保護者で絵本をきっかけに親子で語り合う。各回15組、事前応募・抽選制（締切11/24）。',
     'cats': ['体験・ワークショップ', '本・読み聞かせ'], 'io': '屋内',
     'res': {'required': True, 'note': '事前応募・抽選制。応募締切は11/24（火）、抽選結果は11/26以降にメール連絡予定。都内在住・在勤・在学のいずれかに該当する方が対象。'},
     'quotes': ['12月5日(土) 第一部 13:00~14:00 第二部 15:00~16:00', 'BUNKITSU TOKYO Gallery B', '参加費 無料【注意】事前応募、抽選制', '応募締切 令和8年11月24日（火）', '第1部 未就学児（3〜6歳）、第2部 小学1〜3年生 （小学4〜6年生も参加可）', '都内在住・在勤・在学のいずれかに該当する方', 'お子様と保護者の方が一緒にご参加いただくことを前提としたプログラム'],
     'overall': 'A', 'basis': 'child_program', 'child': True,
     'reason': '未就学児〜小学生と保護者が一緒に参加する、絵本の読み聞かせとカード作りのワークショップで参加費無料。事前応募・抽選制で定員は各回15組。',
     'axes': {'child_target': ['A', '未就学児（3〜6歳）と小学1〜3年生の親子向けのワークショップ'], 'interactivity': ['A', 'クリスマスカード作りや親子の対話など参加型の内容'],
              'age_fit': ['A', '第1部は3〜6歳、第2部は小学1〜3年生と対象年齢が明記されている'], 'stay_flexibility': ['B', '各部1時間で、開始時刻に遅れると参加できない場合がある'],
              'burden': ['B', '事前応募・抽選制で、当選後も開始時刻までに集合が必要'], 'cost': ['A', '参加費無料'],
              'reservation': ['B', '事前応募・抽選制（締切11/24）で定員は各回15組'], 'family_value': ['A', '親子で絵本とカード作りを無料で楽しめる。会場周辺に託児サービスもある']},
     'strengths': ['参加費無料で、親子で読み聞かせとカード作りを体験できる', '同じフロアに授乳室・おむつ交換室がある'], 'limitations': ['事前応募・抽選制で当たらない場合がある', '都内在住・在勤・在学が対象で、各回15組と少人数'],
     'comparison': '総合A：未就学児〜小学生の親子向けで無料。抽選制・少人数が条件。',
     'pf': 'pass', 'pos': ['official_date_confirmed', 'child_activity_confirmed']},
    _hrf('2026-12-05', '12/5(土)', '10:00〜16:00', '2026年12月5日（土） 10：00～16：00 ／東京国際フォーラム'),
    _hrf('2026-12-06', '12/6(日)', '10:00〜15:30', '2026年12月6日（日） 10：00～15：30 ／東京国際フォーラム'),
]
RAW = SPECS_RAW
SPECS = []
for _r in RAW:
    _s = dict(_r)
    _s['categories'] = _s.pop('cats'); _s['indoor_outdoor'] = _s.pop('io'); _s['reservation'] = _s.pop('res')
    _s['child_activity'] = _s.pop('child'); _s['price_field'] = _s.pop('pf'); _s['positive'] = _s.pop('pos')
    SPECS.append(_s)
NEW_IDS = [s['id'] for s in SPECS]
SHARDS = {w: f'{w}-events-lead22-20261121.json' for w in ('2026-11-21', '2026-11-28', '2026-12-05', '2026-12-12', '2026-12-19', '2026-12-26')}
HELD = {
    'kurilabo-game-3d-20261213': 'ゲーム開発ワークショップ（千代田区、12/13）：申込期間がページ本文から取得できず（動的表示）、抽選で申込受付中かを確認できないため見送り。',
    'kaiyo-tsuri-girl-20261128': '釣りガール釣り教室（江東区、11/28）：応募は11/17に締切済み。女性限定。',
    'toyonetsu-balloon-20261206': 'とよにバルーンフェスタ2026（練馬区、12/6）：公式サイトに日時・費用・申込方法の記載がなく（チラシ画像のみ）、費用を推測しないため保留。',
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
        run['lead22_addition_20261121'] = {
            'kind': 'individually_verified_official_events_from_lead_triage', 'added_ids': [i[0]['id'] for i in items],
            'held_not_published': sorted(HELD), 'pages_committed_at': 'research/2026-11-20-thin-wards/pages/',
            'base_data_production_sha': BASE, 'global_source_audit_complete': False}
        S.jdump(d / f'{week}-run.json', run)
        for x in m['weekends']:
            if x['sat'] == week:
                x['count'] += n
    m['generated'] = '2026-11-21T16:00:00+09:00'
    S.jdump(d / 'manifest.json', m)
    h = S.jload(d / 'update_history.json')
    h['history'].append({
        'run_id': 'lead22-addition-20261121', 'run_type': 'manual_verified_lead22_addition',
        'status': 'verified_subset_publication', 'as_of_jst': '2026-11-21', 'executed_at': m['generated'],
        'base_data_production_sha': BASE, 'target_weekends': sorted(derived),
        'prior_active_week_records': 713, 'candidate_active_week_records': 718, 'added_weekly_records': 5,
        'new_event_ids': NEW_IDS, 'held_not_published': sorted(HELD),
        'existing_event_records_physically_deleted': 0, 'image_only_updates': 0,
        'source_failures_remain_unverified': True, 'global_source_audit_complete': False,
        'full_23_ward_25_source_audit_complete': False,
        'note': '板橋区の謎解き体験学習（11/23）、江戸川区の葛西海浜公園ラムサール条約湿地PRイベント（11/23）、港区の尾木ママ親子ワークショップ（12/5）、ヒューマンライツ・フェスタ東京2026（千代田区、12/5・12/6）を各公式ページで確認し、5件を追加。',
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
