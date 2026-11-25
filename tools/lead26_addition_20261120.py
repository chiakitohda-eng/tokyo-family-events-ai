#!/usr/bin/env python3
"""1 weekly record (12/26 Nerima forest festival) from the committed official Nerima page (2026-11-20).

Raw official pages are committed unchanged under research/2026-11-20-thin-wards/pages/
(fetched by read-only workflows, HTTP 200). Quotes must occur verbatim in those pages.
The gate validator re-derives every record from this module and requires exact equality.
"""
import argparse, hashlib, json, pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import suginami_addition_20261118 as S

BASE = '3c2ac519ca2ceb86531448814220b828a64ca01b'   # data-production after the Nerima duplicate removal (673 active week records)
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


SPECS_RAW = [{'id': 'verified-20261121-mizunokagaku-suitekikun_dance', 'week': '2026-11-21', 'ward': '江東区', 'page': 'mizunokagaku_1121.html', 'name': '水滴くん♪のうたをみんなで踊ろう！（東京都水の科学館）', 'url': 'https://www.mizunokagaku.jp/event/261121_suitekikun_dance/', 'date': '2026-11-21', 'period': '11/21(土)', 'time': '①11:00〜 ②13:30〜', 'venue': '東京都水の科学館（江東区有明3-1-8）', 'price': '', 'description': '東京都水道局職員が作詞作曲した「水滴くん♪のうた」に合わせて、親子で踊るステージ。 小学生以下の子どもと保護者向けの催しで、整理券（各回の1時間前から配布、予約不可）が必要。', 'cats': ['科学', '水', '体験'], 'io': '屋内', 'res': {'required': False, 'note': '予約不可。各回1時間前から1Fインフォメーションで整理券を配布。'}, 'quotes': ['開催日：2026年11月21日(土)', '対象：小学生以下のお子様', '会場：1Fオリエンテーションルーム', '各回1時間前から1Fインフォメーションにて整理券を配布いたします。', '開催時間：①11:00～②13:30～'], 'basis': 'child_program', 'reason': '11/21(土)開催。水滴くん♪のうたをみんなで踊ろう！は、小学生以下のお子様を対象に、保護者同伴で参加する催し（各回先着10名）。', 'axes': {'child_target': ['A', '対象が小学生以下のお子様と明記され、保護者同伴で参加する子ども向けの催し'], 'interactivity': ['B', 'ステージや紙芝居を見て楽しむのが中心'], 'age_fit': ['A', '対象が小学生以下のお子様と明記'], 'stay_flexibility': ['B', '①11:00〜、②13:30〜の2回など、時間が決まっている'], 'burden': ['B', '整理券が必要で、定員（各回先着10名）に達すると参加できない'], 'cost': ['unknown', 'このページに参加費の記載がない'], 'reservation': ['C', '予約はできず、各回の1時間前から整理券を配布（各回先着10名）'], 'family_value': ['B', '親子で楽しみながら水について学べる']}, 'strengths': ['小学生以下向けで保護者と参加できる', '水の科学館の催しで学びがある'], 'limitations': ['参加費の記載がない', '整理券が必要で定員がある'], 'comparison': '総合B（11/21(土)）：小学生以下向けで学びのある催しだが、整理券が必要で定員が限られる。', 'pos': ['official_date_confirmed', 'child_activity_confirmed'], 'override': '', 'pf': 'pass', 'overall': 'B', 'child': True}, {'id': 'verified-20261122-mizunokagaku-nankyoku_blizzard', 'week': '2026-11-21', 'ward': '江東区', 'page': 'mizunokagaku_1122.html', 'name': '体感！南極ブリザード（東京都水の科学館）', 'url': 'https://www.mizunokagaku.jp/event/261122_nankyoku_blizzard/', 'date': '2026-11-22', 'period': '11/22(日)', 'time': '①11:00〜 ②13:30〜', 'venue': '東京都水の科学館（江東区有明3-1-8）', 'price': '', 'description': '部屋の中に南極のような環境を作り、水の驚きの変化を目の前で体感する実験ショー。講師はアインシュタインラボ。 小学生以下の子どもと保護者向けの催しで、整理券（各回の1時間前から配布、予約不可）が必要。', 'cats': ['科学', '水', '体験'], 'io': '屋内', 'res': {'required': False, 'note': '予約不可。各回1時間前から1Fインフォメーションで整理券を配布。'}, 'quotes': ['開催日：2026年11月22日(日)', '対象：小学生以下のお子様', '会場：1Fオリエンテーションルーム', '各回1時間前から1Fインフォメーションにて整理券を配布いたします。', '開催時間：①11:00～②13:30～'], 'basis': 'child_program', 'reason': '11/22(日)開催。体感！南極ブリザードは、小学生以下のお子様を対象に、保護者同伴で参加する催し（各回先着60名）。', 'axes': {'child_target': ['A', '対象が小学生以下のお子様と明記され、保護者同伴で参加する子ども向けの催し'], 'interactivity': ['A', '実験や工作、体験に参加できる'], 'age_fit': ['A', '対象が小学生以下のお子様と明記'], 'stay_flexibility': ['B', '①11:00〜、②13:30〜の2回など、時間が決まっている'], 'burden': ['B', '整理券が必要で、定員（各回先着60名）に達すると参加できない'], 'cost': ['unknown', 'このページに参加費の記載がない'], 'reservation': ['B', '予約はできず、各回の1時間前から整理券を配布（各回先着60名）'], 'family_value': ['A', '親子で水や科学を学び、体験できる']}, 'strengths': ['小学生以下向けで保護者と参加できる', '水の科学館の催しで学びがある'], 'limitations': ['参加費の記載がない', '整理券が必要で定員がある'], 'comparison': '総合B（11/22(日)）：小学生以下向けで学びのある催しだが、整理券が必要で定員が限られる。', 'pos': ['official_date_confirmed', 'child_activity_confirmed'], 'override': '', 'pf': 'pass', 'overall': 'B', 'child': True}, {'id': 'verified-20261123-mizunokagaku-kendamashow', 'week': '2026-11-21', 'ward': '江東区', 'page': 'mizunokagaku_1123.html', 'name': 'けん玉ショー＆ワークショップ（東京都水の科学館）', 'url': 'https://www.mizunokagaku.jp/event/261123_kendamashow/', 'date': '2026-11-23', 'period': '11/23(月・祝)', 'time': '①11:00〜 ②13:30〜', 'venue': '東京都水の科学館（江東区有明3-1-8）', 'price': '', 'description': 'ギネス世界記録を持つ演者のけん玉ショーと、けん玉を体験できるワークショップ。 小学生以下の子どもと保護者向けの催しで、整理券（各回の1時間前から配布、予約不可）が必要。', 'cats': ['科学', '水', '体験'], 'io': '屋内', 'res': {'required': False, 'note': '予約不可。各回1時間前から1Fインフォメーションで整理券を配布。'}, 'quotes': ['開催日：2026年11月23日(月・祝)', '対象：小学生以下のお子様', '会場：1Fオリエンテーションルーム', '各回1時間前から1Fインフォメーションにて整理券を配布いたします。', '開催時間：①11:00～②13:30～'], 'basis': 'child_program', 'reason': '11/23(月・祝)開催。けん玉ショー＆ワークショップは、小学生以下のお子様を対象に、保護者同伴で参加する催し（各回先着50名）。', 'axes': {'child_target': ['A', '対象が小学生以下のお子様と明記され、保護者同伴で参加する子ども向けの催し'], 'interactivity': ['A', '実験や工作、体験に参加できる'], 'age_fit': ['A', '対象が小学生以下のお子様と明記'], 'stay_flexibility': ['B', '①11:00〜、②13:30〜の2回など、時間が決まっている'], 'burden': ['B', '整理券が必要で、定員（各回先着50名）に達すると参加できない'], 'cost': ['unknown', 'このページに参加費の記載がない'], 'reservation': ['B', '予約はできず、各回の1時間前から整理券を配布（各回先着50名）'], 'family_value': ['A', '親子で水や科学を学び、体験できる']}, 'strengths': ['小学生以下向けで保護者と参加できる', '水の科学館の催しで学びがある'], 'limitations': ['参加費の記載がない', '整理券が必要で定員がある'], 'comparison': '総合B（11/23(月・祝)）：小学生以下向けで学びのある催しだが、整理券が必要で定員が限られる。', 'pos': ['official_date_confirmed', 'child_activity_confirmed'], 'override': '', 'pf': 'pass', 'overall': 'B', 'child': True}, {'id': 'verified-20261128-mizunokagaku-mori_ikimonotankentai', 'week': '2026-11-28', 'ward': '江東区', 'page': 'mizunokagaku_1128.html', 'name': '森のいきもの探検隊（東京都水の科学館）', 'url': 'https://www.mizunokagaku.jp/event/261128_mori_ikimonotankentai/', 'date': '2026-11-28', 'period': '11/28(土)', 'time': '①11:00〜 ②13:30〜', 'venue': '東京都水の科学館（江東区有明3-1-8）', 'price': '', 'description': '水源林に隠れた動物や虫たちを、3Fのアクアフォレストで探して回る参加型の催し。 小学生以下の子どもと保護者向けの催しで、整理券は不要で、直接会場へ行ける。', 'cats': ['科学', '水', '体験'], 'io': '屋内', 'res': {'required': False, 'note': '整理券なしで直接会場へ。'}, 'quotes': ['開催日：2026年11月28日(土)', '対象：小学生以下のお子様', '会場：3Fアクアフォレスト', '直接会場へお越しください。', '開催時間：①11:00～②13:30～'], 'basis': 'child_program', 'reason': '11/28(土)開催。森のいきもの探検隊は、小学生以下のお子様を対象に、保護者同伴で参加する催し（整理券なしの自由参加）。', 'axes': {'child_target': ['A', '対象が小学生以下のお子様と明記され、保護者同伴で参加する子ども向けの催し'], 'interactivity': ['A', '実験や工作、体験に参加できる'], 'age_fit': ['A', '対象が小学生以下のお子様と明記'], 'stay_flexibility': ['B', '①11:00〜、②13:30〜の2回など、時間が決まっている'], 'burden': ['B', '整理券は不要で、直接会場へ行ける'], 'cost': ['unknown', 'このページに参加費の記載がない'], 'reservation': ['A', '整理券なしの自由参加'], 'family_value': ['A', '親子で水や科学を学び、体験できる']}, 'strengths': ['小学生以下向けで保護者と参加できる', '水の科学館の催しで学びがある'], 'limitations': ['参加費の記載がない', '内容が変更・中止になることがある'], 'comparison': '総合B（11/28(土)）：小学生以下向けで学びのある催しだが、会場や内容が変更になることがある。', 'pos': ['official_date_confirmed', 'child_activity_confirmed'], 'override': '', 'pf': 'pass', 'overall': 'B', 'child': True}, {'id': 'verified-20261129-mizunokagaku-kids_sciense_challenge', 'week': '2026-11-28', 'ward': '江東区', 'page': 'mizunokagaku_1129.html', 'name': '子どもサイエンスチャレンジ「水と音の実験をしよう！」（東京都水の科学館）', 'url': 'https://www.mizunokagaku.jp/event/261129_kids_sciense_challenge/', 'date': '2026-11-29', 'period': '11/29(日)', 'time': '①11:00〜 ②13:30〜', 'venue': '東京都水の科学館（江東区有明3-1-8）', 'price': '', 'description': '目には見えない「音」が見えるようになる実験をして、水と音の関係を学ぶ。 小学生以下の子どもと保護者向けの催しで、整理券（各回の1時間前から配布、予約不可）が必要。', 'cats': ['科学', '水', '体験'], 'io': '屋内', 'res': {'required': False, 'note': '予約不可。各回1時間前から1Fインフォメーションで整理券を配布。'}, 'quotes': ['開催日：2026年11月29日(日)', '対象：小学生以下のお子様', '会場：1Fオリエンテーションルーム', '各回1時間前から1Fインフォメーションにて整理券を配布いたします。', '開催時間：①11:00～②13:30～'], 'basis': 'child_program', 'reason': '11/29(日)開催。子どもサイエンスチャレンジ「水と音の実験をしよう！」は、小学生以下のお子様を対象に、保護者同伴で参加する催し（各回先着10名）。', 'axes': {'child_target': ['A', '対象が小学生以下のお子様と明記され、保護者同伴で参加する子ども向けの催し'], 'interactivity': ['A', '実験や工作、体験に参加できる'], 'age_fit': ['A', '対象が小学生以下のお子様と明記'], 'stay_flexibility': ['B', '①11:00〜、②13:30〜の2回など、時間が決まっている'], 'burden': ['B', '整理券が必要で、定員（各回先着10名）に達すると参加できない'], 'cost': ['unknown', 'このページに参加費の記載がない'], 'reservation': ['C', '予約はできず、各回の1時間前から整理券を配布（各回先着10名）'], 'family_value': ['A', '親子で水や科学を学び、体験できる']}, 'strengths': ['小学生以下向けで保護者と参加できる', '水の科学館の催しで学びがある'], 'limitations': ['参加費の記載がない', '整理券が必要で定員がある'], 'comparison': '総合B（11/29(日)）：小学生以下向けで学びのある催しだが、整理券が必要で定員が限られる。', 'pos': ['official_date_confirmed', 'child_activity_confirmed'], 'override': '', 'pf': 'pass', 'overall': 'B', 'child': True}, {'id': 'verified-20261205-mizunokagaku-kamishibai_koguma', 'week': '2026-12-05', 'ward': '江東区', 'page': 'mizunokagaku_1205.html', 'name': '紙芝居「こぐまのみぃちゃんと水の森」（東京都水の科学館）', 'url': 'https://www.mizunokagaku.jp/event/261205_kamishibai_koguma/', 'date': '2026-12-05', 'period': '12/5(土)', 'time': '①11:00〜 ②13:30〜', 'venue': '東京都水の科学館（江東区有明3-1-8）', 'price': '', 'description': '水の科学館スタッフによる紙芝居。水道水源林を舞台にさまざまな動物が登場する。 小学生以下の子どもと保護者向けの催しで、整理券（各回の1時間前から配布、予約不可）が必要。', 'cats': ['科学', '水', '体験'], 'io': '屋内', 'res': {'required': False, 'note': '予約不可。各回1時間前から1Fインフォメーションで整理券を配布。'}, 'quotes': ['開催日：2026年12月5日(土)', '対象：小学生以下のお子様', '会場：1Fオリエンテーションルーム', '各回1時間前から1Fインフォメーションにて整理券を配布いたします。', '開催時間：①11:00～②13:30～'], 'basis': 'child_program', 'reason': '12/5(土)開催。紙芝居「こぐまのみぃちゃんと水の森」は、小学生以下のお子様を対象に、保護者同伴で参加する催し（各回50名）。', 'axes': {'child_target': ['A', '対象が小学生以下のお子様と明記され、保護者同伴で参加する子ども向けの催し'], 'interactivity': ['B', 'ステージや紙芝居を見て楽しむのが中心'], 'age_fit': ['A', '対象が小学生以下のお子様と明記'], 'stay_flexibility': ['B', '①11:00〜、②13:30〜の2回など、時間が決まっている'], 'burden': ['B', '整理券が必要で、定員（各回50名）に達すると参加できない'], 'cost': ['unknown', 'このページに参加費の記載がない'], 'reservation': ['B', '予約はできず、各回の1時間前から整理券を配布（各回50名）'], 'family_value': ['B', '親子で楽しみながら水について学べる']}, 'strengths': ['小学生以下向けで保護者と参加できる', '水の科学館の催しで学びがある'], 'limitations': ['参加費の記載がない', '整理券が必要で定員がある'], 'comparison': '総合B（12/5(土)）：小学生以下向けで学びのある催しだが、整理券が必要で定員が限られる。', 'pos': ['official_date_confirmed', 'child_activity_confirmed'], 'override': '', 'pf': 'pass', 'overall': 'B', 'child': True}, {'id': 'verified-20261206-mizunokagaku-kids_scienseshow', 'week': '2026-12-05', 'ward': '江東区', 'page': 'mizunokagaku_1206.html', 'name': '子どもサイエンスチャレンジ「実験ショーで知る東京都水道局の仕事」（東京都水の科学館）', 'url': 'https://www.mizunokagaku.jp/event/261206_kids_scienseshow/', 'date': '2026-12-06', 'period': '12/6(日)', 'time': '①11:00〜 ②13:30〜', 'venue': '東京都水の科学館（江東区有明3-1-8）', 'price': '', 'description': '水の実験を通じて、東京都水道局がどんな仕事をしているのかを学ぶ。 小学生以下の子どもと保護者向けの催しで、整理券（各回の1時間前から配布、予約不可）が必要。', 'cats': ['科学', '水', '体験'], 'io': '屋内', 'res': {'required': False, 'note': '予約不可。各回1時間前から1Fインフォメーションで整理券を配布。'}, 'quotes': ['開催日：2026年12月6日(日)', '対象：小学生以下のお子様', '会場：1Fオリエンテーションルーム', '各回1時間前から1Fインフォメーションにて整理券を配布いたします。', '開催時間：①11:00～②13:30～'], 'basis': 'child_program', 'reason': '12/6(日)開催。子どもサイエンスチャレンジ「実験ショーで知る東京都水道局の仕事」は、小学生以下のお子様を対象に、保護者同伴で参加する催し（各回先着10名）。', 'axes': {'child_target': ['A', '対象が小学生以下のお子様と明記され、保護者同伴で参加する子ども向けの催し'], 'interactivity': ['A', '実験や工作、体験に参加できる'], 'age_fit': ['A', '対象が小学生以下のお子様と明記'], 'stay_flexibility': ['B', '①11:00〜、②13:30〜の2回など、時間が決まっている'], 'burden': ['B', '整理券が必要で、定員（各回先着10名）に達すると参加できない'], 'cost': ['unknown', 'このページに参加費の記載がない'], 'reservation': ['C', '予約はできず、各回の1時間前から整理券を配布（各回先着10名）'], 'family_value': ['A', '親子で水や科学を学び、体験できる']}, 'strengths': ['小学生以下向けで保護者と参加できる', '水の科学館の催しで学びがある'], 'limitations': ['参加費の記載がない', '整理券が必要で定員がある'], 'comparison': '総合B（12/6(日)）：小学生以下向けで学びのある催しだが、整理券が必要で定員が限られる。', 'pos': ['official_date_confirmed', 'child_activity_confirmed'], 'override': '', 'pf': 'pass', 'overall': 'B', 'child': True}, {'id': 'verified-20261212-mizunokagaku-original_garland', 'week': '2026-12-12', 'ward': '江東区', 'page': 'mizunokagaku_1212.html', 'name': '親子でたのしく♪水の科学館オリジナルガーランドをつくろう！（東京都水の科学館）', 'url': 'https://www.mizunokagaku.jp/event/261212_original_garland/', 'date': '2026-12-12', 'period': '12/12(土)', 'time': '①11:00〜 ②13:30〜', 'venue': '東京都水の科学館（江東区有明3-1-8）', 'price': '', 'description': '「水の大循環」が学べるオリジナルガーランドを、おうちの方と一緒に作る工作ワークショップ。 小学生以下の子どもと保護者向けの催しで、整理券（各回の1時間前から配布、予約不可）が必要。', 'cats': ['科学', '水', '体験'], 'io': '屋内', 'res': {'required': False, 'note': '予約不可。各回1時間前から1Fインフォメーションで整理券を配布。'}, 'quotes': ['開催日：2026年12月12日(土)', '対象：小学生以下のお子様', '会場：1Fオリエンテーションルーム', '各回1時間前から1Fインフォメーションにて整理券を配布いたします。', '開催時間：①11:00～②13:30～'], 'basis': 'child_program', 'reason': '12/12(土)開催。親子でたのしく♪水の科学館オリジナルガーランドをつくろう！は、小学生以下のお子様を対象に、保護者同伴で参加する催し（各回先着10名）。', 'axes': {'child_target': ['A', '対象が小学生以下のお子様と明記され、保護者同伴で参加する子ども向けの催し'], 'interactivity': ['A', '実験や工作、体験に参加できる'], 'age_fit': ['A', '対象が小学生以下のお子様と明記'], 'stay_flexibility': ['B', '①11:00〜、②13:30〜の2回など、時間が決まっている'], 'burden': ['B', '整理券が必要で、定員（各回先着10名）に達すると参加できない'], 'cost': ['unknown', 'このページに参加費の記載がない'], 'reservation': ['C', '予約はできず、各回の1時間前から整理券を配布（各回先着10名）'], 'family_value': ['A', '親子で水や科学を学び、体験できる']}, 'strengths': ['小学生以下向けで保護者と参加できる', '水の科学館の催しで学びがある'], 'limitations': ['参加費の記載がない', '整理券が必要で定員がある'], 'comparison': '総合B（12/12(土)）：小学生以下向けで学びのある催しだが、整理券が必要で定員が限られる。', 'pos': ['official_date_confirmed', 'child_activity_confirmed'], 'override': '', 'pf': 'pass', 'overall': 'B', 'child': True}, {'id': 'verified-20261219-mizunokagaku-kamishibai_drop', 'week': '2026-12-19', 'ward': '江東区', 'page': 'mizunokagaku_1219.html', 'name': '紙芝居「ドロップちゃんの大冒険」（東京都水の科学館）', 'url': 'https://www.mizunokagaku.jp/event/261219_kamishibai_drop/', 'date': '2026-12-19', 'period': '12/19(土)', 'time': '①11:00〜 ②13:30〜', 'venue': '東京都水の科学館（江東区有明3-1-8）', 'price': '', 'description': '水の科学館スタッフによる紙芝居。物語を通じて「水の大循環」を楽しく学べる。 小学生以下の子どもと保護者向けの催しで、整理券（各回の1時間前から配布、予約不可）が必要。', 'cats': ['科学', '水', '体験'], 'io': '屋内', 'res': {'required': False, 'note': '予約不可。各回1時間前から1Fインフォメーションで整理券を配布。'}, 'quotes': ['開催日：2026年12月19日(土)', '対象：小学生以下のお子様', '会場：1Fオリエンテーションルーム', '各回1時間前から1Fインフォメーションにて整理券を配布いたします。', '開催時間：①11:00～②13:30～'], 'basis': 'child_program', 'reason': '12/19(土)開催。紙芝居「ドロップちゃんの大冒険」は、小学生以下のお子様を対象に、保護者同伴で参加する催し（各回50名）。', 'axes': {'child_target': ['A', '対象が小学生以下のお子様と明記され、保護者同伴で参加する子ども向けの催し'], 'interactivity': ['B', 'ステージや紙芝居を見て楽しむのが中心'], 'age_fit': ['A', '対象が小学生以下のお子様と明記'], 'stay_flexibility': ['B', '①11:00〜、②13:30〜の2回など、時間が決まっている'], 'burden': ['B', '整理券が必要で、定員（各回50名）に達すると参加できない'], 'cost': ['unknown', 'このページに参加費の記載がない'], 'reservation': ['B', '予約はできず、各回の1時間前から整理券を配布（各回50名）'], 'family_value': ['B', '親子で楽しみながら水について学べる']}, 'strengths': ['小学生以下向けで保護者と参加できる', '水の科学館の催しで学びがある'], 'limitations': ['参加費の記載がない', '整理券が必要で定員がある'], 'comparison': '総合B（12/19(土)）：小学生以下向けで学びのある催しだが、整理券が必要で定員が限られる。', 'pos': ['official_date_confirmed', 'child_activity_confirmed'], 'override': '', 'pf': 'pass', 'overall': 'B', 'child': True}, {'id': 'verified-20261220-mizunokagaku-tubc_free_throw', 'week': '2026-12-19', 'ward': '江東区', 'page': 'mizunokagaku_1220.html', 'name': 'フリースローチャレンジ（東京都水の科学館）', 'url': 'https://www.mizunokagaku.jp/event/261220_tubc_free_throw/', 'date': '2026-12-20', 'period': '12/20(日)', 'time': '10:00〜16:00', 'venue': '東京都水の科学館（江東区有明3-1-8）', 'price': '', 'description': '東京ベイタウンエリアで活動する東京ユナイテッドBCが主催する、フリースローに挑戦する催し。 小学生以下の子どもと保護者向けの催しで、整理券は不要で、直接会場へ行ける。', 'cats': ['科学', '水', '体験'], 'io': '屋内', 'res': {'required': False, 'note': '整理券なしで直接会場へ。'}, 'quotes': ['開催日：2026年12月20日(日)', '対象：小学生以下のお子様', '会場：1Fオリエンテーションルーム', '直接会場へお越しください。', '開催時間：10:00～16:00'], 'basis': 'child_program', 'reason': '12/20(日)開催。フリースローチャレンジは、小学生以下のお子様を対象に、保護者同伴で参加する催し（整理券なしの自由参加）。', 'axes': {'child_target': ['A', '対象が小学生以下のお子様と明記され、保護者同伴で参加する子ども向けの催し'], 'interactivity': ['A', '実験や工作、体験に参加できる'], 'age_fit': ['A', '対象が小学生以下のお子様と明記'], 'stay_flexibility': ['B', '10:00〜16:00の間に好きな時間に参加できる'], 'burden': ['B', '整理券は不要で、直接会場へ行ける'], 'cost': ['unknown', 'このページに参加費の記載がない'], 'reservation': ['A', '整理券なしの自由参加'], 'family_value': ['A', '親子で水や科学を学び、体験できる']}, 'strengths': ['小学生以下向けで保護者と参加できる', '水の科学館の催しで学びがある'], 'limitations': ['参加費の記載がない', '内容が変更・中止になることがある'], 'comparison': '総合B（12/20(日)）：小学生以下向けで学びのある催しだが、会場や内容が変更になることがある。', 'pos': ['official_date_confirmed', 'child_activity_confirmed'], 'override': '', 'pf': 'pass', 'overall': 'B', 'child': True}, {'id': 'verified-20261227-mizunokagaku-clown_rio', 'week': '2026-12-26', 'ward': '江東区', 'page': 'mizunokagaku_1227.html', 'name': 'クラウン・リオのパフォーマンスショー（東京都水の科学館）', 'url': 'https://www.mizunokagaku.jp/event/261227_clown_rio/', 'date': '2026-12-27', 'period': '12/27(日)', 'time': '①11:00〜 ②13:30〜', 'venue': '東京都水の科学館（江東区有明3-1-8）', 'price': '', 'description': 'バルーンアート、ジャグリング、水のマジックが楽しめるミニサーカス。 小学生以下の子どもと保護者向けの催しで、整理券（各回の1時間前から配布、予約不可）が必要。', 'cats': ['科学', '水', '体験'], 'io': '屋内', 'res': {'required': False, 'note': '予約不可。各回1時間前から1Fインフォメーションで整理券を配布。'}, 'quotes': ['開催日：2026年12月27日(日)', '※当イベントは小学生以下のお子様を対象としております。', '会場：1Fオリエンテーションルーム', '各回1時間前から1Fインフォメーションにて整理券を配布いたします。', '開催時間：①11:00～②13:30～'], 'basis': 'child_program', 'reason': '12/27(日)開催。クラウン・リオのパフォーマンスショーは、小学生以下のお子様を対象に、保護者同伴で参加する催し（各回先着60名）。', 'axes': {'child_target': ['A', '対象が小学生以下のお子様と明記され、保護者同伴で参加する子ども向けの催し'], 'interactivity': ['B', 'ステージや紙芝居を見て楽しむのが中心'], 'age_fit': ['A', '対象が小学生以下のお子様と明記'], 'stay_flexibility': ['B', '①11:00〜、②13:30〜の2回など、時間が決まっている'], 'burden': ['B', '整理券が必要で、定員（各回先着60名）に達すると参加できない'], 'cost': ['unknown', 'このページに参加費の記載がない'], 'reservation': ['B', '予約はできず、各回の1時間前から整理券を配布（各回先着60名）'], 'family_value': ['B', '親子で楽しみながら水について学べる']}, 'strengths': ['小学生以下向けで保護者と参加できる', '水の科学館の催しで学びがある'], 'limitations': ['参加費の記載がない', '整理券が必要で定員がある'], 'comparison': '総合B（12/27(日)）：小学生以下向けで学びのある催しだが、整理券が必要で定員が限られる。', 'pos': ['official_date_confirmed', 'child_activity_confirmed'], 'override': '', 'pf': 'pass', 'overall': 'B', 'child': True}]
RAW = SPECS_RAW
SPECS = []
for _r in RAW:
    _s = dict(_r)
    _s['categories'] = _s.pop('cats'); _s['indoor_outdoor'] = _s.pop('io'); _s['reservation'] = _s.pop('res')
    _s['child_activity'] = _s.pop('child'); _s['price_field'] = _s.pop('pf'); _s['positive'] = _s.pop('pos')
    SPECS.append(_s)
NEW_IDS = [s['id'] for s in SPECS]
SHARDS = {w: f'{w}-events-lead26-20261120.json' for w in ('2026-11-21', '2026-11-28', '2026-12-05', '2026-12-12', '2026-12-19', '2026-12-26')}
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
        run['lead26_addition_20261120'] = {
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
        'run_id': 'lead26-addition-20261120', 'run_type': 'manual_verified_lead26_addition',
        'status': 'verified_subset_publication', 'as_of_jst': '2026-11-20', 'executed_at': m['generated'],
        'base_data_production_sha': BASE, 'target_weekends': sorted(derived),
        'prior_active_week_records': 673, 'candidate_active_week_records': 684, 'added_weekly_records': 11,
        'new_event_ids': NEW_IDS, 'held_not_published': sorted(HELD),
        'existing_event_records_physically_deleted': 0, 'image_only_updates': 0,
        'source_failures_remain_unverified': True, 'global_source_audit_complete': False,
        'full_23_ward_25_source_audit_complete': False,
        'note': '東京都の公園管理者・東京都水の科学館の公式ページで日付・時間・会場・条件を確認できた11件のみ追加。',
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
