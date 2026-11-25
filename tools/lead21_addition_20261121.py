#!/usr/bin/env python3
"""2 weekly records (TOKYO Shukakusai 2026, Chiyoda, 11/21 and 11/22) from the committed official site and Tokyo Metropolitan Government press release (2026-11-21).

Raw official pages are committed unchanged under research/2026-11-20-thin-wards/pages/
(fetched by read-only workflows, HTTP 200). Quotes must occur verbatim in those pages.
The gate validator re-derives every record from this module and requires exact equality.
"""
import argparse, hashlib, json, pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import suginami_addition_20261118 as S

BASE = '723c1ddcd26620a1f8b7297a5d1148a8af4bfb47'   # data-production after lead20 (711 active week records)
CHECKED = '2026-11-21'
AXES = S.AXES
NOTE_AUDIT = '週別全源照合は未完（ためまっぷ403等）。この2件は公式特設サイトと東京都の報道発表の確認に基づく。'
S.CHECKED = CHECKED


def _page_text(path):
    """Like suginami page_text, but falls back to the whole document when a page has no early <h1>."""
    raw = pathlib.Path(path).read_text(encoding='utf-8', errors='ignore')
    i = raw.find('<h1')
    raw = raw[i:] if 0 <= i < 20000 else raw   # SPA pages (event site) put the only <h1> after the body; use the whole document
    raw = S.re.sub(r'<(script|style).*?</\1>', '', raw, flags=S.re.S)
    raw = S.re.sub(r'<br\s*/?>|</(p|li|tr|dt|dd|h\d|div|th|td)>', '\n', raw)
    return S.re.sub(r'\s+', '', S.html.unescape(S.re.sub(r'<[^>]+>', '', raw)))


_SITE = 'https://tokyo-syuukaku-sai.jp/'
_PRESS = 'https://www.metro.tokyo.lg.jp/information/press/2026/08/2026082612'
_VENUE = '東京国際フォーラム 地上広場・ロビーギャラリー（東京都千代田区丸の内3丁目5番1号）'


def _day(date, period, md, time, tq, ws_quotes, ws_names, ws_tag):
    return {'id': f'verified-{date.replace("-", "")}-chiyoda-tokyo-shukakusai', 'week': '2026-11-21', 'ward': '千代田区',
        'page': 'tokyo_syuukakusai_site_2026.html',
        'name': 'TOKYO周穫祭2026（東京国際フォーラム）', 'url': _SITE, 'date': date, 'period': period, 'time': time,
        'venue': _VENUE, 'price': 'ワークショップは参加費無料（公式サイト）。入場料の記載なし',
        'image': 'https://tokyo-syuukaku-sai.jp/assets/img/ogp/2026/ja.png',
        'description': f'東京都と東京観光財団が都内の観光協会等と開く、観光とグルメのイベント。特産品・ご当地グルメ、360度VR体験、足湯、職人の実演、スタンプラリーのほか、{md}は{ws_names}の親子でも楽しめるワークショップ（参加費無料、会場で抽選券を受け取り抽選）がある。',
        'cats': ['まつり・イベント', '体験・ワークショップ'], 'io': '屋内・屋外',
        'res': {'required': None, 'note': '入場の事前申込の記載なし。ワークショップは会場で抽選券を受け取り1日3回の抽選に応募（9歳以下は保護者1名と一緒に参加、1組1回まで）。'},
        'quotes': ['1名につき保護者1名と一緒にご参加ください。', '抽選券の配布・抽選は1日3回、時間を分けて行います。'] + ws_quotes,
        'extra': [{'page': 'tokyo_syuukakusai_metro_press_20260826.html', 'url': _PRESS, 'q': tq},
                  {'page': 'tokyo_syuukakusai_metro_press_20260826.html', 'url': _PRESS, 'q': '東京国際フォーラム　地上広場・ロビーギャラリー（東京都千代田区丸の内3丁目5番1号）'},
                  {'page': 'tokyo_syuukakusai_metro_press_20260826.html', 'url': _PRESS, 'q': '親子でも楽しめるワークショップ（工芸品の製作体験等）'}],
        'overall': 'B', 'basis': 'all_ages', 'child': True,
        'reason': f'公式サイトと東京都の報道発表に親子でも楽しめるワークショップがあると記載があり、{md}は{ws_names}を体験できる。',
        'axes': {'child_target': ['B', '東京都の報道発表に「親子でも楽しめるワークショップ」とあるが、全体は幅広い年代向けの観光イベント'], 'interactivity': ['A', 'ワークショップ、足湯、VR体験、溶岩ウォーク、スタンプラリーなど体験が多い'],
                 'age_fit': ['B', '9歳以下は保護者1名と参加と明記。ワークショップはお子さまから大人まで'], 'stay_flexibility': ['A', '終日の開催で好きなブースを選べる'],
                 'burden': ['B', 'ワークショップは抽選で、当選しても集合時間に遅れると参加できない'], 'cost': ['unknown', 'ワークショップは参加費無料だが、入場料の記載がない'],
                 'reservation': ['unknown', '入場の事前申込の記載がなく、ワークショップは会場での抽選'], 'family_value': ['B', '工芸品づくりなどの体験と飲食・実演を親子で一か所で楽しめる']},
        'strengths': ['親子でも楽しめるワークショップが無料', 'VR・足湯・実演・スタンプラリーなど体験が多い'], 'limitations': ['ワークショップは抽選で当たらない場合がある', '入場料や各ブースの費用が公式ページに明記されていない'],
        'comparison': f'総合B：{md}は東京国際フォーラムで{time}に体験を選べ、{ws_tag}の無料ワークショップがあるが、抽選制で、入場料の記載がない。',
        'pf': 'unknown', 'pos': ['official_date_confirmed', 'child_activity_confirmed']}


SPECS_RAW = [
    _day('2026-11-21', '11/21(土)', '11/21', '10:00〜18:00', '令和8年11月21日（土曜日）10時00分～18時00分',
         ['高級木材でネームプレートをつくろう', '東京の木で作る、ヒノキのお箸作り'], 'ネームプレート作り・ヒノキのお箸作り・ストラップ作り', 'ネームプレート作りなど3種'),
    _day('2026-11-22', '11/22(日)', '11/22', '10:00〜17:00', '令和8年11月22日（日曜日）10時00分～17時00分',
         ['食品サンプルづくり「かき氷」', '着物のはぎれでつくる花の小物入れ'], '食品サンプル作り・花の小物入れ作り・黒曜石キャンドル作り', '食品サンプル作りなど3種'),
]
RAW = SPECS_RAW
SPECS = []
for _r in RAW:
    _s = dict(_r)
    _s['categories'] = _s.pop('cats'); _s['indoor_outdoor'] = _s.pop('io'); _s['reservation'] = _s.pop('res')
    _s['child_activity'] = _s.pop('child'); _s['price_field'] = _s.pop('pf'); _s['positive'] = _s.pop('pos')
    SPECS.append(_s)
NEW_IDS = [s['id'] for s in SPECS]
SHARDS = {w: f'{w}-events-lead21-20261121.json' for w in ('2026-11-21', '2026-11-28', '2026-12-05', '2026-12-12', '2026-12-19', '2026-12-26')}
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
        run['lead21_addition_20261121'] = {
            'kind': 'individually_verified_official_events_from_lead_triage', 'added_ids': [i[0]['id'] for i in items],
            'held_not_published': sorted(HELD), 'pages_committed_at': 'research/2026-11-20-thin-wards/pages/',
            'base_data_production_sha': BASE, 'global_source_audit_complete': False}
        S.jdump(d / f'{week}-run.json', run)
        for x in m['weekends']:
            if x['sat'] == week:
                x['count'] += n
    m['generated'] = '2026-11-21T13:00:00+09:00'
    S.jdump(d / 'manifest.json', m)
    h = S.jload(d / 'update_history.json')
    h['history'].append({
        'run_id': 'lead21-addition-20261121', 'run_type': 'manual_verified_lead21_addition',
        'status': 'verified_subset_publication', 'as_of_jst': '2026-11-21', 'executed_at': m['generated'],
        'base_data_production_sha': BASE, 'target_weekends': sorted(derived),
        'prior_active_week_records': 711, 'candidate_active_week_records': 713, 'added_weekly_records': 2,
        'new_event_ids': NEW_IDS, 'held_not_published': sorted(HELD),
        'existing_event_records_physically_deleted': 0, 'image_only_updates': 0,
        'source_failures_remain_unverified': True, 'global_source_audit_complete': False,
        'full_23_ward_25_source_audit_complete': False,
        'note': 'TOKYO周穫祭2026（東京都・東京観光財団主催、千代田区の東京国際フォーラム）を、公式特設サイトと東京都の報道発表で確認し、11/21週の2件（11/21・11/22）を追加。',
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
