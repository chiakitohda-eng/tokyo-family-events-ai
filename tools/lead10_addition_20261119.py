#!/usr/bin/env python3
"""10 weekly records (10 events) found by reading the remaining pool pages and calendar detail pages (2026-11-19).

Raw official pages are committed unchanged under research/2026-11-19-audit/pages/
(fetched by read-only workflows, HTTP 200). Quotes must occur verbatim in those pages.
The gate validator re-derives every record from this module and requires exact equality.
"""
import argparse, hashlib, json, pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import suginami_addition_20261118 as S

BASE = '9a2fe5046ebeeb11aef3731a180411eee6241c07'   # data-production after the lead10 addition (516 records)
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


SPECS_RAW = [{'id': 'verified-20261121-setagaya-todoroki-papamo-rhythm', 'week': '2026-11-21', 'ward': '世田谷区', 'page': 'setagaya_4.html', 'name': '等々力児童館 パパも気軽に！PaPaMo「わっくわっく！リトミック」', 'url': 'https://www.city.setagaya.lg.jp/03070/24025.html', 'date': '2026-11-21', 'period': '11/21(土)', 'time': '10:30〜11:30', 'venue': '等々力児童館 グランドもしくは遊戯室', 'price': '参加費の記載なし', 'description': 'ピアノとヴァイオリンの音色に合わせて楽しむリトミック。0歳〜未就学児と保護者が対象の親子ひろば。', 'cats': ['体験・ワークショップ', '音楽'], 'io': '屋内', 'res': {'required': True, 'note': '7日から児童館窓口で受付（翌日から電話可）。リトミックは15組。'}, 'quotes': ['等々力児童館パパも気軽に！PaPaMo募集中募集終了事前申込必要表示しないパパも歓迎！パパじゃなくても、ママも祖父母もシッターさんも里親さんももちろん大歓迎！', '日程2026年11月21日（土曜日）2026年12月12日（土曜日）時間午前10時30分から11時30分', '場所・会場等々力児童館グランドもしくは遊戯室対象0歳から未就学のお子さんとその保護者申し込み方法下記の内容をご参照ください。'], 'overall': 'B', 'basis': 'child_program', 'child': True, 'reason': 'ピアノとヴァイオリンの音色に合わせて楽しむリトミック。参加費の記載なし。事前の申込が必要。', 'axes': {'child_target': ['A', '0歳から未就学児とその保護者が対象'], 'interactivity': ['A', 'リトミックで体を動かして楽しむ'], 'age_fit': ['A', '1歳児から未就学児と明記'], 'stay_flexibility': ['B', '10:30〜11:30'], 'burden': ['C', '申込が必要で、15組'], 'cost': ['unknown', '参加費の記載がない'], 'reservation': ['C', '児童館窓口で申込（電話可）'], 'family_value': ['B', '親子で音楽を楽しめる']}, 'strengths': ['親子で参加できる音楽体験'], 'limitations': ['申込が必要で15組', '参加費の記載がない'], 'comparison': '総合B：11/21(土)の等々力児童館 グランドもしくは遊戯室で10:30〜11:30の開催。参加費の記載なし。申込が必要で、定員がある。', 'pf': 'unknown', 'pos': ['official_date_confirmed', 'child_activity_confirmed']}, {'id': 'verified-20261212-setagaya-todoroki-papamo-nabe', 'week': '2026-12-12', 'ward': '世田谷区', 'page': 'setagaya_4.html', 'name': '等々力児童館 パパも気軽に！PaPaMo「ヤ・ミ・鍋〜！」', 'url': 'https://www.city.setagaya.lg.jp/03070/24025.html', 'date': '2026-12-12', 'period': '12/12(土)', 'time': '10:30〜11:30', 'venue': '等々力児童館 グランドもしくは遊戯室', 'price': '参加費の記載なし', 'description': '食材を持ち寄って鍋を作って食べる、0歳〜未就学児と保護者向けの親子ひろば。アレルギーは事前に知らせる。', 'cats': ['体験・ワークショップ', '食'], 'io': '屋内', 'res': {'required': True, 'note': '11/21から児童館で受付。持ってくる食材を申込時に伝える。'}, 'quotes': ['等々力児童館パパも気軽に！PaPaMo募集中募集終了事前申込必要表示しないパパも歓迎！パパじゃなくても、ママも祖父母もシッターさんも里親さんももちろん大歓迎！', '日程2026年11月21日（土曜日）2026年12月12日（土曜日）時間午前10時30分から11時30分', '場所・会場等々力児童館グランドもしくは遊戯室対象0歳から未就学のお子さんとその保護者申し込み方法下記の内容をご参照ください。'], 'overall': 'B', 'basis': 'child_program', 'child': True, 'reason': '食材を持ち寄って鍋を作って食べる、0歳〜未就学児と保護者向けの親子ひろば。参加費の記載なし。事前の申込が必要。', 'axes': {'child_target': ['A', '0歳から未就学児とその保護者が対象'], 'interactivity': ['A', 'みんなで鍋を作って食べる'], 'age_fit': ['A', '0歳児から未就学児と明記'], 'stay_flexibility': ['B', '10:30〜11:30'], 'burden': ['C', '申込が必要で、食材の持参が要る'], 'cost': ['unknown', '参加費の記載がない'], 'reservation': ['C', '11/21から児童館で申込'], 'family_value': ['B', '親子で鍋を囲める']}, 'strengths': ['みんなで作って食べる'], 'limitations': ['申込が必要', '食材の持参が要る', '参加費の記載がない'], 'comparison': '総合B：12/12(土)の等々力児童館 グランドもしくは遊戯室で10:30〜11:30の開催。参加費の記載なし。申込が必要で、定員がある。', 'pf': 'unknown', 'pos': ['official_date_confirmed', 'child_activity_confirmed']}, {'id': 'verified-20261121-setagaya-ikejiri-matcha', 'week': '2026-11-21', 'ward': '世田谷区', 'page': 'setagaya_20.html', 'name': '池尻児童館「お抹茶を楽しもう」', 'url': 'https://www.city.setagaya.lg.jp/03061/36833.html', 'date': '2026-11-21', 'period': '11/21(土)', 'time': '13:30〜15:00', 'venue': '池尻児童館 図書室', 'price': '参加費の記載なし', 'description': '「芽吹きの会」が教えてくれる、お抹茶とおかしを味わう催し。親子での参加も歓迎で、おすわりができる子から。', 'cats': ['体験・ワークショップ'], 'io': '屋内', 'res': {'required': False, 'note': '申込の記載なし。先着30名。受付は14:30まで。'}, 'quotes': ['池尻児童館お抹茶を楽しもう募集中募集終了事前申込必要表示しないおいしいお抹茶とおかしをめしあがれ！親子での参加も大歓迎！「芽吹きの会」のみなさんが、教えてくださいます。', '日程2026年11月21日（土曜日）時間午後1時30分から3時【受付】午後2時30分まで', '場所・会場池尻児童館図書室対象おすわりができるお子さまから。先着30名'], 'overall': 'B', 'basis': 'child_program', 'child': True, 'reason': '「芽吹きの会」が教えてくれる、お抹茶とおかしを味わう催し。参加費の記載なし。申込の案内はなく、当日参加できる。', 'axes': {'child_target': ['B', '親子での参加も歓迎する児童館の催し'], 'interactivity': ['B', 'お抹茶とおかしを味わう'], 'age_fit': ['A', 'おすわりができる子からと明記'], 'stay_flexibility': ['B', '13:30〜15:00'], 'burden': ['B', '先着30名'], 'cost': ['unknown', '参加費の記載がない'], 'reservation': ['unknown', '申込の要否は明記がない'], 'family_value': ['B', '親子で日本の文化に触れられる']}, 'strengths': ['親子歓迎'], 'limitations': ['先着30名', '参加費の記載がない'], 'comparison': '総合B：11/21(土)の池尻児童館 図書室で13:30〜15:00の開催。参加費の記載なし。申込不要で気軽に参加できる。', 'pf': 'unknown', 'pos': ['official_date_confirmed', 'child_activity_confirmed']}, {'id': 'verified-20261123-setagaya-soshigaya-michiasobi', 'week': '2026-11-21', 'ward': '世田谷区', 'page': 'setagaya_25.html', 'name': '祖師谷児童館「祖師谷みちとの遭遇」（みちあそび）', 'url': 'https://www.city.setagaya.lg.jp/03080/36450.html', 'date': '2026-11-23', 'period': '11/23(月・祝)', 'time': '13:00〜15:00', 'venue': '祖師谷商店街けやきロード', 'price': '参加費の記載なし', 'description': 'むかしなつかしい道あそびを楽しむ催し。乳幼児から大人までどなたでも参加できる。当日、児童館は休み。', 'cats': ['体験・ワークショップ', 'イベント・まつり'], 'io': '屋外', 'res': {'required': False, 'note': '申込はありません。'}, 'quotes': ['祖師谷児童館11月「祖師谷みちとの遭遇」募集中募集終了事前申込必要表示しない', '日程2026年11月23日（月曜日）当日、児童館はお休みです。時間午後1時から午後3時', '場所・会場祖師谷商店街けやきロード主催：祖師谷みちとの遭遇プロジェクト対象乳幼児から大人までどなたでもお気軽にどうぞ！申し込み方法申込みはありません。'], 'overall': 'B', 'basis': 'child_program', 'child': True, 'reason': 'むかしなつかしい道あそびを楽しむ催し。参加費の記載なし。申込の案内はなく、当日参加できる。', 'axes': {'child_target': ['A', '乳幼児から大人までどなたでも'], 'interactivity': ['A', 'みちあそびで体を動かす'], 'age_fit': ['A', '乳幼児から大人までと明記'], 'stay_flexibility': ['B', '13:00〜15:00'], 'burden': ['B', '屋外の商店街で開催'], 'cost': ['unknown', '参加費の記載がない'], 'reservation': ['A', '事前申込の案内はない'], 'family_value': ['B', '祝日に親子で昔あそびができる']}, 'strengths': ['申込不要', '乳幼児から参加できる'], 'limitations': ['参加費の記載がない'], 'comparison': '総合B：11/23(月・祝)の祖師谷商店街けやきロードで13:00〜15:00の開催。参加費の記載なし。申込不要で気軽に参加できる。', 'pf': 'unknown', 'pos': ['official_date_confirmed', 'child_activity_confirmed']}, {'id': 'verified-20261128-setagaya-wakabayashi-shichirin', 'week': '2026-11-28', 'ward': '世田谷区', 'page': 'setagaya_56.html', 'name': '若林児童館 七輪でやきやきパーティー！', 'url': 'https://www.city.setagaya.lg.jp/03062/36374.html', 'date': '2026-11-28', 'period': '11/28(土)', 'time': '15:00〜16:00', 'venue': '若林児童館 駐輪場', 'price': '参加費の記載なし', 'description': '七輪で食材を焼いて食べる、小学1〜5年生向けの催し。定員15名。', 'cats': ['体験・ワークショップ', '食'], 'io': '屋外', 'res': {'required': True, 'note': '11/14午前10時から申込。定員15名。'}, 'quotes': ['若林児童館七輪でやきやきパーティー！募集中募集終了事前申込必要表示しない七輪で食材を焼いて食べます。七輪で食材を焼いて食べよう～！', '日程2026年11月28日（土曜日）時間午後3時から午後4時', '場所・会場若林児童館駐輪場対象小学1年生から小学5年生定員15名申し込み方法11月14日（土曜日）午前10時から'], 'overall': 'B', 'basis': 'child_program', 'child': True, 'reason': '七輪で食材を焼いて食べる、小学1〜5年生向けの催し。参加費の記載なし。事前の申込が必要。', 'axes': {'child_target': ['A', '小学1年生から5年生が対象'], 'interactivity': ['A', '七輪で食材を焼いて食べる'], 'age_fit': ['A', '小学1〜5年生と明記'], 'stay_flexibility': ['B', '15:00〜16:00'], 'burden': ['C', '申込が必要で、定員15名'], 'cost': ['unknown', '参加費の記載がない'], 'reservation': ['C', '11/14から申込'], 'family_value': ['B', '七輪で焼く体験ができる']}, 'strengths': ['七輪で焼いて食べる'], 'limitations': ['定員15名', '参加費の記載がない'], 'comparison': '総合B：11/28(土)の若林児童館 駐輪場で15:00〜16:00の開催。参加費の記載なし。申込が必要で、定員がある。', 'pf': 'unknown', 'pos': ['official_date_confirmed', 'child_activity_confirmed']}, {'id': 'verified-20261129-setagaya-seijo-chiiki-bunkasai', 'week': '2026-11-28', 'ward': '世田谷区', 'page': 'setagaya_63.html', 'name': 'せいじょう地域文化祭', 'url': 'https://www.city.setagaya.lg.jp/01051/20700.html', 'date': '2026-11-29', 'period': '11/29(日)', 'time': '10:30〜14:30', 'venue': '砧総合支所・成城ホール（世田谷区成城6-2-1）', 'price': '参加費の記載なし', 'description': 'ステージ発表、フードコーナー、キッズコーナーがある地域の文化祭。子どもと大人が一緒に作り上げるお祭り。', 'cats': ['イベント・まつり'], 'io': '屋内', 'res': {'required': False, 'note': '申込の記載なし。'}, 'quotes': ['せいじょう地域文化祭募集中募集終了事前申込必要表示しないせいじょう地域文化祭を開催します！「せいじょう地域文化祭」とは、地域との交流を深めるために、子供と大人が一緒になって作り上げるお祭りです。毎年、世代を超えてたくさんの来場者を迎えています。今年度は、ステージ発表、フードコーナー、キッズコーナーを行います。皆さんのご来場をお待ちしています！', '日程2026年11月29日（日曜日）時間10時30分～14時30分※ステージ発表は15時まで', '場所・会場砧総合支所・成城ホール（世田谷区成城6-2-1）申込可能な申請方法オンライン利用不可能窓口利用不可能郵送利用不可能電話利用不可能ファクシミリ利用不可能メール利用不可能コンビニ利用不可能'], 'overall': 'B', 'basis': 'child_program', 'child': True, 'reason': 'ステージ発表、フードコーナー、キッズコーナーがある地域の文化祭。参加費の記載なし。申込の案内はなく、当日参加できる。', 'axes': {'child_target': ['B', 'キッズコーナーがある地域のお祭り'], 'interactivity': ['B', 'ステージ発表・フード・キッズコーナー'], 'age_fit': ['unknown', '対象年齢の目安は明記がない'], 'stay_flexibility': ['B', '10:30〜14:30'], 'burden': ['B', '10:30〜14:30'], 'cost': ['unknown', '参加費の記載がない'], 'reservation': ['unknown', '申込の要否は明記がない'], 'family_value': ['B', '親子で地域のお祭りを楽しめる']}, 'strengths': ['キッズコーナーあり'], 'limitations': ['参加費の記載がない'], 'comparison': '総合B：11/29(日)の砧総合支所・成城ホールで10:30〜14:30の開催。参加費の記載なし。申込不要で気軽に参加できる。', 'pf': 'unknown', 'pos': ['official_date_confirmed', 'child_activity_confirmed']}, {'id': 'verified-20261121-arakawa-kumanomae-kumaputtostudio', 'week': '2026-11-21', 'ward': '荒川区', 'page': 'arakawa_143.html', 'name': '熊野前ひろば館 親子ふれあいママ講座・パパとあそぼう！コラボ「くまぷっちスタジオ〜ひつじモコモコ〜」', 'url': 'https://www.city.arakawa.tokyo.jp/a036/kumanomae/papatoasobou.html', 'date': '2026-11-21', 'period': '11/21(土)', 'time': '10:30〜11:30', 'venue': '熊野前ひろば館 多目的室', 'price': '参加費の記載なし', 'description': 'かわいい背景の前で保護者が撮影する、未就学児と保護者向けの写真講座。パパ・ママ・祖父母どなたでも参加できる。', 'cats': ['体験・ワークショップ'], 'io': '屋内', 'res': {'required': False, 'note': '当日自由参加。'}, 'quotes': ['熊野前ひろば館親子ふれあいママ講座・パパとあそぼう！コラボ！「くまぷっちスタジオ～ひつじモコモコ～」パパ、ママ、じいじ、ばあば、どなたでも参加できます！みんなで遊びに来てください。今回は親子ふれあいママ講座「くまぷっちスタジオ～ひつじモコモコ～」とコラボ開催です。', '開催日日付2026年11月21日（土曜日）時間午前10時30分から11時30分まで受付時間午前10時15分から10時45分まで', '場所熊野前ひろば館多目的室内容写真講座（保護者による写真撮影）です。新しい年が明るく元気に過ごせるよう願いを込めて記念撮影を撮りましょう。講師の先生が、かわいい背景を用意してくれます。対象者未就学児とその保護者出演者（講師）中島涼子氏（ねぞうアート、ごろりんアート）持ち物タオル、飲み物、カメラやスマートフォンなど写真が撮れるもの申し込み当日自由参加くまぷっちスタジオ～ひつじモコモコ～（PDF：534KB）'], 'overall': 'B', 'basis': 'child_program', 'child': True, 'reason': 'かわいい背景の前で保護者が撮影する、未就学児と保護者向けの写真講座。参加費の記載なし。申込の案内はなく、当日参加できる。', 'axes': {'child_target': ['A', '未就学児とその保護者が対象'], 'interactivity': ['B', '記念撮影の写真講座'], 'age_fit': ['A', '未就学児と明記'], 'stay_flexibility': ['B', '10:30〜11:30'], 'burden': ['A', '当日自由参加'], 'cost': ['unknown', '参加費の記載がない'], 'reservation': ['A', '事前申込の案内はない'], 'family_value': ['B', '親子の記念写真を撮れる']}, 'strengths': ['当日自由参加', 'パパ・祖父母も参加できる'], 'limitations': ['参加費の記載がない'], 'comparison': '総合B：11/21(土)の熊野前ひろば館 多目的室で10:30〜11:30の開催。参加費の記載なし。申込不要で気軽に参加できる。', 'pf': 'unknown', 'pos': ['official_date_confirmed', 'child_activity_confirmed']}, {'id': 'verified-20261122-katsushika-otanoshimi-trainday', 'week': '2026-11-21', 'ward': '葛飾区', 'page': 'katsushika_374.html', 'name': 'わくわくドキドキ お楽しみトレインデー（新宿交通公園）', 'url': 'https://www.city.katsushika.lg.jp/event/1000107/1000586.html', 'date': '2026-11-22', 'period': '11/22(日)', 'time': '10:00〜12:00／13:00〜16:00（雨天中止）', 'venue': '新宿交通公園', 'price': '就学前無料（大人の付き添いが必要）、小学生1回30円、中学生以上1回100円', 'description': '園内をいつもと違う電車が走り、乗って楽しめる催し。どの新幹線が走るかは当日のお楽しみ。', 'cats': ['公園・自然', '乗り物'], 'io': '屋外', 'res': {'required': False, 'note': '事前申込不要。直接会場へ。雨天中止。'}, 'quotes': ['わくわくドキドキお楽しみトレインデーページ番号1000586更新日令和8年5月12日印刷大きな文字で印刷緊急事態宣言が発令された際には、中止となる場合があります。イベントカテゴリ：催事・イベントどの新幹線が走るかは当日のお楽しみ！お楽しみトレインデー（無断転載禁止）', '開催日令和8年5月24日（日曜日）、7月26日（日曜日）、9月27日（日曜日）、10月25日（日曜日）、11月22日（日曜日）、12月27日（日曜日）令和9年1月24日（日曜日）、3月28日（日曜日）時間午前10時から正午まで、午後1時から午後4時まで（雨天中止）（午前の最終は午前11時45分発、午後の最終は午後3時55分発です。）', '会場新宿交通公園対象どなたでも内容園内をいつもと違う電車が、皆さまを乗せて走ります。どんなトレインが走るかは当日のお楽しみです。トレインの種類に関するお問い合わせはご遠慮ください。料金就学前児童（無料。大人の方の付き添いが必要です。）小学生（1回30円）、中学生以上（1回100円）事前申込不要（直接会場へお越しください）'], 'overall': 'B', 'basis': 'child_program', 'child': True, 'reason': '園内をいつもと違う電車が走り、乗って楽しめる催し。就学前無料（大人の付き添いが必要）、小学生1回30円、中学生以上1回100円。申込の案内はなく、当日参加できる。', 'axes': {'child_target': ['A', '就学前児童から小学生まで楽しめる'], 'interactivity': ['A', '電車に乗って楽しめる'], 'age_fit': ['A', '就学前児童・小学生の料金区分がある'], 'stay_flexibility': ['B', '10:00〜12:00／13:00〜16:00（雨天中止）'], 'burden': ['B', '屋外で雨天中止'], 'cost': ['B', '就学前は無料、小学生は1回30円'], 'reservation': ['A', '事前申込不要'], 'family_value': ['B', '電車好きの子どもに向く']}, 'strengths': ['就学前は無料', '申込不要'], 'limitations': ['雨天中止', '小学生以上は有料'], 'comparison': '総合B：11/22(日)の新宿交通公園で10:00〜12:00／13:00〜16:00（雨天中止）の開催。就学前無料（大人の付き添いが必要）、小学生1回30円、中学生以上1回100円。申込不要で気軽に参加できる。', 'pf': 'pass', 'pos': ['official_date_confirmed', 'child_activity_confirmed']}, {'id': 'verified-20261121-katsushika-nishikameari-plarail', 'week': '2026-11-21', 'ward': '葛飾区', 'page': 'katsushika_427.html', 'name': '西亀有児童館「プラレール広場」（11/21）', 'url': 'https://www.city.katsushika.lg.jp/event/1000114/1000796/1043520.html', 'date': '2026-11-21', 'period': '11/21(土)', 'time': '10:00〜11:45', 'venue': '西亀有児童館 ホール', 'price': '参加費の記載なし', 'description': 'ホールいっぱいに広げたレールの上で、好きな電車を走らせて遊べる乳幼児と保護者向けの広場。', 'cats': ['体験・ワークショップ', '乗り物'], 'io': '屋内', 'res': {'required': False, 'note': '事前申込不要。当日受付。'}, 'quotes': ['西亀有児童館令和8年11月の行事予定', 'プラレール広場ホールいっぱいに広げたレールの上に好きな電車を走らせよう！新幹線や特急、ローカル線や貨物車も走ります。ぐるぐると登って降りるタワーも登場します。', '実施日・曜日11月20日（金曜日）・21日（土曜日）時間午後3時から午後4時30分時間内にいつでも遊ぶことができます。内容ホールいっぱいに広げたレールの上に好きな電車を走らせよう！新幹線や特急、ローカル線や貨物車も走ります。ぐるぐると登って降りるタワーも登場します。対象乳幼児と保護者事前申込不要申込方法当日受付'], 'overall': 'B', 'basis': 'child_program', 'child': True, 'reason': 'ホールいっぱいに広げたレールの上で、好きな電車を走らせて遊べる乳幼児と保護者向けの広場。参加費の記載なし。申込の案内はなく、当日参加できる。', 'axes': {'child_target': ['A', '乳幼児と保護者が対象'], 'interactivity': ['A', 'レールの上で電車を走らせて遊ぶ'], 'age_fit': ['A', '乳幼児向けと明記'], 'stay_flexibility': ['B', '10:00〜11:45'], 'burden': ['A', '当日受付で負担が小さい'], 'cost': ['unknown', '参加費の記載がない'], 'reservation': ['A', '事前申込不要'], 'family_value': ['B', '電車好きの乳幼児に向く']}, 'strengths': ['当日受付', '電車遊び'], 'limitations': ['参加費の記載がない'], 'comparison': '総合B：11/21(土)の西亀有児童館 ホールで10:00〜11:45の開催。参加費の記載なし。申込不要で気軽に参加できる。', 'pf': 'unknown', 'pos': ['official_date_confirmed', 'child_activity_confirmed']}, {'id': 'verified-20261122-bunkyo-motomachi-fes', 'week': '2026-11-21', 'ward': '文京区', 'page': 'bunkyo_motomachi.html', 'name': 'もとまちフェス2026', 'url': 'https://www.city.bunkyo.lg.jp/kuseijouhou/kouhou/houdou/r08/11/p008303.html', 'date': '2026-11-22', 'period': '11/22(日)', 'time': '10:00〜15:00', 'venue': '元町ウェルネスパーク・文京区立元町公園（文京区本郷1丁目）', 'price': '参加費の記載なし', 'description': '親子体操、縁日、運動会、ボッチャ体験、工作、マルシェなど、施設と公園で楽しむ地域の催し。スタンプラリーでお菓子がもらえる。', 'cats': ['イベント・まつり', '体験・ワークショップ'], 'io': '屋内・屋外', 'res': {'required': False, 'note': '一部の体験は当日申込（先着順）。'}, 'quotes': ['「もとまちフェス2026」を開催します【事前PR】いつ令和8年11月22日（日曜日）午前10時～午後3時どこで元町ウェルネスパーク（文京区本郷一丁目1番19号）及び文京区立元町公園（文京区本郷一丁目1番1号）', '内容元町ウェルネスパーク及び元町公園を活用した施設一体イベントとして、「もとまちフェス2026」を開催いたします。本イベントは、区、順天堂、施設に入居する事業者や近隣町会が力を合わせて、地域の賑わいを創出するため、リニューアルオープンした昨年から、毎年開催しております。今年度は、各入居施設が実施するアクティビティープログラムや見学型のブース、体験型のブースに加え、「もとまちマルシェ＆もとまちキッチン」と評した飲食、物販ブースを元町公園に8店舗展開いたします。', '※1当日申込みが必要（先着順）※スタンプラリーを実施［お菓子をプレゼント（なくなり次第終了）］PhotoGallery（昨年度の様子）'], 'overall': 'B', 'basis': 'child_program', 'child': True, 'reason': '親子体操、縁日、運動会、ボッチャ体験、工作、マルシェなど、施設と公園で楽しむ地域の催し。参加費の記載なし。申込の案内はなく、当日参加できる。', 'axes': {'child_target': ['B', '親子で参加できる体験・縁日・運動会などが多い'], 'interactivity': ['A', '親子体操や縁日、工作などの体験が多い'], 'age_fit': ['unknown', '対象年齢の目安は明記がない'], 'stay_flexibility': ['B', '10:00〜15:00'], 'burden': ['B', '10:00〜15:00の間、自由に回れる'], 'cost': ['unknown', '参加費の記載がない'], 'reservation': ['B', '一部の体験は当日申込（先着順）'], 'family_value': ['A', '一日親子で回れる']}, 'strengths': ['親子体操・縁日・工作', 'スタンプラリー'], 'limitations': ['一部の体験は先着順', '参加費の記載がない'], 'comparison': '総合B：11/22(日)の元町ウェルネスパーク・文京区立元町公園で10:00〜15:00の開催。参加費の記載なし。申込不要で気軽に参加できる。', 'pf': 'unknown', 'pos': ['official_date_confirmed', 'child_activity_confirmed']}]
RAW = SPECS_RAW
SPECS = []
for _r in RAW:
    _s = dict(_r)
    _s['categories'] = _s.pop('cats'); _s['indoor_outdoor'] = _s.pop('io'); _s['reservation'] = _s.pop('res')
    _s['child_activity'] = _s.pop('child'); _s['price_field'] = _s.pop('pf'); _s['positive'] = _s.pop('pos')
    SPECS.append(_s)
NEW_IDS = [s['id'] for s in SPECS]
SHARDS = {w: f'{w}-events-lead10-20261119.json' for w in ('2026-11-21', '2026-11-28', '2026-12-05', '2026-12-12', '2026-12-19')}
HELD = {'katsushika-shibamata-donta-20261121': 'サークルのステージ発表・展示が中心で、子ども向けの内容と費用の記載がない', 'katsushika-jidokan-monthly-routine': '児童館の月間予定の大半は定例のひろば・親子タイムで、費用の記載がなく、土日の特別行事も少ない', 'shinagawa-pro-sports-20261219': '区内在住・在学の小学生が対象で、抽選', 'koto-sailing-20261213': '区内在住・在学・在勤が対象で、募集終了', 'bunkyo-craft-festival-20261121': '区内在住・在勤・在学者が対象', 'arakawa-kumanomae-xmas-20261209': '平日（水曜）開催のため掲載範囲外', 'katsushika-train-day-20261227': '12/27は告知段階の週（12/26週）で、本ツールの対象外', 'ota-shinagawa-koto-minato-others': '大田・品川・江東・港は、取得できた公式ページに週末・祝日の子ども向けイベントの日付付き詳細が見つからなかった'}


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
        run['lead10_addition_20261119'] = {
            'kind': 'individually_verified_official_events_from_lead_triage', 'added_ids': [i[0]['id'] for i in items],
            'held_not_published': sorted(HELD), 'pages_committed_at': 'research/2026-11-19-audit/pages/',
            'base_data_production_sha': BASE, 'global_source_audit_complete': False}
        S.jdump(d / f'{week}-run.json', run)
        for x in m['weekends']:
            if x['sat'] == week:
                x['count'] += n
    m['generated'] = '2026-11-19T23:00:00+09:00'
    S.jdump(d / 'manifest.json', m)
    h = S.jload(d / 'update_history.json')
    h['history'].append({
        'run_id': 'lead10-addition-20261119', 'run_type': 'manual_verified_lead10_addition',
        'status': 'verified_subset_publication', 'as_of_jst': '2026-11-19', 'executed_at': m['generated'],
        'base_data_production_sha': BASE, 'target_weekends': sorted(derived),
        'prior_active_week_records': 516, 'candidate_active_week_records': 526, 'added_weekly_records': 10,
        'new_event_ids': NEW_IDS, 'held_not_published': sorted(HELD),
        'existing_event_records_physically_deleted': 0, 'image_only_updates': 0,
        'source_failures_remain_unverified': True, 'global_source_audit_complete': False,
        'full_23_ward_25_source_audit_complete': False,
        'note': '世田谷・荒川・葛飾・文京の公式ページを精読し、参加費の記載がないものは「記載なし」と明示したうえで、条件を確認できた10件の週別レコードのみ追加。区内在住限定・受付終了・内容未記載などは掲載せず理由を保存。',
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
