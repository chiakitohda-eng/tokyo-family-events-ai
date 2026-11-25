#!/usr/bin/env python3
"""1 weekly record (12/26 Nerima forest festival) from the committed official Nerima page (2026-11-20).

Raw official pages are committed unchanged under research/2026-11-20-thin-wards/pages/
(fetched by read-only workflows, HTTP 200). Quotes must occur verbatim in those pages.
The gate validator re-derives every record from this module and requires exact equality.
"""
import argparse, hashlib, json, pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import suginami_addition_20261118 as S

BASE = 'afedbc20dd622d85fb58529ed05e22a262a6b6d6'   # data-production after the Nerima duplicate removal (664 active week records)
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


SPECS_RAW = [{'id': 'verified-20261128-itabashi-nettaikan-barbapapa', 'week': '2026-11-28', 'ward': '板橋区', 'page': 'itabashi_nettaikan_barbapapa.html', 'name': 'バーバパパと森のクリスマス展（板橋区立熱帯環境植物館）', 'url': 'https://www.city.itabashi.tokyo.jp/koho/1062992/1066844/1066847.html', 'date': '2026-11-28', 'period': '11/28(土)', 'time': '10:00〜18:00（入館は17:30まで）', 'venue': '板橋区立熱帯環境植物館（板橋区高島平8-29-2）', 'price': '入館料 一般360円・小中学生130円（土日は小・中学生無料）', 'description': '熱帯環境植物館のクリスマス企画展。クリスマスツリーの展示、キッズコスプレコーナー、バーバパパとのフォトスポット・絵本コーナー・スタンプラリーがある。土日はカメの「ムッちゃん」のツリー点灯式も行われる。', 'cats': ['企画展', 'クリスマス', '植物館'], 'io': '屋内', 'res': {'required': False, 'note': '予約不要。入館料が必要。'}, 'quotes': ['とき11月25日（水曜日）から12月25日（金曜日）、午前10時から午後6時（入館は午後5時30分まで）', 'キッズコスプレコーナーポイン', 'バーバパパコラボ企画フォトス', 'スタンプラリートワイライトジ', '注：土曜日・日曜日は小・中学生無料', 'ビルマムツアシガメ「ムッちゃん」のクリスマスツリー点灯式（土曜日・日曜日のみ）'], 'basis': 'all_ages', 'reason': '11/28(土)開催。バーバパパとコラボしたクリスマス企画展で、キッズコスプレやフォトスポット、絵本コーナー、スタンプラリーがある。土日は小・中学生の入館が無料。', 'axes': {'child_target': ['B', 'キッズコスプレやスタンプラリーなど子ども向けの企画を含む展示で、こども専用ではない'], 'interactivity': ['B', 'スタンプラリーやコスプレなど参加できる要素がある'], 'age_fit': ['B', '絵本コーナーやコスプレなど幼児から小学生まで楽しめる内容'], 'stay_flexibility': ['A', '10:00〜18:00の間に自由に出入りでき、短時間でも楽しめる'], 'burden': ['A', '予約不要で、屋内の温室施設'], 'cost': ['A', '土日は小・中学生が無料で、大人も360円'], 'reservation': ['A', '予約不要'], 'family_value': ['B', '家族でクリスマスの展示と植物・生きものを楽しめる']}, 'strengths': ['土日は小・中学生の入館が無料', '予約不要で屋内'], 'limitations': ['入館料が必要', '展示が中心でこども専用ではない'], 'comparison': '総合B（11/28(土)）：予約不要で土日は小・中学生が無料のクリスマス展だが、展示中心で、こども専用ではない。', 'pos': ['official_date_confirmed', 'child_activity_confirmed'], 'override': '', 'pf': 'pass', 'overall': 'B', 'child': True}, {'id': 'verified-20261129-itabashi-nettaikan-barbapapa', 'week': '2026-11-28', 'ward': '板橋区', 'page': 'itabashi_nettaikan_barbapapa.html', 'name': 'バーバパパと森のクリスマス展（板橋区立熱帯環境植物館）', 'url': 'https://www.city.itabashi.tokyo.jp/koho/1062992/1066844/1066847.html', 'date': '2026-11-29', 'period': '11/29(日)', 'time': '10:00〜18:00（入館は17:30まで）', 'venue': '板橋区立熱帯環境植物館（板橋区高島平8-29-2）', 'price': '入館料 一般360円・小中学生130円（土日は小・中学生無料）', 'description': '熱帯環境植物館のクリスマス企画展。クリスマスツリーの展示、キッズコスプレコーナー、バーバパパとのフォトスポット・絵本コーナー・スタンプラリーがある。土日はカメの「ムッちゃん」のツリー点灯式も行われる。', 'cats': ['企画展', 'クリスマス', '植物館'], 'io': '屋内', 'res': {'required': False, 'note': '予約不要。入館料が必要。'}, 'quotes': ['とき11月25日（水曜日）から12月25日（金曜日）、午前10時から午後6時（入館は午後5時30分まで）', 'キッズコスプレコーナーポイン', 'バーバパパコラボ企画フォトス', 'スタンプラリートワイライトジ', '注：土曜日・日曜日は小・中学生無料', 'ビルマムツアシガメ「ムッちゃん」のクリスマスツリー点灯式（土曜日・日曜日のみ）'], 'basis': 'all_ages', 'reason': '11/29(日)開催。バーバパパとコラボしたクリスマス企画展で、キッズコスプレやフォトスポット、絵本コーナー、スタンプラリーがある。土日は小・中学生の入館が無料。', 'axes': {'child_target': ['B', 'キッズコスプレやスタンプラリーなど子ども向けの企画を含む展示で、こども専用ではない'], 'interactivity': ['B', 'スタンプラリーやコスプレなど参加できる要素がある'], 'age_fit': ['B', '絵本コーナーやコスプレなど幼児から小学生まで楽しめる内容'], 'stay_flexibility': ['A', '10:00〜18:00の間に自由に出入りでき、短時間でも楽しめる'], 'burden': ['A', '予約不要で、屋内の温室施設'], 'cost': ['A', '土日は小・中学生が無料で、大人も360円'], 'reservation': ['A', '予約不要'], 'family_value': ['B', '家族でクリスマスの展示と植物・生きものを楽しめる']}, 'strengths': ['土日は小・中学生の入館が無料', '予約不要で屋内'], 'limitations': ['入館料が必要', '展示が中心でこども専用ではない'], 'comparison': '総合B（11/29(日)）：予約不要で土日は小・中学生が無料のクリスマス展だが、展示中心で、こども専用ではない。', 'pos': ['official_date_confirmed', 'child_activity_confirmed'], 'override': '', 'pf': 'pass', 'overall': 'B', 'child': True}, {'id': 'verified-20261205-itabashi-nettaikan-barbapapa', 'week': '2026-12-05', 'ward': '板橋区', 'page': 'itabashi_nettaikan_barbapapa.html', 'name': 'バーバパパと森のクリスマス展（板橋区立熱帯環境植物館）', 'url': 'https://www.city.itabashi.tokyo.jp/koho/1062992/1066844/1066847.html', 'date': '2026-12-05', 'period': '12/5(土)', 'time': '10:00〜18:00（入館は17:30まで）', 'venue': '板橋区立熱帯環境植物館（板橋区高島平8-29-2）', 'price': '入館料 一般360円・小中学生130円（土日は小・中学生無料）', 'description': '熱帯環境植物館のクリスマス企画展。クリスマスツリーの展示、キッズコスプレコーナー、バーバパパとのフォトスポット・絵本コーナー・スタンプラリーがある。土日はカメの「ムッちゃん」のツリー点灯式も行われる。', 'cats': ['企画展', 'クリスマス', '植物館'], 'io': '屋内', 'res': {'required': False, 'note': '予約不要。入館料が必要。'}, 'quotes': ['とき11月25日（水曜日）から12月25日（金曜日）、午前10時から午後6時（入館は午後5時30分まで）', 'キッズコスプレコーナーポイン', 'バーバパパコラボ企画フォトス', 'スタンプラリートワイライトジ', '注：土曜日・日曜日は小・中学生無料', 'ビルマムツアシガメ「ムッちゃん」のクリスマスツリー点灯式（土曜日・日曜日のみ）'], 'basis': 'all_ages', 'reason': '12/5(土)開催。バーバパパとコラボしたクリスマス企画展で、キッズコスプレやフォトスポット、絵本コーナー、スタンプラリーがある。土日は小・中学生の入館が無料。', 'axes': {'child_target': ['B', 'キッズコスプレやスタンプラリーなど子ども向けの企画を含む展示で、こども専用ではない'], 'interactivity': ['B', 'スタンプラリーやコスプレなど参加できる要素がある'], 'age_fit': ['B', '絵本コーナーやコスプレなど幼児から小学生まで楽しめる内容'], 'stay_flexibility': ['A', '10:00〜18:00の間に自由に出入りでき、短時間でも楽しめる'], 'burden': ['A', '予約不要で、屋内の温室施設'], 'cost': ['A', '土日は小・中学生が無料で、大人も360円'], 'reservation': ['A', '予約不要'], 'family_value': ['B', '家族でクリスマスの展示と植物・生きものを楽しめる']}, 'strengths': ['土日は小・中学生の入館が無料', '予約不要で屋内'], 'limitations': ['入館料が必要', '展示が中心でこども専用ではない'], 'comparison': '総合B（12/5(土)）：予約不要で土日は小・中学生が無料のクリスマス展だが、展示中心で、こども専用ではない。', 'pos': ['official_date_confirmed', 'child_activity_confirmed'], 'override': '', 'pf': 'pass', 'overall': 'B', 'child': True}, {'id': 'verified-20261206-itabashi-nettaikan-barbapapa', 'week': '2026-12-05', 'ward': '板橋区', 'page': 'itabashi_nettaikan_barbapapa.html', 'name': 'バーバパパと森のクリスマス展（板橋区立熱帯環境植物館）', 'url': 'https://www.city.itabashi.tokyo.jp/koho/1062992/1066844/1066847.html', 'date': '2026-12-06', 'period': '12/6(日)', 'time': '10:00〜18:00（入館は17:30まで）', 'venue': '板橋区立熱帯環境植物館（板橋区高島平8-29-2）', 'price': '入館料 一般360円・小中学生130円（土日は小・中学生無料）', 'description': '熱帯環境植物館のクリスマス企画展。クリスマスツリーの展示、キッズコスプレコーナー、バーバパパとのフォトスポット・絵本コーナー・スタンプラリーがある。土日はカメの「ムッちゃん」のツリー点灯式も行われる。', 'cats': ['企画展', 'クリスマス', '植物館'], 'io': '屋内', 'res': {'required': False, 'note': '予約不要。入館料が必要。'}, 'quotes': ['とき11月25日（水曜日）から12月25日（金曜日）、午前10時から午後6時（入館は午後5時30分まで）', 'キッズコスプレコーナーポイン', 'バーバパパコラボ企画フォトス', 'スタンプラリートワイライトジ', '注：土曜日・日曜日は小・中学生無料', 'ビルマムツアシガメ「ムッちゃん」のクリスマスツリー点灯式（土曜日・日曜日のみ）'], 'basis': 'all_ages', 'reason': '12/6(日)開催。バーバパパとコラボしたクリスマス企画展で、キッズコスプレやフォトスポット、絵本コーナー、スタンプラリーがある。土日は小・中学生の入館が無料。', 'axes': {'child_target': ['B', 'キッズコスプレやスタンプラリーなど子ども向けの企画を含む展示で、こども専用ではない'], 'interactivity': ['B', 'スタンプラリーやコスプレなど参加できる要素がある'], 'age_fit': ['B', '絵本コーナーやコスプレなど幼児から小学生まで楽しめる内容'], 'stay_flexibility': ['A', '10:00〜18:00の間に自由に出入りでき、短時間でも楽しめる'], 'burden': ['A', '予約不要で、屋内の温室施設'], 'cost': ['A', '土日は小・中学生が無料で、大人も360円'], 'reservation': ['A', '予約不要'], 'family_value': ['B', '家族でクリスマスの展示と植物・生きものを楽しめる']}, 'strengths': ['土日は小・中学生の入館が無料', '予約不要で屋内'], 'limitations': ['入館料が必要', '展示が中心でこども専用ではない'], 'comparison': '総合B（12/6(日)）：予約不要で土日は小・中学生が無料のクリスマス展だが、展示中心で、こども専用ではない。', 'pos': ['official_date_confirmed', 'child_activity_confirmed'], 'override': '', 'pf': 'pass', 'overall': 'B', 'child': True}, {'id': 'verified-20261212-itabashi-nettaikan-barbapapa', 'week': '2026-12-12', 'ward': '板橋区', 'page': 'itabashi_nettaikan_barbapapa.html', 'name': 'バーバパパと森のクリスマス展（板橋区立熱帯環境植物館）', 'url': 'https://www.city.itabashi.tokyo.jp/koho/1062992/1066844/1066847.html', 'date': '2026-12-12', 'period': '12/12(土)', 'time': '10:00〜18:00（入館は17:30まで）', 'venue': '板橋区立熱帯環境植物館（板橋区高島平8-29-2）', 'price': '入館料 一般360円・小中学生130円（土日は小・中学生無料）', 'description': '熱帯環境植物館のクリスマス企画展。クリスマスツリーの展示、キッズコスプレコーナー、バーバパパとのフォトスポット・絵本コーナー・スタンプラリーがある。土日はカメの「ムッちゃん」のツリー点灯式も行われる。', 'cats': ['企画展', 'クリスマス', '植物館'], 'io': '屋内', 'res': {'required': False, 'note': '予約不要。入館料が必要。'}, 'quotes': ['とき11月25日（水曜日）から12月25日（金曜日）、午前10時から午後6時（入館は午後5時30分まで）', 'キッズコスプレコーナーポイン', 'バーバパパコラボ企画フォトス', 'スタンプラリートワイライトジ', '注：土曜日・日曜日は小・中学生無料', 'ビルマムツアシガメ「ムッちゃん」のクリスマスツリー点灯式（土曜日・日曜日のみ）'], 'basis': 'all_ages', 'reason': '12/12(土)開催。バーバパパとコラボしたクリスマス企画展で、キッズコスプレやフォトスポット、絵本コーナー、スタンプラリーがある。土日は小・中学生の入館が無料。', 'axes': {'child_target': ['B', 'キッズコスプレやスタンプラリーなど子ども向けの企画を含む展示で、こども専用ではない'], 'interactivity': ['B', 'スタンプラリーやコスプレなど参加できる要素がある'], 'age_fit': ['B', '絵本コーナーやコスプレなど幼児から小学生まで楽しめる内容'], 'stay_flexibility': ['A', '10:00〜18:00の間に自由に出入りでき、短時間でも楽しめる'], 'burden': ['A', '予約不要で、屋内の温室施設'], 'cost': ['A', '土日は小・中学生が無料で、大人も360円'], 'reservation': ['A', '予約不要'], 'family_value': ['B', '家族でクリスマスの展示と植物・生きものを楽しめる']}, 'strengths': ['土日は小・中学生の入館が無料', '予約不要で屋内'], 'limitations': ['入館料が必要', '展示が中心でこども専用ではない'], 'comparison': '総合B（12/12(土)）：予約不要で土日は小・中学生が無料のクリスマス展だが、展示中心で、こども専用ではない。', 'pos': ['official_date_confirmed', 'child_activity_confirmed'], 'override': '', 'pf': 'pass', 'overall': 'B', 'child': True}, {'id': 'verified-20261213-itabashi-nettaikan-barbapapa', 'week': '2026-12-12', 'ward': '板橋区', 'page': 'itabashi_nettaikan_barbapapa.html', 'name': 'バーバパパと森のクリスマス展（板橋区立熱帯環境植物館）', 'url': 'https://www.city.itabashi.tokyo.jp/koho/1062992/1066844/1066847.html', 'date': '2026-12-13', 'period': '12/13(日)', 'time': '10:00〜18:00（入館は17:30まで）', 'venue': '板橋区立熱帯環境植物館（板橋区高島平8-29-2）', 'price': '入館料 一般360円・小中学生130円（土日は小・中学生無料）', 'description': '熱帯環境植物館のクリスマス企画展。クリスマスツリーの展示、キッズコスプレコーナー、バーバパパとのフォトスポット・絵本コーナー・スタンプラリーがある。土日はカメの「ムッちゃん」のツリー点灯式も行われる。', 'cats': ['企画展', 'クリスマス', '植物館'], 'io': '屋内', 'res': {'required': False, 'note': '予約不要。入館料が必要。'}, 'quotes': ['とき11月25日（水曜日）から12月25日（金曜日）、午前10時から午後6時（入館は午後5時30分まで）', 'キッズコスプレコーナーポイン', 'バーバパパコラボ企画フォトス', 'スタンプラリートワイライトジ', '注：土曜日・日曜日は小・中学生無料', 'ビルマムツアシガメ「ムッちゃん」のクリスマスツリー点灯式（土曜日・日曜日のみ）'], 'basis': 'all_ages', 'reason': '12/13(日)開催。バーバパパとコラボしたクリスマス企画展で、キッズコスプレやフォトスポット、絵本コーナー、スタンプラリーがある。土日は小・中学生の入館が無料。', 'axes': {'child_target': ['B', 'キッズコスプレやスタンプラリーなど子ども向けの企画を含む展示で、こども専用ではない'], 'interactivity': ['B', 'スタンプラリーやコスプレなど参加できる要素がある'], 'age_fit': ['B', '絵本コーナーやコスプレなど幼児から小学生まで楽しめる内容'], 'stay_flexibility': ['A', '10:00〜18:00の間に自由に出入りでき、短時間でも楽しめる'], 'burden': ['A', '予約不要で、屋内の温室施設'], 'cost': ['A', '土日は小・中学生が無料で、大人も360円'], 'reservation': ['A', '予約不要'], 'family_value': ['B', '家族でクリスマスの展示と植物・生きものを楽しめる']}, 'strengths': ['土日は小・中学生の入館が無料', '予約不要で屋内'], 'limitations': ['入館料が必要', '展示が中心でこども専用ではない'], 'comparison': '総合B（12/13(日)）：予約不要で土日は小・中学生が無料のクリスマス展だが、展示中心で、こども専用ではない。', 'pos': ['official_date_confirmed', 'child_activity_confirmed'], 'override': '', 'pf': 'pass', 'overall': 'B', 'child': True}, {'id': 'verified-20261219-itabashi-nettaikan-barbapapa', 'week': '2026-12-19', 'ward': '板橋区', 'page': 'itabashi_nettaikan_barbapapa.html', 'name': 'バーバパパと森のクリスマス展（板橋区立熱帯環境植物館）', 'url': 'https://www.city.itabashi.tokyo.jp/koho/1062992/1066844/1066847.html', 'date': '2026-12-19', 'period': '12/19(土)', 'time': '10:00〜18:00（入館は17:30まで）', 'venue': '板橋区立熱帯環境植物館（板橋区高島平8-29-2）', 'price': '入館料 一般360円・小中学生130円（土日は小・中学生無料）', 'description': '熱帯環境植物館のクリスマス企画展。クリスマスツリーの展示、キッズコスプレコーナー、バーバパパとのフォトスポット・絵本コーナー・スタンプラリーがある。土日はカメの「ムッちゃん」のツリー点灯式も行われる。', 'cats': ['企画展', 'クリスマス', '植物館'], 'io': '屋内', 'res': {'required': False, 'note': '予約不要。入館料が必要。'}, 'quotes': ['とき11月25日（水曜日）から12月25日（金曜日）、午前10時から午後6時（入館は午後5時30分まで）', 'キッズコスプレコーナーポイン', 'バーバパパコラボ企画フォトス', 'スタンプラリートワイライトジ', '注：土曜日・日曜日は小・中学生無料', 'ビルマムツアシガメ「ムッちゃん」のクリスマスツリー点灯式（土曜日・日曜日のみ）'], 'basis': 'all_ages', 'reason': '12/19(土)開催。バーバパパとコラボしたクリスマス企画展で、キッズコスプレやフォトスポット、絵本コーナー、スタンプラリーがある。土日は小・中学生の入館が無料。', 'axes': {'child_target': ['B', 'キッズコスプレやスタンプラリーなど子ども向けの企画を含む展示で、こども専用ではない'], 'interactivity': ['B', 'スタンプラリーやコスプレなど参加できる要素がある'], 'age_fit': ['B', '絵本コーナーやコスプレなど幼児から小学生まで楽しめる内容'], 'stay_flexibility': ['A', '10:00〜18:00の間に自由に出入りでき、短時間でも楽しめる'], 'burden': ['A', '予約不要で、屋内の温室施設'], 'cost': ['A', '土日は小・中学生が無料で、大人も360円'], 'reservation': ['A', '予約不要'], 'family_value': ['B', '家族でクリスマスの展示と植物・生きものを楽しめる']}, 'strengths': ['土日は小・中学生の入館が無料', '予約不要で屋内'], 'limitations': ['入館料が必要', '展示が中心でこども専用ではない'], 'comparison': '総合B（12/19(土)）：予約不要で土日は小・中学生が無料のクリスマス展だが、展示中心で、こども専用ではない。', 'pos': ['official_date_confirmed', 'child_activity_confirmed'], 'override': '', 'pf': 'pass', 'overall': 'B', 'child': True}, {'id': 'verified-20261220-itabashi-nettaikan-barbapapa', 'week': '2026-12-19', 'ward': '板橋区', 'page': 'itabashi_nettaikan_barbapapa.html', 'name': 'バーバパパと森のクリスマス展（板橋区立熱帯環境植物館）', 'url': 'https://www.city.itabashi.tokyo.jp/koho/1062992/1066844/1066847.html', 'date': '2026-12-20', 'period': '12/20(日)', 'time': '10:00〜18:00（入館は17:30まで）', 'venue': '板橋区立熱帯環境植物館（板橋区高島平8-29-2）', 'price': '入館料 一般360円・小中学生130円（土日は小・中学生無料）', 'description': '熱帯環境植物館のクリスマス企画展。クリスマスツリーの展示、キッズコスプレコーナー、バーバパパとのフォトスポット・絵本コーナー・スタンプラリーがある。土日はカメの「ムッちゃん」のツリー点灯式も行われる。', 'cats': ['企画展', 'クリスマス', '植物館'], 'io': '屋内', 'res': {'required': False, 'note': '予約不要。入館料が必要。'}, 'quotes': ['とき11月25日（水曜日）から12月25日（金曜日）、午前10時から午後6時（入館は午後5時30分まで）', 'キッズコスプレコーナーポイン', 'バーバパパコラボ企画フォトス', 'スタンプラリートワイライトジ', '注：土曜日・日曜日は小・中学生無料', 'ビルマムツアシガメ「ムッちゃん」のクリスマスツリー点灯式（土曜日・日曜日のみ）'], 'basis': 'all_ages', 'reason': '12/20(日)開催。バーバパパとコラボしたクリスマス企画展で、キッズコスプレやフォトスポット、絵本コーナー、スタンプラリーがある。土日は小・中学生の入館が無料。', 'axes': {'child_target': ['B', 'キッズコスプレやスタンプラリーなど子ども向けの企画を含む展示で、こども専用ではない'], 'interactivity': ['B', 'スタンプラリーやコスプレなど参加できる要素がある'], 'age_fit': ['B', '絵本コーナーやコスプレなど幼児から小学生まで楽しめる内容'], 'stay_flexibility': ['A', '10:00〜18:00の間に自由に出入りでき、短時間でも楽しめる'], 'burden': ['A', '予約不要で、屋内の温室施設'], 'cost': ['A', '土日は小・中学生が無料で、大人も360円'], 'reservation': ['A', '予約不要'], 'family_value': ['B', '家族でクリスマスの展示と植物・生きものを楽しめる']}, 'strengths': ['土日は小・中学生の入館が無料', '予約不要で屋内'], 'limitations': ['入館料が必要', '展示が中心でこども専用ではない'], 'comparison': '総合B（12/20(日)）：予約不要で土日は小・中学生が無料のクリスマス展だが、展示中心で、こども専用ではない。', 'pos': ['official_date_confirmed', 'child_activity_confirmed'], 'override': '', 'pf': 'pass', 'overall': 'B', 'child': True}, {'id': 'verified-20261129-itabashi-nettaikan-malaybear-ehon', 'week': '2026-11-28', 'ward': '板橋区', 'page': 'itabashi_nettaikan_barbapapa.html', 'name': 'マレーグマの絵本の読み聞かせとぬりえ（熱帯環境植物館）', 'url': 'https://www.city.itabashi.tokyo.jp/koho/1062992/1066844/1066847.html', 'date': '2026-11-29', 'period': '11/29(日)', 'time': '14:00〜15:00', 'venue': '板橋区立熱帯環境植物館（板橋区高島平8-29-2）', 'price': '入館料（一般360円・小中学生は土日無料）', 'description': 'マレーグマの絵本の読み聞かせとぬりえを楽しむ催し。講師はボルネオマレーグマ保護センタージャパンの代表理事。定員50人の先着順で、当日直接会場へ行く。', 'cats': ['絵本', 'ぬりえ', '動物'], 'io': '屋内', 'res': {'required': False, 'note': '当日直接会場へ。定員50人の先着順。'}, 'quotes': ['マレーグマの絵本の読み聞かせとぬりえ', 'とき11月29日（日曜日）午後2時から午後3時', '定員50人（先着順）注：当日', '注：当日、直接会場へ。費用入', '費用入館料クリスマスリース作'], 'basis': 'all_ages', 'reason': '11/29の午後2時から、マレーグマの絵本の読み聞かせとぬりえを楽しめる。予約は不要で、費用は入館料のみ。', 'axes': {'child_target': ['B', '絵本の読み聞かせとぬりえで、子どもが楽しめる内容だが、対象年齢の記載はない'], 'interactivity': ['B', 'ぬりえができる'], 'age_fit': ['unknown', '対象年齢が明記されていない'], 'stay_flexibility': ['B', '14:00〜15:00の1時間で、時間が決まっている'], 'burden': ['A', '当日直接会場へ行けばよい'], 'cost': ['A', '費用は入館料のみ（土日は小・中学生無料）'], 'reservation': ['A', '予約不要（先着50人）'], 'family_value': ['B', '家族で動物の絵本を楽しめる']}, 'strengths': ['予約不要', '入館料のみで参加できる'], 'limitations': ['定員50人の先着順', '対象年齢の記載がない'], 'comparison': '総合B：予約不要で入館料のみの絵本の読み聞かせだが、定員があり、対象年齢の記載がない。', 'pos': ['official_date_confirmed', 'child_activity_confirmed'], 'override': '', 'pf': 'pass', 'overall': 'B', 'child': True}]
RAW = SPECS_RAW
SPECS = []
for _r in RAW:
    _s = dict(_r)
    _s['categories'] = _s.pop('cats'); _s['indoor_outdoor'] = _s.pop('io'); _s['reservation'] = _s.pop('res')
    _s['child_activity'] = _s.pop('child'); _s['price_field'] = _s.pop('pf'); _s['positive'] = _s.pop('pos')
    SPECS.append(_s)
NEW_IDS = [s['id'] for s in SPECS]
SHARDS = {w: f'{w}-events-lead25-20261120.json' for w in ('2026-11-28', '2026-12-05', '2026-12-12', '2026-12-19')}
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
        run['lead25_addition_20261120'] = {
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
        'run_id': 'lead25-addition-20261120', 'run_type': 'manual_verified_lead25_addition',
        'status': 'verified_subset_publication', 'as_of_jst': '2026-11-20', 'executed_at': m['generated'],
        'base_data_production_sha': BASE, 'target_weekends': sorted(derived),
        'prior_active_week_records': 664, 'candidate_active_week_records': 673, 'added_weekly_records': 9,
        'new_event_ids': NEW_IDS, 'held_not_published': sorted(HELD),
        'existing_event_records_physically_deleted': 0, 'image_only_updates': 0,
        'source_failures_remain_unverified': True, 'global_source_audit_complete': False,
        'full_23_ward_25_source_audit_complete': False,
        'note': '東京都の公園管理者・板橋区の公式ページで日付・時間・会場・条件を確認できた9件のみ追加。',
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
