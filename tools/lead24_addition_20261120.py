#!/usr/bin/env python3
"""1 weekly record (12/26 Nerima forest festival) from the committed official Nerima page (2026-11-20).

Raw official pages are committed unchanged under research/2026-11-20-thin-wards/pages/
(fetched by read-only workflows, HTTP 200). Quotes must occur verbatim in those pages.
The gate validator re-derives every record from this module and requires exact equality.
"""
import argparse, hashlib, json, pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import suginami_addition_20261118 as S

BASE = '29e7e555c772ba2bc59ee42bd30a6f1de6d63c51'   # data-production after the Nerima duplicate removal (662 active week records)
CHECKED = '2026-11-20'
AXES = S.AXES
NOTE_AUDIT = '週別全源照合は未完（ためまっぷ403等）。この追加分は主催者公式の案内ページの確認に基づく。'
S.CHECKED = CHECKED


def _page_text(path):
    """Like suginami page_text, but falls back to the whole document when a page has no <h1>."""
    raw = pathlib.Path(path).read_text(encoding='utf-8', errors='ignore')
    i = raw.find('<h1')
    raw = raw[i:] if i >= 0 else raw
    raw = S.re.sub(r'<(script|style).*?</\1>', '', raw, flags=S.re.S)
    raw = S.re.sub(r'<br\s*/?>|</(p|li|tr|dt|dd|h\d|div|th|td)>', '\n', raw)
    return S.re.sub(r'\s+', '', S.html.unescape(S.re.sub(r'<[^>]+>', '', raw)))


SPECS_RAW = [{'id': 'verified-20261213-ariake-quest-3', 'week': '2026-12-12', 'ward': '江東区', 'page': 'ariake_quest_1213.html', 'name': '第3回 有明クエスト（有明親水海浜公園）', 'url': 'https://www.tptc.co.jp/park/event/detail/2497', 'date': '2026-12-13', 'period': '12/13(日)', 'time': '9:00〜15:30（新規受付は14:00まで）', 'venue': '有明親水海浜公園・有明テニスの森駅（江東区有明）', 'price': '無料', 'description': '公園内4か所と駅1か所に隠されたナゾを解いて回る謎解きラリー。自分のペースで参加でき、ゴールすると先着300名にお菓子がもらえる。事前申込は不要。', 'cats': ['謎解き', '公園', '体験'], 'io': '屋外', 'res': {'required': False, 'note': '事前申込不要。当日、記念広場中央の受付へ。'}, 'quotes': ['開催日時2026年12月13日（日）9:00～15:30', '参加費無料対象どなたでもご参', 'どなたでもご参加いただけます。小さなお子さまは保護者の方と一緒にご参加ください。', '事前申込不要。当日、受付へお越しください。', '先着300名ゴールした方にお菓子をプレゼント', '5つのナゾ園内4か所と駅1か所をめぐろう'], 'basis': 'all_ages', 'reason': '12/13開催。公園と駅に隠された5つのナゾを好きな順番で解くラリーで、小さな子どもは保護者と一緒に参加できる。無料で事前申込も不要。', 'axes': {'child_target': ['B', '小さな子どもも保護者と参加できる謎解きラリーだが、こども専用ではない'], 'interactivity': ['A', 'ナゾを解きながら園内を歩いて回る参加型'], 'age_fit': ['B', 'どなたでも参加でき、小さな子どもは保護者同伴'], 'stay_flexibility': ['A', '9:00〜14:00の受付で、自分のペースで回れる'], 'burden': ['B', '屋外のため雨天時は12/20に延期、その日も雨なら中止'], 'cost': ['A', '参加費無料'], 'reservation': ['A', '事前申込不要'], 'family_value': ['B', '家族で公園を歩きながら謎解きとお菓子を楽しめる']}, 'strengths': ['無料で事前申込不要', '自分のペースで参加できる'], 'limitations': ['雨天時は延期または中止', 'こども専用ではない'], 'comparison': '総合B：無料・予約不要で家族が気軽に参加できる謎解きラリーだが、こども専用ではなく雨天の影響を受ける。', 'pos': ['official_date_confirmed', 'child_activity_confirmed'], 'override': '', 'pf': 'pass', 'overall': 'B', 'child': True}, {'id': 'verified-20261220-jonanjima-skateboard-class', 'week': '2026-12-19', 'ward': '大田区', 'page': 'jonanjima_skateboard_1220.html', 'name': 'スケートボード教室 12月（城南島海浜公園）', 'url': 'https://tokyo-south-seaside-parks.com/event/%e3%82%b9%e3%82%b1%e3%83%bc%e3%83%88%e3%83%9c%e3%83%bc%e3%83%89%e6%95%99%e5%ae%a4%e3%80%8012%e6%9c%88', 'date': '2026-12-20', 'period': '12/20(日)', 'time': '13:00〜15:00', 'venue': '城南島海浜公園 アスファルト広場（初心者・中級クラス）', 'price': '初心者・中級クラス500円（上級クラス3,000円）', 'description': '日本スケートボード協会公認インストラクターが乗り方を教える教室。初めての人から参加でき、ヘルメット着用が必須で、道具のレンタルもある。事前予約制。', 'cats': ['スポーツ', 'スケートボード', '体験'], 'io': '屋外', 'res': {'required': True, 'note': '事前予約制（Webフォーム）。11/16から受付。'}, 'quotes': ['毎月第3日曜日（6月・11月を除く）13時～15時', 'スケートボードに初めて乗る方から、もっと楽しみたい方まで', '参加費：５００円（税・保険料込み、当日現金払い）', '事前予約制のスケートボード教室です。', 'ヘルメット（安全の為、着用必須）', '11月16日(月)より受付開始です。'], 'basis': 'unspecified', 'overall': 'C', 'override': '初心者向けのスポーツ教室で子どもも参加できる見込みだが、公式ページに子どもの対象年齢が明記されていないため、条件つきの総合Cとして掲載する。', 'reason': '12/20開催。公認インストラクターに教わる初心者・中級向けのスケートボード教室で、参加費は500円。ヘルメット着用が必須で、事前予約が必要。', 'axes': {'child_target': ['unknown', '子ども向けとは明記されていない'], 'interactivity': ['A', 'スケートボードに実際に乗って学ぶ'], 'age_fit': ['unknown', '対象年齢が明記されていない'], 'stay_flexibility': ['B', '13:00〜15:00の時間が決まっている'], 'burden': ['C', 'ヘルメット着用が必須で、道具の持参またはレンタルが必要'], 'cost': ['B', '初心者・中級クラスは500円、レンタルは別料金'], 'reservation': ['B', '事前予約制'], 'family_value': ['B', '初めてのスポーツ体験として参加できる']}, 'strengths': ['初めてでも参加できる', '公認インストラクターが指導'], 'limitations': ['対象年齢の記載がない', 'ヘルメット着用が必須で事前予約が必要'], 'comparison': '総合C：初心者向けで費用も手頃だが、子どもの対象年齢が明記されておらず、予約と装備が必要。', 'pos': ['official_date_confirmed', 'child_activity_confirmed'], 'pf': 'pass', 'child': True}]
RAW = SPECS_RAW
SPECS = []
for _r in RAW:
    _s = dict(_r)
    _s['categories'] = _s.pop('cats'); _s['indoor_outdoor'] = _s.pop('io'); _s['reservation'] = _s.pop('res')
    _s['child_activity'] = _s.pop('child'); _s['price_field'] = _s.pop('pf'); _s['positive'] = _s.pop('pos')
    SPECS.append(_s)
NEW_IDS = [s['id'] for s in SPECS]
SHARDS = {w: f'{w}-events-lead24-20261120.json' for w in ('2026-12-12', '2026-12-19')}
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
                    'description': f"主催者公式ページ（2026-11-20にHTTP200で取得、research/2026-11-20-thin-wards/pages/に不変保存）の本文引用。引用文字列だけのUTF-8 SHA-256。"})
    for x in spec.get('extra', []):
        t2 = _page_text(pathlib.Path(pages_dir) / x['page'])
        if S._strip(x['q']) not in t2:
            raise ValueError(f"{spec['id']}: calendar quote not found verbatim in the committed official calendar page: {x['q']}")
        out.append({'url': x['url'], 'quote': x['q'], 'checked_at': CHECKED,
                    'sha256': hashlib.sha256(x['q'].encode('utf-8')).hexdigest(),
                    'hash_scope': 'quoted_text_only_not_HTTP_response_hash',
                    'description': f"主催者公式ページ（2026-11-20にHTTP200で取得、research/2026-11-20-thin-wards/pages/に不変保存）の本文引用。"})
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
               'evidence': [{'url': s['url'], 'basis': '2026-11-20 official individual event page (HTTP200); 23 ward completeness not asserted'}],
               'override_reason': s.get('override', '')}
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
                    row['note'] += f' 2026-11-20 公式個別ページ確認済み{k}件を非破壊追加。'
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
        run['lead24_addition_20261120'] = {
            'kind': 'individually_verified_official_events_from_lead_triage', 'added_ids': [i[0]['id'] for i in items],
            'held_not_published': sorted(HELD), 'pages_committed_at': 'research/2026-11-20-thin-wards/pages/',
            'base_data_production_sha': BASE, 'global_source_audit_complete': False}
        S.jdump(d / f'{week}-run.json', run)
        for x in m['weekends']:
            if x['sat'] == week:
                x['count'] += n
    m['generated'] = '2026-11-20T19:00:00+09:00'
    S.jdump(d / 'manifest.json', m)
    h = S.jload(d / 'update_history.json')
    h['history'].append({
        'run_id': 'lead24-addition-20261120', 'run_type': 'manual_verified_lead24_addition',
        'status': 'verified_subset_publication', 'as_of_jst': '2026-11-20', 'executed_at': m['generated'],
        'base_data_production_sha': BASE, 'target_weekends': sorted(derived),
        'prior_active_week_records': 662, 'candidate_active_week_records': 664, 'added_weekly_records': 2,
        'new_event_ids': NEW_IDS, 'held_not_published': sorted(HELD),
        'existing_event_records_physically_deleted': 0, 'image_only_updates': 0,
        'source_failures_remain_unverified': True, 'global_source_audit_complete': False,
        'full_23_ward_25_source_audit_complete': False,
        'note': '東京都の公園管理者・東京港埠頭・海上公園南部みらいパートナーズの公式ページで日付・時間・会場・条件を確認できた2件のみ追加。',
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
