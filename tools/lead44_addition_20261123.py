#!/usr/bin/env python3
"""2 weekly records (Komae city x2) from committed official pages (2026-11-21).

Raw official pages are committed unchanged under research/2026-11-20-thin-wards/pages/. The gate validator re-derives every record and requires exact equality.
"""
import argparse, hashlib, json, pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import suginami_addition_20261118 as S

BASE = '92c676a01ccda8fa2bc27cde65f130be55a445ac'   # data-production after lead43 (793 active week records)
CHECKED = '2026-11-23'
AXES = S.AXES
NOTE_AUDIT = '週別全源照合は未完（ためまっぷ403等）。この9件は渋谷区の公式ページの個別確認に基づく。'
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

SPECS_RAW = [{'id': 'verified-20261121-shibuya-hachilabo-space-exhibition-2026',
  'week': '2026-11-21',
  'ward': '渋谷区',
  'page': 'hachilabo_tenji_20261123.html',
  'name': '《特別展》ハチラボ宇宙展（こども科学センター・ハチラボ）',
  'url': 'https://shibu-cul.jp/hachilabo/tenji',
  'date': '2026-11-17',
  'end': '2027-01-17',
  'period': '11/17(火)〜1/17(日)',
  'time': '時間の記載なし（公式ページで確認）',
  'venue': 'こども科学センター・ハチラボ（渋谷区桜丘町23-21、渋谷区文化総合センター大和田3F）',
  'price': '無料',
  'image': '',
  'description': '渋谷の科学館ハチラボで開く、宇宙をテーマにした体験型の特別展。見て、さわって、考える展示で、入館料は無料。',
  'categories': ['科学・自然', '体験・ワークショップ'],
  'indoor_outdoor': '屋内',
  'reservation': {'required': False, 'note': '展示の観覧に申込の記載なし。'},
  'quotes': ['２０２６年１１月１７日（火）～２０２７年１月１７日（日）', '見て、さわって、考える、体験型の展示を行っています。'],
  'overall': 'A',
  'basis': 'child_program',
  'child_activity': True,
  'reason': '宇宙をテーマにした体験型の特別展。入館無料で、小さな子から小・中学生まで、展示で遊びながら学べる。開館時間は公式ページに記載がない。',
  'axes': {'child_target': 'A', 'interactivity': 'A', 'age_fit': 'A', 'stay_flexibility': 'A', 'burden': 'A', 'cost': 'A', 'reservation': 'A', 'family_value': 'A'},
  'strengths': ['入館無料で、2027年1月17日まで長く開いている', '見て・さわって・考える体験型の展示'],
  'limitations': ['開館時間は公式ページに記載がなく、休館日がある'],
  'comparison': '総合A：入館無料で2027年1月17日まで長く開き、宇宙をテーマに見て・さわって・考えられる。時間は公式ページで確認が必要。',
  'status': 'verified',
  'price_field': 'pass',
  'positive': ['official_date_confirmed', 'child_activity_confirmed'],
  'extra': [{'page': 'hachilabo_top_20261123.html', 'url': 'https://shibu-cul.jp/hachilabo', 'q': '入館料はどなたでも無料で'}, {'page': 'hachilabo_top_20261123.html', 'url': 'https://shibu-cul.jp/hachilabo', 'q': '小さなお子様連れから小・中学生まで楽しく遊んで学べる施設です'}]},
 {'id': 'verified-20261121-shibuya-hachilabo-space-mobile-2026',
  'week': '2026-11-21',
  'ward': '渋谷区',
  'page': 'hachilabo_nov_20261123.html',
  'name': '【ひらめきワークショップ】宇宙モビール（ハチラボ）',
  'url': 'https://shibu-cul.jp/event/52646#space-mobile',
  'date': '2026-11-01',
  'end': '2026-11-29',
  'period': '11/1(日)〜11/29(日)',
  'time': '平日13:30・15:00／土日祝11:30・13:30・15:00（各回20分）',
  'venue': 'こども科学センター・ハチラボ（渋谷区桜丘町23-21、渋谷区文化総合センター大和田3F）',
  'price': '無料',
  'image': '',
  'description': '宇宙展に合わせた約20分のミニワークショップで、宇宙モビールをつくる。未就学児から参加でき、無料。',
  'categories': ['科学・自然', '体験・ワークショップ'],
  'indoor_outdoor': '屋内',
  'reservation': {'required': True, 'note': '要申込（先着順）。開催日の1週間前0:00から受付。申込はp-gakushu.jp/hachilabo。'},
  'quotes': ['●開催期間：11月1日（日）～11月29日（日）', '●推奨年齢：未就学児～（小3以下は保護者同伴）', '●申込：開催日の一週間前の0:00から先着順'],
  'overall': 'A',
  'basis': 'child_program',
  'child_activity': True,
  'reason': '11/29まで、未就学児から参加できる20分の工作。無料で、短時間で気軽に体験できる。',
  'axes': {'child_target': 'A', 'interactivity': 'A', 'age_fit': 'A', 'stay_flexibility': 'B', 'burden': 'A', 'cost': 'A', 'reservation': 'C', 'family_value': 'A'},
  'strengths': ['宇宙展に合わせたモビールづくりを、未就学児から体験できる', '11/1〜11/29の毎日開く'],
  'limitations': ['各回4名と少人数で、開催日の1週間前から先着順の申込が必要'],
  'comparison': '総合A：宇宙展に合わせた、未就学児から参加できる無料の20分工作。11/29までで、先着順の申込が必要。',
  'status': 'verified',
  'price_field': 'pass',
  'positive': ['official_date_confirmed', 'child_activity_confirmed']},
 {'id': 'verified-20261205-shibuya-hachilabo-string-phone-2026',
  'week': '2026-12-05',
  'ward': '渋谷区',
  'page': 'hachilabo_dec_20261123.html',
  'name': '【ひらめきワークショップ】ひとり糸電話（ハチラボ）',
  'url': 'https://shibu-cul.jp/event/53568#string-phone',
  'date': '2026-12-01',
  'end': '2026-12-28',
  'period': '12/1(火)〜13(日)、12/26(土)〜28(月)',
  'time': '平日13:30・15:00／土日祝・12/28は11:30・13:30・15:00（各回20分）',
  'venue': 'こども科学センター・ハチラボ（渋谷区桜丘町23-21、渋谷区文化総合センター大和田3F）',
  'price': '無料',
  'image': '',
  'description': '約20分のミニワークショップで、自分だけの糸電話をつくる。未就学児から参加でき、無料。',
  'categories': ['科学・自然', '体験・ワークショップ'],
  'indoor_outdoor': '屋内',
  'reservation': {'required': True, 'note': '要申込（先着順）。開催日の1週間前0:00から受付。申込はp-gakushu.jp/hachilabo。'},
  'quotes': ['●開催期間：12月1日（火）～12月13日（日）', '●推奨年齢：未就学児～（小3以下は保護者同伴）', '●申込：開催日の一週間前の0:00から先着順'],
  'overall': 'A',
  'basis': 'child_program',
  'child_activity': True,
  'reason': '未就学児から参加できる20分の工作。12月は2期間に分けて開く。無料。',
  'axes': {'child_target': 'A', 'interactivity': 'A', 'age_fit': 'A', 'stay_flexibility': 'B', 'burden': 'A', 'cost': 'A', 'reservation': 'C', 'family_value': 'A'},
  'strengths': ['糸電話づくりを体験でき、未就学児から参加できる', '12/1〜13と12/26〜28の2期間に開く'],
  'limitations': ['各回4名と少人数で、開催日の1週間前から先着順の申込が必要', '12/14〜25は開かない'],
  'comparison': '総合A：12月の2期間に開く、未就学児から参加できる無料の糸電話づくり。先着順で少人数。',
  'status': 'verified',
  'price_field': 'pass',
  'positive': ['official_date_confirmed', 'child_activity_confirmed']},
 {'id': 'verified-20261219-shibuya-hachilabo-snowman-lamp-2026',
  'week': '2026-12-19',
  'ward': '渋谷区',
  'page': 'hachilabo_dec_20261123.html',
  'name': '【ひらめきワークショップ】雪だるまランプ（ハチラボ）',
  'url': 'https://shibu-cul.jp/event/53568#snowman-lamp',
  'date': '2026-12-15',
  'end': '2026-12-25',
  'period': '12/15(火)〜12/25(金)',
  'time': '平日13:30・15:00／土日祝11:30・13:30・15:00（各回20分）',
  'venue': 'こども科学センター・ハチラボ（渋谷区桜丘町23-21、渋谷区文化総合センター大和田3F）',
  'price': '無料',
  'image': '',
  'description': '約20分のミニワークショップで、雪だるまのランプをつくる。未就学児は保護者といっしょにつくれる。無料。',
  'categories': ['科学・自然', '体験・ワークショップ'],
  'indoor_outdoor': '屋内',
  'reservation': {'required': True, 'note': '要申込（先着順）。開催日の1週間前0:00から受付。申込はp-gakushu.jp/hachilabo。'},
  'quotes': ['●開催期間：12月15日（火）～12月25日（金）', '（小3以下は保護者同伴/未就学児は保護者と作成）', '●申込：開催日の一週間前の0:00から先着順'],
  'overall': 'A',
  'basis': 'child_program',
  'child_activity': True,
  'reason': '12/15〜25に開く、未就学児も保護者といっしょにつくれる雪だるまランプづくり。無料で約20分。',
  'axes': {'child_target': 'A', 'interactivity': 'A', 'age_fit': 'A', 'stay_flexibility': 'B', 'burden': 'A', 'cost': 'A', 'reservation': 'C', 'family_value': 'A'},
  'strengths': ['未就学児も保護者といっしょにつくれる', 'クリスマス前の時期に、ランプを持ち帰れる'],
  'limitations': ['各回4名と少人数で、開催日の1週間前から先着順の申込が必要'],
  'comparison': '総合A：クリスマス前に開く、保護者といっしょにつくれる無料のランプ工作。先着順で少人数。',
  'status': 'verified',
  'price_field': 'pass',
  'positive': ['official_date_confirmed', 'child_activity_confirmed']},
 {'id': 'verified-20261212-shibuya-hachilabo-luminescence-chem-2026',
  'week': '2026-12-12',
  'ward': '渋谷区',
  'page': 'hachilabo_dec_20261123.html',
  'name': '【ワークショップ】発光の化学（ハチラボ）',
  'url': 'https://shibu-cul.jp/event/53568#luminescence',
  'date': '2026-12-12',
  'end': '2026-12-12',
  'period': '12/12(土)',
  'time': '14:00〜16:00（120分）',
  'venue': 'こども科学センター・ハチラボ（渋谷区桜丘町23-21、渋谷区文化総合センター大和田3F）',
  'price': '無料',
  'image': '',
  'description': '電気通信大学の先生が協力する、光る仕組みを学ぶ実験ワークショップ。小学5年生から中学生が対象で、無料。',
  'categories': ['科学・自然', '体験・ワークショップ'],
  'indoor_outdoor': '屋内',
  'reservation': {'required': True, 'note': '要申込（抽選）。受付は11/18 0:00〜11/25 23:59、当落連絡は11/28。申込はp-gakushu.jp/hachilabo。'},
  'quotes': ['●開催日：12月12日（土）', '●推奨年齢：小5～中学生', '●募集期間：11月18日（水）0:00～11月25日（水）23:59＜抽選＞'],
  'overall': 'B',
  'basis': 'child_program',
  'child_activity': True,
  'reason': '小5〜中学生向けの無料の化学実験。抽選で、受付は11/25まで。',
  'axes': {'child_target': 'A', 'interactivity': 'A', 'age_fit': 'C', 'stay_flexibility': 'C', 'burden': 'A', 'cost': 'A', 'reservation': 'C', 'family_value': 'B'},
  'strengths': ['大学の先生が協力する本格的な実験', '無料'],
  'limitations': ['小5〜中学生向けで、定員12名の抽選。受付は11/25 23:59まで'],
  'comparison': '総合B：高学年向けの無料実験。抽選で定員が少ない。',
  'status': 'verified',
  'price_field': 'pass',
  'positive': ['official_date_confirmed', 'child_activity_confirmed']},
 {'id': 'verified-20261219-shibuya-hachilabo-artemis-moon-2026',
  'week': '2026-12-19',
  'ward': '渋谷区',
  'page': 'hachilabo_dec_20261123.html',
  'name': '【ワークショップ】月へGO！アルテミス計画がえがく未来と月探査ミッションにチャレンジ！（ハチラボ）',
  'url': 'https://shibu-cul.jp/event/53568#artemis',
  'date': '2026-12-19',
  'end': '2026-12-19',
  'period': '12/19(土)',
  'time': '①10:30〜12:00 ②13:30〜15:00（各回90分）',
  'venue': 'こども科学センター・ハチラボ（渋谷区桜丘町23-21、渋谷区文化総合センター大和田3F）',
  'price': '無料',
  'image': '',
  'description': '月探査をテーマに、ミッションに挑戦しながら学ぶ体験型ワークショップ。小学3年生から6年生が対象で、無料。',
  'categories': ['科学・自然', '体験・ワークショップ'],
  'indoor_outdoor': '屋内',
  'reservation': {'required': True, 'note': '要申込（抽選）。受付は11/25 0:00〜12/2 23:59、当落連絡は12/5。申込はp-gakushu.jp/hachilabo。'},
  'quotes': ['●開催日：12月19日（土）', '●推奨年齢：小3～小6●定員：各回18名', '●募集期間：11月25日（水）0:00～12月2日（水）23:59＜抽選＞'],
  'overall': 'B',
  'basis': 'child_program',
  'child_activity': True,
  'reason': '小3〜小6向けの無料の月探査ミッション体験。抽選で、受付は11/25〜12/2。',
  'axes': {'child_target': 'A', 'interactivity': 'A', 'age_fit': 'B', 'stay_flexibility': 'C', 'burden': 'A', 'cost': 'A', 'reservation': 'C', 'family_value': 'B'},
  'strengths': ['月探査のミッションに挑戦する体験型', '無料で、各回18名と比較的多め'],
  'limitations': ['小3〜小6向けの抽選。受付は11/25 0:00〜12/2 23:59'],
  'comparison': '総合B：小学生向けの無料の宇宙体験。抽選で申込が必要。',
  'status': 'verified',
  'price_field': 'pass',
  'positive': ['official_date_confirmed', 'child_activity_confirmed']},
 {'id': 'verified-20261220-shibuya-hachilabo-semiconductor-xmas-2026',
  'week': '2026-12-19',
  'ward': '渋谷区',
  'page': 'hachilabo_dec_20261123.html',
  'name': '【ワークショップ】半導体のしくみを使った光るクリスマスオブジェづくり（ハチラボ）',
  'url': 'https://shibu-cul.jp/event/53568#semiconductor',
  'date': '2026-12-20',
  'end': '2026-12-20',
  'period': '12/20(日)',
  'time': '13:00〜15:00（120分）',
  'venue': 'こども科学センター・ハチラボ（渋谷区桜丘町23-21、渋谷区文化総合センター大和田3F）',
  'price': '無料',
  'image': '',
  'description': '半導体のしくみを使って、光るクリスマスオブジェをつくる。小学5年生から中学生が対象で、無料。',
  'categories': ['科学・自然', '体験・ワークショップ'],
  'indoor_outdoor': '屋内',
  'reservation': {'required': True, 'note': '要申込（抽選）。受付は11/25 0:00〜12/2 23:59、当落連絡は12/5。申込はp-gakushu.jp/hachilabo。'},
  'quotes': ['●開催日：12月20日（日）', '●推奨年齢：小5～中学生', '●募集期間：11月25日（水）0:00～12月2日（水）23:59＜抽選＞'],
  'overall': 'B',
  'basis': 'child_program',
  'child_activity': True,
  'reason': '小5〜中学生向けの無料のものづくり。光るクリスマスオブジェをつくる。抽選。',
  'axes': {'child_target': 'A', 'interactivity': 'A', 'age_fit': 'C', 'stay_flexibility': 'C', 'burden': 'A', 'cost': 'A', 'reservation': 'C', 'family_value': 'B'},
  'strengths': ['光るオブジェをつくって持ち帰れる', '無料'],
  'limitations': ['小5〜中学生向けで、定員12名の抽選。受付は12/2 23:59まで'],
  'comparison': '総合B：高学年向けの無料ものづくり。抽選で定員が少ない。',
  'status': 'verified',
  'price_field': 'pass',
  'positive': ['official_date_confirmed', 'child_activity_confirmed']},
 {'id': 'verified-20261226-shibuya-hachilabo-light-planet-2026',
  'week': '2026-12-26',
  'ward': '渋谷区',
  'page': 'hachilabo_dec_20261123.html',
  'name': '【ワークショップ】算数と光の実験で惑星のナゾを解き明かせ！（ハチラボ）',
  'url': 'https://shibu-cul.jp/event/53568#planet',
  'date': '2026-12-26',
  'end': '2026-12-26',
  'period': '12/26(土)',
  'time': '①10:30〜11:40 ②13:30〜14:40（各回70分）',
  'venue': 'こども科学センター・ハチラボ（渋谷区桜丘町23-21、渋谷区文化総合センター大和田3F）',
  'price': '無料',
  'image': '',
  'description': '宇宙展に関連して、算数と光の実験で惑星のナゾにせまるワークショップ。小学3年生から6年生が対象で、無料。',
  'categories': ['科学・自然', '体験・ワークショップ'],
  'indoor_outdoor': '屋内',
  'reservation': {'required': True, 'note': '要申込（抽選）。受付は12/2 0:00〜12/9 23:59、当落連絡は12/12。申込はp-gakushu.jp/hachilabo。'},
  'quotes': ['●開催日：12月26日（土）', '●推奨年齢：小3～小6（小3は保護者同伴）', '●募集期間：12月2日（水）0:00～12月9日（水）23:59＜抽選＞'],
  'overall': 'B',
  'basis': 'child_program',
  'child_activity': True,
  'reason': '小3〜小6向けの無料の実験。算数と光で惑星を調べる。抽選で、受付は12/2〜12/9。',
  'axes': {'child_target': 'A', 'interactivity': 'A', 'age_fit': 'B', 'stay_flexibility': 'C', 'burden': 'A', 'cost': 'A', 'reservation': 'C', 'family_value': 'B'},
  'strengths': ['算数と光の実験で惑星を学べる', '無料で、各回12名'],
  'limitations': ['小3〜小6向けの抽選。受付は12/2 0:00〜12/9 23:59'],
  'comparison': '総合B：小学生向けの無料の宇宙実験。抽選で申込が必要。',
  'status': 'verified',
  'price_field': 'pass',
  'positive': ['official_date_confirmed', 'child_activity_confirmed']},
 {'id': 'verified-20261227-shibuya-hachilabo-coin-bank-2026',
  'week': '2026-12-26',
  'ward': '渋谷区',
  'page': 'hachilabo_dec_20261123.html',
  'name': '【ワークショップ】コインが消える貯金箱（ハチラボ）',
  'url': 'https://shibu-cul.jp/event/53568#coin-bank',
  'date': '2026-12-27',
  'end': '2026-12-28',
  'period': '12/27(日)・12/28(月)',
  'time': '①10:30〜11:30 ②13:30〜14:30（各回60分）',
  'venue': 'こども科学センター・ハチラボ（渋谷区桜丘町23-21、渋谷区文化総合センター大和田3F）',
  'price': '無料',
  'image': '',
  'description': 'コインが消えたように見える貯金箱をつくる工作。小学1年生から6年生が対象で、無料。',
  'categories': ['科学・自然', '体験・ワークショップ'],
  'indoor_outdoor': '屋内',
  'reservation': {'required': True, 'note': '要申込（抽選）。受付は12/2 0:00〜12/9 23:59、当落連絡は12/12。申込はp-gakushu.jp/hachilabo。'},
  'quotes': ['●開催日：12月27日（日）、28日（月）', '●推奨年齢：小1～小6（小3以下は保護者同伴）', '●募集期間：12月2日（水）0:00～12月9日（水）23:59＜抽選＞'],
  'overall': 'A',
  'basis': 'child_program',
  'child_activity': True,
  'reason': '小1〜小6向けの無料の工作。2日間開くので日を選べる。抽選で、受付は12/2〜12/9。',
  'axes': {'child_target': 'A', 'interactivity': 'A', 'age_fit': 'A', 'stay_flexibility': 'B', 'burden': 'A', 'cost': 'A', 'reservation': 'C', 'family_value': 'A'},
  'strengths': ['小1から参加でき、無料', '2日間開くので日を選べる'],
  'limitations': ['各回8名の抽選。受付は12/2 0:00〜12/9 23:59'],
  'comparison': '総合A：小学生向けの無料の工作。抽選で、各回8名と少人数。',
  'status': 'verified',
  'price_field': 'pass',
  'positive': ['official_date_confirmed', 'child_activity_confirmed']}]

AXIS_REASON = {
    'child_target': {'A': '子ども・家族向けの内容', 'B': '対象の限定はなく、家族で楽しめる'},
    'interactivity': {'A': '体験や参加ができる', 'B': 'ステージを見ながら参加できる部分がある', 'C': '見て楽しむ内容が中心'},
    'age_fit': {'A': '幼児から参加できる', 'B': '年齢の限定はない'},
    'stay_flexibility': {'A': '期間が長く、好きな日に行ける', 'C': '決まった日・回に合わせる必要がある'},
    'burden': {'A': '短時間で気軽に立ち寄れる', 'B': '屋外のため、寒さと混雑に注意'},
    'cost': {'C': '有料で、費用がかかる', 'A': '無料', 'unknown': '公式ページに記載がない'},
    'reservation': {'A': '申込・予約の記載なし。当日行ける', 'C': '事前予約が必要'},
    'family_value': {'A': '子どもが楽しめる体験がある', 'B': '家族で楽しめる'},
}
AXIS_REASON['child_target']['A']='子ども向けの内容（公式ページに年齢の目安がある）'
AXIS_REASON['interactivity']['A']='つくる・実験するなど体験ができる'
AXIS_REASON['age_fit'].update({'A':'未就学児から参加できる','B':'小学生が対象','C':'小5〜中学生向け'})
AXIS_REASON['stay_flexibility'].update({'B':'日や時間帯を選べるが、回ごとの申込が必要'})
AXIS_REASON['burden']['A']='屋内で短時間。気軽に参加できる'
AXIS_REASON['cost']['A']='無料'
AXIS_REASON['reservation'].update({'A':'展示の観覧に申込の記載なし','C':'事前申込（先着順または抽選）が必要'})
AXIS_REASON['family_value'].update({'A':'子どもが楽しめる体験がある','B':'体験型で、家族の学びになる'})
for _s in SPECS_RAW:
    _s['axes'] = {k: (v, AXIS_REASON[k][v]) for k, v in _s['axes'].items()}

SPECS = [dict(_r) for _r in SPECS_RAW]
NEW_IDS = [s['id'] for s in SPECS]
SHARDS = {w: f'{w}-events-lead44-20261123.json' for w in ('2026-11-21', '2026-11-28', '2026-12-05', '2026-12-12', '2026-12-19', '2026-12-26')}
HELD = {
    'hachilabo-space-slime-20261121': '宇宙スライムすくい（11/21〜23）：11/23が最終日のため保留。',
    'hachilabo-flying-seed-20261123': '飛ぶ種の模型をつくろう（11/23）：抽選の受付が終了しているため掲載しない。',
    'hachilabo-cosmic-college-20261128': 'コズミックカレッジ（11/28）：抽選の受付が終了しているため掲載しない。',
    'hachilabo-color-play-20261205': '色あそび工作（12/5）：抽選の受付が終了しているため掲載しない。',
    'hachilabo-lecture-20261206-20261213': 'ハチラボ講座（人工イクラ12/6・ちきゅうをみつめて12/13）：渋谷区在住・在学の方限定のため掲載しない。',
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
                    'description': f"公式ページ（2026-11-23にHTTP200で取得、research/2026-11-20-thin-wards/pages/に不変保存）の本文引用。引用文字列だけのUTF-8 SHA-256。"})
    for x in spec.get('extra', []):
        t2 = _page_text(pathlib.Path(pages_dir) / x['page'])
        if S._strip(x['q']) not in t2:
            raise ValueError(f"{spec['id']}: calendar quote not found verbatim in the committed official calendar page: {x['q']}")
        out.append({'url': x['url'], 'quote': x['q'], 'checked_at': CHECKED,
                    'sha256': hashlib.sha256(x['q'].encode('utf-8')).hexdigest(),
                    'hash_scope': 'quoted_text_only_not_HTTP_response_hash',
                    'description': f"公式ページ（2026-11-23にHTTP200で取得、research/2026-11-20-thin-wards/pages/に不変保存）の本文引用。"})
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
               'evidence': [{'url': s['url'], 'basis': '2026-11-23 official individual event page (HTTP200); 23 ward completeness not asserted'}],
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
            row['note'] += f' 2026-11-22 公式個別ページ確認済み{k}件を非破壊追加。'
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
        run['lead44_addition_20261123'] = {
            'kind': 'individually_verified_official_events_from_lead_triage', 'added_ids': [i[0]['id'] for i in items],
            'held_not_published': sorted(HELD), 'pages_committed_at': 'research/2026-11-20-thin-wards/pages/',
            'base_data_production_sha': BASE, 'global_source_audit_complete': False}
        S.jdump(d / f'{week}-run.json', run)
        for x in m['weekends']:
            if x['sat'] == week:
                x['count'] += n
    m['generated'] = '2026-11-23T10:30:00+09:00'
    S.jdump(d / 'manifest.json', m)
    h = S.jload(d / 'update_history.json')
    h['history'].append({
        'run_id': 'lead44-addition-20261123', 'run_type': 'manual_verified_lead44_addition',
        'status': 'verified_subset_publication', 'as_of_jst': '2026-11-23', 'executed_at': m['generated'],
        'base_data_production_sha': BASE, 'target_weekends': sorted(derived),
        'prior_active_week_records': 793, 'candidate_active_week_records': 802, 'added_weekly_records': 9,
        'new_event_ids': NEW_IDS, 'held_not_published': sorted(HELD),
        'existing_event_records_physically_deleted': 0, 'image_only_updates': 0,
        'source_failures_remain_unverified': True, 'global_source_audit_complete': False,
        'full_23_ward_25_source_audit_complete': False,
        'note': '渋谷区文化総合センター大和田「こども科学センター・ハチラボ」の公式ページから、受付中・申込不要の9件を追加。杉並区の保留分は別途。'
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
