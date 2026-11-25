#!/usr/bin/env python3
"""Ten weekly records (seven events) found by reading the remaining pool pages and calendar detail pages (2026-11-19).

Raw official pages are committed unchanged under research/2026-11-19-audit/pages/
(fetched by read-only workflows, HTTP 200). Quotes must occur verbatim in those pages.
The gate validator re-derives every record from this module and requires exact equality.
"""
import argparse, hashlib, json, pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import suginami_addition_20261118 as S

BASE = '4896e679ff43b1b29abdfa2a61abe5f1a923d8b5'   # data-production after the lead4 addition (459 records)
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


SPECS_RAW = [{'id': 'verified-20261121-edogawa-rakuichi', 'week': '2026-11-21', 'ward': '江戸川区', 'page': 'edogawa_rakuichi.html', 'name': 'えどがわ楽市2026 ～笑顔がつながる2日間～', 'url': 'https://www.city.edogawa.tokyo.jp/event/rakuichi2026.html', 'date': '2026-11-21', 'end': '2026-11-22', 'period': '11/21(土)・11/22(日)', 'time': '11/21 11:00〜／11/22 〜17:00', 'venue': 'アリオ葛西（江戸川区東葛西9丁目3番3号）', 'price': '無料', 'image': 'https://www.city.edogawa.tokyo.jp/images/74579/edogawarakuichi.jpg', 'description': '地域の店舗・企業の出店、キッズダンスやライブ、スポーツ体験などがある2日間のイベント。子どもから大人まで1日楽しめる。申込不要。', 'cats': ['体験・ワークショップ', '地域交流'], 'io': '屋内・屋外', 'res': {'required': False, 'note': '申し込み不要。'}, 'quotes': ['地域の店舗・企業による出店をはじめ、キッズダンスやライブ、スポーツ体験など、子どもから大人まで1日楽しめるイベントです。', '開催日時2026年11月21日（土曜日）11時00分から2026年11月22日（日曜日）17時00分', '申し込み不要場所アリオ葛西住所江戸川区東葛西9丁目3番3号', 'ダンスなどのステージ発表やスポーツ体験などを行います。', '費用無料問合せえどがわ楽市実行委員会'], 'overall': 'B', 'basis': 'child_program', 'child': True, 'reason': 'キッズダンスやスポーツ体験がある、子どもから大人まで楽しめるイベント。無料・申込不要で、2日間開催。', 'axes': {'child_target': ('B', 'キッズダンスやスポーツ体験など、子どもから大人まで1日楽しめると案内'), 'interactivity': ('B', 'スポーツ体験やステージ発表。体験内容の詳細は公式ページにない'), 'age_fit': ('unknown', '対象年齢は公式案内に明記がない'), 'stay_flexibility': ('A', '2日間で、都合のよい時間に立ち寄れる'), 'burden': ('B', '商業施設での開催で、内容の詳細は公式ページに少ない'), 'cost': ('A', '費用無料'), 'reservation': ('A', '申し込み不要'), 'family_value': ('B', '店舗の出店とキッズ向けの催しを家族で楽しめる')}, 'strengths': ['無料・申込不要で2日間開催', 'キッズダンスやスポーツ体験'], 'limitations': ['体験内容の詳細は公式ページに少ない'], 'comparison': '総合B：無料・申込不要で気軽だが、体験内容の詳細は公式ページに少ない。', 'pf': 'pass', 'pos': ['official_date_confirmed', 'child_activity_confirmed']}, {'id': 'verified-20261122-suginami-irori-ohanashi', 'week': '2026-11-21', 'ward': '杉並区', 'page': 'suginami_irori.html', 'name': '囲炉裏端でのお話し会（郷土博物館）', 'url': 'https://www.city.suginami.tokyo.jp/s113/event/28911.html', 'date': '2026-11-22', 'period': '11/22(日)', 'time': '13:00〜15:00', 'venue': '杉並区立郷土博物館 古民家（杉並区大宮1丁目20番8号）', 'price': '無料（別途郷土博物館の観覧料100円）', 'description': '古民家の囲炉裏端で、昔の囲炉裏端での生活や家族によるお話しの場を再現する催し。どなたでも参加でき、当日直接会場へ。', 'cats': ['体験・ワークショップ', '地域交流'], 'io': '屋内', 'res': {'required': False, 'note': '当日直接会場へ。'}, 'quotes': ['囲炉裏端で祖父母等からお話を聞いていた昔の様子を再現します。', '開催日2026年11月22日（日曜日）開催時間午後1時から午後3時まで', '対象者どなたでも開催場所杉並区立郷土博物館古民家杉並区大宮1丁目20番8号', '昔の囲炉裏端での生活を紹介するとともに、娯楽の少ない時代の家族によるお話しの場を再現します。', '申し込み当日直接会場へお越しください。費用無料（別途郷土博物館の観覧料100円が必要です。）'], 'overall': 'B', 'basis': 'all_ages', 'child': False, 'reason': '古民家の囲炉裏端で昔の暮らしやお話しの場を体験できる。どなたでも参加でき、当日直接行ける。子ども向けの内容は明記がない。', 'axes': {'child_target': ('unknown', '子ども向けとは明記されていない。どなたでも参加できる'), 'interactivity': ('B', 'お話しを聞く鑑賞・体験型'), 'age_fit': ('unknown', '対象年齢は公式案内に明記がない'), 'stay_flexibility': ('B', '2時間の開催'), 'burden': ('A', '当日直接会場へ行ける'), 'cost': ('B', '無料（別途、郷土博物館の観覧料100円）'), 'reservation': ('A', '当日直接会場へ'), 'family_value': ('B', '古民家で昔の暮らしを家族で体験できる')}, 'strengths': ['古民家で昔の暮らしを体験できる', '当日直接行ける'], 'limitations': ['子ども向けとは明記されていない', '別途観覧料100円'], 'comparison': '総合B：気軽に体験できるが、子ども向けの内容は明記がない。', 'pf': 'pass', 'pos': ['official_date_confirmed']}, {'id': 'verified-20261128-adachi-seibutsuen-night', 'week': '2026-11-28', 'ward': '足立区', 'page': 'adachi_seibutsuen_night.html', 'name': '足立区生物園 夜間特別開園 in 光の祭典', 'url': 'https://www.city.adachi.tokyo.jp/k-iji/event/seibutsuen_yakankaien.html', 'date': '2026-11-28', 'end': '2026-11-29', 'period': '11/28〜12/20の土日（11/28・29、12/5・6、12/12・13、12/19・20）', 'time': '17:00〜21:00（最終入園20:30）', 'venue': '足立区生物園（足立区保木間2丁目17番1号 元渕江公園内）', 'price': '入園料が必要（金額は公式ページに記載なし）', 'image': 'https://www.city.adachi.tokyo.jp/images/70167/seibutsuen2.jpg', 'description': '光の祭典の開催期間に合わせて、生物園を夜間に特別開園。小学生以下は保護者同伴、事前申込不要。', 'cats': ['体験・ワークショップ', '公園・自然'], 'io': '屋内', 'res': {'required': False, 'note': '事前の申し込みは不要。直接会場へ。'}, 'quotes': ['光の祭典の開催期間に合わせて、生物園を夜間に特別開園します。', '開催日時2026年11月28日（土曜日）から2026年11月29日（日曜日）2026年12月5日（土曜日）から2026年12月6日（日曜日）', '各日、午後5時から午後9時※最終入園は午後8時30分', '足立区保木間二丁目17番1号（元渕江公園内）', '対象どなたでも※小学生以下の方は保護者の同伴が必要です。', '費用入園料が必要です。申込方法事前の申し込みは不要です。'], 'overall': 'B', 'basis': 'all_ages', 'child': False, 'reason': '夜に生物園を楽しめる特別開園。どなたでも入れ、小学生以下は保護者同伴。入園料が必要で、事前申込は不要。', 'axes': {'child_target': ('B', 'どなたでも入れ、小学生以下は保護者同伴と案内されている'), 'interactivity': ('B', '生き物の観察が中心で、体験内容の詳細は公式ページにない'), 'age_fit': ('unknown', '対象年齢の目安は公式案内に明記がない'), 'stay_flexibility': ('A', '17時〜21時の間、好きな時間に入園できる'), 'burden': ('B', '夜の開催で、天候や感染症等でプログラムが変更・中止になる場合がある'), 'cost': ('B', '入園料が必要（金額は公式ページにない）'), 'reservation': ('A', '事前の申し込みは不要'), 'family_value': ('B', '夜の生物園を家族で楽しめる')}, 'strengths': ['申込不要で夜の生物園に入れる'], 'limitations': ['入園料が必要（金額は公式ページにない）', '夜間の開催', 'プログラムが変更・中止になる場合がある'], 'comparison': '総合B：申込不要で気軽に行けるが、費用の金額と体験内容の詳細は公式ページにない。', 'pf': 'unknown', 'pos': ['official_date_confirmed']}, {'id': 'verified-20261205-adachi-seibutsuen-night', 'week': '2026-12-05', 'ward': '足立区', 'page': 'adachi_seibutsuen_night.html', 'name': '足立区生物園 夜間特別開園 in 光の祭典', 'url': 'https://www.city.adachi.tokyo.jp/k-iji/event/seibutsuen_yakankaien.html', 'date': '2026-12-05', 'end': '2026-12-06', 'period': '11/28〜12/20の土日（11/28・29、12/5・6、12/12・13、12/19・20）', 'time': '17:00〜21:00（最終入園20:30）', 'venue': '足立区生物園（足立区保木間2丁目17番1号 元渕江公園内）', 'price': '入園料が必要（金額は公式ページに記載なし）', 'image': 'https://www.city.adachi.tokyo.jp/images/70167/seibutsuen2.jpg', 'description': '光の祭典の開催期間に合わせて、生物園を夜間に特別開園。小学生以下は保護者同伴、事前申込不要。', 'cats': ['体験・ワークショップ', '公園・自然'], 'io': '屋内', 'res': {'required': False, 'note': '事前の申し込みは不要。直接会場へ。'}, 'quotes': ['光の祭典の開催期間に合わせて、生物園を夜間に特別開園します。', '開催日時2026年11月28日（土曜日）から2026年11月29日（日曜日）2026年12月5日（土曜日）から2026年12月6日（日曜日）', '各日、午後5時から午後9時※最終入園は午後8時30分', '足立区保木間二丁目17番1号（元渕江公園内）', '対象どなたでも※小学生以下の方は保護者の同伴が必要です。', '費用入園料が必要です。申込方法事前の申し込みは不要です。'], 'overall': 'B', 'basis': 'all_ages', 'child': False, 'reason': '夜に生物園を楽しめる特別開園。どなたでも入れ、小学生以下は保護者同伴。入園料が必要で、事前申込は不要。', 'axes': {'child_target': ('B', 'どなたでも入れ、小学生以下は保護者同伴と案内されている'), 'interactivity': ('B', '生き物の観察が中心で、体験内容の詳細は公式ページにない'), 'age_fit': ('unknown', '対象年齢の目安は公式案内に明記がない'), 'stay_flexibility': ('A', '17時〜21時の間、好きな時間に入園できる'), 'burden': ('B', '夜の開催で、天候や感染症等でプログラムが変更・中止になる場合がある'), 'cost': ('B', '入園料が必要（金額は公式ページにない）'), 'reservation': ('A', '事前の申し込みは不要'), 'family_value': ('B', '夜の生物園を家族で楽しめる')}, 'strengths': ['申込不要で夜の生物園に入れる'], 'limitations': ['入園料が必要（金額は公式ページにない）', '夜間の開催', 'プログラムが変更・中止になる場合がある'], 'comparison': '総合B：申込不要で気軽に行けるが、費用の金額と体験内容の詳細は公式ページにない。', 'pf': 'unknown', 'pos': ['official_date_confirmed']}, {'id': 'verified-20261212-adachi-seibutsuen-night', 'week': '2026-12-12', 'ward': '足立区', 'page': 'adachi_seibutsuen_night.html', 'name': '足立区生物園 夜間特別開園 in 光の祭典', 'url': 'https://www.city.adachi.tokyo.jp/k-iji/event/seibutsuen_yakankaien.html', 'date': '2026-12-12', 'end': '2026-12-13', 'period': '11/28〜12/20の土日（11/28・29、12/5・6、12/12・13、12/19・20）', 'time': '17:00〜21:00（最終入園20:30）', 'venue': '足立区生物園（足立区保木間2丁目17番1号 元渕江公園内）', 'price': '入園料が必要（金額は公式ページに記載なし）', 'image': 'https://www.city.adachi.tokyo.jp/images/70167/seibutsuen2.jpg', 'description': '光の祭典の開催期間に合わせて、生物園を夜間に特別開園。小学生以下は保護者同伴、事前申込不要。', 'cats': ['体験・ワークショップ', '公園・自然'], 'io': '屋内', 'res': {'required': False, 'note': '事前の申し込みは不要。直接会場へ。'}, 'quotes': ['光の祭典の開催期間に合わせて、生物園を夜間に特別開園します。', '開催日時2026年11月28日（土曜日）から2026年11月29日（日曜日）2026年12月5日（土曜日）から2026年12月6日（日曜日）', '各日、午後5時から午後9時※最終入園は午後8時30分', '足立区保木間二丁目17番1号（元渕江公園内）', '対象どなたでも※小学生以下の方は保護者の同伴が必要です。', '費用入園料が必要です。申込方法事前の申し込みは不要です。'], 'overall': 'B', 'basis': 'all_ages', 'child': False, 'reason': '夜に生物園を楽しめる特別開園。どなたでも入れ、小学生以下は保護者同伴。入園料が必要で、事前申込は不要。', 'axes': {'child_target': ('B', 'どなたでも入れ、小学生以下は保護者同伴と案内されている'), 'interactivity': ('B', '生き物の観察が中心で、体験内容の詳細は公式ページにない'), 'age_fit': ('unknown', '対象年齢の目安は公式案内に明記がない'), 'stay_flexibility': ('A', '17時〜21時の間、好きな時間に入園できる'), 'burden': ('B', '夜の開催で、天候や感染症等でプログラムが変更・中止になる場合がある'), 'cost': ('B', '入園料が必要（金額は公式ページにない）'), 'reservation': ('A', '事前の申し込みは不要'), 'family_value': ('B', '夜の生物園を家族で楽しめる')}, 'strengths': ['申込不要で夜の生物園に入れる'], 'limitations': ['入園料が必要（金額は公式ページにない）', '夜間の開催', 'プログラムが変更・中止になる場合がある'], 'comparison': '総合B：申込不要で気軽に行けるが、費用の金額と体験内容の詳細は公式ページにない。', 'pf': 'unknown', 'pos': ['official_date_confirmed']}, {'id': 'verified-20261219-adachi-seibutsuen-night', 'week': '2026-12-19', 'ward': '足立区', 'page': 'adachi_seibutsuen_night.html', 'name': '足立区生物園 夜間特別開園 in 光の祭典', 'url': 'https://www.city.adachi.tokyo.jp/k-iji/event/seibutsuen_yakankaien.html', 'date': '2026-12-19', 'end': '2026-12-20', 'period': '11/28〜12/20の土日（11/28・29、12/5・6、12/12・13、12/19・20）', 'time': '17:00〜21:00（最終入園20:30）', 'venue': '足立区生物園（足立区保木間2丁目17番1号 元渕江公園内）', 'price': '入園料が必要（金額は公式ページに記載なし）', 'image': 'https://www.city.adachi.tokyo.jp/images/70167/seibutsuen2.jpg', 'description': '光の祭典の開催期間に合わせて、生物園を夜間に特別開園。小学生以下は保護者同伴、事前申込不要。', 'cats': ['体験・ワークショップ', '公園・自然'], 'io': '屋内', 'res': {'required': False, 'note': '事前の申し込みは不要。直接会場へ。'}, 'quotes': ['光の祭典の開催期間に合わせて、生物園を夜間に特別開園します。', '開催日時2026年11月28日（土曜日）から2026年11月29日（日曜日）2026年12月5日（土曜日）から2026年12月6日（日曜日）', '各日、午後5時から午後9時※最終入園は午後8時30分', '足立区保木間二丁目17番1号（元渕江公園内）', '対象どなたでも※小学生以下の方は保護者の同伴が必要です。', '費用入園料が必要です。申込方法事前の申し込みは不要です。'], 'overall': 'B', 'basis': 'all_ages', 'child': False, 'reason': '夜に生物園を楽しめる特別開園。どなたでも入れ、小学生以下は保護者同伴。入園料が必要で、事前申込は不要。', 'axes': {'child_target': ('B', 'どなたでも入れ、小学生以下は保護者同伴と案内されている'), 'interactivity': ('B', '生き物の観察が中心で、体験内容の詳細は公式ページにない'), 'age_fit': ('unknown', '対象年齢の目安は公式案内に明記がない'), 'stay_flexibility': ('A', '17時〜21時の間、好きな時間に入園できる'), 'burden': ('B', '夜の開催で、天候や感染症等でプログラムが変更・中止になる場合がある'), 'cost': ('B', '入園料が必要（金額は公式ページにない）'), 'reservation': ('A', '事前の申し込みは不要'), 'family_value': ('B', '夜の生物園を家族で楽しめる')}, 'strengths': ['申込不要で夜の生物園に入れる'], 'limitations': ['入園料が必要（金額は公式ページにない）', '夜間の開催', 'プログラムが変更・中止になる場合がある'], 'comparison': '総合B：申込不要で気軽に行けるが、費用の金額と体験内容の詳細は公式ページにない。', 'pf': 'unknown', 'pos': ['official_date_confirmed']}, {'id': 'verified-20261128-edogawa-harue-fes', 'week': '2026-11-28', 'ward': '江戸川区', 'page': 'edogawa_harue_fes.html', 'name': '第3回はるえフェス 未来をつなぐ福祉体験型スタンプラリー！', 'url': 'https://www.city.edogawa.tokyo.jp/event/1128fes.html', 'date': '2026-11-28', 'period': '11/28(土)', 'time': '10:00〜16:00', 'venue': '春江小学校 体育館・グラウンド（江戸川区瑞江1丁目3番30号）', 'price': '無料', 'image': 'https://www.city.edogawa.tokyo.jp/images/73616/1128fes.jpg', 'description': '音楽フェスティバルと、障害者施設のブースを巡る体験型スタンプラリー。小学生・中学生・地域住民が対象。申込不要。', 'cats': ['体験・ワークショップ', '地域交流'], 'io': '屋内・屋外', 'res': {'required': False, 'note': '申し込み不要。'}, 'quotes': ['音楽フェスティバルや体験型のスタンプラリーを実施します。', '開催日時2026年11月28日（土曜日）10時00分から16時00分', '申し込み不要場所春江小学校（体育館・グラウンド）住所瑞江一丁目3番30号', '複数の障害者施設や春江小学校が協力し、小学生たちに障害者の日常や困難を理解し、共感する機会を提供します。', '対象小学生、中学生、地域住民の方'], 'overall': 'B', 'basis': 'child_program', 'child': True, 'reason': '小学生向けに、障害者施設のブースを巡るスタンプラリーと音楽フェスティバルがある。無料・申込不要。', 'axes': {'child_target': ('A', '小学生・中学生・地域住民が対象で、小学生向けのスタンプラリーがある'), 'interactivity': ('A', 'ブースを巡る体験型のスタンプラリーと音楽'), 'age_fit': ('B', '小学生・中学生・地域住民と案内。細かな年齢条件は明記がない'), 'stay_flexibility': ('A', '10時〜16時の間、好きな時間に参加できる'), 'burden': ('B', '小学校での開催。内容の詳細は公式ページに少ない'), 'cost': ('A', '費用無料'), 'reservation': ('A', '申し込み不要'), 'family_value': ('B', '福祉の体験を家族で無料で楽しめる')}, 'strengths': ['無料・申込不要で体験型スタンプラリー', '音楽フェスティバル'], 'limitations': ['内容の詳細は公式ページに少ない'], 'comparison': '総合B：無料・申込不要で体験できるが、詳細な内容は公式ページに少ない。', 'pf': 'pass', 'pos': ['official_date_confirmed', 'child_activity_confirmed']}, {'id': 'verified-20261129-edogawa-seinen-carnival', 'week': '2026-11-28', 'ward': '江戸川区', 'page': 'edogawa_seinen_carnival.html', 'name': '第46回青年カーニバル', 'url': 'https://www.city.edogawa.tokyo.jp/event/46seikani.html', 'date': '2026-11-29', 'period': '11/29(日)', 'time': '11:00〜18:00（式典16:00）', 'venue': '小松川小学校校庭ほか（江戸川区）', 'price': '無料', 'image': 'https://www.city.edogawa.tokyo.jp/images/73673/mikoshi.jpg', 'description': '平井小松川青年連絡会が企画する地域のおまつり。みこし・模擬店・ステージなどがある。申込不要。', 'cats': ['体験・ワークショップ', '地域交流'], 'io': '屋外', 'res': {'required': False, 'note': '申し込み不要。'}, 'quotes': ['平井小松川青年連絡会【各町会・自治会の青年部の集まり】が企画・立案しているおまつりです。', 'みこし・模擬店・ステージ等、多様なプログラムをお届けします！', '開催日時2026年11月29日（日曜日）11時00分から18時00分【式典】16時00分', '申し込み不要場所小松川小学校校庭ほかホームページ第46回青年カーニバル費用無料'], 'overall': 'B', 'basis': 'all_ages', 'child': False, 'reason': 'みこし・模擬店・ステージがある地域のおまつり。無料・申込不要で、小学校の校庭で開催。子ども向けとは明記されていない。', 'axes': {'child_target': ('unknown', '子ども向けとは明記されていない。地域のおまつり'), 'interactivity': ('B', 'みこし・模擬店・ステージなど。体験内容の詳細は公式ページにない'), 'age_fit': ('unknown', '対象年齢は公式案内に明記がない'), 'stay_flexibility': ('A', '11時〜18時の間、好きな時間に立ち寄れる'), 'burden': ('B', '屋外の校庭での開催'), 'cost': ('A', '費用無料（模擬店は購入）'), 'reservation': ('A', '申し込み不要'), 'family_value': ('B', '地域のおまつりを家族で楽しめる')}, 'strengths': ['無料・申込不要で7時間の開催'], 'limitations': ['子ども向けとは明記されていない', '屋外開催'], 'comparison': '総合B：無料・申込不要で気軽だが、子ども向けの内容は明記がない。', 'pf': 'pass', 'pos': ['official_date_confirmed']}, {'id': 'verified-20261128-taito-asobo-festa', 'week': '2026-11-28', 'ward': '台東区', 'page': 'taito_asobo_festa.html', 'name': '親子で遊ぼう！「アソボーフェスタ」', 'url': 'https://www.city.taito.lg.jp/kosodatekyouiku/kosodate/mokutei/kouzaevent/kodomo_center/combination/asobo.html', 'date': '2026-11-28', 'period': '11/28(土)', 'time': '10:30〜15:30', 'venue': '寿子ども家庭支援センター のびのびひろば（ことぶきこども園3階体育館・台東区寿1丁目10番10号）', 'price': '無料', 'description': 'いろいろなおもちゃに触れて遊べる親子向けイベント。手作り体験のコーナーもある。0歳から小学3年生までの児童と保護者が対象。申込不要・無料。', 'cats': ['体験・ワークショップ', '親子あそび'], 'io': '屋内', 'res': {'required': False, 'note': '事前申込不要。'}, 'quotes': ['いろいろなおもちゃに触れて遊んでいただくイベントです。', '手作り体験のコーナーもあります。', '日時令和8年11月28日（土曜日）10時30分～15時30分', '会場寿子ども家庭支援センターのびのびひろば（ことぶきこども園3階体育館）', '対象0歳から小学3年生までの児童と保護者', '申込・費用事前申込不要参加費無料'], 'overall': 'A', 'basis': 'child_program', 'child': True, 'reason': '0歳から小学3年生までの親子向けに、おもちゃで遊ぶ・手作り体験ができる。無料・申込不要で、5時間開催。', 'axes': {'child_target': ('A', '0歳から小学3年生までの児童と保護者が対象'), 'interactivity': ('A', 'おもちゃで遊び、手作り体験もできる'), 'age_fit': ('A', '対象は0歳から小学3年生までと明記'), 'stay_flexibility': ('A', '10時30分〜15時30分の間、好きな時間に参加できる'), 'burden': ('A', '事前申込不要・無料で気軽に参加できる'), 'cost': ('A', '参加費無料'), 'reservation': ('A', '事前申込不要'), 'family_value': ('A', '小さな子どもと無料で遊べる親子イベント')}, 'strengths': ['0歳から小3の親子向け', '無料・申込不要で5時間開催'], 'limitations': ['会場は園の体育館'], 'comparison': '総合A：対象年齢が明確で、無料・申込不要の参加型。', 'pf': 'pass', 'pos': ['official_date_confirmed', 'child_activity_confirmed']}, {'id': 'verified-20261128-itabashi-hasune-panda-time', 'week': '2026-11-28', 'ward': '板橋区', 'page': 'itabashi_panda_time.html', 'name': '【蓮根図書館】パンダたいむ（おはなし会・工作）', 'url': 'https://www.city.itabashi.tokyo.jp/kosodate/1000930/etc/1066379.html', 'date': '2026-11-28', 'period': '11/28(土)', 'time': '11:00〜11:40', 'venue': '舟渡ホール（板橋区・蓮根図書館主催）', 'price': '無料', 'description': '小学生以下を対象にした、おはなし会と簡単な工作。未就学児は保護者同伴。申込不要、定員15人（先着順）。', 'cats': ['体験・ワークショップ', '絵本・お話'], 'io': '屋内', 'res': {'required': False, 'note': '申込不要。定員15人（先着順）。'}, 'quotes': ['開催日2026年11月28日（土曜日）開催時間午前11時から午前11時40分まで', '開催場所舟渡ホール内容おはなし会・簡単な工作', '申込み不要費用不要定員15人（先着順）', '対象小学生以下（未就学児は保護者同伴）', 'イベントカテゴリ：子ども・保護者向け'], 'overall': 'B', 'basis': 'child_program', 'child': True, 'reason': '小学生以下向けのおはなし会と簡単な工作。無料・申込不要だが、40分で定員15人の先着順。', 'axes': {'child_target': ('A', '小学生以下が対象の子ども・保護者向けイベント'), 'interactivity': ('B', 'おはなし会と簡単な工作'), 'age_fit': ('A', '対象は小学生以下（未就学児は保護者同伴）と明記'), 'stay_flexibility': ('C', '11時〜11時40分の40分間'), 'burden': ('B', '定員15人の先着順'), 'cost': ('A', '費用不要'), 'reservation': ('A', '申込不要'), 'family_value': ('B', '小さな子どもと気軽に参加できる短時間のイベント')}, 'strengths': ['無料・申込不要で小学生以下向け'], 'limitations': ['40分と短い', '定員15人の先着順'], 'comparison': '総合B：子ども向けで無料・申込不要だが、短時間で定員が少ない。', 'pf': 'pass', 'pos': ['official_date_confirmed', 'child_activity_confirmed']}]
RAW = SPECS_RAW
SPECS = []
for _r in RAW:
    _s = dict(_r)
    _s['categories'] = _s.pop('cats'); _s['indoor_outdoor'] = _s.pop('io'); _s['reservation'] = _s.pop('res')
    _s['child_activity'] = _s.pop('child'); _s['price_field'] = _s.pop('pf'); _s['positive'] = _s.pop('pos')
    SPECS.append(_s)
NEW_IDS = [s['id'] for s in SPECS]
SHARDS = {w: f'{w}-events-lead5-20261119.json' for w in ('2026-11-21', '2026-11-28', '2026-12-05', '2026-12-12', '2026-12-19')}
HELD = {'suginami-nishiogi-library-oshanashi-20261129': '条件は合うが11/28週の画像率が70%を割るため保留（申込制）', 'suginami-asagaya-xmas-market-20261129': '条件は合うが11/28週の画像率が70%を割るため保留', 'suginami-beach-sports-20261129': '条件は合うが11/28週の画像率が70%を割るため保留', 'shinjuku-3r-festa-20261128': '条件は合うが11/28週の画像率が70%を割るため保留（画像宣言なし）', 'shinjuku-poreporefes-20261128': '条件は合うが11/28週の画像率が70%を割るため保留', 'itabashi-hasune-programming-20261121': '申込制で定員10人（先着）。満員の可能性があり未確認', 'edogawa-kodomo-mirai-kan-20261123': '子ども未来館の3講座は抽選で、申込期間が終了済み', 'toshima-kumanokko-day-20261123': '対象が豊島区立学校等の保護者', 'edogawa-konnitsuto-ichi-20261121': 'おもちゃの病院は修理サービスで、子ども向けの催しではない'}


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
        run['lead5_addition_20261119'] = {
            'kind': 'individually_verified_official_events_from_lead_triage', 'added_ids': [i[0]['id'] for i in items],
            'held_not_published': sorted(HELD), 'pages_committed_at': 'research/2026-11-19-audit/pages/',
            'base_data_production_sha': BASE, 'global_source_audit_complete': False}
        S.jdump(d / f'{week}-run.json', run)
        for x in m['weekends']:
            if x['sat'] == week:
                x['count'] += n
    m['generated'] = '2026-11-19T14:00:00+09:00'
    S.jdump(d / 'manifest.json', m)
    h = S.jload(d / 'update_history.json')
    h['history'].append({
        'run_id': 'lead5-addition-20261119', 'run_type': 'manual_verified_lead5_addition',
        'status': 'verified_subset_publication', 'as_of_jst': '2026-11-19', 'executed_at': m['generated'],
        'base_data_production_sha': BASE, 'target_weekends': sorted(derived),
        'prior_active_week_records': 459, 'candidate_active_week_records': 469, 'added_weekly_records': 10,
        'new_event_ids': NEW_IDS, 'held_not_published': sorted(HELD),
        'existing_event_records_physically_deleted': 0, 'image_only_updates': 0,
        'source_failures_remain_unverified': True, 'global_source_audit_complete': False,
        'full_23_ward_25_source_audit_complete': False,
        'note': '残りの候補プールとカレンダーの個別ページを精読し、公式個別ページで条件を確認できた7イベント（10週別レコード）のみ追加。条件が合わないものは掲載せず理由を保存。',
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
