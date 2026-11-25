#!/usr/bin/env python3
"""Eight weekly records (eight events) found by reading the remaining pool pages and calendar detail pages (2026-11-19).

Raw official pages are committed unchanged under research/2026-11-19-audit/pages/
(fetched by read-only workflows, HTTP 200). Quotes must occur verbatim in those pages.
The gate validator re-derives every record from this module and requires exact equality.
"""
import argparse, hashlib, json, pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import suginami_addition_20261118 as S

BASE = 'e68dbb647f405c97175bb5cd5337466dddb37720'   # data-production after the lead4 addition (476 records)
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


SPECS_RAW = [{'id': 'verified-20261121-edogawa-fuyusakura', 'week': '2026-11-21', 'ward': '江戸川区', 'page': 'edogawa_fuyusakura.html', 'name': '新川さくら館 冬ざくらイルミネーション', 'url': 'https://www.city.edogawa.tokyo.jp/event/26fuyusakura.html', 'date': '2026-11-21', 'end': '2026-11-22', 'period': '11/21〜12/25', 'time': '16:30〜21:30', 'venue': '新川さくら館広場（江戸川区船堀7丁目15番12号）', 'price': '無料', 'description': '新川さくら館の広場で開催するイルミネーション。冬の夜を彩る光を楽しめる。無料・申込不要。', 'cats': ['公園・自然', '地域交流'], 'io': '屋外', 'res': {'required': False, 'note': '申し込み不要。'}, 'quotes': ['きらめく光に包まれた幻想的な冬のお花見をお楽しみください。', '開催日時2026年11月21日（土曜日）から2026年12月25日（金曜日）16時30分～21時30分', '申し込み不要場所新川さくら館広場住所江戸川区船堀7丁目15番12号', '冬の夜を彩るイルミネーションを、ぜひお楽しみください。', '費用無料問合せ新川さくら館'], 'overall': 'B', 'basis': 'all_ages', 'child': False, 'reason': '冬の夜のイルミネーション。無料・申込不要で、5時間の開催。子ども向けとは明記されていない。', 'axes': {'child_target': ('unknown', '子ども向けとは明記されていない'), 'interactivity': ('B', 'イルミネーションの観賞が中心'), 'age_fit': ('unknown', '対象年齢は明記がない'), 'stay_flexibility': ('A', '16時30分〜21時30分の間、好きな時間に立ち寄れる'), 'burden': ('B', '夜の屋外での開催'), 'cost': ('A', '費用無料'), 'reservation': ('A', '申し込み不要'), 'family_value': ('B', '冬の夜の光を家族で楽しめる')}, 'strengths': ['無料・申込不要で5週間にわたり開催'], 'limitations': ['子ども向けとは明記されていない', '夜の屋外開催'], 'comparison': '総合B：無料・申込不要で気軽に行けるが、子ども向けの内容は明記がない。', 'pf': 'unknown', 'pos': ['official_date_confirmed']}, {'id': 'verified-20261128-adachi-seibutsuen-hotaru', 'week': '2026-11-28', 'ward': '足立区', 'page': 'adachi_seibutsuen_hotaru.html', 'name': '足立区生物園 冬のホタル観賞会（夜間特別開園）', 'url': 'https://www.city.adachi.tokyo.jp/k-iji/event/seibutsuen_huyuhotaru.html', 'date': '2026-11-28', 'end': '2026-11-29', 'period': '11/28〜12/20の土日', 'time': '18:00〜21:00（20分ごと9回、最終回20:40開始）', 'venue': '足立区生物園（足立区保木間2丁目17番1号 元渕江公園内）', 'price': '無料（別途入園料が必要）', 'description': '室内の水槽で光るヘイケボタルを観賞できる夜間特別開園。各回40人の先着順で、事前申込は不要。就学前の子どもは保護者同伴。', 'cats': ['体験・ワークショップ', '公園・自然'], 'io': '屋内', 'res': {'required': False, 'note': '事前の申し込みは不要。直接会場へ。'}, 'quotes': ['室内に置かれた水槽の中で輝くヘイケボタルの幻想的な光を観賞できます。', '各日、午後6時から午後9時※最終回は午後8時40分開始。20分ごとに9回実施。', '対象どなたでも※就学前の子どもは保護者の同伴が必要です。', '募集人数各40人（先着順）費用無料※入園料が必要です。申込方法事前の申し込みは不要です。'], 'overall': 'B', 'basis': 'all_ages', 'child': False, 'reason': '冬のホタルを水槽で観賞できる夜の特別開園。どなたでも入れ、就学前は保護者同伴。各回40人の先着で、事前申込は不要。', 'axes': {'child_target': ('B', 'どなたでも入れ、就学前の子どもは保護者同伴と案内'), 'interactivity': ('B', 'ホタルの観賞が中心'), 'age_fit': ('unknown', '対象年齢の目安は明記がない'), 'stay_flexibility': ('B', '20分ごと9回の入れ替え制で、各回40人の先着'), 'burden': ('B', '夜の開催で、生体の状況により中止になる場合がある'), 'cost': ('B', '費用無料だが、別途入園料が必要'), 'reservation': ('A', '事前の申し込みは不要'), 'family_value': ('B', '冬にホタルを家族で観賞できる')}, 'strengths': ['申込不要で冬のホタルを観賞できる'], 'limitations': ['各回40人の先着順', '別途入園料が必要', '生体の状況により中止になる場合がある'], 'comparison': '総合B：申込不要で珍しい観賞ができるが、各回の定員が40人で入園料が別に必要。', 'pf': 'unknown', 'pos': ['official_date_confirmed']}, {'id': 'verified-20261122-taito-asakusabashi-kosaku', 'week': '2026-11-21', 'ward': '台東区', 'page': 'taito_asakusabashi_kosaku.html', 'name': 'あさくさばしぶんしつ おはなしこうさく会（台東区立図書館）', 'url': 'https://www.city.taito.lg.jp/library/kodomo/event/event11/01583891201702041601.html', 'date': '2026-11-22', 'period': '11/22(日)', 'time': '11:00〜11:30', 'venue': '浅草橋区民館 6階和室', 'price': '無料', 'description': '幼児から小学生までの子どもと保護者向けの、おはなしと工作の会。申込不要・参加費無料で、材料は図書館が用意。8組まで。', 'cats': ['体験・ワークショップ', '絵本・お話'], 'io': '屋内', 'res': {'required': False, 'note': '申込不要。当日直接会場へ。8組まで。'}, 'quotes': ['日時令和8年11月（がつ）22日（にち）（日曜日（にちようび））午前11時（じ）から11時（じ）30分（ふん）まで', '場所浅草橋区民館（あさくさばしくみんかん）6階和室（かいわしつ）', '対象・人数幼児（ようじ）から小学生（しょうがくせい）までのお子（こ）さんとその保護者（ほごしゃ）8組（くみ）', '申込不要（ふよう）※当日直接会場（とうじつちょくせつかいじょう）にお越（こ）しください', '参加費無料（むりょう）※材料（ざいりょう）は図書館（としょかん）で用意（ようい）します'], 'overall': 'B', 'basis': 'child_program', 'child': True, 'reason': '幼児から小学生の子どもと保護者向けの、おはなしと工作。無料・申込不要だが、30分で8組まで。', 'axes': {'child_target': ('A', '幼児から小学生までの子どもと保護者が対象'), 'interactivity': ('B', 'おはなしと工作'), 'age_fit': ('A', '幼児から小学生までと明記'), 'stay_flexibility': ('C', '11時〜11時30分の30分間'), 'burden': ('B', '8組までの定員'), 'cost': ('A', '参加費無料'), 'reservation': ('A', '申込不要'), 'family_value': ('B', '小さな子どもと無料で参加できる')}, 'strengths': ['無料・申込不要で子ども向け', '材料は図書館が用意'], 'limitations': ['30分と短い', '8組までの定員'], 'comparison': '総合B：子ども向けで無料・申込不要だが、短時間で8組までの定員。', 'pf': 'pass', 'pos': ['official_date_confirmed', 'child_activity_confirmed']}, {'id': 'verified-20261128-meguro-gohongi-oyako-asobo', 'week': '2026-11-28', 'ward': '目黒区', 'page': 'meguro_gohongi_oyako.html', 'name': '五本木住区センター児童館 乳幼児のつどい「親子で体を使って遊ぼう」', 'url': 'https://www.city.meguro.tokyo.jp/houkago/event/8gohongi-tudoi11.html', 'date': '2026-11-28', 'period': '11/28(土)', 'time': '10:30〜（受付10:20、終了時刻は公式ページの表記が不明確）', 'venue': '五本木住区センター児童館 プレイルーム（目黒区）', 'price': '公式ページに記載なし', 'description': 'ベビーから5歳児までと保護者が、体を使って遊ぶ乳幼児のつどい。日本体操研究所の講師が来る。予約不要で、当日児童館へ。', 'cats': ['体験・ワークショップ', '親子あそび'], 'io': '屋内', 'res': {'required': False, 'note': '予約不要。当日児童館へ。'}, 'quotes': ['日時令和8年11月28日（土曜日）午前10時30分から', '10時20分より受付を開始します。', '会場五本木住区センター児童館プレイルーム', '対象ベビーから5歳児までとその保護者', '講師日本体操研究所荒金幸子氏', '参加希望のかたは、当日児童館へお越しください。予約は不要です。'], 'overall': 'B', 'basis': 'child_program', 'child': True, 'reason': 'ベビーから5歳児までの親子が体を使って遊べる。予約不要。終了時刻と費用は公式ページに明記がない。', 'axes': {'child_target': ('A', 'ベビーから5歳児までとその保護者が対象'), 'interactivity': ('A', '親子で体を使って遊ぶ内容'), 'age_fit': ('A', 'ベビーから5歳児までと明記'), 'stay_flexibility': ('unknown', '終了時刻の表記が不明確'), 'burden': ('A', '予約不要で当日そのまま行ける'), 'cost': ('unknown', '費用の記載がない'), 'reservation': ('A', '予約不要'), 'family_value': ('B', '乳幼児と親子で体を動かして遊べる')}, 'strengths': ['0〜5歳の親子向け', '予約不要'], 'limitations': ['終了時刻と費用が公式ページに明記されていない'], 'comparison': '総合B：乳幼児向けで予約不要だが、終了時刻と費用の記載がない。', 'pf': 'pass', 'pos': ['official_date_confirmed', 'child_activity_confirmed']}, {'id': 'verified-20261128-suginami-unesco-tsudoi', 'week': '2026-11-28', 'ward': '杉並区', 'page': 'suginami_unesco_tsudoi.html', 'name': 'ユネスコのつどい2026『みんなが輝く未来のために』（展示）', 'url': 'https://www.city.suginami.tokyo.jp/s113/event/28869.html', 'date': '2026-11-28', 'end': '2026-11-29', 'period': '11/27(金)〜11/30(月)の展示（11/28・29が週末）', 'time': '10:00〜19:00', 'venue': 'セシオン杉並 1階・展示室（杉並区梅里1-22-32）', 'price': '展示は無料', 'description': 'ユネスコの紹介、子どもの権利のパネル展示、ちがいを発見する体験コーナー、キッズコーナー（絵本・工作）、世界遺産クイズなどの展示。展示は当日直接会場へ。', 'cats': ['体験・ワークショップ', '地域交流'], 'io': '屋内', 'res': {'required': False, 'note': '展示は当日直接会場へ（講演会は別途申込）。'}, 'quotes': ['子どもの権利、平和・さまざまな人との共生について考えるつどいです。', 'キッズコーナー（絵本・工作）、世界遺産クイズ等があります。', '（1）11月27日（金曜日）から11月30日（月曜日）午前10時から午後7時まで（最終日は午後4時まで）', '（1）セシオン杉並1階・展示室', '（1）当日直接会場へお越しください。', '費用（1）無料（2）資料代500円（学生以下は無料）'], 'overall': 'B', 'basis': 'child_program', 'child': True, 'reason': '展示室にキッズコーナー（絵本・工作）や体験コーナーがある。展示は無料で、当日直接行ける。', 'axes': {'child_target': ('B', 'どなたでも。キッズコーナー（絵本・工作）がある'), 'interactivity': ('B', '体験コーナーやクイズ、絵本・工作'), 'age_fit': ('unknown', '対象年齢の目安は明記がない'), 'stay_flexibility': ('A', '4日間、午前10時から夜7時まで好きな時間に立ち寄れる'), 'burden': ('A', '展示は当日直接会場へ行ける'), 'cost': ('A', '展示は無料'), 'reservation': ('A', '展示は申込不要'), 'family_value': ('B', '展示を見て、絵本や工作を家族で楽しめる')}, 'strengths': ['無料で当日直接行ける', 'キッズコーナーで絵本・工作'], 'limitations': ['講演会は別に申込が必要', '展示が中心で子ども向けの詳細は少ない'], 'comparison': '総合B：無料で気軽に立ち寄れるが、展示が中心で子ども向けの詳細は少ない。', 'pf': 'pass', 'pos': ['official_date_confirmed', 'child_activity_confirmed']}, {'id': 'verified-20261129-suginami-beach-sports', 'week': '2026-11-28', 'ward': '杉並区', 'page': 'suginami_beach_sports.html', 'name': 'ビーチスポーツイベント（TAC杉並区永福体育館）', 'url': 'https://www.city.suginami.tokyo.jp/s032/event/28976.html', 'date': '2026-11-29', 'period': '11/29(日)', 'time': '14:00〜16:30（雨天中止）', 'venue': 'TAC杉並区永福体育館 ビーチコート（杉並区永福1丁目7番6号）', 'price': '無料', 'description': 'ビーチフラッグスなど、大人も子どももビーチで楽しめるイベント。どなたでも参加でき、当日直接会場へ。小学3年生以下は保護者同伴。', 'cats': ['体験・ワークショップ', 'スポーツ'], 'io': '屋外', 'res': {'required': False, 'note': '当日直接会場へ。雨天中止。'}, 'quotes': ['子どもから大人までどなたでもご参加いただけます。', '（小学3年生以下保護者同伴）', 'ビーチフラッグスなど大人も子どももビーチで楽しめるイベントもりだくさん', '開催日2026年11月29日（日曜日）開催時間午後2時から午後4時30分まで（雨天中止）', '申し込み当日直接会場へお越しください。費用無料'], 'overall': 'B', 'basis': 'child_program', 'child': True, 'reason': 'ビーチフラッグスなど子どもも楽しめるビーチスポーツ。無料で当日直接行ける。雨天中止。', 'axes': {'child_target': ('B', '子どもから大人までどなたでも参加でき、小3以下は保護者同伴'), 'interactivity': ('A', 'ビーチフラッグスなどのスポーツ体験'), 'age_fit': ('B', '小学3年生以下は保護者同伴と明記'), 'stay_flexibility': ('B', '2時間30分の開催'), 'burden': ('B', '屋外で、雨天中止'), 'cost': ('A', '無料'), 'reservation': ('A', '当日直接会場へ'), 'family_value': ('B', '体を動かす体験を家族で楽しめる')}, 'strengths': ['無料・当日直接でビーチスポーツ体験'], 'limitations': ['雨天中止', '屋外開催'], 'comparison': '総合B：無料・当日直接でスポーツ体験ができるが、屋外開催で雨天中止になる。', 'pf': 'pass', 'pos': ['official_date_confirmed', 'child_activity_confirmed']}, {'id': 'verified-20261129-suginami-asagaya-xmas-market', 'week': '2026-11-28', 'ward': '杉並区', 'page': 'suginami_asagaya_xmas_market.html', 'name': 'クリスマス ワークショップ＆マーケット（コミュニティふらっと阿佐谷）', 'url': 'https://www.city.suginami.tokyo.jp/s113/event/28934.html', 'date': '2026-11-29', 'period': '11/29(日)', 'time': '10:00〜15:00', 'venue': 'コミュニティふらっと阿佐谷（杉並区阿佐谷北2丁目18番17号）', 'price': 'ワークショップにより有料', 'description': 'ハンドメイド作家によるクリスマスのワークショップとマーケット。子どもから大人まで楽しめる。当日直接会場へ（一部は事前申込可）。ワークショップは有料。', 'cats': ['体験・ワークショップ', '地域交流'], 'io': '屋内', 'res': {'required': False, 'note': '当日直接会場へ。一部のワークショップは事前申込が可能。'}, 'quotes': ['ハンドメイド作家によるクリスマスワークショップを開催します。', 'いろいろなワークショップを開催しますので、お子さんから大人までお楽しみいただけます。', '開催日2026年11月29日（日曜日）開催時間午前10時から午後3時まで', '申し込み当日直接会場へお越しください。一部事前申込が可能です。', '費用有料（参加するワークショップにより費用が異なります。）'], 'overall': 'B', 'basis': 'child_program', 'child': True, 'reason': 'クリスマスの飾りづくりなどのワークショップがあり、お子さんから大人まで楽しめる。当日直接行ける。ワークショップは有料で各ブース約10名。', 'axes': {'child_target': ('B', 'お子さんから大人までと案内'), 'interactivity': ('A', 'クリスマスの飾りづくりなどのワークショップ'), 'age_fit': ('unknown', '対象年齢は明記がない'), 'stay_flexibility': ('A', '10時〜15時の間、好きな時間に立ち寄れる'), 'burden': ('B', '各ブース約10名の定員'), 'cost': ('B', 'ワークショップにより有料'), 'reservation': ('A', '当日直接会場へ'), 'family_value': ('B', 'クリスマスの工作を家族で楽しめる')}, 'strengths': ['クリスマスの工作を体験できる', '当日直接行ける'], 'limitations': ['ワークショップは有料', '各ブース約10名'], 'comparison': '総合B：工作を体験できるが、有料で各ブースの定員が少ない。', 'pf': 'pass', 'pos': ['official_date_confirmed', 'child_activity_confirmed']}, {'id': 'verified-20261128-shinjuku-3r-festa', 'week': '2026-11-28', 'ward': '新宿区', 'page': 'shinjuku_3r_festa.html', 'name': '新宿3Rフェスタ～みんなでつくる地球の未来～', 'url': 'https://www.city.shinjuku.lg.jp/event/seikankyo03_002041.html', 'date': '2026-11-28', 'period': '11/28(土)', 'time': '11:00〜16:00（10:45オープニング）', 'venue': '新宿駅西口広場イベントコーナー', 'price': '参加無料', 'description': 'ごみ減量のヒントとなる3Rを楽しみながら学ぶイベント。スタンプラリー、抽選会、ステージ、20以上のブース出展。当日直接会場へ。', 'cats': ['体験・ワークショップ', '地域交流'], 'io': '屋外', 'res': {'required': False, 'note': '当日、マイバッグを持って直接会場へ。'}, 'quotes': ['新宿3Rフェスタはごみ減量のヒントとなる3Ｒについて、楽しみながら理解を深めるイベントです。', '毎年、スタンプラリーや抽選会、ステージのほか、区内の事業者や区民団体など20以上のブースが出展します。', '当日マイバッグをお持ちの上、直接会場へおいでください。', '日程令和8年11月28日（土）11:00～16:00（10:45からオープニングセレモニー）', '会場新宿駅西口広場イベントコーナー地図費用参加無料'], 'overall': 'B', 'basis': 'all_ages', 'child': False, 'reason': 'スタンプラリーや抽選会、ステージ、20以上のブースがある環境イベント。無料・当日直接参加。子ども向けとは明記されていない。', 'axes': {'child_target': ('unknown', '子ども向けとは明記されていない'), 'interactivity': ('B', 'スタンプラリーやブース、ステージ'), 'age_fit': ('unknown', '対象年齢は明記がない'), 'stay_flexibility': ('A', '11時〜16時の間、好きな時間に立ち寄れる'), 'burden': ('B', '駅前広場での開催'), 'cost': ('A', '参加無料'), 'reservation': ('A', '当日直接会場へ'), 'family_value': ('B', 'スタンプラリーなどを家族で楽しめる')}, 'strengths': ['無料・当日直接でスタンプラリーなど'], 'limitations': ['子ども向けとは明記されていない', '駅前広場の屋外開催'], 'comparison': '総合B：無料で参加できるが、子ども向けとは明記されていない。', 'pf': 'unknown', 'pos': ['official_date_confirmed']}]
RAW = SPECS_RAW
SPECS = []
for _r in RAW:
    _s = dict(_r)
    _s['categories'] = _s.pop('cats'); _s['indoor_outdoor'] = _s.pop('io'); _s['reservation'] = _s.pop('res')
    _s['child_activity'] = _s.pop('child'); _s['price_field'] = _s.pop('pf'); _s['positive'] = _s.pop('pos')
    SPECS.append(_s)
NEW_IDS = [s['id'] for s in SPECS]
SHARDS = {w: f'{w}-events-lead7-20261119.json' for w in ('2026-11-21', '2026-11-28', '2026-12-05', '2026-12-12', '2026-12-19')}
HELD = {'shinjuku-poreporefes-20261128': 'ゲームコーナー等はあるが、子ども向けの情報・費用・対象年齢の記載が乏しく、評価がC（掲載基準のB以上に届かない）', 'itabashi-hasune-programming-20261121': '申込制で定員10人（先着）。満員の可能性があり未確認', 'suginami-nishiogi-library-oshanashi-20261129': '申込制（電話・窓口、定員20名の先着）。11/1受付開始で満員の可能性があり未確認', 'edogawa-kodomo-mirai-kan-20261123': '子ども未来館の3講座は抽選で、申込期間が終了済み', 'toshima-kumanokko-day-20261123': '対象が豊島区立学校等の保護者', 'edogawa-konnitsuto-ichi-20261121': 'おもちゃの病院は修理サービスで、子ども向けの催しではない', 'adachi-ouka-hakoniwa-20261128': '材料費3,300円・先着10人で申込が必要', 'chiyoda-first-bicycle-20261129': '千代田区在住者のみが対象', 'suginami-nazo-sanpo-20261116': '区内在住・在勤・在学の方が対象', 'suginami-futago-ryuseigun-20261212': '抽選で、申込が12/1までに終了', 'itabashi-shimizu-berezza-20261123': '公式ページに内容が「準備中」', 'arakawa-ishihama-papa-20261123': '石浜ふれあい館パパとあそぼうは日時・内容の記載がなく確認できない'}


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
        run['lead7_addition_20261119'] = {
            'kind': 'individually_verified_official_events_from_lead_triage', 'added_ids': [i[0]['id'] for i in items],
            'held_not_published': sorted(HELD), 'pages_committed_at': 'research/2026-11-19-audit/pages/',
            'base_data_production_sha': BASE, 'global_source_audit_complete': False}
        S.jdump(d / f'{week}-run.json', run)
        for x in m['weekends']:
            if x['sat'] == week:
                x['count'] += n
    m['generated'] = '2026-11-19T18:00:00+09:00'
    S.jdump(d / 'manifest.json', m)
    h = S.jload(d / 'update_history.json')
    h['history'].append({
        'run_id': 'lead7-addition-20261119', 'run_type': 'manual_verified_lead7_addition',
        'status': 'verified_subset_publication', 'as_of_jst': '2026-11-19', 'executed_at': m['generated'],
        'base_data_production_sha': BASE, 'target_weekends': sorted(derived),
        'prior_active_week_records': 476, 'candidate_active_week_records': 484, 'added_weekly_records': 8,
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
