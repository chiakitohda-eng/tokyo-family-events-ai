#!/usr/bin/env python3
"""2 weekly records (Theme parks: Sumida x1, Minato x1) from committed official pages (2026-11-21).

Raw official pages are committed unchanged under research/2026-11-20-thin-wards/pages/. The gate validator re-derives every record and requires exact equality.
"""
import argparse, hashlib, json, pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import suginami_addition_20261118 as S

BASE = '3e19e5e5c4998264bdbc26e1d2e3eac77d2ab4b1'   # data-production after lead27 (764 active week records)
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
    {'id': 'verified-20261121-sumida-solamachi-xmasmarket-2026', 'week': '2026-11-21', 'ward': '墨田区', 'page': 'solamachi_xmasmarket_2026.html',
     'name': '絵本の中のクリスマスマーケットin東京スカイツリータウン2026', 'url': 'https://www.tokyo-solamachi.jp/event/20261105_xmasmarket/', 'date': '2026-11-21', 'end': '2026-12-25', 'period': '11/5(木)〜12/25(金)（開催中）', 'time': '11:00〜22:00（L.O.21:00）',
     'venue': '東京スカイツリータウン 4F スカイアリーナ（墨田区押上1-1-2）', 'price': '参加費は無料（飲食・物販は有料）',
     'description': '東京スカイツリータウンの冬の風物詩、クリスマスマーケット。ヨーロッパ式の木の小屋（ヒュッテ）15棟が並び、雪だるま・サンタ・トナカイをモチーフにしたクリスマスグルメや、会場限定のマグカップなどを楽しめる。飲食エリアのため、補助犬を除くペットは同伴できない。',
     'cats': ['まつり・イベント'], 'io': '屋内・屋外',
     'res': {'required': False, 'note': '予約の記載なし。参加費は無料。'},
     'quotes': ['期間：2026年11月5日～2026年12月25日', '会場には15棟のヨーロッパ式ヒュッテ（木の小屋）が並びます。', '開催時間11:00～22:00（L.O.21:00）場所4Fスカイアリーナ', '4Fスカイアリーナフロアガイド参加費無料'],
     'overall': 'B', 'basis': 'all_ages', 'child': False,
     'reason': 'ヨーロッパ風の小屋が並ぶクリスマスマーケット。参加費は無料で、クリスマスらしいグルメと雰囲気を家族で楽しめる。飲食や買い物は別に費用がかかる。',
     'axes': _ax(['B', '対象はどなたでも。絵本がテーマの家族向けの会場'], ['B', '見て歩いて、飲食を楽しむ内容が中心'], ['B', '年齢の限定はない'], ['A', '約1か月半と長く、11:00〜22:00で好きな時間に行ける'], ['B', '混む日があり、飲食エリアはペット同伴不可'], ['A', '参加費は無料（飲食・物販は別）'], ['A', '予約の記載なし'], ['A', '商業施設の中で、クリスマスの雰囲気を楽しめる']),
     'strengths': ['参加費が無料で、期間が長い', '雪だるまやサンタをモチーフにした、見た目も楽しいメニューがある'], 'limitations': ['飲食や買い物は別に費用がかかる', '混む日があり、飲食エリアはペット同伴不可'],
     'comparison': '総合B：無料で入れる、家族向けのクリスマスマーケット。飲食や買い物は別料金。',
     'pf': 'pass', 'pos': ['official_date_confirmed']},
    {'id': 'verified-20261121-minato-joypolis-digitareal-illumination-2026', 'week': '2026-11-21', 'ward': '港区', 'page': 'joypolis_event_list_2026.html',
     'name': 'デジタリアルイルミネーション2026（東京ジョイポリス）', 'url': 'https://tokyo-joypolis.com/event/index.html', 'date': '2026-11-21', 'end': '2027-02-11', 'period': '11/20(土)〜2027/2/11(木・祝)（開催中）', 'time': '東京ジョイポリスの営業時間内（営業時間は公式サイトで確認）',
     'venue': '東京ジョイポリス（港区台場1-6-1 デックス東京ビーチ内）館内', 'price': '入場券は大人（18歳以上）1,700円・小中高生1,400円。未就学児は入場無料。アトラクションは別料金（パスポートは大人6,000円・小中高生5,000円）',
     'description': 'お台場の屋内型アミューズメント施設「東京ジョイポリス」の館内を飾る、期間限定のイルミネーション。館内で楽しめる。アトラクションはパスポートか回数券が別に必要。',
     'cats': ['まつり・イベント', 'テーマパーク・遊園地'], 'io': '屋内',
     'res': {'required': False, 'note': '予約の記載なし。入場券（またはパスポート）の購入が必要。'},
     'quotes': ['寒い冬は暖かい館内でイルミネーション☆', '開催期間：2026年11月20日（土）～2027年2月11日（木・祝）', '煌びやかに彩られた館内で、期間限定のイベントを楽しもう♪'],
     'extra': [{'page': 'joypolis_ticket_2026.html', 'url': 'https://tokyo-joypolis.com/ticket/index.html', 'q': '入場券大人（18歳以上）1,700円小・中・高生1,400円'},
               {'page': 'joypolis_ticket_2026.html', 'url': 'https://tokyo-joypolis.com/ticket/index.html', 'q': '未就学児身長110cm未満のかたアトラクションのご利用には保護者の同伴が必要です。'}],
     'overall': 'B', 'basis': 'all_ages', 'child': False,
     'reason': '屋内のアミューズメント施設で楽しむ冬のイルミネーション。入場料が必要で、アトラクションは別料金。未就学児は入場無料。',
     'axes': _ax(['B', '対象はどなたでも。アトラクション中心の施設'], ['B', 'イルミネーションに加え、アトラクションも利用できる'], ['B', '未就学児は入場無料だが、アトラクションには身長制限がある'], ['A', '約2.5か月と長く、好きな日に行ける'], ['A', '屋内で、冬の寒さや雨を気にせず過ごせる'], ['C', '入場券（小中高生1,400円〜）に加え、アトラクションは別料金'], ['A', '予約の記載なし'], ['B', '屋内でイルミネーションとアトラクションを一緒に楽しめる']),
     'strengths': ['屋内で、寒さや雨を気にせず楽しめる', '未就学児は入場無料'], 'limitations': ['入場料に加えてアトラクションは別料金で、費用がかさむ', 'アトラクションには身長制限がある'],
     'comparison': '総合B：屋内で天候に左右されないが、入場料とアトラクション料金がかかる。',
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
SHARDS = {w: f'{w}-events-lead35-20261121.json' for w in ('2026-11-21', '2026-11-28', '2026-12-05', '2026-12-12', '2026-12-19', '2026-12-26')}
HELD = {
    'sumida-skytree-dream-christmas-2026': '墨田区 東京スカイツリータウン ドリームクリスマス2026（11/5〜12/25）：公式ページに参加費の記載がなく保留（クリスマスマーケットは別に登録）。',
    'minato-joypolis-collab-events': '港区 東京ジョイポリスのホロライブ・KING OF PRISM・アイドルマスターSideMのコラボ：子ども向けではなく、保留。',
    'taito-hanayashiki-events': '台東区 浅草花やしき：イベントカレンダーが取得できた本文に含まれず、保留。',
    'toshima-sunshine-city': '豊島区 サンシャインシティ：イベント一覧が取得できた本文に含まれず、保留。',
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
            is_ward = ward.endswith('区')
            row = next((r for r in (cov['wards'] if is_ward else munis) if r['ward'] == ward), None)
            if row is None and is_ward:
                raise SystemExit(f'ward row missing: {ward}')
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
        run['lead35_addition_20261121'] = {
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
        'run_id': 'lead35-addition-20261121', 'run_type': 'manual_verified_lead35_addition',
        'status': 'verified_subset_publication', 'as_of_jst': '2026-11-21', 'executed_at': m['generated'],
        'base_data_production_sha': BASE, 'target_weekends': sorted(derived),
        'prior_active_week_records': 764, 'candidate_active_week_records': 766, 'added_weekly_records': 2,
        'new_event_ids': NEW_IDS, 'held_not_published': sorted(HELD),
        'existing_event_records_physically_deleted': 0, 'image_only_updates': 0,
        'source_failures_remain_unverified': True, 'global_source_audit_complete': False,
        'full_23_ward_25_source_audit_complete': False,
        'note': 'テーマパーク・大型施設の第2弾として、東京スカイツリータウンのクリスマスマーケットと東京ジョイポリスのイルミネーションを公式サイトの個別ページと料金ページで確認して追加。'
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
