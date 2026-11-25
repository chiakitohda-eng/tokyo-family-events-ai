#!/usr/bin/env python3
"""4 weekly records (Tama expansion: Tachikawa Showa Kinen Park x4) from committed official pages (2026-11-21).

Raw official pages are committed unchanged under research/2026-11-20-thin-wards/pages/. The gate validator re-derives every record and requires exact equality.
"""
import argparse, hashlib, json, pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import suginami_addition_20261118 as S

BASE = 'da7c29fd173c9fe3e1ab9718daec13b33121d2f3'   # data-production after lead27 (756 active week records)
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
    {'id': 'verified-20261121-tachikawa-showakinen-craft-leaf-2026', 'week': '2026-11-21', 'ward': '立川市', 'page': 'showakinen_craft_leaf_2026.html',
     'name': 'こどもの森クラフト教室「葉っぱでアート」（国営昭和記念公園）', 'url': 'https://www.showakinen-koen.jp/event/25743/', 'date': '2026-11-23', 'end': '2026-12-13', 'period': '11/23(祝)・28・29、12/5・6・12・13（土日祝。各月の第3土日は除く）', 'time': '受付10:30〜11:30、13:00〜14:30',
     'venue': '国営昭和記念公園 こどもの森木工房（立川市緑町3173）', 'price': '300円（別途入園料）',
     'description': '園内の葉っぱを組み合わせて、小枝の額に飾る「葉っぱアート」を作る工作教室。当日受付で、先着順・入替制（一度に入れるのは9名）。制作は子どもが自分で行い、保護者は木工房の周りで待つ。',
     'cats': ['体験・ワークショップ', '工作'], 'io': '屋内',
     'res': {'required': False, 'note': '当日受付（先着順・入室定員9名・随時入替制）。事前予約は不要。'},
     'quotes': ['園内の葉っぱを使って、すてきな葉っぱアートを作ろう！', '10月3日(土)～12月13日（日）の土日祝日', '※各月の第3土曜日と第3日曜日を除く', '参加費300円（入園料別）', '対象小学生・中学生協力立川市クラフト同好会'],
     'overall': 'A', 'basis': 'child_program', 'child': True,
     'reason': '小学生・中学生向けの工作教室。当日受付で、300円（入園料別）。保護者は木工房の周りで待つ形で、親子で一緒に作る内容ではない。',
     'axes': _ax(['A', '対象は小学生・中学生'], ['A', '葉っぱを選んで組み合わせる工作'], ['B', '小学生・中学生が対象で、未就学児は対象外'], ['B', '受付時間内に来れば参加できる（入替制）'], ['B', '先着順で、混む日は待つことがある'], ['A', '300円と手頃（入園料は別）'], ['A', '事前予約は不要（当日受付）'], ['A', '公園で遊ぶ日に、自分だけの作品を作れる']),
     'strengths': ['小中学生が自分で作れる工作で、予約がいらない', '参加費が300円と手頃'], 'limitations': ['入園料が別に必要', '先着順・入替制で、混む日は待つことがある', '対象は小学生・中学生で、未就学児は対象外'],
     'comparison': '総合A：小中学生向けで当日受付、300円と手頃な工作教室。入園料は別。',
     'pf': 'pass', 'pos': ['official_date_confirmed']},
    {'id': 'verified-20261121-tachikawa-showakinen-greenexpo-20261123', 'week': '2026-11-21', 'ward': '立川市', 'page': 'showakinen_greenexpo_20261123.html',
     'name': 'GREEN×EXPO 2027ってなんだろう？ Vol.5 ペーパークラフト・缶バッジづくり（国営昭和記念公園）', 'url': 'https://www.showakinen-koen.jp/event/77455/', 'date': '2026-11-23', 'period': '11/23(月・祝) 9:30〜16:00（パネル展示は29日まで）', 'time': '9:30〜16:00',
     'venue': '国営昭和記念公園 総合案内所（立川市緑町3173、あけぼの口から徒歩1分）', 'price': '無料（駐車料は別途）',
     'description': '2027年3月に横浜で開かれる「GREEN×EXPO 2027」のマスコット「トゥンクトゥンク」のペーパークラフト（先着100名）と缶バッジ（先着250名）を作るワークショップ。1回5〜15分で、ハサミを使わず小さな子どもでも作れる。パネル展示は11/29まで。',
     'cats': ['体験・ワークショップ', '工作'], 'io': '屋外',
     'res': {'required': False, 'note': '当日受付（先着順）。事前予約は不要。'},
     'quotes': ['ハサミを使わないので、小さなお子様でも簡単に作ることが出来ます。', '5～15分程度先着100名', '5～15分程度先着250名', '2026年11月23日（月祝）9：30～16：00', '参加費無料※駐車料は別途必要。'],
     'overall': 'B', 'basis': 'all_ages', 'child': False,
     'reason': '無料で、5〜15分でできるペーパークラフトと缶バッジづくり。小さな子どもでも作れるが、先着順で数に限りがある。',
     'axes': _ax(['B', '子ども向けとは限らないが、小さな子どもでも作れる内容'], ['A', '作って持ち帰る体験'], ['A', 'ハサミを使わず、小さな子どもでも作れる'], ['B', '9:30〜16:00の間で好きな時間に参加できる'], ['B', '先着順（100名・250名）で、遅いと終わる'], ['A', '無料（駐車料は別）'], ['A', '事前予約は不要（当日受付）'], ['B', '公園で遊ぶついでに、短時間で記念品を作れる']),
     'strengths': ['無料で、5〜15分の短い体験', 'ハサミを使わず、小さな子どもでも作れる'], 'limitations': ['先着順で、数に限りがある', '駐車料や入園料は別に必要な場合がある'],
     'comparison': '総合B：無料の短時間の工作体験。先着順で、遅い時間は終わる場合がある。',
     'pf': 'pass', 'pos': ['official_date_confirmed']},
    {'id': 'verified-20261121-tachikawa-showakinen-sippofesta-20261205', 'week': '2026-12-05', 'ward': '立川市', 'page': 'showakinen_sippofesta_20261205.html',
     'name': 'Sippo Festa（しっぽフェスタ）2026 冬（国営昭和記念公園）', 'url': 'https://www.showakinen-koen.jp/event/76869/', 'date': '2026-12-05', 'end': '2026-12-06', 'period': '12/5(土)・6(日) 10:00〜16:00', 'time': '10:00〜16:00',
     'venue': '国営昭和記念公園 みどりの文化ゾーン ゆめひろば（無料エリア）（立川市緑町3173）', 'price': '無料（一部有料プログラムあり。駐車場料金は別）',
     'description': '「愛犬と一緒に遊ぶ・学ぶ・思い出を作る」総合ペットイベント。エクストリーム全国決勝大会やわんわんネームビンゴなどのプログラムと、犬用品の販売がある。雨天決行・荒天中止。',
     'cats': ['まつり・イベント', '自然・公園'], 'io': '屋外',
     'res': {'required': False, 'note': '予約の記載なし。'},
     'quotes': ['「愛犬と一緒に遊ぶ・学ぶ・思い出を作る」総合ペットイベントで', '12月5日（土）、6日（日）10：00～16：00', '場所みどりの文化ゾーンゆめひろば（無料エリア）', '参加費無料※一部有料のプログラムがあります。'],
     'overall': 'B', 'basis': 'all_ages', 'child': False,
     'reason': '犬と遊び・学ぶ屋外のペットイベント。無料エリアで開かれ、参加費は無料（一部有料プログラムあり）。犬を飼っていない子どもは見て楽しむ内容。',
     'axes': _ax(['B', '子ども向けではなく、どなたでも参加できるペットイベント'], ['B', '犬のプログラムを見たり、参加したりできる'], ['B', '年齢の限定はない'], ['A', '2日間、10:00〜16:00に好きな時間に行ける'], ['B', '屋外で、冬の寒さに注意'], ['A', '参加費は無料（一部有料、駐車場は別）'], ['A', '予約の記載なし'], ['B', '犬が好きな子どもと、公園で過ごせる']),
     'strengths': ['無料エリアで開かれ、参加費が無料', '2日間あり、好きな時間に行ける'], 'limitations': ['屋外で冬の寒さに注意', '子ども向けのプログラムとは限らない', '一部有料のプログラムがある'],
     'comparison': '総合B：犬好きの家族向けの無料の屋外イベント。子ども向けの内容とは限らない。',
     'pf': 'pass', 'pos': ['official_date_confirmed']},
    {'id': 'verified-20261121-tachikawa-showakinen-craft-oshogatsu-20261219', 'week': '2026-12-19', 'ward': '立川市', 'page': 'showakinen_craft_oshogatsu_20261219.html',
     'name': 'こどもの森クラフト教室 特別編「お正月かざり」（国営昭和記念公園）', 'url': 'https://www.showakinen-koen.jp/event/29722/', 'date': '2026-12-19', 'end': '2026-12-20', 'period': '12/19(土)・20(日)', 'time': '受付10:30〜11:30、13:00〜14:30',
     'venue': '国営昭和記念公園 こどもの森木工房（立川市緑町3173）', 'price': '500円（別途入園料）',
     'description': '園内の竹や松葉、ナンテンを使って、自分だけのお正月飾りを作る工作教室。当日受付で、先着順・入替制（一度に入れるのは9名）。制作は子どもが自分で行い、保護者は木工房の周りで待つ。',
     'cats': ['体験・ワークショップ', '工作'], 'io': '屋内',
     'res': {'required': False, 'note': '当日受付（先着順・入室定員9名・随時入替制）。事前予約は不要。'},
     'quotes': ['園内の竹や松葉、ナンテンを使って、すてきなお正月飾りを作ろう！', 'スケジュール12月19日（土）12月20日(日)', '参加費500円（入園料別）', '制作はお子様ご自身で行っていただきますので、保護者の方は木工房周辺でお待ちください。'],
     'overall': 'B', 'basis': 'child_program', 'child': True,
     'reason': '子どもが自分でお正月飾りを作る工作教室。当日受付で、500円（入園料別）。対象年齢の記載はなく、保護者は木工房の周りで待つ形。',
     'axes': _ax(['B', '制作は子ども自身が行う内容で、対象年齢の記載はない'], ['A', '竹や松葉でお正月飾りを作る'], ['B', '対象年齢の記載がなく、年齢は目安がない'], ['B', '受付時間内に来れば参加できる（入替制）'], ['B', '先着順で、混む日は待つことがある'], ['B', '500円（入園料は別）'], ['A', '事前予約は不要（当日受付）'], ['A', '季節の飾りを自分で作れる']),
     'strengths': ['お正月の飾りを自分で作れて、予約がいらない', '参加費は500円'], 'limitations': ['対象年齢の記載がない', '入園料が別に必要', '先着順・入替制で、混む日は待つことがある'],
     'comparison': '総合B：お正月飾りを作る当日受付の工作教室。対象年齢の記載がない点に注意。',
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
SHARDS = {w: f'{w}-events-lead33-20261121.json' for w in ('2026-11-21', '2026-11-28', '2026-12-05', '2026-12-12', '2026-12-19', '2026-12-26')}
HELD = {
    'tachikawa-showakinen-projectwild-20261212': '立川市 昭和記念公園 プロジェクトワイルド自然発見塾（12/12）：事前申込制（定員12名）で、申込受付の状況が確認できず保留。',
    'tachikawa-showakinen-birdcall-20261220': '立川市 昭和記念公園 バードコール作りと野鳥観察（12/20）：事前申込制（定員20名）で、申込受付の状況が確認できず保留。',
    'remaining-parks': '多摩動物公園・東京ドームシティ・WBスタジオツアーの個別ページは、公式根拠（日付・場所・費用）を引き続き調査中。',
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
        run['lead33_addition_20261121'] = {
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
        'run_id': 'lead33-addition-20261121', 'run_type': 'manual_verified_lead33_addition',
        'status': 'verified_subset_publication', 'as_of_jst': '2026-11-21', 'executed_at': m['generated'],
        'base_data_production_sha': BASE, 'target_weekends': sorted(derived),
        'prior_active_week_records': 756, 'candidate_active_week_records': 760, 'added_weekly_records': 4,
        'new_event_ids': NEW_IDS, 'held_not_published': sorted(HELD),
        'existing_event_records_physically_deleted': 0, 'image_only_updates': 0,
        'source_failures_remain_unverified': True, 'global_source_audit_complete': False,
        'full_23_ward_25_source_audit_complete': False,
        'note': '多摩拡張の第9弾として、立川市の国営昭和記念公園（クラフト教室2件・GREEN×EXPO・しっぽフェスタ）を公式サイトの個別ページで確認して追加。'
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
