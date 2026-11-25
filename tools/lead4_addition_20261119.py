#!/usr/bin/env python3
"""Five individually verified official events found by reading the 367 undated candidate pages (2026-11-19).

Raw official pages are committed unchanged under research/2026-11-19-audit/pages/
(fetched by read-only workflows, HTTP 200). Quotes must occur verbatim in those pages.
The gate validator re-derives every record from this module and requires exact equality.
"""
import argparse, hashlib, json, pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import suginami_addition_20261118 as S

BASE = 'ca369883be37d90327f59b21d5bc33d50d79b554'   # data-production after the lead3 addition (454 records)
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


SPECS_RAW = [{'id': 'verified-20261121-kita-kodomo-kenri-sugoroku', 'week': '2026-11-21', 'ward': '北区', 'page': 'kita_sugoroku.html', 'name': 'みんなで楽しく知ろう・学ぼう！子どもの権利すごろくイベント', 'url': 'https://www.city.kita.lg.jp/children-edu/kids/1019177/1027059.html', 'date': '2026-11-21', 'period': '11/21(土)', 'time': '14:00〜16:00', 'venue': '中央図書館 3階ホール（北区）', 'price': '無料', 'description': '「子どもの権利」をすごろくで遊びながら学ぶイベント。未就学児から高校生世代と保護者が対象で、途中参加・途中退出OK。参加者にプレゼントがある。', 'cats': ['体験・ワークショップ', '地域交流'], 'io': '屋内', 'res': {'required': False, 'note': '申込不要。途中参加・途中退出OK。'}, 'quotes': ['開催日2026年11月21日（土曜日）開催時間午後2時から午後4時まで', '開催場所中央図書館3Fホール', '対象未就学児、小学生から高校生世代保護者の方もご一緒に！', '途中参加・途中退出OK！申込も不要！当日、会場まで気軽にお越しください。', 'そんな大切な「子どもの権利」について、すごろくで遊びながら楽しく学びましょう！'], 'overall': 'A', 'basis': 'child_program', 'child': True, 'reason': '未就学児から高校生世代と保護者が対象の、すごろくで遊びながら学ぶ企画。無料・申込不要で、途中参加・退出もできる。', 'axes': {'child_target': ('A', '未就学児から高校生世代と保護者が対象'), 'interactivity': ('A', 'すごろくで遊びながら学ぶ参加型'), 'age_fit': ('A', '対象は未就学児・小学生から高校生世代と明記'), 'stay_flexibility': ('A', '途中参加・途中退出OK'), 'burden': ('A', '申込不要・無料で気軽に参加できる'), 'cost': ('A', '費用無料（参加者にプレゼント）'), 'reservation': ('A', '申込不要'), 'family_value': ('B', '家族で子どもの権利を遊びながら学べる')}, 'strengths': ['無料・申込不要で途中参加・退出OK', '参加者にプレゼントあり'], 'limitations': ['内容はすごろく1種類', '会場の詳細な住所は公式ページにない'], 'comparison': '総合A：対象年齢が明確で、無料・申込不要の参加型。内容は1種類に限られる。', 'pf': 'pass', 'pos': ['official_date_confirmed', 'child_activity_confirmed']}, {'id': 'verified-20261122-suginami-boyscout-akimatsuri', 'week': '2026-11-21', 'ward': '杉並区', 'page': 'suginami_boyscout.html', 'name': 'ボーイスカウト秋まつり（杉並第一小学校）', 'url': 'https://www.city.suginami.tokyo.jp/s059/event/28842.html', 'date': '2026-11-22', 'period': '11/22(日)', 'time': '10:00〜14:00', 'venue': '杉並第一小学校（杉並区阿佐谷北1丁目5番27号）', 'price': '無料', 'description': '野外ゲーム体験、模擬店、寄贈品バザーがあるボーイスカウトの秋まつり。どなたでも参加でき、当日直接会場へ。', 'cats': ['体験・ワークショップ', '地域交流'], 'io': '屋外', 'res': {'required': False, 'note': '当日直接会場へ。'}, 'quotes': ['開催日2026年11月22日（日曜日）開催時間午前10時から午後2時まで', '開催場所杉並第一小学校杉並区阿佐谷北1丁目5番27号', '野外ゲーム体験、模擬店、寄贈品バザー', 'おいしい野外料理を食べてゲームを楽しもう', '申し込み当日直接会場へお越しください。費用無料'], 'overall': 'B', 'basis': 'all_ages', 'child': True, 'reason': '野外ゲーム体験や模擬店がある、ボーイスカウトの秋まつり。無料・申込不要で、どなたでも参加できる。', 'axes': {'child_target': ('B', 'どなたでも参加でき、野外ゲームを楽しめる'), 'interactivity': ('A', '野外ゲーム体験などの参加型'), 'age_fit': ('unknown', '対象年齢は公式案内に明記がない'), 'stay_flexibility': ('A', '10時〜14時の間、好きな時間に参加できる'), 'burden': ('B', '屋外の催しで、模擬店・バザーもある'), 'cost': ('A', '費用無料'), 'reservation': ('A', '当日直接会場へ'), 'family_value': ('B', '野外ゲームと模擬店を家族で無料で楽しめる')}, 'strengths': ['無料・申込不要で野外ゲーム体験'], 'limitations': ['内容の詳細は公式ページに少ない', '屋外開催'], 'comparison': '総合B：無料・申込不要の参加型。内容の詳細は少ない。', 'pf': 'pass', 'pos': ['official_date_confirmed', 'child_activity_confirmed']}, {'id': 'verified-20261205-suginami-higashihara-xmas-market', 'week': '2026-12-05', 'ward': '杉並区', 'page': 'suginami_higashihara_xmas.html', 'name': '大人も子供も楽しめるクリスマスマーケット（コミュニティふらっと東原）', 'url': 'https://www.city.suginami.tokyo.jp/s020/event/28883.html', 'date': '2026-12-05', 'period': '12/5(土)', 'time': '10:30〜14:30', 'venue': 'コミュニティふらっと東原（杉並区下井草1-23-23）', 'price': '一部有料', 'description': 'ミニコンサート、クリスマスワークショップ、クリスマスゲーム、親子参加プログラム、雑貨・食品の販売がある多世代向けのクリスマスイベント。一部は事前申込が必要。', 'cats': ['体験・ワークショップ', '音楽・ステージ'], 'io': '屋内', 'res': {'required': None, 'note': '一部（親子参加型プログラム、ワークショップ等）は事前申し込みが必要。'}, 'quotes': ['開催日2026年12月5日（土曜日）開催時間午前10時30分から午後2時30分まで', '開催場所コミュニティふらっと東原杉並区下井草1-23-23', 'ミニコンサート、クリスマスワークショップ、クリスマスゲームなど、多世代が楽しめるクリスマスイベントです。', 'クリスマスコンサート、親子で参加プログラム、ワークショップ、雑貨・食品の販売など。', '一部事前申し込み必要（親子参加型プログラム、ワークショップ等）。'], 'overall': 'B', 'basis': 'child_program', 'child': True, 'reason': '親子参加プログラムやクリスマスワークショップ、ゲームがある多世代向けのイベント。一部有料で、親子参加型プログラムなどは事前申込が必要。', 'axes': {'child_target': ('B', 'どなたでも参加でき、親子で参加するプログラムがある'), 'interactivity': ('A', 'ワークショップやゲーム、親子参加プログラムなどの参加型'), 'age_fit': ('unknown', '対象年齢は公式案内に明記がない'), 'stay_flexibility': ('A', '10時30分〜14時30分の間で参加できる'), 'burden': ('B', '親子参加型プログラムやワークショップは事前申込が必要'), 'cost': ('B', '一部有料'), 'reservation': ('B', '一部のみ事前申込が必要'), 'family_value': ('B', 'クリスマスの催しを家族で楽しめる')}, 'strengths': ['親子参加プログラムとクリスマスワークショップ'], 'limitations': ['一部有料', '一部は事前申込が必要'], 'comparison': '総合B：親子向けの内容があるが、一部有料で一部は事前申込が必要。', 'pf': 'pass', 'pos': ['official_date_confirmed', 'child_activity_confirmed']}, {'id': 'verified-20261206-suginami-bremen-concert', 'week': '2026-12-05', 'ward': '杉並区', 'page': 'suginami_bremen.html', 'name': '音楽と絵画とお話でつづるブレーメンの音楽隊（杉並公会堂）', 'url': 'https://www.city.suginami.tokyo.jp/s030/event/28895.html', 'date': '2026-12-06', 'period': '12/6(日)', 'time': '11:00〜12:00／14:00〜15:00（2回公演）', 'venue': '杉並公会堂 小ホール（杉並区上荻1丁目23番15号）', 'price': '一般2,000円／中学生以下1,000円（1歳以下ひざ上無料）', 'description': 'グリム童話「ブレーメンの音楽隊」を、フルート・バイオリン・電子ピアノの演奏と語りで届ける親子向けのコンサート。0歳から入場可。チケット制（定員160名）。', 'cats': ['音楽・ステージ', '絵本・お話'], 'io': '屋内', 'res': {'required': True, 'note': 'チケット販売サイト（テケト）でのお申し込み。定員160名、申込順。'}, 'quotes': ['グリム童話「ブレーメンの音楽隊」。フルート、バイオリン、電子ピアノによる演奏と語りに加え、', '開催日2026年12月6日（日曜日）開催時間【午前の部】午前11時から正午【午後の部】午後2時から午後3時', '対象者どなたでも0歳から入場可', '開催場所杉並公会堂小ホール杉並区上荻1丁目23番15号', '一般：2,000円子ども（中学生以下）：1,000円1歳以下ひざ上無料'], 'overall': 'B', 'basis': 'child_program', 'child': True, 'reason': 'グリム童話を演奏と語りで楽しむ家族向けのコンサート。0歳から入場できるが、チケット制で有料。', 'axes': {'child_target': ('A', '0歳から入場できる、子ども向けの童話コンサート'), 'interactivity': ('B', '主に鑑賞型のコンサート'), 'age_fit': ('A', '0歳から入場可と明記（1歳以下はひざ上無料）'), 'stay_flexibility': ('B', '各回1時間の2回公演'), 'burden': ('C', 'チケットの事前購入が必要'), 'cost': ('C', '一般2,000円・中学生以下1,000円'), 'reservation': ('C', 'チケット販売サイトでの申込が必要（定員160名）'), 'family_value': ('B', '小さな子どもと一緒に童話の世界を楽しめる')}, 'strengths': ['0歳から入場できる童話コンサート'], 'limitations': ['有料のチケット制', '定員160名'], 'comparison': '総合B：0歳から楽しめるが、有料・チケット制で事前の購入が必要。', 'pf': 'pass', 'pos': ['official_date_confirmed', 'child_activity_confirmed']}, {'id': 'verified-20261213-suginami-motoamanuma-noel', 'week': '2026-12-12', 'ward': '杉並区', 'page': 'suginami_motoamanuma_noel.html', 'name': 'コミふら本天沼ノエルフェスティバル', 'url': 'https://www.city.suginami.tokyo.jp/s022/event/28941.html', 'date': '2026-12-13', 'period': '12/13(日)', 'time': '10:00〜14:00', 'venue': 'コミュニティふらっと本天沼（杉並区本天沼2丁目12番10号）', 'price': '一部有料', 'description': 'クリスマス音楽イベント、オーナメント作りなどのワークショップ、縁日・屋台がある冬のクリスマスイベント。子どもから大人まで参加でき、ワークショップのみ事前申込制。', 'cats': ['体験・ワークショップ', '音楽・ステージ'], 'io': '屋内', 'res': {'required': None, 'note': '当日直接会場へ。ワークショップのみ事前申込制。'}, 'quotes': ['開催日2026年12月13日（日曜日）開催時間午前10時から午後2時まで', '開催場所コミュニティふらっと本天沼杉並区本天沼2丁目12番10号', 'クリスマス音楽イベントをはじめ、オーナメント作りなどのワークショップなど', '縁日や屋台もクリスマス一色で充実。子どもから大人まで一日中楽しめます。', '申し込み当日直接会場へお越しください。ワークショップのみ事前申込制です。'], 'overall': 'B', 'basis': 'all_ages', 'child': True, 'reason': 'オーナメント作りのワークショップや縁日・屋台がある、子どもから大人まで楽しめるクリスマスイベント。一部有料で、ワークショップのみ事前申込制。', 'axes': {'child_target': ('B', '子どもから大人まで楽しめると案内されている'), 'interactivity': ('A', 'オーナメント作りなどのワークショップや縁日の参加型'), 'age_fit': ('B', '子どもから大人までと案内。細かな年齢条件は明記がない'), 'stay_flexibility': ('A', '10時〜14時の間、好きな時間に回れる'), 'burden': ('B', 'ワークショップは事前申込制'), 'cost': ('B', '一部有料'), 'reservation': ('B', 'ワークショップのみ事前申込制。それ以外は当日直接会場へ'), 'family_value': ('B', 'クリスマスの縁日とワークショップを家族で楽しめる')}, 'strengths': ['オーナメント作りと縁日・屋台', '当日直接行ける'], 'limitations': ['一部有料', 'ワークショップは事前申込制'], 'comparison': '総合B：参加型で気軽に行けるが、ワークショップは事前申込制で一部有料。', 'pf': 'pass', 'pos': ['official_date_confirmed', 'child_activity_confirmed']}]
RAW = SPECS_RAW
SPECS = []
for _r in RAW:
    _s = dict(_r)
    _s['categories'] = _s.pop('cats'); _s['indoor_outdoor'] = _s.pop('io'); _s['reservation'] = _s.pop('res')
    _s['child_activity'] = _s.pop('child'); _s['price_field'] = _s.pop('pf'); _s['positive'] = _s.pop('pos')
    SPECS.append(_s)
NEW_IDS = [s['id'] for s in SPECS]
SHARDS = {w: f'{w}-events-lead4-20261119.json' for w in ('2026-11-21', '2026-12-05', '2026-12-12')}
HELD = {'suginami-nishiogi-library-oshanashi-20261129': '条件は合うが11/28週の画像率が70%を割るため保留（申込制）', 'suginami-asagaya-xmas-market-20261129': '条件は合うが11/28週の画像率が70%を割るため保留', 'suginami-beach-sports-20261129': '条件は合うが11/28週の画像率が70%を割るため保留', 'meguro-kyogen-tamasudare-20261213': '目黒区在住・在学の小学生限定', 'ota-bicycle-class-20261212': '大田区在住の小学生限定', 'suginami-environment-center-classes-20261206': '杉並区在住・在学の小学生限定で申込締切済み', 'tokyo-women-children-festival-20261121': '公式の個別ページを確認できていない（第三者サイトの告知のみ）'}


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
    return out


def derive(pages_dir):
    out = {}
    for s in SPECS:
        ev = evidence(s, pages_dir)
        if s.get('image'):
            _raw = (pathlib.Path(pages_dir) / s['page']).read_text(encoding='utf-8', errors='ignore')
            if s['image'] not in _raw:
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
        run['lead4_addition_20261119'] = {
            'kind': 'individually_verified_official_events_from_lead_triage', 'added_ids': [i[0]['id'] for i in items],
            'held_not_published': sorted(HELD), 'pages_committed_at': 'research/2026-11-19-audit/pages/',
            'base_data_production_sha': BASE, 'global_source_audit_complete': False}
        S.jdump(d / f'{week}-run.json', run)
        for x in m['weekends']:
            if x['sat'] == week:
                x['count'] += n
    m['generated'] = '2026-11-19T13:00:00+09:00'
    S.jdump(d / 'manifest.json', m)
    h = S.jload(d / 'update_history.json')
    h['history'].append({
        'run_id': 'lead4-addition-20261119', 'run_type': 'manual_verified_lead4_addition',
        'status': 'verified_subset_publication', 'as_of_jst': '2026-11-19', 'executed_at': m['generated'],
        'base_data_production_sha': BASE, 'target_weekends': sorted(derived),
        'prior_active_week_records': 454, 'candidate_active_week_records': 459, 'added_weekly_records': 5,
        'new_event_ids': NEW_IDS, 'held_not_published': sorted(HELD),
        'existing_event_records_physically_deleted': 0, 'image_only_updates': 0,
        'source_failures_remain_unverified': True, 'global_source_audit_complete': False,
        'full_23_ward_25_source_audit_complete': False,
        'note': '日付なし候補367件のページを精読し、公式個別ページで条件を確認できた5件のみ追加。条件が合わないものは掲載せず理由を保存。',
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
