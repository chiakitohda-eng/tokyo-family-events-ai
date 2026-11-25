#!/usr/bin/env python3
"""3 weekly records (Tama expansion: Fuchu x2, Inagi x1) from committed official municipal pages (2026-11-21).

Raw official pages are committed unchanged under research/2026-11-20-thin-wards/pages/. The gate validator re-derives every record and requires exact equality.
"""
import argparse, hashlib, json, pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import suginami_addition_20261118 as S

BASE = 'f6695d542ca58cc1a43451bf5be9571e864c9ae6'   # data-production after lead24 (726 active week records)
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


SPECS_RAW = [
    {'id': 'verified-20261129-fuchu-oshitate-kodomo-kagaku', 'week': '2026-11-28', 'ward': '府中市', 'page': 'fuchu_kodomo_kagaku_20261129.html',
     'name': '子ども科学体験（押立文化センター）', 'url': 'https://www.city.fuchu.tokyo.jp/bunka/bunkacenter/oshitate/kodomokagakutaikenn.html', 'date': '2026-11-29', 'period': '11/29(日)', 'time': '10:00〜11:30',
     'venue': '押立文化センター 2階 講堂（府中市）', 'price': '無料',
     'description': '万華鏡、はねとびピンポン玉、くるくる磁石人形を作る科学工作の体験。中学生以下が対象（未就学児は保護者同伴）。事前申込は不要で、受付は10:00〜11:30、材料がなくなり次第終了。',
     'cats': ['体験・ワークショップ', '工作'], 'io': '屋内',
     'res': {'required': False, 'note': '事前申込不要。当日10:00〜11:30に会場で受付。材料がなくなり次第終了。'},
     'quotes': ['令和8年11月29日（日曜日）午前10時から午前11時30分', '押立文化センター 2階 講堂', '中学生以下(未就学児は保護者同伴）', '費用 無料 内容 万華鏡 はねとびピンポン玉 くるくる磁石人形', '事前申し込みは不要です。当日、会場へお越しください。'],
     'overall': 'A', 'basis': 'child_program', 'child': True,
     'reason': '中学生以下（未就学児は保護者同伴）が対象の無料の科学工作体験。事前申込不要で、材料がなくなり次第終了する。',
     'axes': _ax(['A', '対象は中学生以下で、未就学児は保護者同伴と明記'], ['A', '万華鏡やはねとびピンポン玉などを自分で作る体験'], ['A', '中学生以下と対象年齢が明記されている'], ['B', '10:00〜11:30の受付時間内に参加。材料がなくなり次第終了'], ['A', '事前申込不要で、当日会場へ行けばよい'], ['A', '費用は無料'], ['A', '事前申込不要'], ['A', '子どもが科学工作を作って持ち帰れる無料の体験']),
     'strengths': ['無料・事前申込不要で、中学生以下が工作を体験できる'], 'limitations': ['材料がなくなり次第終了するため、早めの来場が安心', '作った物を持ち帰る袋の持参が必要'],
     'comparison': '総合A：対象が子どもで、無料・申込不要。材料がなくなり次第終了する点だけが制約。',
     'pf': 'pass', 'pos': ['official_date_confirmed', 'child_activity_confirmed']},
    {'id': 'verified-20261205-fuchu-nobinobi-soccer', 'week': '2026-12-05', 'ward': '府中市', 'page': 'fuchu_nobinobi_soccer_20261205.html',
     'name': 'のびのびサッカーひろば（小学生から高校生の部・FC東京パーク府中）', 'url': 'https://www.city.fuchu.tokyo.jp/kenko/shogai/hoyou/soccer1205.html', 'date': '2026-12-05', 'period': '12/5(土)', 'time': '（1）13:00〜14:00／（2）14:00〜15:00（どちらか1回）',
     'venue': 'FC東京パーク府中（ミッテン府中屋上、京王線府中駅南口から徒歩約1分）', 'price': '無料',
     'description': '知的・発達の障害特性のあるお子さま向けのサッカーイベント、および障害の有無にかかわらずみんなで楽しむインクルーシブサッカー。小学生から高校生の部で、サッカー経験は問わない。各回約20名、申込多数の場合は抽選。',
     'cats': ['スポーツ', '体験・ワークショップ'], 'io': '屋外',
     'res': {'required': True, 'note': '12/2(水)までにオンラインフォームで申込。各回約20名で、申込多数の場合は抽選。'},
     'quotes': ['小学生から高校生の部（インクルーシブ編） 日時 12月5日（土曜日）', '（1） 午後1時から2時', 'FC東京パーク府中（ミッテン府中屋上、京王線「府中駅」南口より徒歩約1分）', '知的・発達の障害特性のあるお子さま向けのサッカーイベント', '各ひろば 約20名（申込多数の場合は抽選）', '12月2日（水曜日）までにオンラインフォーム（外部サイト）よりお申込ください。'],
     'overall': 'B', 'basis': 'child_program', 'child': True,
     'reason': '小学生から高校生を対象にした、サッカー経験を問わない無料のサッカーひろば。申込（12/2まで）と、多数の場合の抽選が必要。',
     'axes': _ax(['A', '「小学生から高校生の部」で、お子さま向けのサッカーイベントと明記'], ['A', '実際にサッカーをして体を動かす'], ['B', '小学生から高校生と幅が広く、学年別の案内はない'], ['B', '13:00か14:00開始のどちらか1回に参加'], ['B', '事前のオンライン申込と抽選が必要'], ['A', '費用は無料'], ['B', '12/2(水)までにオンライン申込。多数の場合は抽選'], ['A', '障害の有無やサッカー経験に関わらず、無料で楽しめる']),
     'strengths': ['無料で、サッカー経験を問わず参加できる', '障害の有無にかかわらずみんなで楽しめる'], 'limitations': ['12/2までの申込と抽選が必要（各回約20名）', '学年別の案内はない'],
     'comparison': '総合B：無料で子ども向けの体験だが、申込・抽選・少人数の条件がある。',
     'pf': 'pass', 'pos': ['official_date_confirmed', 'child_activity_confirmed']},
    {'id': 'verified-20261205-inagi-giants-hometown-fes', 'week': '2026-12-05', 'ward': '稲城市', 'page': 'komae_giants_hometown_fes_20261205.html',
     'name': 'GIANTS HOMETOWN fes 2026（午後の部・ジャイアンツタウンスタジアム）', 'url': 'https://www.city.komae.tokyo.jp/events/index.cfm/detail.4.146380.html', 'date': '2026-12-05', 'period': '12/5(土)', 'time': '午後の部 13:00〜16:00',
     'venue': 'ジャイアンツタウンスタジアム（稲城市矢野口3228番地南山95街区1号）', 'price': '無料',
     'description': '読売ジャイアンツの新ファーム球場で、選手なりきり体験、プロ野球のお仕事体験（グラウンド整備・アナウンス・カメラマン）、小学生向けの体を動かす講座などを行う。午前の部は連携7市の在住・在学者限定のため、ここでは誰でも参加できる午後の部（13:00〜16:00）を掲載。',
     'cats': ['まつり・イベント', 'スポーツ', '体験・ワークショップ'], 'io': '屋外',
     'res': {'required': None, 'note': '参加受付は当日。体験によって定員があり、定員を超える応募があった場合は抽選。選手なりきり体験はラリー用紙を受け取って参加。'},
     'quotes': ['令和８年12月５日(土曜日)', '午後の部：午後１時から午後４時', 'ジャイアンツタウンスタジアム（稲城市矢野口）（稲城市矢野口3228番地南山95街区１号）', '料金 無料 内容 〇選手なりきり体験', 'ゲーム形式で野球の動きが楽しめるコンテンツです。', '②の回/③の回＝小学１年生～３年生', '＜参加方法＞イベント当日、参加受付を行います。定員を越える応募があった場合は、抽選となります。'],
     'overall': 'B', 'basis': 'all_ages', 'child': True,
     'reason': '無料で、選手なりきり体験や小学生向けの体を動かす企画がある野球のお祭り。午後の部は誰でも参加でき、午前の部は7市在住・在学者限定。体験ごとに定員と抽選がある。',
     'axes': _ax(['B', '地域の皆様向けのイベントだが、小学生・幼児向けの回が複数ある'], ['A', '選手なりきり体験やバックホームゲームなど体験が中心'], ['B', '小学1〜3年生や小学生向けの回があり、年齢別に分かれている'], ['B', '13:00〜16:00の間に体験を選んで参加'], ['B', '体験ごとに定員があり、超えた場合は抽選。無料シャトルバスあり'], ['A', '料金は無料'], ['B', '当日の参加受付で、定員を超えた場合は抽選'], ['A', '無料でプロ野球の球場を体験できる']),
     'strengths': ['無料で、プロ野球の球場で選手なりきり体験ができる', '小学生・幼児向けの回がある'], 'limitations': ['体験ごとに定員があり、超えた場合は抽選', '午前の部は連携7市の在住・在学者限定', '屋外開催'],
     'comparison': '総合B：無料で体験が多く子どもも参加できるが、年齢別の回と体験ごとの定員・抽選がある。',
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
SHARDS = {w: f'{w}-events-lead25-20261121.json' for w in ('2026-11-21', '2026-11-28', '2026-12-05', '2026-12-12', '2026-12-19', '2026-12-26')}
HELD = {
    'fuchu-kodomo-togei-20261220': '府中市 子ども陶芸教室（12/20ほか）：対象が「市民の小学生」で、市内在住限定のため保留。',
    'fuchu-kodomo-cooking-20261219': '府中市 子どもクッキング教室（12/19）：対象が「小学生の府中市民」で市内在住限定のため保留。',
    'fuchu-harbarium-momijigaoka-20261209': '府中市 子どもハーバリウム教室（紅葉丘、12/9）：対象が「小学生の市民」で市内在住限定、申込は11/10に締切済みのため保留。',
    'fuchu-daikon-harvest-20261212': '府中市 大根収穫体験（12/12）：対象が「中学生以下の市民」で市内在住限定のため保留。',
    'fuchu-kazaripan-musashidai': '府中市 子どもかざりパン教室：公式ページが抽せん結果の掲載で、申込は終了しているため保留。',
    'komae-ohanashi-20261125': '狛江市 親子で楽しむおはなし会（0〜3歳、11/25）：公式ページに参加費の記載がなく、費用を推測しないため保留。',
    'komae-ohanashi-20261129': '狛江市 親子で楽しむおはなし会（3歳〜小学校低学年、11/29）：公式ページに参加費の記載がなく保留。',
    'komae-sports-festa-20270124': '狛江市 こまえスポーツフェスタ2026（2027/1/24）：対象が市内在住の小学3〜6年生で市内在住限定、かつ6週間の範囲外のため保留。',
    'tachikawa-xmas-movie-20261205': '立川市 クリスマス映画会「パンダコパンダ」（12/5）：対象は「どなたでも」で、公式ページ本文に子ども向けの記載がなく、子連れ向けの根拠が不足し保留。',
    'tachikawa-undou-20261213': '立川市 遊びながら運動能力アップ！（12/13、小学生）：公式ページに費用の記載がなく保留。',
    'giants-fes-morning-20261205': 'GIANTS HOMETOWN fes 午前の部（12/5）：連携7市の在住・在学者限定のため掲載しない（午後の部は登録）。',
    'inagi-kirafes-20261128': '稲城市 矢野口駅前きらきらフェスタ2026（11/28）：出演が学校の演奏等で、子ども向けの体験企画としての根拠が不足し保留。',
    'kodaira-kunitachi-etc-lists': '小平・国立・西東京・東久留米・清瀬・東村山・多摩・三鷹・武蔵野・調布・町田・八王子・昭島・日野・小金井・国分寺：一覧ページが動的で個別ページに届いていないため、今回は未確認（未解消）。',
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
        run['lead25_addition_20261121'] = {
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
        'run_id': 'lead25-addition-20261121', 'run_type': 'manual_verified_lead25_addition',
        'status': 'verified_subset_publication', 'as_of_jst': '2026-11-21', 'executed_at': m['generated'],
        'base_data_production_sha': BASE, 'target_weekends': sorted(derived),
        'prior_active_week_records': 726, 'candidate_active_week_records': 729, 'added_weekly_records': 3,
        'new_event_ids': NEW_IDS, 'held_not_published': sorted(HELD),
        'existing_event_records_physically_deleted': 0, 'image_only_updates': 0,
        'source_failures_remain_unverified': True, 'global_source_audit_complete': False,
        'full_23_ward_25_source_audit_complete': False,
        'note': '多摩拡張の最初の調査として、府中市（子ども科学体験11/29・のびのびサッカーひろば12/5）と稲城市（ジャイアンツホームタウンフェス12/5・午後の部）の公式ページを確認し、3件を追加。市民限定や費用未記載のものは保留。',
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
