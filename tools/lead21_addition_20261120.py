#!/usr/bin/env python3
"""1 weekly record (12/26 Nerima forest festival) from the committed official Nerima page (2026-11-20).

Raw official pages are committed unchanged under research/2026-11-20-thin-wards/pages/
(fetched by read-only workflows, HTTP 200). Quotes must occur verbatim in those pages.
The gate validator re-derives every record from this module and requires exact equality.
"""
import argparse, hashlib, json, pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import suginami_addition_20261118 as S

BASE = '027c6d6e57187ef39849e4917fbcab3fab0a43e1'   # data-production after the Nerima duplicate removal (644 active week records)
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


SPECS_RAW = [{'id': 'verified-20261205-nakano-nogata-edit', 'week': '2026-12-05', 'ward': '中野区', 'page': 'nakano_nogata_edit_1205.html', 'name': '小学生のための編集教室「世界の図書館と本を知ろう！」（野方図書館）', 'url': 'https://kodomo-smile.metro.tokyo.lg.jp/events/4269', 'date': '2026-12-05', 'period': '12/5(土)', 'time': '10:00〜12:00（受付9:45〜）', 'venue': '中野区立野方図書館（中野区野方3-19-5）', 'price': '無料', 'description': '世界の図書館や日本語と外国語の絵本の違いを見て、デンマーク語の絵本を作るワークショップ。小学生対象、定員30名で事前予約（定員に満たない場合は当日受付あり）。', 'cats': ['ワークショップ', '図書館', '本・絵本'], 'io': '屋内', 'res': {'required': True, 'note': '事前予約（定員30名）。定員に満たない場合は当日受付も行う。'}, 'quotes': ['2026年12月5日（土曜日）10:00～12:00受付は9:45から', '対象小学生定員30名（事前予約）', '中野区立野方図書館東京都中野', '参加費無料●定員30名（事前予約）', '定員に満たない場合は当日受付も行います'], 'overall': 'B', 'basis': 'child_program', 'child': True, 'reason': '小学生を対象に、世界の図書館や絵本を知り、デンマーク語の絵本を作るワークショップ。参加費無料で、定員30名の事前予約制。', 'axes': {'child_target': ['A', '対象が小学生と明記された子ども向けの教室'], 'interactivity': ['A', '絵本づくりのワークショップに参加できる'], 'age_fit': ['B', '対象は小学生で、学年の細かい目安はない'], 'stay_flexibility': ['B', '10〜12時の2時間で、時間が決まっている'], 'burden': ['B', '定員30名の事前予約が必要'], 'cost': ['A', '参加費無料'], 'reservation': ['B', '事前予約。定員に満たない場合は当日受付あり'], 'family_value': ['B', '図書館で本と世界に触れる学びの体験']}, 'strengths': ['小学生向けで無料', '絵本づくりを体験できる'], 'limitations': ['事前予約制で定員30名', '2時間の拘束がある'], 'comparison': '総合B：小学生向けで無料の絵本づくり教室だが、定員30名の事前予約制。', 'pf': 'pass', 'pos': ['official_date_confirmed', 'child_activity_confirmed'], 'override': ''}, {'id': 'verified-20261205-ota-kawasaki-robot-operate', 'week': '2026-12-05', 'ward': '大田区', 'page': 'kawasaki_robo_haneda.html', 'name': 'カワサキロボットエンジニアになろう！ 操作編（羽田イノベーションシティ）', 'url': 'https://kodomo-smile.metro.tokyo.lg.jp/events/4261', 'date': '2026-12-05', 'period': '12/5(土)・6(日)', 'time': '11:00〜12:00／14:00〜15:00', 'venue': '羽田イノベーションシティ B棟2階 カワサキロボットスクール（大田区羽田空港1-1-4）', 'price': '500円', 'description': '本物の産業用ロボットの操作を体験し、制服を着た記念撮影もできる。小学3〜6年生対象、事前予約制。子どもだけでの参加は不可。', 'cats': ['科学・ロボット', '体験・ワークショップ'], 'io': '屋内', 'res': {'required': True, 'note': '事前予約制。お子様のみでの参加はできません。'}, 'quotes': ['【操作編】12/5(土）～6(日）11：00～12：00、14：00～15：00', 'プログラミング編：小学3年生～中学生操作編：小学3年生～6年生', '操作編：500円プログラミン', '事前予約制お申し込みの詳細は', 'お子様のみでの参加はできません。'], 'overall': 'B', 'basis': 'child_program', 'child': True, 'reason': '本物の産業用ロボットの操作を体験できる小学3〜6年生向けの教室。参加費500円で、事前予約制。', 'axes': {'child_target': ['A', '小学3〜6年生を対象にした子ども向けイベント'], 'interactivity': ['A', '実機のロボットを操作できる'], 'age_fit': ['A', '操作編は小学3〜6年生と明記'], 'stay_flexibility': ['B', '各1時間の回で、時間が決まっている'], 'burden': ['B', '保護者の同行が必要で、事前予約が必要'], 'cost': ['A', '操作編は500円'], 'reservation': ['B', '事前予約制'], 'family_value': ['B', 'ものづくりと技術への興味を親子で広げられる']}, 'strengths': ['本物のロボットを操作できる', '500円と手頃'], 'limitations': ['小学3〜6年生に限られる', '事前予約が必要'], 'comparison': '総合B：本物の産業用ロボットを動かせて参加費も手頃だが、対象学年が限られ事前予約が必要。', 'pf': 'pass', 'pos': ['official_date_confirmed', 'child_activity_confirmed'], 'override': ''}, {'id': 'verified-20261219-ota-kawasaki-robot-prog', 'week': '2026-12-19', 'ward': '大田区', 'page': 'kawasaki_robo_haneda.html', 'name': 'カワサキロボットエンジニアになろう！ プログラミング編（羽田イノベーションシティ）', 'url': 'https://kodomo-smile.metro.tokyo.lg.jp/events/4261', 'date': '2026-12-19', 'period': '12/19(土)・20(日)', 'time': '11:00〜12:30／14:00〜15:30', 'venue': '羽田イノベーションシティ B棟2階 カワサキロボットスクール（大田区羽田空港1-1-4）', 'price': '3,500円', 'description': '産業用ロボットの実機をプログラミングして動かす体験。小学3年生〜中学生対象、事前予約制。子どもだけでの参加は不可。', 'cats': ['科学・ロボット', 'プログラミング', '体験・ワークショップ'], 'io': '屋内', 'res': {'required': True, 'note': '事前予約制。お子様のみでの参加はできません。'}, 'quotes': ['【プロ編】12/19(土）～20(日）11：00～12：30、14：00～15：30', 'プログラミング編：小学3年生～中学生', 'プログラミング編：3,500円', '事前予約制お申し込みの詳細は', 'お子様のみでの参加はできません。'], 'overall': 'B', 'basis': 'child_program', 'child': True, 'reason': '産業用ロボットの実機をプログラミングして動かす、小学3年生〜中学生向けの教室。参加費3,500円で、事前予約制。', 'axes': {'child_target': ['A', '小学3年生〜中学生を対象にした子ども向けイベント'], 'interactivity': ['A', 'ロボットの実機をプログラミングして動かせる'], 'age_fit': ['A', '小学3年生〜中学生と明記'], 'stay_flexibility': ['B', '各1時間半の回で、時間が決まっている'], 'burden': ['B', '保護者の同行が必要で、事前予約が必要'], 'cost': ['C', 'プログラミング編は3,500円'], 'reservation': ['B', '事前予約制'], 'family_value': ['B', '技術への興味を育てる体験']}, 'strengths': ['実機をプログラミングできる', '小学3年〜中学生が対象'], 'limitations': ['参加費3,500円', '事前予約が必要'], 'comparison': '総合B：実機のロボットをプログラミングできる本格的な体験だが、参加費が高めで事前予約が必要。', 'pf': 'pass', 'pos': ['official_date_confirmed', 'child_activity_confirmed'], 'override': ''}, {'id': 'verified-20261121-edo-wonder-lab-bunkyo', 'week': '2026-11-21', 'ward': '文京区', 'page': 'edo_wonder_1121.html', 'name': '江戸ワンダー・ラボ（千駄木・養源寺）', 'url': 'https://www.yasosuke.co.jp/edowonderlabo11event', 'date': '2026-11-21', 'period': '11/21(土)', 'time': '11:00〜15:00（プログラムにより時間が異なる）', 'venue': '千駄木・養源寺（文京区千駄木）', 'price': '500円〜2,000円（プログラムごと。当日払い）', 'description': '江戸時代をテーマにした子ども向けワークショップ。伊能忠敬の測量体験と和算のほか、張り子絵付け（1,000円）、からくり屏風づくり（500円）などを体験できる。小学生は保護者と参加する。', 'cats': ['ワークショップ', '伝統文化', '工作'], 'io': '屋内', 'res': {'required': None, 'note': 'お申込みフォームあり。張り子絵付けは当日受付も可能だが、事前予約を推奨。'}, 'quotes': ['日程：2026年11月21日（土）会場：千駄木・養源寺', '11時～15時張り子絵付け（狐面・犬張り子・干支未／1000円材料費込）', '14時～14時45分からくり屏風づくり（500円材料費込）', '小学生のお子様は必ず保護者の方が一緒にご参加ください。', '当日も受付可能ですが、数に限りがあるため、事前予約をおすすめします。'], 'overall': 'B', 'basis': 'child_program', 'child': True, 'reason': '11/21の会場（千駄木・養源寺）で開かれる、江戸時代をテーマにした子ども向けのワークショップ群。小学校低学年向けの張り子絵付けや工作から、高学年向けの測量・和綴じ体験まで選べる。', 'axes': {'child_target': ['B', '小学校低学年・高学年向けのレベル表示があるワークショップ'], 'interactivity': ['A', '工作や体験型の学びが中心'], 'age_fit': ['B', 'プログラムごとに低学年・高学年のレベルが示されている'], 'stay_flexibility': ['B', 'プログラムごとに時間が決まっているが、張り子は随時受付'], 'burden': ['B', '小学生は保護者の同伴が必要'], 'cost': ['B', '500円〜2,000円（プログラムごと）'], 'reservation': ['unknown', '申込フォームはあるが、予約が必須かはページに明記がない'], 'family_value': ['A', '親子で江戸の文化・算数・ものづくりを体験できる']}, 'strengths': ['複数のプログラムから選べる', '小学校低学年から参加できる'], 'limitations': ['プログラムごとに料金と時間が異なる', '予約の要否が明記されていない'], 'comparison': '総合B（11/21(土)）：親子で江戸文化を学べる体験が選べるが、プログラムごとに料金と時間が異なり、予約の要否が分からない。', 'pf': 'pass', 'pos': ['official_date_confirmed', 'child_activity_confirmed'], 'override': ''}, {'id': 'verified-20261122-edo-wonder-lab-taito', 'week': '2026-11-21', 'ward': '台東区', 'page': 'edo_wonder_1121.html', 'name': '江戸ワンダー・ラボ（上野・宋雲院）', 'url': 'https://www.yasosuke.co.jp/edowonderlabo11event', 'date': '2026-11-22', 'period': '11/22(日)', 'time': '11:00〜15:00（プログラムにより時間が異なる）', 'venue': '上野・宋雲院（台東区上野）', 'price': '500円〜2,000円（プログラムごと。当日払い）', 'description': '江戸時代をテーマにした子ども向けワークショップ。江戸の本屋体験（和綴じ本づくり）と和算のほか、張り子絵付け（1,000円）、からくり屏風づくり（500円）などを体験できる。小学生は保護者と参加する。', 'cats': ['ワークショップ', '伝統文化', '工作'], 'io': '屋内', 'res': {'required': None, 'note': 'お申込みフォームあり。張り子絵付けは当日受付も可能だが、事前予約を推奨。'}, 'quotes': ['日程：2026年11月22日（日）会場：上野・宋雲院', '11時～15時張り子絵付け（狐面・犬張り子・干支未／1000円材料費込）', '14時～14時45分からくり屏風づくり（500円材料費込）', '小学生のお子様は必ず保護者の方が一緒にご参加ください。', '当日も受付可能ですが、数に限りがあるため、事前予約をおすすめします。'], 'overall': 'B', 'basis': 'child_program', 'child': True, 'reason': '11/22の会場（上野・宋雲院）で開かれる、江戸時代をテーマにした子ども向けのワークショップ群。小学校低学年向けの張り子絵付けや工作から、高学年向けの測量・和綴じ体験まで選べる。', 'axes': {'child_target': ['B', '小学校低学年・高学年向けのレベル表示があるワークショップ'], 'interactivity': ['A', '工作や体験型の学びが中心'], 'age_fit': ['B', 'プログラムごとに低学年・高学年のレベルが示されている'], 'stay_flexibility': ['B', 'プログラムごとに時間が決まっているが、張り子は随時受付'], 'burden': ['B', '小学生は保護者の同伴が必要'], 'cost': ['B', '500円〜2,000円（プログラムごと）'], 'reservation': ['unknown', '申込フォームはあるが、予約が必須かはページに明記がない'], 'family_value': ['A', '親子で江戸の文化・算数・ものづくりを体験できる']}, 'strengths': ['複数のプログラムから選べる', '小学校低学年から参加できる'], 'limitations': ['プログラムごとに料金と時間が異なる', '予約の要否が明記されていない'], 'comparison': '総合B（11/22(日)）：親子で江戸文化を学べる体験が選べるが、プログラムごとに料金と時間が異なり、予約の要否が分からない。', 'pf': 'pass', 'pos': ['official_date_confirmed', 'child_activity_confirmed'], 'override': ''}]
RAW = SPECS_RAW
SPECS = []
for _r in RAW:
    _s = dict(_r)
    _s['categories'] = _s.pop('cats'); _s['indoor_outdoor'] = _s.pop('io'); _s['reservation'] = _s.pop('res')
    _s['child_activity'] = _s.pop('child'); _s['price_field'] = _s.pop('pf'); _s['positive'] = _s.pop('pos')
    SPECS.append(_s)
NEW_IDS = [s['id'] for s in SPECS]
SHARDS = {w: f'{w}-events-lead21-20261120.json' for w in ('2026-11-21', '2026-12-05', '2026-12-19')}
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
        run['lead21_addition_20261120'] = {
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
        'run_id': 'lead21-addition-20261120', 'run_type': 'manual_verified_lead21_addition',
        'status': 'verified_subset_publication', 'as_of_jst': '2026-11-20', 'executed_at': m['generated'],
        'base_data_production_sha': BASE, 'target_weekends': sorted(derived),
        'prior_active_week_records': 644, 'candidate_active_week_records': 649, 'added_weekly_records': 5,
        'new_event_ids': NEW_IDS, 'held_not_published': sorted(HELD),
        'existing_event_records_physically_deleted': 0, 'image_only_updates': 0,
        'source_failures_remain_unverified': True, 'global_source_audit_complete': False,
        'full_23_ward_25_source_audit_complete': False,
        'note': '東京都の公園管理者・東京都こども向け行事ポータル・川崎重工業・八十介などの主催者公式ページで日付・時間・会場・条件を確認できた5件のみ追加。',
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
