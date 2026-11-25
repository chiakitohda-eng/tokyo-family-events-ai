#!/usr/bin/env python3
"""4 weekly records (Tama expansion: Tama x2, Kiyose x2) from committed official pages (2026-11-21).

Raw official pages are committed unchanged under research/2026-11-20-thin-wards/pages/. The gate validator re-derives every record and requires exact equality.
"""
import argparse, hashlib, json, pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import suginami_addition_20261118 as S

BASE = '2d008f1f168583e82bf5e1a7d9eab60a48e2bdc3'   # data-production after lead27 (747 active week records)
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
    {'id': 'verified-20261123-tama-news-sports-taiken', 'week': '2026-11-21', 'ward': '多摩市', 'page': 'tama_news_sports_taiken_20261123.html',
     'name': 'ニュースポーツ体験教室（リフォームプライス多摩アリーナ）', 'url': 'https://www.city.tama.lg.jp/kenkofukushi/1008238/sports/joho/suisin/1014545/1018413.html', 'date': '2026-11-23', 'period': '11/23(月・祝)', 'time': '9:20〜11:30',
     'venue': 'リフォームプライス多摩アリーナ（総合体育館）第1スポーツホール', 'price': '無料（費用不要）',
     'description': 'ネオテニス、ボッチャ、モルックなどのニュースポーツを体験する教室。年齢や運動経験に関係なく楽しめる内容で、対象は小学生以上。申込不要で、当日会場へ行く。室内シューズ、タオル、飲み物が必要。',
     'cats': ['スポーツ', '体験・ワークショップ'], 'io': '屋内',
     'res': {'required': False, 'note': '申込不要。当日会場へ。'},
     'quotes': ['ニュースポーツ体験教室～子どもから大人まで、誰でも楽しめるスポーツ体験～',
                '開催日 2026年11月23日（月曜日） 2027年1月10日（日曜日） 、3月20日（土曜日） 開催時間 午前9時20分 から 午前11時30分 まで',
                '開催場所 リフォームプライス多摩アリーナ（総合体育館）第1スポーツホール 対象 小学生以上 内容 ネオテニス / ボッチャ / モルック等',
                '申込み 不要 ※当日会場にお越しください。 費用 不要'],
     'overall': 'B', 'basis': 'all_ages', 'child': False,
     'reason': '小学生以上が対象の、ネオテニス・ボッチャ・モルックを体験できる無料の教室。申込不要で、年齢や運動経験を問わない。',
     'axes': _ax(['B', '対象は小学生以上で、子どもから大人まで参加できる'], ['A', 'ネオテニス・ボッチャ・モルックを体験する参加型'], ['B', '対象は小学生以上（未就学児は対象外）'], ['B', '9:20〜11:30の1回'], ['A', '申込不要で、当日会場へ行く'], ['A', '費用は不要'], ['A', '申込不要'], ['B', '親子で新しいスポーツを無料で体験できる']),
     'strengths': ['無料・申込不要で、道具を使った体験ができる', '年齢や運動経験を問わない'], 'limitations': ['対象は小学生以上で、未就学児は対象外', '室内シューズ・タオル・飲み物の持参が必要'],
     'comparison': '総合B：無料・申込不要のスポーツ体験。小学生以上向けで、未就学児は参加できない。',
     'pf': 'pass', 'pos': ['official_date_confirmed']},
    {'id': 'verified-20261121-tama-center-illumination-2026', 'week': '2026-11-21', 'ward': '多摩市', 'page': 'tama_illumination_2026.html',
     'name': '多摩センターイルミネーション2026（パルテノン大通り周辺）', 'url': 'https://www.city.tama.lg.jp/kurashi/machi/tamacenter/1011236/1013499.html', 'date': '2026-11-21', 'end': '2027-01-11', 'period': '〜1/11(月)の毎日（11/14から開催中）', 'time': '16:30〜22:30（ハローキティバルーンイルミは20:30まで）',
     'venue': '多摩センターパルテノン大通り周辺', 'price': '無料（費用不要）',
     'description': '多摩センター駅前のパルテノン大通り周辺で行われる冬のイルミネーション。開催期間は2026年11月14日から2027年1月11日まで。ハローキティバルーンイルミの点灯は20:30まで。クスノキイルミネーションは2027年2月28日まで点灯する。',
     'cats': ['まつり・イベント', '自然・散歩'], 'io': '屋外',
     'res': {'required': False, 'note': '申込の記載なし。費用は不要。'},
     'quotes': ['多摩センターイルミネーション2026 点灯スケジュール',
                '開催期間 2026年11月14日（土曜日）から2027年1月11日（月曜日）まで',
                '開催時間 午後4時30分 から 午後10時30分 まで ※ハローキティバルーンイルミの点灯時間は20時30分まで',
                '開催場所 多摩センターパルテノン大通り周辺 費用 不要'],
     'overall': 'B', 'basis': 'all_ages', 'child': False,
     'reason': '多摩センター駅前で、2027年1月11日まで毎日点灯する無料のイルミネーション。ハローキティのバルーンイルミもあり、家族で夜の散歩ができる。',
     'axes': _ax(['B', '対象の限定はなく、ハローキティのバルーンイルミがある'], ['C', '見て歩く内容が中心'], ['B', '年齢の限定はない'], ['A', '期間中の16:30〜22:30に、好きな時間に立ち寄れる'], ['B', '屋外で、夜間の寒さと帰りの時間に注意'], ['A', '費用は不要'], ['A', '申込の記載なし'], ['B', '冬の夜に家族で無料のイルミネーションを楽しめる']),
     'strengths': ['無料で、期間が長く、好きな時間に立ち寄れる', 'ハローキティのバルーンイルミがある'], 'limitations': ['屋外で夜間のため、防寒と帰りの時間に注意', 'バルーンイルミの点灯は20:30まで'],
     'comparison': '総合B：無料で立ち寄りやすい冬のイルミネーション。体験型ではなく、屋外で夜の開催。',
     'pf': 'pass', 'pos': ['official_date_confirmed']},
    {'id': 'verified-20261206-kiyose-museum-theater6-sumikko', 'week': '2026-12-05', 'ward': '清瀬市', 'page': 'kiyose_museum_theater6_20261206.html',
     'name': 'ミュージアム・シアター6 映画「すみっコぐらし ツギハギ工場のふしぎなコ」（郷土博物館）', 'url': 'https://www.city.kiyose.lg.jp/bunkasportskankou/bunka/kyoudo/1002770/1016841.html', 'date': '2026-12-06', 'period': '12/6(日)', 'time': '10:30〜（上映70分）',
     'venue': '清瀬市郷土博物館 映像展示室', 'price': '無料（入場無料）',
     'description': '劇場版アニメ「映画 すみっコぐらし ツギハギ工場のふしぎなコ」（70分）をDVDで上映する。映画鑑賞が初めてのお子さまも気軽に参加できる。申込不要で、直接会場へ。定員は40席程度。',
     'cats': ['舞台・音楽', 'まつり・イベント'], 'io': '屋内',
     'res': {'required': False, 'note': '申込不要。直接会場へ。定員40席程度。'},
     'quotes': ['令和8年度 ミュージアム・シアター6',
                '開催日 2026年12月6日（日曜日） 開催時間 午前10時30分～ 開催場所 郷土博物館 映像展示室 ※直接会場へ 対象 どなたでも',
                '『映画 すみっコぐらし ツギハギ工場のふしぎなコ 』70分',
                '映画鑑賞が初めてのお子さまも、ぜひお気軽にご参加ください。',
                '費用 不要 入場無料 定員 40席程度'],
     'overall': 'B', 'basis': 'all_ages', 'child': True,
     'reason': '子どもに人気のキャラクター映画「すみっコぐらし」を無料で上映する博物館の映画会。映画鑑賞が初めての子も歓迎で、申込不要。定員40席程度。',
     'axes': _ax(['B', '対象はどなたでも。映画鑑賞が初めての子も歓迎と明記'], ['C', '映画の鑑賞が中心'], ['B', '年齢の限定はなく、70分の上映'], ['B', '10:30からの上映1回（70分）'], ['A', '申込不要で、直接会場へ行く'], ['A', '入場無料'], ['A', '申込不要（定員40席程度）'], ['B', '子ども向けのアニメ映画を無料で見られる']),
     'strengths': ['無料・申込不要で、子ども向けのアニメ映画を見られる', '映画が初めての子も歓迎と明記'], 'limitations': ['定員が40席程度で、満席の場合は入れない', '映画の鑑賞が中心で、上映は70分'],
     'comparison': '総合B：無料・申込不要の子ども向け映画会。鑑賞中心で、定員が少ない。',
     'pf': 'pass', 'pos': ['official_date_confirmed', 'child_activity_confirmed']},
    {'id': 'verified-20261128-kiyose-tamaroku-news-sports-festa', 'week': '2026-11-28', 'ward': '清瀬市', 'page': 'kiyose_tamaroku_news_sports_20261128.html',
     'name': 'たまろくとニュースポーツフェスタ（下宿地域市民センター・下宿運動公園広場）', 'url': 'https://www.city.kiyose.lg.jp/bunkasportskankou/sports/sportsevent/1016896.html', 'date': '2026-11-28', 'period': '11/28(土)', 'time': '9:30〜12:00',
     'venue': '下宿地域市民センター（市民体育館・下宿運動公園広場）', 'price': '無料（費用不要）',
     'description': 'モルック、ラダーゲッター、ベースボール5などのニュースポーツを楽しむイベント。子どもから高齢者まで楽しめる。体験に応じてスタンプを集めると、限定のぷっくりシールがもらえる。多摩六都の物品販売やキャラクターのグリーティングも予定。申込不要で、直接会場へ。',
     'cats': ['スポーツ', 'まつり・イベント'], 'io': '屋内・屋外',
     'res': {'required': False, 'note': '申込不要。直接会場へ。'},
     'quotes': ['たまろくとニュースポーツフェスタ',
                '開催日 2026年11月28日（土曜日） 開催時間 午前9時30分 から 正午 まで 開催場所 下宿地域市民センター 対象 どなたでも',
                'モルックやラダーゲッタ、ベースボール5など様々なニュースポーツを楽しめるイベントです。',
                '体験に応じたスタンプを集めると、イベント限定オリジナルぷっくりシールがもらえます。',
                '会場では多摩六都の物品販売、キャラクターたちのグリーティングも予定しています。',
                '申込み 不要 直接会場へお越しください。 費用 不要'],
     'overall': 'B', 'basis': 'all_ages', 'child': False,
     'reason': '子どもから高齢者まで楽しめるニュースポーツを無料で体験できるイベント。スタンプを集めるとシールがもらえ、キャラクターのグリーティングもある。申込不要。',
     'axes': _ax(['B', '対象はどなたでも。子どもから高齢者まで楽しめると明記'], ['A', 'モルックなどのニュースポーツを体験する参加型'], ['B', '年齢の限定はない（種目により体験できる時間が異なる）'], ['A', '9:30〜12:00の間に好きな種目を選んで参加できる'], ['A', '申込不要で、直接会場へ行く'], ['A', '費用は不要'], ['A', '申込不要'], ['B', '親子で複数のスポーツを無料で体験できる']),
     'strengths': ['無料・申込不要で、複数のニュースポーツを体験できる', 'スタンプラリーでシールがもらえる'], 'limitations': ['時間によって体験できない種目がある', '種目は変更になる可能性がある'],
     'comparison': '総合B：無料・申込不要の体験型スポーツイベント。種目は時間帯により変わる。',
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
SHARDS = {w: f'{w}-events-lead29-20261121.json' for w in ('2026-11-21', '2026-11-28', '2026-12-05', '2026-12-12', '2026-12-19', '2026-12-26')}
HELD = {
    'tama-genki-festival-20261205': '多摩市 たまげんきフェスティバル（12/5）：公式ページに費用の記載がなく保留。',
    'tama-nogyosai-20261128': '多摩市 第2回多摩市農業祭（11/28）：公式ページに費用の記載がなく保留。',
    'tama-monomatsuri-20261121': '多摩市 多摩モノまつり2026（11/21）：多摩市のページに費用の記載がなく保留（主催は多摩都市モノレール）。',
    'tama-camp-ryori-20261129': '多摩市 農作物収穫×キャンプ料理体験会（11/29）：申込必要・費用必要だが、申込状況が確認できず保留。',
    'higashikurume-xmas-concert-20261220': '東久留米市 まろにえ★クリスマスコンサート（12/20）：整理券が必要で、配布方法の詳細が外部の生涯学習センターのページにあり、公式の確認が取れず保留。',
    'kiyose-kominka-20261121': '清瀬市 古民家de昔の暮らし体験（11/21）：定員15名・10/3受付開始で、当日開催のため申込受付中か確認できず保留。',
    'musashino-inokashira-rekishi-tour-20261212': '武蔵野市 井の頭自然文化園 れきしたんけんツアー（12/12）：定員超過時は抽選で、申込期間が確認できず保留。',
    'remaining-cities': '三鷹・小金井・小平・国分寺・西東京・日野・狛江・稲城・町田・国立の週末の個別イベントは、公式根拠（日付・場所・費用）を引き続き調査中。',
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
            row = next((r for r in munis if r['ward'] == ward), None)
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
        run['lead29_addition_20261121'] = {
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
        'run_id': 'lead29-addition-20261121', 'run_type': 'manual_verified_lead29_addition',
        'status': 'verified_subset_publication', 'as_of_jst': '2026-11-21', 'executed_at': m['generated'],
        'base_data_production_sha': BASE, 'target_weekends': sorted(derived),
        'prior_active_week_records': 747, 'candidate_active_week_records': 751, 'added_weekly_records': 4,
        'new_event_ids': NEW_IDS, 'held_not_published': sorted(HELD),
        'existing_event_records_physically_deleted': 0, 'image_only_updates': 0,
        'source_failures_remain_unverified': True, 'global_source_audit_complete': False,
        'full_23_ward_25_source_audit_complete': False,
        'note': '多摩拡張の第5弾として、多摩市（ニュースポーツ体験教室・多摩センターイルミネーション）、清瀬市（ミュージアム・シアター・たまろくとニュースポーツフェスタ）を公式の個別ページで確認して追加。'
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
