#!/usr/bin/env python3
"""1 weekly record (12/26 Nerima forest festival) from the committed official Nerima page (2026-11-20).

Raw official pages are committed unchanged under research/2026-11-20-thin-wards/pages/
(fetched by read-only workflows, HTTP 200). Quotes must occur verbatim in those pages.
The gate validator re-derives every record from this module and requires exact equality.
"""
import argparse, hashlib, json, pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import suginami_addition_20261118 as S

BASE = '5e2b515a44a3333ecccfbac3551d89d921955838'   # data-production after the Nerima duplicate removal (684 active week records)
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


SPECS_RAW = [{'id': 'verified-20261122-tohaku-nurie', 'week': '2026-11-21', 'ward': '台東区', 'page': 'tohaku_nurie_1122.html', 'name': 'キッズぬりえ（東京国立博物館）', 'url': 'https://www.tnm.jp/modules/r_event/index.php?controller=dtl&cid=15&id=11808', 'date': '2026-11-22', 'period': '11/22(日)', 'time': '10:00〜16:00（随時参加可、最終受付15:45）', 'venue': '東京国立博物館 平成館 ファミリースペース（台東区上野公園13-9）', 'price': '参加費無料', 'description': 'ファミリースペースで休憩しながら、東博オリジナルのぬりえを楽しむ。11月は《犬型埴輪》《埴輪 踊る人々》のぬりえ。 毎月第4日曜日のトーハクプチキッズデーの催しで、当日受付。', 'cats': ['博物館', '工作', '体験'], 'io': '屋内', 'res': {'required': False, 'note': '当日受付。随時参加できる。'}, 'quotes': ['トーハクプチキッズデー（毎月第4日曜日、12月20日）', '日程2026年11月22日（日）', '参加費無料〒110-8712', '会場平成館-ファミリースペース', 'ファミリースペースで休憩しながら、東博オリジナルのぬりえを楽しんでみませんか。'], 'basis': 'child_program', 'reason': '11/22開催。トーハクプチキッズデーの催し「キッズぬりえ」で、参加費は無料。当日受付で随時参加できる。', 'axes': {'child_target': ['A', '子ども向けの「プチキッズデー」の催しとして実施される'], 'interactivity': ['B', 'ぬりえを楽しむ内容'], 'age_fit': ['A', '幼児から小学生まで楽しめる内容'], 'stay_flexibility': ['A', '当日、随時参加できる'], 'burden': ['A', '当日受付で、予約が不要'], 'cost': ['A', '参加費無料'], 'reservation': ['A', '予約不要の当日受付'], 'family_value': ['A', '親子でぬりえを楽しみながら休憩できる']}, 'strengths': ['予約不要で随時参加できる', '子ども向けのプチキッズデーの催し'], 'limitations': ['資料や席に限りがある', '毎月第4日曜日の催し'], 'comparison': '総合B（キッズぬりえ）：予約不要で随時参加できる子ども向けプログラムだが、席や材料に限りがある。', 'pos': ['official_date_confirmed', 'child_activity_confirmed'], 'override': '', 'pf': 'pass', 'overall': 'B', 'child': True}, {'id': 'verified-20261122-tohaku-canbadge', 'week': '2026-11-21', 'ward': '台東区', 'page': 'tohaku_canbadge_1122.html', 'name': 'プチキッズデー 缶バッジづくり（東京国立博物館）', 'url': 'https://www.tnm.jp/modules/r_event/index.php?controller=dtl&cid=15&id=11833', 'date': '2026-11-22', 'period': '11/22(日)', 'time': '10:00〜12:00、13:00〜16:00（随時参加可、最終受付15:45）', 'venue': '東京国立博物館 平成館 ファミリースペース（台東区上野公園13-9）', 'price': '', 'description': '博物館の作品やイラスト、千代紙などから1枚選んで、オリジナルの缶バッジを作る。自分で絵を描くこともできる。 毎月第4日曜日のトーハクプチキッズデーの催しで、当日受付。', 'cats': ['博物館', '工作', '体験'], 'io': '屋内', 'res': {'required': False, 'note': '当日受付。随時参加できる。'}, 'quotes': ['トーハクプチキッズデー（毎月第4日曜日、12月20日）', '日程2026年11月22日（日）', '会場平成館-ファミリースペース', '東京国立博物館の作品やイラスト、千代紙などから1枚選んで、オリジナルの缶バッジを作れます。'], 'basis': 'child_program', 'reason': '11/22開催。トーハクプチキッズデーの催し「プチキッズデー 缶バッジづくり」。当日受付で随時参加できる。', 'axes': {'child_target': ['A', '子ども向けの「プチキッズデー」の催しとして実施される'], 'interactivity': ['A', 'ぬりえや工作、探検に参加できる'], 'age_fit': ['A', '幼児から小学生まで楽しめる内容'], 'stay_flexibility': ['A', '当日、随時参加できる'], 'burden': ['A', '当日受付で、予約が不要'], 'cost': ['unknown', 'このページに参加費の記載がない'], 'reservation': ['A', '予約不要の当日受付'], 'family_value': ['A', '缶バッジを作って持ち帰れる']}, 'strengths': ['予約不要で随時参加できる', '子ども向けのプチキッズデーの催し'], 'limitations': ['資料や席に限りがある', '毎月第4日曜日の催し'], 'comparison': '総合B（プチキッズデー 缶バッジづくり）：予約不要で随時参加できる子ども向けプログラムだが、席や材料に限りがある。', 'pos': ['official_date_confirmed', 'child_activity_confirmed'], 'override': '', 'pf': 'pass', 'overall': 'B', 'child': True}, {'id': 'verified-20261122-tohaku-papercraft', 'week': '2026-11-21', 'ward': '台東区', 'page': 'tohaku_papercraft_1122.html', 'name': 'ペーパークラフト かさねてつくるおひめさま（東京国立博物館）', 'url': 'https://www.tnm.jp/modules/r_event/index.php?controller=dtl&cid=15&id=11834', 'date': '2026-11-22', 'period': '11/22(日)', 'time': '10:00〜16:00（随時参加可、最終受付15:45）', 'venue': '東京国立博物館 平成館 ファミリースペース（台東区上野公園13-9）', 'price': '', 'description': 'ぬりえと工作で、きものを着たおひめさまを作る。作品は屏風やくらしの道具と一緒に飾れる。 毎月第4日曜日のトーハクプチキッズデーの催しで、当日受付。', 'cats': ['博物館', '工作', '体験'], 'io': '屋内', 'res': {'required': False, 'note': '当日受付。随時参加できる。'}, 'quotes': ['トーハクプチキッズデー（毎月第4日曜日、12月20日）', '日程2026年11月22日（日）', '会場平成館-ファミリースペース', 'ぬりえと工作をして、おひめさまを作ってみましょう。'], 'basis': 'child_program', 'reason': '11/22開催。トーハクプチキッズデーの催し「ペーパークラフト かさねてつくるおひめさま」。当日受付で随時参加できる。', 'axes': {'child_target': ['A', '子ども向けの「プチキッズデー」の催しとして実施される'], 'interactivity': ['A', 'ぬりえや工作、探検に参加できる'], 'age_fit': ['A', '幼児から小学生まで楽しめる内容'], 'stay_flexibility': ['A', '当日、随時参加できる'], 'burden': ['A', '当日受付で、予約が不要'], 'cost': ['unknown', 'このページに参加費の記載がない'], 'reservation': ['A', '予約不要の当日受付'], 'family_value': ['A', 'ぬりえと工作をして持ち帰れる']}, 'strengths': ['予約不要で随時参加できる', '子ども向けのプチキッズデーの催し'], 'limitations': ['資料や席に限りがある', '毎月第4日曜日の催し'], 'comparison': '総合B（ペーパークラフト かさねてつくるおひめさま）：予約不要で随時参加できる子ども向けプログラムだが、席や材料に限りがある。', 'pos': ['official_date_confirmed', 'child_activity_confirmed'], 'override': '', 'pf': 'pass', 'overall': 'B', 'child': True}, {'id': 'verified-20261122-tohaku-tanken', 'week': '2026-11-21', 'ward': '台東区', 'page': 'tohaku_tanken_1122.html', 'name': 'トーハク本館たんけん（東京国立博物館）', 'url': 'https://www.tnm.jp/modules/r_event/index.php?controller=dtl&cid=15&id=11840', 'date': '2026-11-22', 'period': '11/22(日)', 'time': 'なくなり次第配布終了', 'venue': '東京国立博物館 本館9室（配布場所）（台東区上野公園13-9）', 'price': '参加費無料', 'description': '「たんけんブック」を持って、本館のたてもののデザインを探しながら家族や友だちと探検する。すべてのミッションをクリアすると缶バッジがもらえる。 毎月第4日曜日のトーハクプチキッズデーの催しで、当日受付。', 'cats': ['博物館', '工作', '体験'], 'io': '屋内', 'res': {'required': False, 'note': '当日受付。随時参加できる。'}, 'quotes': ['トーハクプチキッズデー（毎月第4日曜日、12月20日）', '日程2026年11月22日（日）', '参加費無料〒110-8712', '配布場所本館9室参加費無料〒', '「トーハク本館たんけんブック」をもって、たてもののデザインに注目しながら、家族やお友だちと本館をたんけんしよう！'], 'basis': 'child_program', 'reason': '11/22開催。トーハクプチキッズデーの催し「トーハク本館たんけん」で、参加費は無料。当日受付で随時参加できる。', 'axes': {'child_target': ['A', '子ども向けの「プチキッズデー」の催しとして実施される'], 'interactivity': ['A', 'ぬりえや工作、探検に参加できる'], 'age_fit': ['A', '幼児から小学生まで楽しめる内容'], 'stay_flexibility': ['A', '当日、随時参加できる'], 'burden': ['A', '当日受付で、予約が不要'], 'cost': ['A', '参加費無料'], 'reservation': ['A', '予約不要の当日受付'], 'family_value': ['B', '家族で本館を探検しながらデザインを学べる']}, 'strengths': ['予約不要で随時参加できる', '子ども向けのプチキッズデーの催し'], 'limitations': ['資料や席に限りがある', '毎月第4日曜日の催し'], 'comparison': '総合B（トーハク本館たんけん）：予約不要で随時参加できる子ども向けプログラムだが、席や材料に限りがある。', 'pos': ['official_date_confirmed', 'child_activity_confirmed'], 'override': '', 'pf': 'pass', 'overall': 'B', 'child': True}, {'id': 'verified-20261122-tohaku-kimono', 'week': '2026-11-21', 'ward': '台東区', 'page': 'tohaku_kimono_1122.html', 'name': 'きもののもようコレクション～秋草のもよう～（東京国立博物館）', 'url': 'https://www.tnm.jp/modules/r_event/index.php?controller=dtl&cid=15&id=11844', 'date': '2026-11-22', 'period': '11/22(日)', 'time': '10:00〜16:00（随時参加可、最終受付15:45）', 'venue': '東京国立博物館 本館C室ほか（本館2階18室・20室）（台東区上野公園13-9）', 'price': '参加費無料', 'description': '展示室できものの秋草のもようを探し、見つけたもようをヒントに自分だけのきものデザインを完成させる。 毎月第4日曜日のトーハクプチキッズデーの催しで、当日受付。', 'cats': ['博物館', '工作', '体験'], 'io': '屋内', 'res': {'required': False, 'note': '当日受付。随時参加できる。'}, 'quotes': ['トーハクプチキッズデー（毎月第4日曜日、12月20日）', '日程2026年11月22日（日）', '参加費無料対象小学3年生以上', '会場本館-C室参加費無料対象', '展示室でもようを見つけて、自分だけのきものデザインをつくろう！'], 'basis': 'child_program', 'reason': '11/22開催。トーハクプチキッズデーの催し「きもののもようコレクション～秋草のもよう～」で、参加費は無料。当日受付で随時参加できる。', 'axes': {'child_target': ['A', '子ども向けの「プチキッズデー」の催しとして実施される'], 'interactivity': ['A', 'ぬりえや工作、探検に参加できる'], 'age_fit': ['B', '小学3年生以上が推奨'], 'stay_flexibility': ['A', '当日、随時参加できる'], 'burden': ['A', '当日受付で、予約が不要'], 'cost': ['A', '参加費無料'], 'reservation': ['A', '予約不要の当日受付'], 'family_value': ['B', '展示を観察しながら自分のデザインを作れる']}, 'strengths': ['予約不要で随時参加できる', '子ども向けのプチキッズデーの催し'], 'limitations': ['資料や席に限りがある', '毎月第4日曜日の催し'], 'comparison': '総合B（きもののもようコレクション～秋草のもよう～）：予約不要で随時参加できる子ども向けプログラムだが、席や材料に限りがある。', 'pos': ['official_date_confirmed', 'child_activity_confirmed'], 'override': '', 'pf': 'pass', 'overall': 'B', 'child': True}]
RAW = SPECS_RAW
SPECS = []
for _r in RAW:
    _s = dict(_r)
    _s['categories'] = _s.pop('cats'); _s['indoor_outdoor'] = _s.pop('io'); _s['reservation'] = _s.pop('res')
    _s['child_activity'] = _s.pop('child'); _s['price_field'] = _s.pop('pf'); _s['positive'] = _s.pop('pos')
    SPECS.append(_s)
NEW_IDS = [s['id'] for s in SPECS]
SHARDS = {w: f'{w}-events-lead27-20261120.json' for w in ('2026-11-21',)}
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
        run['lead27_addition_20261120'] = {
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
        'run_id': 'lead27-addition-20261120', 'run_type': 'manual_verified_lead27_addition',
        'status': 'verified_subset_publication', 'as_of_jst': '2026-11-20', 'executed_at': m['generated'],
        'base_data_production_sha': BASE, 'target_weekends': sorted(derived),
        'prior_active_week_records': 684, 'candidate_active_week_records': 689, 'added_weekly_records': 5,
        'new_event_ids': NEW_IDS, 'held_not_published': sorted(HELD),
        'existing_event_records_physically_deleted': 0, 'image_only_updates': 0,
        'source_failures_remain_unverified': True, 'global_source_audit_complete': False,
        'full_23_ward_25_source_audit_complete': False,
        'note': '東京都の公園管理者・東京国立博物館の公式ページで日付・時間・会場・条件を確認できた5件のみ追加。',
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
