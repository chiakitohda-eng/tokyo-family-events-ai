#!/usr/bin/env python3
"""4 weekly records (4 events) found by reading the remaining pool pages and calendar detail pages (2026-11-19).

Raw official pages are committed unchanged under research/2026-11-19-audit/pages/
(fetched by read-only workflows, HTTP 200). Quotes must occur verbatim in those pages.
The gate validator re-derives every record from this module and requires exact equality.
"""
import argparse, hashlib, json, pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import suginami_addition_20261118 as S

BASE = '1dedddfea851b7a2ebe8d09f4b5cb664039eb030'   # data-production after the lead11 addition (526 records)
CHECKED = '2026-11-19'
AXES = S.AXES
NOTE_AUDIT = '週別全源照合は未完（ためまっぷ403等）。この1件は各区公式ページの個別確認に基づく。'
S.CHECKED = CHECKED


def _page_text(path):
    """Like suginami page_text, but falls back to the whole document when a page has no <h1>."""
    raw = pathlib.Path(path).read_text(encoding='utf-8', errors='ignore')
    i = raw.find('<h1')
    raw = raw[i:] if i >= 0 else raw
    raw = S.re.sub(r'<(script|style).*?</\1>', '', raw, flags=S.re.S)
    raw = S.re.sub(r'<br\s*/?>|</(p|li|tr|dt|dd|h\d|div|th|td)>', '\n', raw)
    return S.re.sub(r'\s+', '', S.html.unescape(S.re.sub(r'<[^>]+>', '', raw)))


SPECS_RAW = [{'id': 'verified-20261128-chuo-harumi-matsuri', 'week': '2026-11-28', 'ward': '中央区', 'page': 'chuo_harumi_matsuri.html', 'name': '第3回中央区晴海まつり', 'url': 'https://www.city.chuo.lg.jp/a0013/bunkakankou/kankoujouhou/event/harumimaturi.html', 'date': '2026-11-28', 'period': '11/28(土)', 'time': '10:00〜15:00', 'venue': '晴海地域交流センター「はるみらい」・晴海ふ頭公園', 'price': '「食」コーナーを除き無料', 'description': '縁日コーナーやステージ、体験型デジタルアトラクションなど、さまざまな世代が楽しめる地域のまつり。縁日とデジタルアトラクションは事前予約が必要。', 'cats': ['イベント・まつり', '体験・ワークショップ'], 'io': '屋内・屋外', 'res': {'required': True, 'note': '縁日コーナーと体験型デジタルアトラクションは事前予約（先着）。'}, 'quotes': ['中央区晴海まつり地域の方々のご協力による縁日コーナーやステージイベントなど、さまざまな世代が楽しめるイベントを開催します。今年度で第3回目を迎える中央区晴海まつりは、「はるみらい会場」と昨年度から新たに追加した「晴海ふ頭公園会場」の2か所で実施します。会場図等も含めた詳細については、下記チラシをご覧ください。', '日時令和8年11月28日（土曜日）午前10時～午後3時', '料金「食」コーナーを除き、無料です。', '「縁日コーナー」及び「体験型デジタルアトラクションコーナー」は、事前予約が必要です。'], 'overall': 'B', 'basis': 'child_program', 'child': True, 'reason': '縁日コーナーやステージ、体験型デジタルアトラクションなど、さまざまな世代が楽しめる地域のまつり。「食」コーナーを除き無料。事前の申込が必要。', 'axes': {'child_target': ['A', '縁日やデジタルアトラクションなど子ども向けの体験がある'], 'interactivity': ['A', '射的・スーパーボールすくい・デジタル体験など'], 'age_fit': ['unknown', '対象年齢の目安は明記がない'], 'stay_flexibility': ['B', '10:00〜15:00'], 'burden': ['B', '縁日とデジタル体験は事前予約が必要'], 'cost': ['B', '「食」コーナーを除き無料'], 'reservation': ['C', '縁日とデジタル体験は事前予約が必要'], 'family_value': ['A', '家族で一日楽しめる地域のまつり']}, 'strengths': ['縁日とデジタル体験', 'ほとんど無料'], 'limitations': ['一部は事前予約が必要', '「食」は有料'], 'comparison': '総合B：11/28(土)の晴海地域交流センター「はるみらい」・晴海ふ頭公園で10:00〜15:00の開催。「食」コーナーを除き無料。申込が必要で、定員がある。', 'extra': [], 'pf': 'pass', 'pos': ['official_date_confirmed', 'child_activity_confirmed']}, {'id': 'verified-20261205-minato-aiport-xmas-concert', 'week': '2026-12-05', 'ward': '港区', 'page': 'minato_aiport_xmas.html', 'name': '子育てひろば「あい・ぽーと」クリスマスコンサート', 'url': 'https://www.city.minato.tokyo.jp/kouhou/event/261205-christmasconcert.html', 'date': '2026-12-05', 'period': '12/5(土)', 'time': '時間は公式ページに記載なし', 'venue': '子育てひろば「あい・ぽーと」', 'price': '区内在住・在勤者300円、その他500円', 'description': '三重奏、オリジナル音楽絵本、リズム遊びを楽しめる、就学前の子どもと保護者向けのコンサート。要会員登録で、定員120人。', 'cats': ['ショー・観劇', '音楽'], 'io': '屋内', 'res': {'required': True, 'note': '11/6午前10時から直接、11/11午前10時から電話で受付。定員120人（申込順）。'}, 'quotes': ['子育てひろば「あい・ぽーと」クリスマスコンサート', 'イベント詳細三重奏・オリジナル音楽絵本・リズム遊び等、小さなお子さんから楽しめるコンサートです。対象就学前の子どもとその保護者（要会員登録）開催場所子育てひろば「あい・ぽーと」定員120人（申込順）費用区内在住・在勤者：300円、その他：500円申込・予約11月6日（金曜）午前10時から直接（窓口販売優先）、11月11日（水曜）午前10時から電話で、子育てひろば「あい・ぽーと」へ。電話：03-5786-3250詳しくは、あい・ぽーとホームページ（'], 'overall': 'B', 'basis': 'child_program', 'child': True, 'reason': '三重奏、オリジナル音楽絵本、リズム遊びを楽しめる、就学前の子どもと保護者向けのコンサート。区内在住・在勤者300円、その他500円。事前の申込が必要。', 'axes': {'child_target': ['A', '就学前の子どもとその保護者が対象'], 'interactivity': ['A', '三重奏・音楽絵本・リズム遊び'], 'age_fit': ['A', '小さな子どもから楽しめると明記'], 'stay_flexibility': ['B', '時間は公式ページに記載なし'], 'burden': ['C', '要会員登録で、定員120人（申込順）'], 'cost': ['B', '区内在住・在勤者300円、その他500円'], 'reservation': ['C', '窓口または電話で申込（要会員登録）'], 'family_value': ['B', '親子で生演奏とリズム遊びを楽しめる']}, 'strengths': ['親子で楽しめるコンサート'], 'limitations': ['要会員登録', '有料', '開始時間の記載がない'], 'comparison': '総合B：12/5(土)の子育てひろば「あい・ぽーと」で時間は公式ページに記載なしの開催。区内在住・在勤者300円、その他500円。申込が必要で、定員がある。', 'extra': [{'page': 'minato_cal_1205.html', 'url': 'https://www.city.minato.tokyo.jp/cgi-bin/event_cal_multi/calendar.cgi?type=3&year=2026&month=12&day=5', 'q': 'あい・ぽーと」クリスマスコンサート2026年12月5日（土曜日）'}], 'pf': 'pass', 'pos': ['official_date_confirmed', 'child_activity_confirmed']}, {'id': 'verified-20261206-minato-mizube-sanpo-nurie', 'week': '2026-12-05', 'ward': '港区', 'page': 'minato_mizube_sanpo.html', 'name': '水辺のイラストさんぽ×塗り絵のワークショップ', 'url': 'https://www.city.minato.tokyo.jp/kouhou/event/261206-sanpoworkshop.html', 'date': '2026-12-06', 'period': '12/6(日)', 'time': '時間は公式ページに記載なし', 'venue': '伝統文化交流館（スタート・ゴール）', 'price': '500円（資料代）', 'description': '水辺のまち歩き（45分程度）と塗り絵ワークショップを楽しむ、小学生以上向けの催し。定員15人（申込順）。', 'cats': ['体験・ワークショップ', '公園・自然'], 'io': '屋内・屋外', 'res': {'required': True, 'note': '11/5〜11/26に申込フォームから申込。定員15人（申込順）。'}, 'quotes': ['水辺のイラストさんぽ×塗り絵のワークショップ', 'イベント詳細伝統文化交流館（スタート・ゴール）から水辺のまち歩き（45分程度）と塗り絵ワークショップ対象小学生以上どなたでも開催場所伝統文化交流館定員15人（申込順）費用500円（資料代）申込・予約11月5日（木曜）から11月26日（木曜）に、申し込みフォーム（'], 'overall': 'B', 'basis': 'child_program', 'child': True, 'reason': '水辺のまち歩き（45分程度）と塗り絵ワークショップを楽しむ、小学生以上向けの催し。500円（資料代）。事前の申込が必要。', 'axes': {'child_target': ['A', '小学生以上どなたでも参加できる'], 'interactivity': ['A', 'まち歩きと塗り絵を体験する'], 'age_fit': ['A', '小学生以上と明記'], 'stay_flexibility': ['B', '時間は公式ページに記載なし'], 'burden': ['C', '申込が必要で、定員15人'], 'cost': ['B', '資料代500円'], 'reservation': ['C', '申込フォームから申込（11/26まで）'], 'family_value': ['B', '親子でまち歩きと塗り絵を楽しめる']}, 'strengths': ['まち歩きと塗り絵'], 'limitations': ['申込が必要で15人', '資料代500円', '開始時間の記載がない'], 'comparison': '総合B：12/6(日)の伝統文化交流館で時間は公式ページに記載なしの開催。500円（資料代）。申込が必要で、定員がある。', 'extra': [{'page': 'minato_cal_1206.html', 'url': 'https://www.city.minato.tokyo.jp/cgi-bin/event_cal_multi/calendar.cgi?type=3&year=2026&month=12&day=6', 'q': '水辺のイラストさんぽ×塗り絵のワークショップ2026年12月6日（日曜日）'}], 'pf': 'pass', 'pos': ['official_date_confirmed', 'child_activity_confirmed']}, {'id': 'verified-20261212-minato-plaza-shinmei-festival', 'week': '2026-12-12', 'ward': '港区', 'page': 'minato_shinmei_fes.html', 'name': 'プラザ神明フェスティバル2026', 'url': 'https://www.city.minato.tokyo.jp/kouhou/event/261212-purazashinmei.html', 'date': '2026-12-12', 'period': '12/12(土)', 'time': '時間は公式ページに記載なし', 'venue': 'プラザ神明', 'price': '無料（食事代は自己負担）', 'description': '各種展示・体験コーナー・ステージ発表などがある、どなたでも参加できる地域のフェスティバル。', 'cats': ['イベント・まつり', '体験・ワークショップ'], 'io': '屋内', 'res': {'required': False, 'note': '当日直接会場へ。一部のイベントは申し込みが必要。'}, 'quotes': ['プラザ神明フェスティバル2026', 'イベント詳細各種展示・体験コーナー・ステージ発表等対象どなたでも開催場所プラザ神明（ステージ観覧は靴の履き替えが必要です。室内履き・靴袋を持参してください）費用無料（食事代は自己負担）申込・予約当日直接会場へ（一部のイベントは申し込みが必要です。電話または直接、神明いきいきプラザへ）。'], 'overall': 'B', 'basis': 'child_program', 'child': True, 'reason': '各種展示・体験コーナー・ステージ発表などがある、どなたでも参加できる地域のフェスティバル。無料（食事代は自己負担）。申込の案内はなく、当日参加できる。', 'axes': {'child_target': ['B', 'どなたでも参加できる地域のフェスティバル'], 'interactivity': ['B', '体験コーナーやステージ発表'], 'age_fit': ['unknown', '対象年齢の目安は明記がない'], 'stay_flexibility': ['B', '時間は公式ページに記載なし'], 'burden': ['B', '開始時間の記載がない'], 'cost': ['A', '無料（食事代は自己負担）'], 'reservation': ['B', '当日直接会場へ。一部は申込が必要'], 'family_value': ['B', '親子で体験コーナーを回れる']}, 'strengths': ['無料', '体験コーナーがある'], 'limitations': ['開始時間の記載がない', '一部のイベントは申込が必要'], 'comparison': '総合B：12/12(土)のプラザ神明で時間は公式ページに記載なしの開催。無料（食事代は自己負担）。申込不要で気軽に参加できる。', 'extra': [{'page': 'minato_cal_1212.html', 'url': 'https://www.city.minato.tokyo.jp/cgi-bin/event_cal_multi/calendar.cgi?type=3&year=2026&month=12&day=12', 'q': 'プラザ神明フェスティバル20262026年12月12日（土曜日）'}], 'pf': 'pass', 'pos': ['official_date_confirmed', 'child_activity_confirmed']}]
RAW = SPECS_RAW
SPECS = []
for _r in RAW:
    _s = dict(_r)
    _s['categories'] = _s.pop('cats'); _s['indoor_outdoor'] = _s.pop('io'); _s['reservation'] = _s.pop('res')
    _s['child_activity'] = _s.pop('child'); _s['price_field'] = _s.pop('pf'); _s['positive'] = _s.pop('pos')
    SPECS.append(_s)
NEW_IDS = [s['id'] for s in SPECS]
SHARDS = {w: f'{w}-events-lead11-20261119.json' for w in ('2026-11-21', '2026-11-28', '2026-12-05', '2026-12-12', '2026-12-19')}
HELD = {'minato-eco-nijimi-card-20261206': '区内在住の親子が対象', 'minato-weekday-hoikuen-asobo': '平日開催で、定員5名程度の予約制のため掲載範囲外', 'ota-jidokan-monthly-pdf': '大田区の児童館イベントは児童館ごとの月間PDFで、取得した公式ページに日付付きの詳細がない', 'shinagawa-koto-event-lists': '品川・江東は取得できた子育て・子ども向け一覧に、週末・祝日の日付付きの個別イベントが見つからなかった'}


def evidence(spec, pages_dir):
    text = _page_text(pathlib.Path(pages_dir) / spec['page'])
    out = []
    for q in spec['quotes']:
        if S._strip(q) not in text:
            raise ValueError(f"{spec['id']}: quote not found verbatim in the committed official page: {q}")
        out.append({'url': spec['url'], 'quote': q, 'checked_at': CHECKED,
                    'sha256': hashlib.sha256(q.encode('utf-8')).hexdigest(),
                    'hash_scope': 'quoted_text_only_not_HTTP_response_hash',
                    'description': f"{spec['ward']}公式ページ（2026-11-19にHTTP200で取得、research/2026-11-19-audit/pages/に不変保存）の本文引用。引用文字列だけのUTF-8 SHA-256。"})
    for x in spec.get('extra', []):
        t2 = _page_text(pathlib.Path(pages_dir) / x['page'])
        if S._strip(x['q']) not in t2:
            raise ValueError(f"{spec['id']}: calendar quote not found verbatim in the committed official calendar page: {x['q']}")
        out.append({'url': x['url'], 'quote': x['q'], 'checked_at': CHECKED,
                    'sha256': hashlib.sha256(x['q'].encode('utf-8')).hexdigest(),
                    'hash_scope': 'quoted_text_only_not_HTTP_response_hash',
                    'description': f"{spec['ward']}公式イベントカレンダーの日別ページ（2026-11-19にHTTP200で取得、research/2026-11-19-audit/pages/に不変保存）の本文引用。開催日の確認用。"})
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
               'evidence': [{'url': s['url'], 'basis': '2026-11-19 official individual event page (HTTP200); 23 ward completeness not asserted'}],
               'override_reason': ''}
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
                    row['note'] += f' 2026-11-19 公式個別ページ確認済み{k}件を非破壊追加。'
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
        run['lead11_addition_20261119'] = {
            'kind': 'individually_verified_official_events_from_lead_triage', 'added_ids': [i[0]['id'] for i in items],
            'held_not_published': sorted(HELD), 'pages_committed_at': 'research/2026-11-19-audit/pages/',
            'base_data_production_sha': BASE, 'global_source_audit_complete': False}
        S.jdump(d / f'{week}-run.json', run)
        for x in m['weekends']:
            if x['sat'] == week:
                x['count'] += n
    m['generated'] = '2026-11-20T00:00:00+09:00'
    S.jdump(d / 'manifest.json', m)
    h = S.jload(d / 'update_history.json')
    h['history'].append({
        'run_id': 'lead11-addition-20261119', 'run_type': 'manual_verified_lead11_addition',
        'status': 'verified_subset_publication', 'as_of_jst': '2026-11-19', 'executed_at': m['generated'],
        'base_data_production_sha': BASE, 'target_weekends': sorted(derived),
        'prior_active_week_records': 526, 'candidate_active_week_records': 530, 'added_weekly_records': 4,
        'new_event_ids': NEW_IDS, 'held_not_published': sorted(HELD),
        'existing_event_records_physically_deleted': 0, 'image_only_updates': 0,
        'source_failures_remain_unverified': True, 'global_source_audit_complete': False,
        'full_23_ward_25_source_audit_complete': False,
        'note': '中央区の晴海まつりと、港区の公式カレンダーで日付を確認できた3件の週別レコードのみ追加。区内在住限定・平日・予約制などは掲載せず理由を保存。',
    })
    S.jdump(d / 'update_history.json', h)


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--data-dir', required=True)
    ap.add_argument('--pages-dir', default='research/2026-11-19-audit/pages')
    a = ap.parse_args()
    try:
        build(a.data_dir, a.pages_dir)
    except ValueError as exc:
        print('ERROR:', exc, file=sys.stderr)
        sys.exit(1)
