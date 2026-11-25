#!/usr/bin/env python3
"""1 weekly record (12/26 Nerima forest festival) from the committed official Nerima page (2026-11-20).

Raw official pages are committed unchanged under research/2026-11-20-thin-wards/pages/
(fetched by read-only workflows, HTTP 200). Quotes must occur verbatim in those pages.
The gate validator re-derives every record from this module and requires exact equality.
"""
import argparse, hashlib, json, pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import suginami_addition_20261118 as S

BASE = '22e4a457ceadb6a313cd631a270f1c950f5f39ba'   # data-production after the Nerima duplicate removal (689 active week records)
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


SPECS_RAW = [{'id': 'verified-20261121-sumida-aquarium-kingyo', 'week': '2026-11-21', 'ward': '墨田区', 'page': 'sumida_kingyo_1121.html', 'name': 'きんぎょ色合わせ（すみだ水族館）', 'url': 'https://www.sumida-aquarium.com/event/fu355-12q/', 'date': '2026-11-21', 'period': '11/21(土)', 'time': '10:00〜17:00（最終受付16:30）', 'venue': 'すみだ水族館 5階アクアアカデミー（墨田区押上1-1-2）', 'price': '参加無料（水族館の入場料は別途必要）', 'description': '金魚の形の台紙に色紙をちぎって貼り、ちぎり絵で金魚の模様を作るワークショップ。完成した金魚は持ち帰れる。当日受付で、参加は無料（入場料は別途必要）。', 'cats': ['水族館', '工作', '体験'], 'io': '屋内', 'res': {'required': False, 'note': '当日受付。定員になり次第終了。'}, 'quotes': ['開催期間2026年11月17日（火）～2026年12月10日（木）', '土日祝日：午前10時～午後5時（最終受付：午後4時30分）', '参加費無料入場料は別途必要となります。', '参加方法当日受付ワークショッ', '金魚の形をした台紙に赤・白・黒など5色の色紙をちぎって貼り付け'], 'basis': 'unspecified', 'overall': 'C', 'override': '水族館の無料の工作ワークショップで子どもも参加できる見込みだが、公式ページに対象年齢の記載がなく、入場料も別に必要なため、条件つきの総合Cとして掲載する。', 'reason': '11/21(土)開催。すみだ水族館の無料ワークショップ「きんぎょ色合わせ」で、当日受付で参加できる。水族館の入場料は別に必要。', 'axes': {'child_target': ['unknown', '子ども向けとは明記されていない'], 'interactivity': ['A', '工作を作って参加できる'], 'age_fit': ['unknown', '対象年齢が明記されていない'], 'stay_flexibility': ['A', '10:00〜17:00の間に好きな時間に参加でき、短時間で終わる'], 'burden': ['B', '定員になり次第終了となる場合がある'], 'cost': ['B', 'ワークショップは無料だが、水族館の入場料が必要'], 'reservation': ['A', '予約不要の当日受付'], 'family_value': ['B', '水族館で工作をして持ち帰れる']}, 'strengths': ['ワークショップは無料で予約不要', '好きな時間に参加できる'], 'limitations': ['対象年齢の記載がない', '水族館の入場料が必要'], 'comparison': '総合C（きんぎょ色合わせ・11/21(土)）：無料で予約不要の工作だが、対象年齢の記載がなく、入場料が別に必要。', 'pos': ['official_date_confirmed', 'child_activity_confirmed'], 'pf': 'pass', 'child': True}, {'id': 'verified-20261122-sumida-aquarium-kingyo', 'week': '2026-11-21', 'ward': '墨田区', 'page': 'sumida_kingyo_1121.html', 'name': 'きんぎょ色合わせ（すみだ水族館）', 'url': 'https://www.sumida-aquarium.com/event/fu355-12q/', 'date': '2026-11-22', 'period': '11/22(日)', 'time': '10:00〜17:00（最終受付16:30）', 'venue': 'すみだ水族館 5階アクアアカデミー（墨田区押上1-1-2）', 'price': '参加無料（水族館の入場料は別途必要）', 'description': '金魚の形の台紙に色紙をちぎって貼り、ちぎり絵で金魚の模様を作るワークショップ。完成した金魚は持ち帰れる。当日受付で、参加は無料（入場料は別途必要）。', 'cats': ['水族館', '工作', '体験'], 'io': '屋内', 'res': {'required': False, 'note': '当日受付。定員になり次第終了。'}, 'quotes': ['開催期間2026年11月17日（火）～2026年12月10日（木）', '土日祝日：午前10時～午後5時（最終受付：午後4時30分）', '参加費無料入場料は別途必要となります。', '参加方法当日受付ワークショッ', '金魚の形をした台紙に赤・白・黒など5色の色紙をちぎって貼り付け'], 'basis': 'unspecified', 'overall': 'C', 'override': '水族館の無料の工作ワークショップで子どもも参加できる見込みだが、公式ページに対象年齢の記載がなく、入場料も別に必要なため、条件つきの総合Cとして掲載する。', 'reason': '11/22(日)開催。すみだ水族館の無料ワークショップ「きんぎょ色合わせ」で、当日受付で参加できる。水族館の入場料は別に必要。', 'axes': {'child_target': ['unknown', '子ども向けとは明記されていない'], 'interactivity': ['A', '工作を作って参加できる'], 'age_fit': ['unknown', '対象年齢が明記されていない'], 'stay_flexibility': ['A', '10:00〜17:00の間に好きな時間に参加でき、短時間で終わる'], 'burden': ['B', '定員になり次第終了となる場合がある'], 'cost': ['B', 'ワークショップは無料だが、水族館の入場料が必要'], 'reservation': ['A', '予約不要の当日受付'], 'family_value': ['B', '水族館で工作をして持ち帰れる']}, 'strengths': ['ワークショップは無料で予約不要', '好きな時間に参加できる'], 'limitations': ['対象年齢の記載がない', '水族館の入場料が必要'], 'comparison': '総合C（きんぎょ色合わせ・11/22(日)）：無料で予約不要の工作だが、対象年齢の記載がなく、入場料が別に必要。', 'pos': ['official_date_confirmed', 'child_activity_confirmed'], 'pf': 'pass', 'child': True}, {'id': 'verified-20261123-sumida-aquarium-kingyo', 'week': '2026-11-21', 'ward': '墨田区', 'page': 'sumida_kingyo_1121.html', 'name': 'きんぎょ色合わせ（すみだ水族館）', 'url': 'https://www.sumida-aquarium.com/event/fu355-12q/', 'date': '2026-11-23', 'period': '11/23(月・祝)', 'time': '10:00〜17:00（最終受付16:30）', 'venue': 'すみだ水族館 5階アクアアカデミー（墨田区押上1-1-2）', 'price': '参加無料（水族館の入場料は別途必要）', 'description': '金魚の形の台紙に色紙をちぎって貼り、ちぎり絵で金魚の模様を作るワークショップ。完成した金魚は持ち帰れる。当日受付で、参加は無料（入場料は別途必要）。', 'cats': ['水族館', '工作', '体験'], 'io': '屋内', 'res': {'required': False, 'note': '当日受付。定員になり次第終了。'}, 'quotes': ['開催期間2026年11月17日（火）～2026年12月10日（木）', '土日祝日：午前10時～午後5時（最終受付：午後4時30分）', '参加費無料入場料は別途必要となります。', '参加方法当日受付ワークショッ', '金魚の形をした台紙に赤・白・黒など5色の色紙をちぎって貼り付け'], 'basis': 'unspecified', 'overall': 'C', 'override': '水族館の無料の工作ワークショップで子どもも参加できる見込みだが、公式ページに対象年齢の記載がなく、入場料も別に必要なため、条件つきの総合Cとして掲載する。', 'reason': '11/23(月・祝)開催。すみだ水族館の無料ワークショップ「きんぎょ色合わせ」で、当日受付で参加できる。水族館の入場料は別に必要。', 'axes': {'child_target': ['unknown', '子ども向けとは明記されていない'], 'interactivity': ['A', '工作を作って参加できる'], 'age_fit': ['unknown', '対象年齢が明記されていない'], 'stay_flexibility': ['A', '10:00〜17:00の間に好きな時間に参加でき、短時間で終わる'], 'burden': ['B', '定員になり次第終了となる場合がある'], 'cost': ['B', 'ワークショップは無料だが、水族館の入場料が必要'], 'reservation': ['A', '予約不要の当日受付'], 'family_value': ['B', '水族館で工作をして持ち帰れる']}, 'strengths': ['ワークショップは無料で予約不要', '好きな時間に参加できる'], 'limitations': ['対象年齢の記載がない', '水族館の入場料が必要'], 'comparison': '総合C（きんぎょ色合わせ・11/23(月・祝)）：無料で予約不要の工作だが、対象年齢の記載がなく、入場料が別に必要。', 'pos': ['official_date_confirmed', 'child_activity_confirmed'], 'pf': 'pass', 'child': True}, {'id': 'verified-20261128-sumida-aquarium-kingyo', 'week': '2026-11-28', 'ward': '墨田区', 'page': 'sumida_kingyo_1121.html', 'name': 'きんぎょ色合わせ（すみだ水族館）', 'url': 'https://www.sumida-aquarium.com/event/fu355-12q/', 'date': '2026-11-28', 'period': '11/28(土)', 'time': '10:00〜17:00（最終受付16:30）', 'venue': 'すみだ水族館 5階アクアアカデミー（墨田区押上1-1-2）', 'price': '参加無料（水族館の入場料は別途必要）', 'description': '金魚の形の台紙に色紙をちぎって貼り、ちぎり絵で金魚の模様を作るワークショップ。完成した金魚は持ち帰れる。当日受付で、参加は無料（入場料は別途必要）。', 'cats': ['水族館', '工作', '体験'], 'io': '屋内', 'res': {'required': False, 'note': '当日受付。定員になり次第終了。'}, 'quotes': ['開催期間2026年11月17日（火）～2026年12月10日（木）', '土日祝日：午前10時～午後5時（最終受付：午後4時30分）', '参加費無料入場料は別途必要となります。', '参加方法当日受付ワークショッ', '金魚の形をした台紙に赤・白・黒など5色の色紙をちぎって貼り付け'], 'basis': 'unspecified', 'overall': 'C', 'override': '水族館の無料の工作ワークショップで子どもも参加できる見込みだが、公式ページに対象年齢の記載がなく、入場料も別に必要なため、条件つきの総合Cとして掲載する。', 'reason': '11/28(土)開催。すみだ水族館の無料ワークショップ「きんぎょ色合わせ」で、当日受付で参加できる。水族館の入場料は別に必要。', 'axes': {'child_target': ['unknown', '子ども向けとは明記されていない'], 'interactivity': ['A', '工作を作って参加できる'], 'age_fit': ['unknown', '対象年齢が明記されていない'], 'stay_flexibility': ['A', '10:00〜17:00の間に好きな時間に参加でき、短時間で終わる'], 'burden': ['B', '定員になり次第終了となる場合がある'], 'cost': ['B', 'ワークショップは無料だが、水族館の入場料が必要'], 'reservation': ['A', '予約不要の当日受付'], 'family_value': ['B', '水族館で工作をして持ち帰れる']}, 'strengths': ['ワークショップは無料で予約不要', '好きな時間に参加できる'], 'limitations': ['対象年齢の記載がない', '水族館の入場料が必要'], 'comparison': '総合C（きんぎょ色合わせ・11/28(土)）：無料で予約不要の工作だが、対象年齢の記載がなく、入場料が別に必要。', 'pos': ['official_date_confirmed', 'child_activity_confirmed'], 'pf': 'pass', 'child': True}, {'id': 'verified-20261129-sumida-aquarium-kingyo', 'week': '2026-11-28', 'ward': '墨田区', 'page': 'sumida_kingyo_1121.html', 'name': 'きんぎょ色合わせ（すみだ水族館）', 'url': 'https://www.sumida-aquarium.com/event/fu355-12q/', 'date': '2026-11-29', 'period': '11/29(日)', 'time': '10:00〜17:00（最終受付16:30）', 'venue': 'すみだ水族館 5階アクアアカデミー（墨田区押上1-1-2）', 'price': '参加無料（水族館の入場料は別途必要）', 'description': '金魚の形の台紙に色紙をちぎって貼り、ちぎり絵で金魚の模様を作るワークショップ。完成した金魚は持ち帰れる。当日受付で、参加は無料（入場料は別途必要）。', 'cats': ['水族館', '工作', '体験'], 'io': '屋内', 'res': {'required': False, 'note': '当日受付。定員になり次第終了。'}, 'quotes': ['開催期間2026年11月17日（火）～2026年12月10日（木）', '土日祝日：午前10時～午後5時（最終受付：午後4時30分）', '参加費無料入場料は別途必要となります。', '参加方法当日受付ワークショッ', '金魚の形をした台紙に赤・白・黒など5色の色紙をちぎって貼り付け'], 'basis': 'unspecified', 'overall': 'C', 'override': '水族館の無料の工作ワークショップで子どもも参加できる見込みだが、公式ページに対象年齢の記載がなく、入場料も別に必要なため、条件つきの総合Cとして掲載する。', 'reason': '11/29(日)開催。すみだ水族館の無料ワークショップ「きんぎょ色合わせ」で、当日受付で参加できる。水族館の入場料は別に必要。', 'axes': {'child_target': ['unknown', '子ども向けとは明記されていない'], 'interactivity': ['A', '工作を作って参加できる'], 'age_fit': ['unknown', '対象年齢が明記されていない'], 'stay_flexibility': ['A', '10:00〜17:00の間に好きな時間に参加でき、短時間で終わる'], 'burden': ['B', '定員になり次第終了となる場合がある'], 'cost': ['B', 'ワークショップは無料だが、水族館の入場料が必要'], 'reservation': ['A', '予約不要の当日受付'], 'family_value': ['B', '水族館で工作をして持ち帰れる']}, 'strengths': ['ワークショップは無料で予約不要', '好きな時間に参加できる'], 'limitations': ['対象年齢の記載がない', '水族館の入場料が必要'], 'comparison': '総合C（きんぎょ色合わせ・11/29(日)）：無料で予約不要の工作だが、対象年齢の記載がなく、入場料が別に必要。', 'pos': ['official_date_confirmed', 'child_activity_confirmed'], 'pf': 'pass', 'child': True}, {'id': 'verified-20261205-sumida-aquarium-kingyo', 'week': '2026-12-05', 'ward': '墨田区', 'page': 'sumida_kingyo_1121.html', 'name': 'きんぎょ色合わせ（すみだ水族館）', 'url': 'https://www.sumida-aquarium.com/event/fu355-12q/', 'date': '2026-12-05', 'period': '12/5(土)', 'time': '10:00〜17:00（最終受付16:30）', 'venue': 'すみだ水族館 5階アクアアカデミー（墨田区押上1-1-2）', 'price': '参加無料（水族館の入場料は別途必要）', 'description': '金魚の形の台紙に色紙をちぎって貼り、ちぎり絵で金魚の模様を作るワークショップ。完成した金魚は持ち帰れる。当日受付で、参加は無料（入場料は別途必要）。', 'cats': ['水族館', '工作', '体験'], 'io': '屋内', 'res': {'required': False, 'note': '当日受付。定員になり次第終了。'}, 'quotes': ['開催期間2026年11月17日（火）～2026年12月10日（木）', '土日祝日：午前10時～午後5時（最終受付：午後4時30分）', '参加費無料入場料は別途必要となります。', '参加方法当日受付ワークショッ', '金魚の形をした台紙に赤・白・黒など5色の色紙をちぎって貼り付け'], 'basis': 'unspecified', 'overall': 'C', 'override': '水族館の無料の工作ワークショップで子どもも参加できる見込みだが、公式ページに対象年齢の記載がなく、入場料も別に必要なため、条件つきの総合Cとして掲載する。', 'reason': '12/5(土)開催。すみだ水族館の無料ワークショップ「きんぎょ色合わせ」で、当日受付で参加できる。水族館の入場料は別に必要。', 'axes': {'child_target': ['unknown', '子ども向けとは明記されていない'], 'interactivity': ['A', '工作を作って参加できる'], 'age_fit': ['unknown', '対象年齢が明記されていない'], 'stay_flexibility': ['A', '10:00〜17:00の間に好きな時間に参加でき、短時間で終わる'], 'burden': ['B', '定員になり次第終了となる場合がある'], 'cost': ['B', 'ワークショップは無料だが、水族館の入場料が必要'], 'reservation': ['A', '予約不要の当日受付'], 'family_value': ['B', '水族館で工作をして持ち帰れる']}, 'strengths': ['ワークショップは無料で予約不要', '好きな時間に参加できる'], 'limitations': ['対象年齢の記載がない', '水族館の入場料が必要'], 'comparison': '総合C（きんぎょ色合わせ・12/5(土)）：無料で予約不要の工作だが、対象年齢の記載がなく、入場料が別に必要。', 'pos': ['official_date_confirmed', 'child_activity_confirmed'], 'pf': 'pass', 'child': True}, {'id': 'verified-20261206-sumida-aquarium-kingyo', 'week': '2026-12-05', 'ward': '墨田区', 'page': 'sumida_kingyo_1121.html', 'name': 'きんぎょ色合わせ（すみだ水族館）', 'url': 'https://www.sumida-aquarium.com/event/fu355-12q/', 'date': '2026-12-06', 'period': '12/6(日)', 'time': '10:00〜17:00（最終受付16:30）', 'venue': 'すみだ水族館 5階アクアアカデミー（墨田区押上1-1-2）', 'price': '参加無料（水族館の入場料は別途必要）', 'description': '金魚の形の台紙に色紙をちぎって貼り、ちぎり絵で金魚の模様を作るワークショップ。完成した金魚は持ち帰れる。当日受付で、参加は無料（入場料は別途必要）。', 'cats': ['水族館', '工作', '体験'], 'io': '屋内', 'res': {'required': False, 'note': '当日受付。定員になり次第終了。'}, 'quotes': ['開催期間2026年11月17日（火）～2026年12月10日（木）', '土日祝日：午前10時～午後5時（最終受付：午後4時30分）', '参加費無料入場料は別途必要となります。', '参加方法当日受付ワークショッ', '金魚の形をした台紙に赤・白・黒など5色の色紙をちぎって貼り付け'], 'basis': 'unspecified', 'overall': 'C', 'override': '水族館の無料の工作ワークショップで子どもも参加できる見込みだが、公式ページに対象年齢の記載がなく、入場料も別に必要なため、条件つきの総合Cとして掲載する。', 'reason': '12/6(日)開催。すみだ水族館の無料ワークショップ「きんぎょ色合わせ」で、当日受付で参加できる。水族館の入場料は別に必要。', 'axes': {'child_target': ['unknown', '子ども向けとは明記されていない'], 'interactivity': ['A', '工作を作って参加できる'], 'age_fit': ['unknown', '対象年齢が明記されていない'], 'stay_flexibility': ['A', '10:00〜17:00の間に好きな時間に参加でき、短時間で終わる'], 'burden': ['B', '定員になり次第終了となる場合がある'], 'cost': ['B', 'ワークショップは無料だが、水族館の入場料が必要'], 'reservation': ['A', '予約不要の当日受付'], 'family_value': ['B', '水族館で工作をして持ち帰れる']}, 'strengths': ['ワークショップは無料で予約不要', '好きな時間に参加できる'], 'limitations': ['対象年齢の記載がない', '水族館の入場料が必要'], 'comparison': '総合C（きんぎょ色合わせ・12/6(日)）：無料で予約不要の工作だが、対象年齢の記載がなく、入場料が別に必要。', 'pos': ['official_date_confirmed', 'child_activity_confirmed'], 'pf': 'pass', 'child': True}, {'id': 'verified-20261212-sumida-aquarium-penguin-calendar', 'week': '2026-12-12', 'ward': '墨田区', 'page': 'sumida_penguin_calendar_1212.html', 'name': 'ペンギンカレンダー（すみだ水族館）', 'url': 'https://www.sumida-aquarium.com/event/7x2a4asvu/', 'date': '2026-12-12', 'period': '12/12(土)', 'time': '10:00〜17:00（最終受付16:30）', 'venue': 'すみだ水族館 5階アクアアカデミー（墨田区押上1-1-2）', 'price': '参加無料（水族館の入場料は別途必要）', 'description': 'カレンダー台紙の各月にペンギンの写真カードを貼ってカレンダーを完成させるワークショップ。当日受付で、参加は無料（入場料は別途必要）。', 'cats': ['水族館', '工作', '体験'], 'io': '屋内', 'res': {'required': False, 'note': '当日受付。定員になり次第終了。'}, 'quotes': ['開催期間2026年12月11日（金）～', '土日祝日と特定日：午前10時～午後5時（最終受付：午後4時30分）', '参加費無料入場料は別途必要となります。', '参加方法当日受付ワークショッ', 'カレンダー台紙のそれぞれの月にペンギンたちの写真カードを貼ってカレンダーを完成させましょう！'], 'basis': 'unspecified', 'overall': 'C', 'override': '水族館の無料の工作ワークショップで子どもも参加できる見込みだが、公式ページに対象年齢の記載がなく、入場料も別に必要なため、条件つきの総合Cとして掲載する。', 'reason': '12/12(土)開催。すみだ水族館の無料ワークショップ「ペンギンカレンダー」で、当日受付で参加できる。水族館の入場料は別に必要。', 'axes': {'child_target': ['unknown', '子ども向けとは明記されていない'], 'interactivity': ['A', '工作を作って参加できる'], 'age_fit': ['unknown', '対象年齢が明記されていない'], 'stay_flexibility': ['A', '10:00〜17:00の間に好きな時間に参加でき、短時間で終わる'], 'burden': ['B', '定員になり次第終了となる場合がある'], 'cost': ['B', 'ワークショップは無料だが、水族館の入場料が必要'], 'reservation': ['A', '予約不要の当日受付'], 'family_value': ['B', '水族館で工作をして持ち帰れる']}, 'strengths': ['ワークショップは無料で予約不要', '好きな時間に参加できる'], 'limitations': ['対象年齢の記載がない', '水族館の入場料が必要'], 'comparison': '総合C（ペンギンカレンダー・12/12(土)）：無料で予約不要の工作だが、対象年齢の記載がなく、入場料が別に必要。', 'pos': ['official_date_confirmed', 'child_activity_confirmed'], 'pf': 'pass', 'child': True}, {'id': 'verified-20261213-sumida-aquarium-penguin-calendar', 'week': '2026-12-12', 'ward': '墨田区', 'page': 'sumida_penguin_calendar_1212.html', 'name': 'ペンギンカレンダー（すみだ水族館）', 'url': 'https://www.sumida-aquarium.com/event/7x2a4asvu/', 'date': '2026-12-13', 'period': '12/13(日)', 'time': '10:00〜17:00（最終受付16:30）', 'venue': 'すみだ水族館 5階アクアアカデミー（墨田区押上1-1-2）', 'price': '参加無料（水族館の入場料は別途必要）', 'description': 'カレンダー台紙の各月にペンギンの写真カードを貼ってカレンダーを完成させるワークショップ。当日受付で、参加は無料（入場料は別途必要）。', 'cats': ['水族館', '工作', '体験'], 'io': '屋内', 'res': {'required': False, 'note': '当日受付。定員になり次第終了。'}, 'quotes': ['開催期間2026年12月11日（金）～', '土日祝日と特定日：午前10時～午後5時（最終受付：午後4時30分）', '参加費無料入場料は別途必要となります。', '参加方法当日受付ワークショッ', 'カレンダー台紙のそれぞれの月にペンギンたちの写真カードを貼ってカレンダーを完成させましょう！'], 'basis': 'unspecified', 'overall': 'C', 'override': '水族館の無料の工作ワークショップで子どもも参加できる見込みだが、公式ページに対象年齢の記載がなく、入場料も別に必要なため、条件つきの総合Cとして掲載する。', 'reason': '12/13(日)開催。すみだ水族館の無料ワークショップ「ペンギンカレンダー」で、当日受付で参加できる。水族館の入場料は別に必要。', 'axes': {'child_target': ['unknown', '子ども向けとは明記されていない'], 'interactivity': ['A', '工作を作って参加できる'], 'age_fit': ['unknown', '対象年齢が明記されていない'], 'stay_flexibility': ['A', '10:00〜17:00の間に好きな時間に参加でき、短時間で終わる'], 'burden': ['B', '定員になり次第終了となる場合がある'], 'cost': ['B', 'ワークショップは無料だが、水族館の入場料が必要'], 'reservation': ['A', '予約不要の当日受付'], 'family_value': ['B', '水族館で工作をして持ち帰れる']}, 'strengths': ['ワークショップは無料で予約不要', '好きな時間に参加できる'], 'limitations': ['対象年齢の記載がない', '水族館の入場料が必要'], 'comparison': '総合C（ペンギンカレンダー・12/13(日)）：無料で予約不要の工作だが、対象年齢の記載がなく、入場料が別に必要。', 'pos': ['official_date_confirmed', 'child_activity_confirmed'], 'pf': 'pass', 'child': True}, {'id': 'verified-20261219-sumida-aquarium-penguin-calendar', 'week': '2026-12-19', 'ward': '墨田区', 'page': 'sumida_penguin_calendar_1212.html', 'name': 'ペンギンカレンダー（すみだ水族館）', 'url': 'https://www.sumida-aquarium.com/event/7x2a4asvu/', 'date': '2026-12-19', 'period': '12/19(土)', 'time': '10:00〜17:00（最終受付16:30）', 'venue': 'すみだ水族館 5階アクアアカデミー（墨田区押上1-1-2）', 'price': '参加無料（水族館の入場料は別途必要）', 'description': 'カレンダー台紙の各月にペンギンの写真カードを貼ってカレンダーを完成させるワークショップ。当日受付で、参加は無料（入場料は別途必要）。', 'cats': ['水族館', '工作', '体験'], 'io': '屋内', 'res': {'required': False, 'note': '当日受付。定員になり次第終了。'}, 'quotes': ['開催期間2026年12月11日（金）～', '土日祝日と特定日：午前10時～午後5時（最終受付：午後4時30分）', '参加費無料入場料は別途必要となります。', '参加方法当日受付ワークショッ', 'カレンダー台紙のそれぞれの月にペンギンたちの写真カードを貼ってカレンダーを完成させましょう！'], 'basis': 'unspecified', 'overall': 'C', 'override': '水族館の無料の工作ワークショップで子どもも参加できる見込みだが、公式ページに対象年齢の記載がなく、入場料も別に必要なため、条件つきの総合Cとして掲載する。', 'reason': '12/19(土)開催。すみだ水族館の無料ワークショップ「ペンギンカレンダー」で、当日受付で参加できる。水族館の入場料は別に必要。', 'axes': {'child_target': ['unknown', '子ども向けとは明記されていない'], 'interactivity': ['A', '工作を作って参加できる'], 'age_fit': ['unknown', '対象年齢が明記されていない'], 'stay_flexibility': ['A', '10:00〜17:00の間に好きな時間に参加でき、短時間で終わる'], 'burden': ['B', '定員になり次第終了となる場合がある'], 'cost': ['B', 'ワークショップは無料だが、水族館の入場料が必要'], 'reservation': ['A', '予約不要の当日受付'], 'family_value': ['B', '水族館で工作をして持ち帰れる']}, 'strengths': ['ワークショップは無料で予約不要', '好きな時間に参加できる'], 'limitations': ['対象年齢の記載がない', '水族館の入場料が必要'], 'comparison': '総合C（ペンギンカレンダー・12/19(土)）：無料で予約不要の工作だが、対象年齢の記載がなく、入場料が別に必要。', 'pos': ['official_date_confirmed', 'child_activity_confirmed'], 'pf': 'pass', 'child': True}, {'id': 'verified-20261220-sumida-aquarium-penguin-calendar', 'week': '2026-12-19', 'ward': '墨田区', 'page': 'sumida_penguin_calendar_1212.html', 'name': 'ペンギンカレンダー（すみだ水族館）', 'url': 'https://www.sumida-aquarium.com/event/7x2a4asvu/', 'date': '2026-12-20', 'period': '12/20(日)', 'time': '10:00〜17:00（最終受付16:30）', 'venue': 'すみだ水族館 5階アクアアカデミー（墨田区押上1-1-2）', 'price': '参加無料（水族館の入場料は別途必要）', 'description': 'カレンダー台紙の各月にペンギンの写真カードを貼ってカレンダーを完成させるワークショップ。当日受付で、参加は無料（入場料は別途必要）。', 'cats': ['水族館', '工作', '体験'], 'io': '屋内', 'res': {'required': False, 'note': '当日受付。定員になり次第終了。'}, 'quotes': ['開催期間2026年12月11日（金）～', '土日祝日と特定日：午前10時～午後5時（最終受付：午後4時30分）', '参加費無料入場料は別途必要となります。', '参加方法当日受付ワークショッ', 'カレンダー台紙のそれぞれの月にペンギンたちの写真カードを貼ってカレンダーを完成させましょう！'], 'basis': 'unspecified', 'overall': 'C', 'override': '水族館の無料の工作ワークショップで子どもも参加できる見込みだが、公式ページに対象年齢の記載がなく、入場料も別に必要なため、条件つきの総合Cとして掲載する。', 'reason': '12/20(日)開催。すみだ水族館の無料ワークショップ「ペンギンカレンダー」で、当日受付で参加できる。水族館の入場料は別に必要。', 'axes': {'child_target': ['unknown', '子ども向けとは明記されていない'], 'interactivity': ['A', '工作を作って参加できる'], 'age_fit': ['unknown', '対象年齢が明記されていない'], 'stay_flexibility': ['A', '10:00〜17:00の間に好きな時間に参加でき、短時間で終わる'], 'burden': ['B', '定員になり次第終了となる場合がある'], 'cost': ['B', 'ワークショップは無料だが、水族館の入場料が必要'], 'reservation': ['A', '予約不要の当日受付'], 'family_value': ['B', '水族館で工作をして持ち帰れる']}, 'strengths': ['ワークショップは無料で予約不要', '好きな時間に参加できる'], 'limitations': ['対象年齢の記載がない', '水族館の入場料が必要'], 'comparison': '総合C（ペンギンカレンダー・12/20(日)）：無料で予約不要の工作だが、対象年齢の記載がなく、入場料が別に必要。', 'pos': ['official_date_confirmed', 'child_activity_confirmed'], 'pf': 'pass', 'child': True}, {'id': 'verified-20261226-sumida-aquarium-penguin-calendar', 'week': '2026-12-26', 'ward': '墨田区', 'page': 'sumida_penguin_calendar_1212.html', 'name': 'ペンギンカレンダー（すみだ水族館）', 'url': 'https://www.sumida-aquarium.com/event/7x2a4asvu/', 'date': '2026-12-26', 'period': '12/26(土)', 'time': '10:00〜17:00（最終受付16:30）', 'venue': 'すみだ水族館 5階アクアアカデミー（墨田区押上1-1-2）', 'price': '参加無料（水族館の入場料は別途必要）', 'description': 'カレンダー台紙の各月にペンギンの写真カードを貼ってカレンダーを完成させるワークショップ。当日受付で、参加は無料（入場料は別途必要）。', 'cats': ['水族館', '工作', '体験'], 'io': '屋内', 'res': {'required': False, 'note': '当日受付。定員になり次第終了。'}, 'quotes': ['開催期間2026年12月11日（金）～', '土日祝日と特定日：午前10時～午後5時（最終受付：午後4時30分）', '参加費無料入場料は別途必要となります。', '参加方法当日受付ワークショッ', 'カレンダー台紙のそれぞれの月にペンギンたちの写真カードを貼ってカレンダーを完成させましょう！'], 'basis': 'unspecified', 'overall': 'C', 'override': '水族館の無料の工作ワークショップで子どもも参加できる見込みだが、公式ページに対象年齢の記載がなく、入場料も別に必要なため、条件つきの総合Cとして掲載する。', 'reason': '12/26(土)開催。すみだ水族館の無料ワークショップ「ペンギンカレンダー」で、当日受付で参加できる。水族館の入場料は別に必要。', 'axes': {'child_target': ['unknown', '子ども向けとは明記されていない'], 'interactivity': ['A', '工作を作って参加できる'], 'age_fit': ['unknown', '対象年齢が明記されていない'], 'stay_flexibility': ['A', '10:00〜17:00の間に好きな時間に参加でき、短時間で終わる'], 'burden': ['B', '定員になり次第終了となる場合がある'], 'cost': ['B', 'ワークショップは無料だが、水族館の入場料が必要'], 'reservation': ['A', '予約不要の当日受付'], 'family_value': ['B', '水族館で工作をして持ち帰れる']}, 'strengths': ['ワークショップは無料で予約不要', '好きな時間に参加できる'], 'limitations': ['対象年齢の記載がない', '水族館の入場料が必要'], 'comparison': '総合C（ペンギンカレンダー・12/26(土)）：無料で予約不要の工作だが、対象年齢の記載がなく、入場料が別に必要。', 'pos': ['official_date_confirmed', 'child_activity_confirmed'], 'pf': 'pass', 'child': True}, {'id': 'verified-20261227-sumida-aquarium-penguin-calendar', 'week': '2026-12-26', 'ward': '墨田区', 'page': 'sumida_penguin_calendar_1212.html', 'name': 'ペンギンカレンダー（すみだ水族館）', 'url': 'https://www.sumida-aquarium.com/event/7x2a4asvu/', 'date': '2026-12-27', 'period': '12/27(日)', 'time': '10:00〜17:00（最終受付16:30）', 'venue': 'すみだ水族館 5階アクアアカデミー（墨田区押上1-1-2）', 'price': '参加無料（水族館の入場料は別途必要）', 'description': 'カレンダー台紙の各月にペンギンの写真カードを貼ってカレンダーを完成させるワークショップ。当日受付で、参加は無料（入場料は別途必要）。', 'cats': ['水族館', '工作', '体験'], 'io': '屋内', 'res': {'required': False, 'note': '当日受付。定員になり次第終了。'}, 'quotes': ['開催期間2026年12月11日（金）～', '土日祝日と特定日：午前10時～午後5時（最終受付：午後4時30分）', '参加費無料入場料は別途必要となります。', '参加方法当日受付ワークショッ', 'カレンダー台紙のそれぞれの月にペンギンたちの写真カードを貼ってカレンダーを完成させましょう！'], 'basis': 'unspecified', 'overall': 'C', 'override': '水族館の無料の工作ワークショップで子どもも参加できる見込みだが、公式ページに対象年齢の記載がなく、入場料も別に必要なため、条件つきの総合Cとして掲載する。', 'reason': '12/27(日)開催。すみだ水族館の無料ワークショップ「ペンギンカレンダー」で、当日受付で参加できる。水族館の入場料は別に必要。', 'axes': {'child_target': ['unknown', '子ども向けとは明記されていない'], 'interactivity': ['A', '工作を作って参加できる'], 'age_fit': ['unknown', '対象年齢が明記されていない'], 'stay_flexibility': ['A', '10:00〜17:00の間に好きな時間に参加でき、短時間で終わる'], 'burden': ['B', '定員になり次第終了となる場合がある'], 'cost': ['B', 'ワークショップは無料だが、水族館の入場料が必要'], 'reservation': ['A', '予約不要の当日受付'], 'family_value': ['B', '水族館で工作をして持ち帰れる']}, 'strengths': ['ワークショップは無料で予約不要', '好きな時間に参加できる'], 'limitations': ['対象年齢の記載がない', '水族館の入場料が必要'], 'comparison': '総合C（ペンギンカレンダー・12/27(日)）：無料で予約不要の工作だが、対象年齢の記載がなく、入場料が別に必要。', 'pos': ['official_date_confirmed', 'child_activity_confirmed'], 'pf': 'pass', 'child': True}]
RAW = SPECS_RAW
SPECS = []
for _r in RAW:
    _s = dict(_r)
    _s['categories'] = _s.pop('cats'); _s['indoor_outdoor'] = _s.pop('io'); _s['reservation'] = _s.pop('res')
    _s['child_activity'] = _s.pop('child'); _s['price_field'] = _s.pop('pf'); _s['positive'] = _s.pop('pos')
    SPECS.append(_s)
NEW_IDS = [s['id'] for s in SPECS]
SHARDS = {w: f'{w}-events-lead28-20261120.json' for w in ('2026-11-21', '2026-11-28', '2026-12-05', '2026-12-12', '2026-12-19', '2026-12-26')}
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
        run['lead28_addition_20261120'] = {
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
        'run_id': 'lead28-addition-20261120', 'run_type': 'manual_verified_lead28_addition',
        'status': 'verified_subset_publication', 'as_of_jst': '2026-11-20', 'executed_at': m['generated'],
        'base_data_production_sha': BASE, 'target_weekends': sorted(derived),
        'prior_active_week_records': 689, 'candidate_active_week_records': 702, 'added_weekly_records': 13,
        'new_event_ids': NEW_IDS, 'held_not_published': sorted(HELD),
        'existing_event_records_physically_deleted': 0, 'image_only_updates': 0,
        'source_failures_remain_unverified': True, 'global_source_audit_complete': False,
        'full_23_ward_25_source_audit_complete': False,
        'note': '東京都の公園管理者・すみだ水族館の公式ページで日付・時間・会場・条件を確認できた13件のみ追加。',
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
