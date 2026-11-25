#!/usr/bin/env python3
"""3 weekly records (Tama expansion: Inagi theme park x3) from committed official pages (2026-11-21).

Raw official pages are committed unchanged under research/2026-11-20-thin-wards/pages/. The gate validator re-derives every record and requires exact equality.
"""
import argparse, hashlib, json, pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import suginami_addition_20261118 as S

BASE = 'd06b8da2c5546c177d0007a607e4eda643c73c4d'   # data-production after lead27 (753 active week records)
CHECKED = '2026-11-21'
AXES = S.AXES
NOTE_AUDIT = '週別全源照合は未完（ためまっぷ403等）。この3件は多摩各市の公式ページの個別確認に基づく。'
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
    {'id': 'verified-20261121-inagi-yomiuriland-xmas-2026', 'week': '2026-11-21', 'ward': '稲城市', 'page': 'yomiuriland_christmas_2026.html',
     'name': 'よみランXmas！2026 ～ブライトフル メモリーズ～（よみうりランド）', 'url': 'https://www.yomiuriland.com/event/christmas2026/', 'date': '2026-11-21', 'end': '2026-12-25', 'period': '11/21(土)〜12/25(金)（ショー・グリーティングは土日祝と12/24・25）', 'time': 'ダンスショー15:30・18:30ほか、グリーティング13:00（内容により異なる）',
     'venue': 'よみうりランド（稲城市矢野口4015-1）太陽の広場・フラッグストリート・波のプールほか', 'price': 'ショー・グリーティング・噴水ショーは無料（別途入園料）。入園料込みのワンデーパスは、おとな5,900円・中高生4,700円・小学生4,100円・3歳以上の未就学児2,500円（通常価格。公式オンライン価格は各400円安い）',
     'description': '遊園地「よみうりランド」で開く、クリスマスのイベント。グッド＆ラッキーのホーリーダンスショー、小学生以下にキャンディーをプレゼントするグリーティング、クリスマス特別版の噴水ショー、サンタの演奏、アトラクションのクラフトラリーなどがある。ショーなどは無料だが、園内に入るには入園料が必要。雨天中止のショーがある。',
     'cats': ['まつり・イベント', 'テーマパーク・遊園地'], 'io': '屋内・屋外',
     'res': {'required': False, 'note': '予約の記載なし。入園券（ワンデーパス等）の購入が必要。'},
     'quotes': ['よみランXmas！2026 ～ブライトフル メモリーズ～ ダンスショーやアトラクションラリー、クリスマスフードなどが盛りだくさん！',
                'グッド＆ラッキー、ダンサーが光り輝くステージからお届けするクリスマス限定のダンスショーです！ 期間 11/21(土)～12/20(日)の土日祝日及び12/24(木)、25(金) 時間 15:30、18:30',
                'ダンスパフォーマンスと小学生以下のお子さまへキャンディーをプレゼントするグリーティングです。',
                '場所 太陽の広場 料金 無料※別途、入園料が必要です。',
                '噴水ショー「ラ・フォンテーヌ」クリスマス特別バージョン 大迫力の噴水ショーを、クリスマスの特別な演出でお楽しみいただけます。 期間 11/21(土)～12/25(金)'],
     'extra': [{'page': 'yomiuriland_charge_2026.html', 'url': 'https://www.yomiuriland.com/charge/', 'q': 'ワンデーパス 入園＋アトラクション乗り放題＋HANA・BIYORI入園'},
               {'page': 'yomiuriland_charge_2026.html', 'url': 'https://www.yomiuriland.com/charge/', 'q': 'おとな（18歳～64歳） 中高生 小学生/ シニア（65歳以上） 未就学児 （3歳以上～小学生未満） 通常価格 5,900円 4,700円 4,100円 2,500円'}],
     'overall': 'B', 'basis': 'all_ages', 'child': False,
     'reason': 'グッド＆ラッキーのダンスショーや、小学生以下へのキャンディーのプレゼントがあるクリスマスの遊園地イベント。ショーは無料だが入園料が必要で、屋外中心。',
     'axes': _ax(['B', '遊園地のイベントで対象はどなたでも。小学生以下へのキャンディーのプレゼントがある'], ['B', 'ショーやアトラクションラリーなど、見る・乗る内容が中心'], ['B', '年齢の限定はない（未就学児の入園は2,500円）'], ['A', '期間中の好きな時間に、ショーの時刻に合わせて回れる'], ['B', '屋外のショーが多く、寒さと混雑に注意'], ['C', '入園料が必要（小学生4,100円、未就学児2,500円など）'], ['A', '予約の記載なし（入園券を購入）'], ['B', 'クリスマスのショーとアトラクションを一日で楽しめる']),
     'strengths': ['ショーやグリーティングは無料で、アトラクションとあわせて一日楽しめる', '小学生以下にキャンディーのプレゼントがある'], 'limitations': ['入園料が必要で、家族だと費用がかさむ', '屋外のショーは雨天中止があり、寒さにも注意が必要'],
     'comparison': '総合B：クリスマスのショーが無料で見られる遊園地イベント。入園料が必要で、屋外中心。',
     'pf': 'pass', 'pos': ['official_date_confirmed']},
    {'id': 'verified-20261121-inagi-yomiuriland-kamenrider-ten', 'week': '2026-11-21', 'ward': '稲城市', 'page': 'yomiuriland_kamenrider_2026.html',
     'name': '仮面ライダー生誕55周年記念 ゴーゴー・レッツゴー！仮面ライダー展（よみうりランド）', 'url': 'https://www.yomiuriland.com/event/55letsgo_kamen-rider/', 'date': '2026-11-21', 'end': '2027-01-11', 'period': '11/21(土)〜1/11(月・祝)', 'time': '遊園地の営業時間に準じる（イベント会場の最終入場20:00）',
     'venue': 'よみうりランド（稲城市矢野口4015-1）グッジョバ!!スペース', 'price': '展示の入場券は、中学生以上1,200円、3歳〜小学生800円（別途、遊園地の入園料が必要）',
     'description': '仮面ライダーの55年の歴史をたどる展示。歴代の仮面ライダー37人の立像や、撮影で使われた武器・小道具などが並ぶ。展示会場の入口の券売機で入場券を買う。よみうりランドの入園料は別に必要。',
     'cats': ['展示・博物館', 'テーマパーク・遊園地'], 'io': '屋内',
     'res': {'required': False, 'note': '予約の記載なし。展示会場入口の券売機で入場券を購入。'},
     'quotes': ['1971年4月3日の放送開始から今年で55周年を迎えた「仮面ライダー」の歴史を辿れる展示イベント',
                '日程 2026年11月21日(土)～2027年1月11日(月祝) 時間 遊園地営業時間に準ずる(イベント会場最終入場20:00)',
                '初代の仮面ライダー1号から、現在テレビシリーズが放送中の仮面ライダーマイスに至る歴代の仮面ライダー総勢37人',
                '◆別途遊園地入園料が必要です。 ◆展示会場入口の券売機でご購入ください。 入場券 中学生以上 1,200円 3歳～小学生 800円'],
     'extra': [{'page': 'yomiuriland_charge_2026.html', 'url': 'https://www.yomiuriland.com/charge/', 'q': 'ワンデーパス 入園＋アトラクション乗り放題＋HANA・BIYORI入園'},
               {'page': 'yomiuriland_charge_2026.html', 'url': 'https://www.yomiuriland.com/charge/', 'q': 'おとな（18歳～64歳） 中高生 小学生/ シニア（65歳以上） 未就学児 （3歳以上～小学生未満） 通常価格 5,900円 4,700円 4,100円 2,500円'}],
     'overall': 'B', 'basis': 'all_ages', 'child': False,
     'reason': '仮面ライダーの歴代のヒーローや撮影の小道具を見られる展示。3歳〜小学生は800円で入れる。別途、遊園地の入園料が必要で、見る展示が中心。',
     'axes': _ax(['B', '対象はどなたでも。仮面ライダー好きの子どもが楽しめる展示'], ['C', '立像や小道具を見る展示が中心'], ['B', '3歳以上から料金が設定されている'], ['A', '遊園地の営業時間内に好きな時間に見られる'], ['A', '展示会場の入口の券売機で買える'], ['C', '展示800〜1,200円に加え、遊園地の入園料が必要'], ['A', '予約の記載なし'], ['B', '遊園地とあわせて、好きなヒーローの展示を楽しめる']),
     'strengths': ['約2か月と期間が長く、好きな日に行ける', '3歳〜小学生は800円と子ども料金がある'], 'limitations': ['遊園地の入園料が別に必要で、費用が高め', '展示を見る内容が中心'],
     'comparison': '総合B：仮面ライダー好きの子向けの展示。入園料と合わせると費用がかかる。',
     'pf': 'pass', 'pos': ['official_date_confirmed']},
    {'id': 'verified-20261121-inagi-yomiuriland-jewellumination-2026', 'week': '2026-11-21', 'ward': '稲城市', 'page': 'yomiuriland_jewellumination_2026.html',
     'name': 'ジュエルミネーション（よみうりランド）', 'url': 'https://www.yomiuriland.com/jewellumination/', 'date': '2026-11-21', 'end': '2027-04-04', 'period': '2027/4/4まで（10/29から開催中）', 'time': '夕方から夜（営業時間・カレンダーは公式サイトで確認）。アフターパスは15:00から入園',
     'venue': 'よみうりランド（稲城市矢野口4015-1）', 'price': '夕方から入るアフターパス（入園＋アトラクション乗り放題）は、おとな3,100円・中高生2,500円・小学生2,200円・3歳以上の未就学児1,500円（通常価格。公式オンライン価格は各300円安い）',
     'description': '世界的な照明デザイナー石井幹子さんがプロデュースする、よみうりランドのイルミネーション。今シーズンは新色が登場。ジュエルミネーション開催日の15:00から入園できるアフターパスがある。',
     'cats': ['まつり・イベント', 'テーマパーク・遊園地'], 'io': '屋外',
     'res': {'required': False, 'note': '予約の記載なし。入園券（アフターパス・ワンデーパス等）の購入が必要。'},
     'quotes': ['2026-2027 Season 開催中'],
     'extra': [{'page': 'yomiuriland_event_list_2026.html', 'url': 'https://www.yomiuriland.com/event/', 'q': '10月 29日 ~ 4月 4日 今シーズンは新色登場！世界的照明デザイナー石井幹子プロデュース「ジュエルミネーション」開催中'},
               {'page': 'yomiuriland_charge_2026.html', 'url': 'https://www.yomiuriland.com/charge/', 'q': 'アフターパス ジュエルミネーション開催日の15:00～の入園＋アトラクション乗り放題 観覧車「Sky-Go-LAND」ほか一部アトラクション除く'},
               {'page': 'yomiuriland_charge_2026.html', 'url': 'https://www.yomiuriland.com/charge/', 'q': 'おとな（18歳～64歳） 中高生 小学生/ シニア（65歳以上） 未就学児 （3歳以上～小学生未満） 通常価格 3,100円 2,500円 2,200円 1,500円'}],
     'overall': 'B', 'basis': 'all_ages', 'child': False,
     'reason': 'よみうりランドで、約半年にわたり開かれるイルミネーション。夕方から入れるアフターパスがあり、小学生2,200円、未就学児1,500円。屋外で夜の寒さに注意。',
     'axes': _ax(['B', '対象はどなたでも。遊園地の夜のイルミネーション'], ['C', '見て歩く内容が中心（アトラクションも利用できる）'], ['B', '年齢の限定はなく、未就学児の料金もある'], ['A', '期間が長く、15:00から好きな時間に入れる'], ['B', '屋外で、夜の寒さと帰りの時間に注意'], ['C', '入園料が必要（アフターパス：小学生2,200円、未就学児1,500円など）'], ['A', '予約の記載なし'], ['B', '遊園地のアトラクションとイルミネーションを一緒に楽しめる']),
     'strengths': ['期間が長く、アフターパスで夕方から安く入れる', 'アトラクションとイルミネーションを同じ日に楽しめる'], 'limitations': ['入園料が必要で、費用がかかる', '屋外で夜は冷え、帰りが遅くなる'],
     'comparison': '総合B：長期間のイルミネーション。夕方から入るアフターパスで費用を抑えられるが、屋外で夜の寒さに注意。',
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
SHARDS = {w: f'{w}-events-lead32-20261121.json' for w in ('2026-11-21', '2026-11-28', '2026-12-05', '2026-12-12', '2026-12-19', '2026-12-26')}
HELD = {
    'inagi-giants-day-special-20261206': '稲城市 GIANTS Day Special 2026 inよみうりランド（12/6）：トークショー・アトラクション体験会は抽選で、申込期間の状況が確認できず保留。',
    'inagi-yomiuriland-okome-fes-20261121': '稲城市 「お米のよろこび再発見」フェス（11/21〜23）：開催が今日から3日間で、参加費の記載が整理券・提供セットの記載のみで保留。',
    'inagi-yomiuriland-jujutsu-20261213': '稲城市 呪術廻戦×よみうりランド（〜12/13）：公式ページの本文が外部サイトで取得できず保留。',
    'tama-puroland-christmas-2026': '多摩市 サンリオピューロランド Puroland Illumination Christmas：公式ページの開催期間が取得した本文から読み取れず、料金も日ごとに変わるため保留。',
    'remaining-cities': '小金井・小平・国分寺・日野・町田・国立・狛江の週末の個別イベントと、昭和記念公園・多摩動物公園・東京ドームシティなどの個別ページは、公式根拠（日付・場所・費用）を引き続き調査中。',
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
        run['lead32_addition_20261121'] = {
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
        'run_id': 'lead32-addition-20261121', 'run_type': 'manual_verified_lead32_addition',
        'status': 'verified_subset_publication', 'as_of_jst': '2026-11-21', 'executed_at': m['generated'],
        'base_data_production_sha': BASE, 'target_weekends': sorted(derived),
        'prior_active_week_records': 753, 'candidate_active_week_records': 756, 'added_weekly_records': 3,
        'new_event_ids': NEW_IDS, 'held_not_published': sorted(HELD),
        'existing_event_records_physically_deleted': 0, 'image_only_updates': 0,
        'source_failures_remain_unverified': True, 'global_source_audit_complete': False,
        'full_23_ward_25_source_audit_complete': False,
        'note': '多摩拡張の第8弾として、稲城市のよみうりランド（よみランXmas・仮面ライダー展・ジュエルミネーション）を公式サイトの個別ページと料金ページで確認して追加。'
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
