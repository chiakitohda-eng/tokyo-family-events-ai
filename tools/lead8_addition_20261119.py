#!/usr/bin/env python3
"""Six weekly records (six events) found by reading the remaining pool pages and calendar detail pages (2026-11-19).

Raw official pages are committed unchanged under research/2026-11-19-audit/pages/
(fetched by read-only workflows, HTTP 200). Quotes must occur verbatim in those pages.
The gate validator re-derives every record from this module and requires exact equality.
"""
import argparse, hashlib, json, pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import suginami_addition_20261118 as S

BASE = 'badd9f948fc48a31061dc2576110d897d2e728d8'   # data-production after the lead4 addition (476 records)
CHECKED = '2026-11-19'
AXES = S.AXES
NOTE_AUDIT = '週別全源照合は未完（ためまっぷ403等）。この1件は各区公式ページの個別確認に基づく。'
S.CHECKED = CHECKED


def _page_text(path):
    """Like suginami page_text, but falls back to the whole document when a page has no <h1>."""
    raw = pathlib.Path(path).read_text(encoding='utf-8', errors='ignore')
    i = raw.find('<h1')
    raw = raw[i:] if i >= 0 else raw
    raw = S.re.sub(r'<(script|style).*?</\1>', '', raw, flags=S.re.S)
    raw = S.re.sub(r'<br\s*/?>|</(p|li|tr|dt|dd|h\d|div|th|td)>', '\n', raw)
    return S.re.sub(r'\s+', '', S.html.unescape(S.re.sub(r'<[^>]+>', '', raw)))


SPECS_RAW = [{'id': 'verified-20261121-itabashi-hasune-programming', 'week': '2026-11-21', 'ward': '板橋区', 'page': 'itabashi_hasune_programming.html', 'name': '【蓮根図書館】はじめてのプログラミング', 'url': 'https://www.city.itabashi.tokyo.jp/kosodate/1000930/etc/1066375.html', 'date': '2026-11-21', 'period': '11/21(土)', 'time': '14:00〜15:30', 'venue': '蓮根図書館（板橋区）', 'price': '無料', 'description': 'プログラミングソフトで「すいぞくかん」を作る、小学3年生以下向けの体験。申込が必要で、定員10人（申込順）。費用は不要。', 'cats': ['体験・ワークショップ', '学び'], 'io': '屋内', 'res': {'required': True, 'note': '申込必要。10/17午前9時から直接または電話で蓮根図書館へ。定員10人（申込順）。'}, 'quotes': ['【蓮根図書館】はじめてのプログラミング', 'イベントカテゴリ：子ども・保護者向け', '開催日2026年11月21日（土曜日）開催時間午後2時から午後3時30分まで', '開催場所蓮根図書館内容プログラミングソフトですいぞくかん作り', '申込み必要10月17日（土曜日）午前9時から、直接または電話で、蓮根図書館費用不要定員10人（申込順）対象小学3年生以下'], 'overall': 'B', 'basis': 'child_program', 'child': True, 'reason': '小学3年生以下向けに、プログラミングで水族館を作る体験ができる。無料だが申込が必要で、定員は10人。', 'axes': {'child_target': ('A', '小学3年生以下の子ども・保護者向け'), 'interactivity': ('A', 'プログラミングソフトで作る体験型'), 'age_fit': ('A', '対象は小学3年生以下と明記'), 'stay_flexibility': ('B', '1時間30分'), 'burden': ('C', '申込が必要で、定員は10人'), 'cost': ('A', '費用不要'), 'reservation': ('C', '申込が必要（直接または電話、申込順）'), 'family_value': ('B', '子どもがプログラミングを体験できる')}, 'strengths': ['プログラミング体験', '無料'], 'limitations': ['申込が必要', '定員10人（申込順）'], 'comparison': '総合B：子ども向けの体験で無料だが、申込が必要で定員が少ない。', 'pf': 'pass', 'pos': ['official_date_confirmed', 'child_activity_confirmed']}, {'id': 'verified-20261129-suginami-nishiogi-oshanashi', 'week': '2026-11-28', 'ward': '杉並区', 'page': 'suginami_nishiogi_oshanashi.html', 'name': '西荻図書館児童講演会「おはなしとワークショップ」', 'url': 'https://www.city.suginami.tokyo.jp/s116/event/28394.html', 'date': '2026-11-29', 'period': '11/29(日)', 'time': '14:00〜15:30', 'venue': '西荻図書館 2階多目的ホール（杉並区西荻北2丁目33番9号）', 'price': '無料', 'description': '絵本作家の出口かずみさんによるおはなしと、「おにぎり型たからばこ」を作るワークショップ。4歳以上（未就学児は保護者同伴）。申込が必要で、定員20名。', 'cats': ['体験・ワークショップ', '絵本・お話'], 'io': '屋内', 'res': {'required': True, 'note': '申込必要。電話または1階カウンターで受付（西荻図書館 03-3301-1670）。定員20名（申込順）。'}, 'quotes': ['絵本作家出口かずみさんによるおはなしとワークショップです。', '開催日2026年11月29日（日曜日）開催時間午後2時から午後3時30分まで', '対象者未就学児｜小学生4歳以上（未就学児は保護者同伴）', '開催場所西荻図書館2階多目的ホール杉並区西荻北2丁目33番9号', '絵本作家出口かずみさんによるおはなしと、ワークショップ『おにぎり型たからばこをつくろう』を行います。', '申し込み必要11月1日（日曜日）午前9時から電話または1階カウンターで受付', '定員20名申込順講師出口かずみ氏費用無料'], 'overall': 'B', 'basis': 'child_program', 'child': True, 'reason': '絵本作家のおはなしと工作が楽しめる、4歳以上の子ども向けの講演会。無料だが申込が必要で、定員は20名。', 'axes': {'child_target': ('A', '未就学児・小学生向け（4歳以上）'), 'interactivity': ('A', 'おはなしと、たからばこを作る工作'), 'age_fit': ('A', '4歳以上と明記'), 'stay_flexibility': ('B', '1時間30分'), 'burden': ('C', '申込が必要で、定員は20名。託児はない'), 'cost': ('A', '無料'), 'reservation': ('C', '電話または窓口での申込が必要'), 'family_value': ('B', '絵本作家のおはなしと工作を体験できる')}, 'strengths': ['絵本作家のおはなしと工作', '無料'], 'limitations': ['申込が必要', '定員20名', '託児はない'], 'comparison': '総合B：子ども向けの体験で無料だが、申込が必要で定員が20名。', 'pf': 'pass', 'pos': ['official_date_confirmed', 'child_activity_confirmed']}, {'id': 'verified-20261129-nerima-molkky', 'week': '2026-11-28', 'ward': '練馬区', 'page': 'nerima_nomori_kodomofesta.html', 'name': 'ねりまの森こどもフェスタ「モルックであそぼう」（きたっぱら憩いの森）', 'url': 'https://www.city.nerima.tokyo.jp/kurashi/shigoto/midori/shokai/nerimanomori.html', 'date': '2026-11-29', 'period': '11/29(日)', 'time': '10:00〜15:00', 'venue': 'きたっぱら憩いの森（練馬区谷原3丁目9番）', 'price': '無料（一部有料のイベントがあります）', 'description': 'モルック大会と四輪自転車体験ができる、ねりまの森こどもフェスタの催し。無料・予約不要。', 'cats': ['体験・ワークショップ', '公園・自然'], 'io': '屋外', 'res': {'required': False, 'note': '事前予約不要。当日会場へ。雨天中止。'}, 'quotes': ['令和8年11月29日（日曜）午前10時から午後3時までモルックであそぼう（モルック大会、四輪自転車体験）きたっぱら憩いの森（谷原3丁目9番）明治大学校友会練馬区地域支部', '参加方法当日会場へお越しください。事前予約不要・参加費無料です（一部有料のイベントがあります）。', '（注釈）オリジナルグッズが貰えるのは18歳以下が対象です。', '（注釈）雨天中止となります（一部除く）。'], 'overall': 'B', 'basis': 'child_program', 'child': True, 'reason': 'モルック大会と四輪自転車体験ができる、ねりまの森こどもフェスタの催し。きたっぱら憩いの森で開催。無料・予約不要で、18歳以下にはグッズのプレゼントがある。屋外で雨天中止。', 'axes': {'child_target': ('B', 'こどもフェスタの催しで、18歳以下にグッズのプレゼントがある'), 'interactivity': ('B', '森の中での体験・遊び'), 'age_fit': ('unknown', '対象年齢の目安は明記がない'), 'stay_flexibility': ('B', '開催時間が限られている'), 'burden': ('B', '屋外開催で雨天中止。駐車場がない'), 'cost': ('A', '参加費無料（一部有料のイベントあり）'), 'reservation': ('A', '事前予約不要'), 'family_value': ('B', '森で家族で遊べる')}, 'strengths': ['無料・予約不要', '18歳以下にグッズのプレゼント'], 'limitations': ['屋外で雨天中止', '各会場に駐車場がない'], 'comparison': '総合B：きたっぱら憩いの森で10:00〜15:00の間、無料・予約不要で参加できるが、屋外で雨天中止になる。', 'pf': 'pass', 'pos': ['official_date_confirmed', 'child_activity_confirmed']}, {'id': 'verified-20261205-nerima-ochiba-matsuri', 'week': '2026-12-05', 'ward': '練馬区', 'page': 'nerima_nomori_kodomofesta.html', 'name': 'ねりまの森こどもフェスタ「落ち葉祭り」（石庭の森緑地）', 'url': 'https://www.city.nerima.tokyo.jp/kurashi/shigoto/midori/shokai/nerimanomori.html', 'date': '2026-12-05', 'period': '12/5(土)', 'time': '10:00〜12:00', 'venue': '石庭の森緑地（練馬区東大泉7丁目50番48号）', 'price': '無料（一部有料のイベントがあります）', 'description': '落ち葉掃きと腐葉土づくりができる、ねりまの森こどもフェスタの催し。無料・予約不要。', 'cats': ['体験・ワークショップ', '公園・自然'], 'io': '屋外', 'res': {'required': False, 'note': '事前予約不要。当日会場へ。雨天中止。'}, 'quotes': ['令和8年12月5日（土曜）午前10時から正午まで落ち葉祭り（落ち葉掃き、腐葉土づくり）石庭の森緑地（東大泉7丁目50番48号）石庭みどり会イベント共催：宮本南町会', '参加方法当日会場へお越しください。事前予約不要・参加費無料です（一部有料のイベントがあります）。', '（注釈）オリジナルグッズが貰えるのは18歳以下が対象です。', '（注釈）雨天中止となります（一部除く）。'], 'overall': 'B', 'basis': 'child_program', 'child': True, 'reason': '落ち葉掃きと腐葉土づくりができる、ねりまの森こどもフェスタの催し。石庭の森緑地で開催。無料・予約不要で、18歳以下にはグッズのプレゼントがある。屋外で雨天中止。', 'axes': {'child_target': ('B', 'こどもフェスタの催しで、18歳以下にグッズのプレゼントがある'), 'interactivity': ('B', '森の中での体験・遊び'), 'age_fit': ('unknown', '対象年齢の目安は明記がない'), 'stay_flexibility': ('B', '開催時間が限られている'), 'burden': ('B', '屋外開催で雨天中止。駐車場がない'), 'cost': ('A', '参加費無料（一部有料のイベントあり）'), 'reservation': ('A', '事前予約不要'), 'family_value': ('B', '森で家族で遊べる')}, 'strengths': ['無料・予約不要', '18歳以下にグッズのプレゼント'], 'limitations': ['屋外で雨天中止', '各会場に駐車場がない'], 'comparison': '総合B：石庭の森緑地で10:00〜12:00の間、無料・予約不要で参加できるが、屋外で雨天中止になる。', 'pf': 'pass', 'pos': ['official_date_confirmed', 'child_activity_confirmed']}, {'id': 'verified-20261205-nerima-oshigoto-minamitakamatsu', 'week': '2026-12-05', 'ward': '練馬区', 'page': 'nerima_nomori_kodomofesta.html', 'name': 'ねりまの森こどもフェスタ「森のおしごと体験」（南高松の森緑地）', 'url': 'https://www.city.nerima.tokyo.jp/kurashi/shigoto/midori/shokai/nerimanomori.html', 'date': '2026-12-05', 'period': '12/5(土)', 'time': '13:30〜14:30', 'venue': '南高松の森緑地（練馬区高松2丁目14番4号）', 'price': '無料（一部有料のイベントがあります）', 'description': '落ち葉掃きをする森のおしごと体験。ねりまの森こどもフェスタの催しで、無料・予約不要。', 'cats': ['体験・ワークショップ', '公園・自然'], 'io': '屋外', 'res': {'required': False, 'note': '事前予約不要。当日会場へ。雨天中止。'}, 'quotes': ['令和8年12月5日（土曜）午後1時30分から午後2時30分まで森のおしごと体験（落ち葉掃き）南高松の森緑地（高松2丁目14番4号）南高松もりファンクラブ', '参加方法当日会場へお越しください。事前予約不要・参加費無料です（一部有料のイベントがあります）。', '（注釈）オリジナルグッズが貰えるのは18歳以下が対象です。', '（注釈）雨天中止となります（一部除く）。'], 'overall': 'B', 'basis': 'child_program', 'child': True, 'reason': '落ち葉掃きをする森のおしごと体験。南高松の森緑地で開催。無料・予約不要で、18歳以下にはグッズのプレゼントがある。屋外で雨天中止。', 'axes': {'child_target': ('B', 'こどもフェスタの催しで、18歳以下にグッズのプレゼントがある'), 'interactivity': ('B', '森の中での体験・遊び'), 'age_fit': ('unknown', '対象年齢の目安は明記がない'), 'stay_flexibility': ('B', '開催時間が限られている'), 'burden': ('B', '屋外開催で雨天中止。駐車場がない'), 'cost': ('A', '参加費無料（一部有料のイベントあり）'), 'reservation': ('A', '事前予約不要'), 'family_value': ('B', '森で家族で遊べる')}, 'strengths': ['無料・予約不要', '18歳以下にグッズのプレゼント'], 'limitations': ['屋外で雨天中止', '各会場に駐車場がない'], 'comparison': '総合B：南高松の森緑地で13:30〜14:30の間、無料・予約不要で参加できるが、屋外で雨天中止になる。', 'pf': 'pass', 'pos': ['official_date_confirmed', 'child_activity_confirmed']}, {'id': 'verified-20261205-nerima-oshigoto-oozekiyama', 'week': '2026-12-05', 'ward': '練馬区', 'page': 'nerima_nomori_kodomofesta.html', 'name': 'ねりまの森こどもフェスタ「森のおしごと体験」（大関山の森緑地）', 'url': 'https://www.city.nerima.tokyo.jp/kurashi/shigoto/midori/shokai/nerimanomori.html', 'date': '2026-12-05', 'period': '12/5(土)', 'time': '9:30〜11:00', 'venue': '大関山の森緑地（練馬区関町北4丁目33番19号）', 'price': '無料（一部有料のイベントがあります）', 'description': '落ち葉掃きをする森のおしごと体験。ねりまの森こどもフェスタの催しで、無料・予約不要。', 'cats': ['体験・ワークショップ', '公園・自然'], 'io': '屋外', 'res': {'required': False, 'note': '事前予約不要。当日会場へ。雨天中止。'}, 'quotes': ['令和8年12月5日（土曜）午前9時30分から午前11時まで森のおしごと体験（落ち葉掃き）大関山の森緑地（関町北4丁目33番19号）大関山森もりクラブ', '参加方法当日会場へお越しください。事前予約不要・参加費無料です（一部有料のイベントがあります）。', '（注釈）オリジナルグッズが貰えるのは18歳以下が対象です。', '（注釈）雨天中止となります（一部除く）。'], 'overall': 'B', 'basis': 'child_program', 'child': True, 'reason': '落ち葉掃きをする森のおしごと体験。大関山の森緑地で開催。無料・予約不要で、18歳以下にはグッズのプレゼントがある。屋外で雨天中止。', 'axes': {'child_target': ('B', 'こどもフェスタの催しで、18歳以下にグッズのプレゼントがある'), 'interactivity': ('B', '森の中での体験・遊び'), 'age_fit': ('unknown', '対象年齢の目安は明記がない'), 'stay_flexibility': ('B', '開催時間が限られている'), 'burden': ('B', '屋外開催で雨天中止。駐車場がない'), 'cost': ('A', '参加費無料（一部有料のイベントあり）'), 'reservation': ('A', '事前予約不要'), 'family_value': ('B', '森で家族で遊べる')}, 'strengths': ['無料・予約不要', '18歳以下にグッズのプレゼント'], 'limitations': ['屋外で雨天中止', '各会場に駐車場がない'], 'comparison': '総合B：大関山の森緑地で9:30〜11:00の間、無料・予約不要で参加できるが、屋外で雨天中止になる。', 'pf': 'pass', 'pos': ['official_date_confirmed', 'child_activity_confirmed']}]
RAW = SPECS_RAW
SPECS = []
for _r in RAW:
    _s = dict(_r)
    _s['categories'] = _s.pop('cats'); _s['indoor_outdoor'] = _s.pop('io'); _s['reservation'] = _s.pop('res')
    _s['child_activity'] = _s.pop('child'); _s['price_field'] = _s.pop('pf'); _s['positive'] = _s.pop('pos')
    SPECS.append(_s)
NEW_IDS = [s['id'] for s in SPECS]
SHARDS = {w: f'{w}-events-lead8-20261119.json' for w in ('2026-11-21', '2026-11-28', '2026-12-05', '2026-12-12', '2026-12-19')}
HELD = {'suginami-zenpukuji-patapata-20261206': '杉並区在住・在勤・在学の方が対象', 'suginami-futago-ryuseigun-20261212': '杉並区在住・在学・在勤の方とそのご家族が対象', 'suginami-inawara-20261206': '申込期間が11/5で終了（抽選）', 'suginami-takekatombo-20261123': '申込期間が11/9で終了（抽選）', 'adachi-ouka-hakoniwa-20261128': '申込期限が11/19で、材料費3,300円・先着10人', 'edogawa-kodomo-mirai-kan-20261123': '子ども未来館の3講座は抽選で、申込期間が11/10に終了', 'toshima-kumanokko-day-20261123': '対象が豊島区立学校等の保護者', 'edogawa-konnitsuto-ichi-20261121': 'おもちゃの病院は修理サービスで、子ども向けの催しではない', 'chiyoda-first-bicycle-20261129': '千代田区在住者のみが対象', 'suginami-nazo-sanpo-20261116': '区内在住・在勤・在学の方が対象', 'shinjuku-poreporefes-20261128': '子ども向けの情報・費用・対象年齢の記載が乏しく、評価がC', 'itabashi-shimizu-berezza-20261123': '公式ページに内容が「準備中」', 'arakawa-ishihama-papa-20261123': '石浜ふれあい館パパとあそぼうは内容の記載がなく確認できない'}


def evidence(spec, pages_dir):
    text = _page_text(pathlib.Path(pages_dir) / spec['page'])
    out = []
    for q in spec['quotes']:
        if S._strip(q) not in text:
            raise ValueError(f"{spec['id']}: quote not found verbatim in the committed official page: {q}")
        out.append({'url': spec['url'], 'quote': q, 'checked_at': CHECKED,
                    'sha256': hashlib.sha256(q.encode('utf-8')).hexdigest(),
                    'hash_scope': 'quoted_text_only_not_HTTP_response_hash',
                    'description': f"{spec['ward']}公式ページ（2026-11-19にHTTP200で取得、research/2026-11-19-audit/pages/に不変保存）の本文引用。引用文字列だけのUTF-8 SHA-256。"})
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
               'evidence': [{'url': s['url'], 'basis': '2026-11-19 official individual event page (HTTP200); 23 ward completeness not asserted'}],
               'override_reason': ''}
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
                    row['note'] += f' 2026-11-19 公式個別ページ確認済み{k}件を非破壊追加。'
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
        run['lead8_addition_20261119'] = {
            'kind': 'individually_verified_official_events_from_lead_triage', 'added_ids': [i[0]['id'] for i in items],
            'held_not_published': sorted(HELD), 'pages_committed_at': 'research/2026-11-19-audit/pages/',
            'base_data_production_sha': BASE, 'global_source_audit_complete': False}
        S.jdump(d / f'{week}-run.json', run)
        for x in m['weekends']:
            if x['sat'] == week:
                x['count'] += n
    m['generated'] = '2026-11-19T20:00:00+09:00'
    S.jdump(d / 'manifest.json', m)
    h = S.jload(d / 'update_history.json')
    h['history'].append({
        'run_id': 'lead8-addition-20261119', 'run_type': 'manual_verified_lead8_addition',
        'status': 'verified_subset_publication', 'as_of_jst': '2026-11-19', 'executed_at': m['generated'],
        'base_data_production_sha': BASE, 'target_weekends': sorted(derived),
        'prior_active_week_records': 484, 'candidate_active_week_records': 490, 'added_weekly_records': 6,
        'new_event_ids': NEW_IDS, 'held_not_published': sorted(HELD),
        'existing_event_records_physically_deleted': 0, 'image_only_updates': 0,
        'source_failures_remain_unverified': True, 'global_source_audit_complete': False,
        'full_23_ward_25_source_audit_complete': False,
        'note': '残りの候補プールとカレンダーの個別ページを精読し、公式個別ページで条件を確認できた10件の週別レコード（画像なしを含む保留分）のみ追加。条件が合わないものは掲載せず理由を保存。',
    })
    S.jdump(d / 'update_history.json', h)


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--data-dir', required=True)
    ap.add_argument('--pages-dir', default='research/2026-11-19-audit/pages')
    a = ap.parse_args()
    try:
        build(a.data_dir, a.pages_dir)
    except ValueError as exc:
        print('ERROR:', exc, file=sys.stderr)
        sys.exit(1)
