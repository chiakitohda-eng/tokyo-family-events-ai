#!/usr/bin/env python3
"""1 weekly record (Tama expansion: Inagi x1) from committed official pages (2026-11-21).

Raw official pages are committed unchanged under research/2026-11-20-thin-wards/pages/. The gate validator re-derives every record and requires exact equality.
"""
import argparse, hashlib, json, pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import suginami_addition_20261118 as S

BASE = 'b5afacabf0ea007f89653ad7e08e132067e48ca5'   # data-production after lead27 (752 active week records)
CHECKED = '2026-11-21'
AXES = S.AXES
NOTE_AUDIT = '週別全源照合は未完（ためまっぷ403等）。この1件は多摩各市の公式ページの個別確認に基づく。'
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
    {'id': 'verified-20261205-inagi-giants-hometown-fes-2026', 'week': '2026-12-05', 'ward': '稲城市', 'page': 'hino_giants_hometown_fes_20261205.html',
     'name': 'GIANTS HOMETOWN fes 2026（ジャイアンツタウンスタジアム）', 'url': 'https://www.city.hino.lg.jp/bunka/kigyo/1027368/1029740.html', 'date': '2026-12-05', 'period': '12/5(土)', 'time': '午前の部10:00〜12:00（周辺7市の在住・在学・在勤の方）／午後の部13:00〜16:00（どなたでも）',
     'venue': 'ジャイアンツタウンスタジアム（稲城市矢野口3228 南山95街区1号）', 'price': '無料（無料シャトルバスあり）',
     'description': '読売ジャイアンツの新ファーム球場で、ウォーミングアップ・トスバッティング・ピッチング・ノックなどの選手なりきり体験や、アナウンス・カメラマンなどのお仕事体験、現役選手から学ぶ投げ方教室などを行う。事前申込は不要で、当日受付。午前の部は周辺7市（稲城・府中・調布・多摩・狛江・立川・日野）の在住・在学・在勤の方、午後の部はどなたでも参加できる。',
     'cats': ['スポーツ', '体験・ワークショップ'], 'io': '屋外',
     'res': {'required': False, 'note': '事前申込不要（当日受付）。体験によっては当日配布の抽選券・定員（各回3〜10名）がある。'},
     'quotes': ['「GIANTS HOMETOWN fes 2026」開催！ジャイアンツタウンスタジアム周辺自治体7市の子どもたちを対象にスポーツイベントを開催します！',
                '日時 令和8年12月5日（土曜日） （1）午前の部：午前10時から正午 （2）午後の部：午後1時から午後4時',
                '場所 ジャイアンツタウンスタジアム（稲城市矢野口3228南山95街区1号） 対象 （1）午前の部：周辺自治体7市在住・在学・在勤の方 （2）午後の部：どなたでも 申込 事前申込不要（当日受付）',
                'プロ野球選手が使用するグラウンドでジャイアンツの選手さながらの体験が楽しめます。',
                'サブグラウンドを一般開放し、さまざまなスポーツを無料で体験することができます。',
                '無料シャトルバス 当日は、京王相模原線「京王よみうりランド駅」より無料シャトルバスを運行します。'],
     'overall': 'A', 'basis': 'child_program', 'child': True,
     'reason': '周辺7市の子どもたちを対象にした、プロ野球選手の体験やお仕事体験が無料でできるスポーツイベント。午後の部はどなたでも参加でき、事前申込は不要。',
     'axes': _ax(['A', '周辺自治体の子どもたちを対象にしたスポーツイベントと明記'], ['A', 'ウォーミングアップ・ピッチング・ノック・お仕事体験などの参加型'], ['B', '年齢の限定はなく、体験ごとに定員がある'], ['A', '午後の部は13:00〜16:00の間に好きな体験を選べる'], ['B', '体験によっては抽選券・定員があり、屋外で待つ時間がある'], ['A', '無料（無料シャトルバスもある）'], ['A', '事前申込不要（当日受付）'], ['A', 'プロ野球の球場で、親子で本格的な体験を無料でできる']),
     'strengths': ['無料・事前申込不要で、プロの球場で体験できる', '午後の部はどなたでも参加でき、無料シャトルバスがある'], 'limitations': ['体験ごとに定員（各回3〜10名）や抽選券があり、人気の体験は参加できない場合がある', '午前の部は周辺7市の在住・在学・在勤の方のみ'],
     'comparison': '総合A：無料・申込不要でプロの球場の体験ができる子ども向けイベント。人気の体験は定員に注意。',
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
SHARDS = {w: f'{w}-events-lead31-20261121.json' for w in ('2026-11-21', '2026-11-28', '2026-12-05', '2026-12-12', '2026-12-19', '2026-12-26')}
HELD = {
    'nishitokyo-hokutto-matsuri-20261123': '西東京市 第4回ほくっとまつり（11/23）：公式ページに費用の記載がなく保留。',
    'nishitokyo-tomato-20261123': '西東京市 トマトのひみつ大研究（11/23）：対象が市内在住・在学の小学3〜6年生のため保留。',
    'komae-sports-festa-20270124': '狛江市 こまえスポーツフェスタ（2027/1/24）：対象が市内在住の小学3〜6年生で、開催が対象期間外のため保留。',
    'kodaira-onuma-minibunkasai-20261121': '小平市 大沼公民館 ミニ文化祭（11/21）：開催日が本日で、調査時点で終了済みの可能性があるため保留。',
    'kodaira-nihongo-happyokai-20261219': '小平市 第12回日本語発表会（12/19）：子ども向けの記載が少なく、費用の記載もないため保留。',
    'remaining-cities': '小金井・小平・国分寺・日野・町田・国立・狛江の週末の個別イベントは、公式根拠（日付・場所・費用）を引き続き調査中。',
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
        run['lead31_addition_20261121'] = {
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
        'run_id': 'lead31-addition-20261121', 'run_type': 'manual_verified_lead31_addition',
        'status': 'verified_subset_publication', 'as_of_jst': '2026-11-21', 'executed_at': m['generated'],
        'base_data_production_sha': BASE, 'target_weekends': sorted(derived),
        'prior_active_week_records': 752, 'candidate_active_week_records': 753, 'added_weekly_records': 1,
        'new_event_ids': NEW_IDS, 'held_not_published': sorted(HELD),
        'existing_event_records_physically_deleted': 0, 'image_only_updates': 0,
        'source_failures_remain_unverified': True, 'global_source_audit_complete': False,
        'full_23_ward_25_source_audit_complete': False,
        'note': '多摩拡張の第7弾として、稲城市のジャイアンツタウンスタジアムで開催されるGIANTS HOMETOWN fes 2026を、日野市・狛江市の公式ページで確認して追加。'
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
