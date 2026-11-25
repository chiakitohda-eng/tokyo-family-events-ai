#!/usr/bin/env python3
"""2 weekly records (Komae city x2) from committed official pages (2026-11-21).

Raw official pages are committed unchanged under research/2026-11-20-thin-wards/pages/. The gate validator re-derives every record and requires exact equality.
"""
import argparse, hashlib, json, pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import suginami_addition_20261118 as S

BASE = 'cac356b40ea8d6229a1305859b3a1507151360c1'   # data-production after lead39 (781 active week records)
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
    {'id': 'verified-20261121-komae-mirai-terrace-festival-2026', 'week': '2026-11-21', 'ward': '狛江市', 'page': 'komae_mirai_terrace_fes_2026.html',
     'name': 'こまえみらいテラスフェスティバル（開館1周年）', 'url': 'https://www.komae.ed.jp/events/index.cfm/detail.10.11343.html', 'date': '2026-11-21', 'end': '2026-11-22',
     'period': '11/21(土)・11/22(日)（開催中）', 'time': '11/21 9:30〜16:00・11/22 9:30〜17:00',
     'venue': 'こまえみらいテラス（中央公民館・市民活動支援センター・こまえみライブラリーkids）・しみんひろば（狛江市和泉本町1-1-5）', 'price': '入場無料（一部のワークショップ・体験は参加費が必要）',
     'description': '開館1周年を記念した2日間のイベント。11/21は音楽・人形劇・幼児ダンスのステージや、クリスマスリースづくり・木の実を使った工作などのものづくり体験、11/22は防災をテーマにした展示・体験（消防車の展示、初期消火体験、パラコードのブレスレットづくりなど）。会場をめぐるスタンプラリーもある（先着300名にノベルティ）。',
     'categories': ['まつり・イベント', '体験・ワークショップ'], 'indoor_outdoor': '屋内・屋外',
     'reservation': {'required': False, 'note': '事前申込が必要な企画がある（詳細はパンフレット）。申込不要で見られる展示・ステージもある。'},
     'quotes': ['11月21日（土）午前9時30分～午後4時', '11月22日（日）午前9時30分～午後5時', '子どもから大人まで楽しめる', '木の実を使った工作やポケモンカード教室', '入場は無料です（一部のワークショップ・体験には参加費が必要です）。', '事前申込が必要な企画があります。'],
     'overall': 'B', 'basis': 'all_ages', 'child_activity': True,
     'reason': '子どもから大人まで楽しめる、図書館・公民館の合同イベント。人形劇やものづくり体験、消防車の展示や初期消火体験などがあり、入場は無料。一部の体験は参加費や事前申込が必要。',
     'axes': {
         'child_target': ('B', '子どもから大人までが対象で、子ども向けの体験も多い'),
         'interactivity': ('A', 'ものづくり・工作・初期消火体験などの体験が多い'),
         'age_fit': ('B', '年齢の限定はない'),
         'stay_flexibility': ('A', '開催時間内で自由に出入りして回れる'),
         'burden': ('B', '会場は1か所にまとまっているが、混雑する可能性がある'),
         'cost': ('A', '入場は無料（一部の体験のみ参加費）'),
         'reservation': ('B', '事前申込が必要な企画が一部ある'),
         'family_value': ('B', '工作や防災体験を親子で楽しめる'),
     },
     'strengths': ['入場無料で、工作や防災体験が多い', '2日間のうち好きな時間に回れる'], 'limitations': ['一部の体験は参加費や事前申込が必要', '11/22は防災が中心で、子ども向けの内容は一部'],
     'comparison': '総合B：入場無料で体験が多い地域のイベント。一部は申込や参加費が必要。',
     'status': 'verified', 'price_field': 'pass', 'positive': ['official_date_confirmed']},
    {'id': 'verified-20261129-komae-iwato-ohanashikai-3sai-2026', 'week': '2026-11-28', 'ward': '狛江市', 'page': 'komae_iwato_ohanashi_20261129.html',
     'name': '親子で楽しむおはなし会（3歳〜小学校低学年と保護者）（岩戸地域センター）', 'url': 'https://www.city.komae.tokyo.jp/events/index.cfm/detail.4.146670.html', 'date': '2026-11-29', 'end': '2026-11-29',
     'period': '11/29(日)', 'time': '11:00〜12:00',
     'venue': '岩戸地域センター（狛江市）', 'price': '公式ページに金額の明記なし（申込時に要確認）',
     'description': '大型絵本の読み聞かせや紙芝居、工作を楽しむ、3歳から小学校低学年の子どもと保護者のためのおはなし会。先着20組で、要予約。',
     'categories': ['体験・ワークショップ', '親子・地域体験'], 'indoor_outdoor': '屋内',
     'reservation': {'required': True, 'note': '要予約・先着20組。専用フォームまたは電話（岩戸地域センター 03-3488-7040）で申し込む。'},
     'quotes': ['2026年11月29日日曜日', '11月29日(日曜日)午前11時～正午', '3歳～小学校低学年とその保護者', '定員先着20組（要予約）内容大型絵本読み聞かせや紙芝居、工作'],
     'overall': 'B', 'basis': 'child_program', 'child_activity': True,
     'reason': '3歳から小学校低学年の子どもと保護者のためのおはなし会。大型絵本や紙芝居、工作があり、対象年齢がはっきりしている。要予約で先着20組、料金は公式ページに金額の記載がない。',
     'axes': {
         'child_target': ('A', '3歳〜小学校低学年と保護者のための催し'),
         'interactivity': ('A', '大型絵本・紙芝居の読み聞かせと工作'),
         'age_fit': ('A', '対象年齢がはっきりしている'),
         'stay_flexibility': ('C', '11:00〜12:00の1時間'),
         'burden': ('B', '地域センターの屋内で、1時間と短い'),
         'cost': ('unknown', '公式ページに金額の記載がない'),
         'reservation': ('C', '要予約で先着20組'),
         'family_value': ('A', '身近な地域センターで、親子で絵本と工作を楽しめる'),
     },
     'strengths': ['3歳〜小学校低学年が楽しめる', '絵本と工作を親子で体験できる'], 'limitations': ['要予約で先着20組', '料金は公式ページに記載がなく、申込時の確認が必要'],
     'comparison': '総合B：対象がはっきりした親子向けの催し。予約と定員があり、料金は要確認。',
     'status': 'verified', 'price_field': 'unknown', 'positive': ['official_date_confirmed']},
]
SPECS = [dict(_r) for _r in SPECS_RAW]
NEW_IDS = [s['id'] for s in SPECS]
SHARDS = {w: f'{w}-events-lead40-20261121.json' for w in ('2026-11-21', '2026-11-28', '2026-12-05', '2026-12-12', '2026-12-19', '2026-12-26')}
HELD = {
    'komae-jikken-kyoshitsu-20261128': '狛江市 子どもの実験教室（11/28）：申込が11/12で締切済み・抽選のため対象外。',
    'komae-giants-hometown-fes-20261205': '狛江市ページのジャイアンツホームタウンフェス（12/5）：稲城市分としてlead31で登録済みのため追加せず。',
    'urayasu-tokyo-disney-resort': '浦安市 東京ディズニーリゾート：公式サイトを取得できず保留。',
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
        run['lead40_addition_20261121'] = {
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
        'run_id': 'lead40-addition-20261121', 'run_type': 'manual_verified_lead40_addition',
        'status': 'verified_subset_publication', 'as_of_jst': '2026-11-21', 'executed_at': m['generated'],
        'base_data_production_sha': BASE, 'target_weekends': sorted(derived),
        'prior_active_week_records': 781, 'candidate_active_week_records': 783, 'added_weekly_records': 2,
        'new_event_ids': NEW_IDS, 'held_not_published': sorted(HELD),
        'existing_event_records_physically_deleted': 0, 'image_only_updates': 0,
        'source_failures_remain_unverified': True, 'global_source_audit_complete': False,
        'full_23_ward_25_source_audit_complete': False,
        'note': '狛江市の公式ページから、こまえみらいテラスフェスティバル（11/21〜22）と岩戸地域センターの親子おはなし会（11/29）を個別に確認して追加。おはなし会の料金は公式ページに金額の記載がないため「料金要確認」で掲載。',
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
