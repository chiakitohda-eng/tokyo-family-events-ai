#!/usr/bin/env python3
"""1 weekly record (12/26 Nerima forest festival) from the committed official Nerima page (2026-11-20).

Raw official pages are committed unchanged under research/2026-11-20-thin-wards/pages/
(fetched by read-only workflows, HTTP 200). Quotes must occur verbatim in those pages.
The gate validator re-derives every record from this module and requires exact equality.
"""
import argparse, hashlib, json, pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import suginami_addition_20261118 as S

BASE = 'a58d6c51a15757198e02b458962fc1337d9ec28a'   # data-production after the Nerima duplicate removal (649 active week records)
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


SPECS_RAW = [{'id': 'verified-20261205-nerima-chihiro-warabeuta', 'week': '2026-12-05', 'ward': '練馬区', 'page': 'chihiro_warabeuta_1205.html', 'name': 'わらべうたあそび（ちひろ美術館・東京）', 'url': 'https://chihiro.jp/tokyo/events/94213/', 'date': '2026-12-05', 'period': '12/5(土)', 'time': '11:00〜11:40', 'venue': 'ちひろ美術館・東京（練馬区下石神井4-7-2）', 'price': '1組500円（入館料別。子ども無料）', 'description': 'リズムにあわせて体を動かしたり、声を出して歌ったりする、0〜2歳児と保護者のための「わらべうた」あそび。10組20名で要事前予約。', 'cats': ['音楽', '乳幼児', '美術館'], 'io': '屋内', 'res': {'required': True, 'note': '要事前予約（11/5 10時から受付）。10組20名。'}, 'quotes': ['2026年12月5日(土)11:00-11:40', '0～2歳児と保護者【定員】1', '10組20名【参加費】1組5', '1組500円（入館料別／子ども無料、保護者割引あり）', '要事前予約（11/5（木）10時より、公式サイト、TEL.03-3995-0612にて）', 'リズムにあわせて体を動かしたり、声を出して歌ったり。'], 'basis': 'child_program', 'reason': '0〜2歳児と保護者が、リズムに合わせて体を動かし、わらべうたを歌って楽しむ。参加費は1組500円で、10組限定の要事前予約。', 'axes': {'child_target': ['A', '対象が0〜2歳児と保護者と明記された乳幼児向けのプログラム'], 'interactivity': ['A', '体を動かして歌うあそびに参加できる'], 'age_fit': ['A', '対象が0〜2歳児と明記'], 'stay_flexibility': ['B', '11:00〜11:40の短い1回のみ'], 'burden': ['B', '定員10組で、事前予約が必要'], 'cost': ['B', '1組500円と入館料が別にかかる'], 'reservation': ['C', '要事前予約で定員が少ない'], 'family_value': ['B', '親子で歌と体を動かすあそびを楽しめる']}, 'strengths': ['0〜2歳の親子向け', '短時間で参加しやすい'], 'limitations': ['10組限定の要事前予約', '入館料が別にかかる'], 'comparison': '総合B：0〜2歳の親子に合う内容だが、10組限定の要事前予約で入館料も別にかかる。', 'pos': ['official_date_confirmed', 'child_activity_confirmed'], 'override': '', 'pf': 'pass', 'overall': 'B', 'child': True}, {'id': 'verified-20261205-bunkyo-noma-ornament', 'week': '2026-12-05', 'ward': '文京区', 'page': 'bunkyo_noma_ornament_1205.html', 'name': '親子でクリスマスオーナメントづくり（community space＆cafe noma）', 'url': 'https://kodomo-smile.metro.tokyo.lg.jp/events/4258', 'date': '2026-12-05', 'period': '12/5(土)', 'time': '10:30〜11:30', 'venue': 'community space＆cafe noma（文京区小石川2-6-9 101）', 'price': '1組1,000円', 'description': 'カラフルな超軽量粘土を混ぜて形づくり、世界にひとつのクリスマスオーナメントを作る。幼児または小学生の親子が対象で、先着5組。', 'cats': ['工作', 'クリスマス', '体験・ワークショップ'], 'io': '屋内', 'res': {'required': True, 'note': '先着5組。参加方法の詳細は申込ページ。'}, 'quotes': ['2026年12月5日10：30～11：30', '対象：幼児～小学生の親子参加費：1組1,000円', '幼児または小学生の親子開催エ', 'communityspace＆cafenoma', '先着５組様お申し込みの詳細は'], 'basis': 'child_program', 'reason': '粘土を混ぜて形を作り、クリスマスのオーナメントを親子で作る。対象は幼児または小学生の親子で、先着5組・1組1,000円。', 'axes': {'child_target': ['A', '幼児または小学生の親子を対象にした工作'], 'interactivity': ['A', '粘土で自分の作品を作れる'], 'age_fit': ['A', '対象が幼児または小学生と明記'], 'stay_flexibility': ['B', '10:30〜11:30の1回のみ'], 'burden': ['B', '先着5組と少人数で、会場はカフェスペース'], 'cost': ['B', '1組1,000円'], 'reservation': ['B', '先着5組の申込制'], 'family_value': ['B', '親子で作品を作って飾れる']}, 'strengths': ['親子で作って持ち帰れる', '小さな子も参加できる'], 'limitations': ['先着5組と定員が少ない', '開催は10:30〜11:30の1回のみ'], 'comparison': '総合B：幼児から小学生の親子で作品を作れるが、先着5組と定員が少なく1回のみ。', 'pos': ['official_date_confirmed', 'child_activity_confirmed'], 'override': '', 'pf': 'pass', 'overall': 'B', 'child': True}, {'id': 'verified-20261121-ota-kawasaki-robot-1121', 'week': '2026-11-21', 'ward': '大田区', 'page': 'kawasaki_robo_1121.html', 'name': 'カワサキロボットエンジニアになろう！ 操作編（羽田イノベーションシティ）', 'url': 'https://kodomo-smile.metro.tokyo.lg.jp/events/4206', 'date': '2026-11-21', 'period': '11/21(土)・22(日)', 'time': '11:00〜12:00／14:00〜15:00', 'venue': '羽田イノベーションシティ B棟2階 カワサキロボットスクール（大田区羽田空港1-1-4）', 'price': '500円', 'description': '本物の産業用ロボットの操作を体験し、制服を着た記念撮影もできる。小学3〜6年生対象、事前予約制。子どもだけでの参加は不可。', 'cats': ['科学・ロボット', '体験・ワークショップ'], 'io': '屋内', 'res': {'required': True, 'note': '事前予約制。お子様のみでの参加はできません。'}, 'quotes': ['【操作編】11/21(土）～22(日）11：00～12：00、14：00～15：00', '操作編：500円参加方法事前', '事前予約制お申し込みの詳細は', 'お子様のみでの参加はできません。', '操作編：小学3年生～6年生'], 'basis': 'child_program', 'reason': '11/21〜22の2日間、本物の産業用ロボットの操作を体験できる小学3〜6年生向けの教室。参加費500円で、事前予約制。', 'axes': {'child_target': ['A', '小学3〜6年生を対象にした子ども向けイベント'], 'interactivity': ['A', '実機のロボットを操作できる'], 'age_fit': ['A', '操作編は小学3〜6年生と明記'], 'stay_flexibility': ['B', '各1時間の回で、時間が決まっている'], 'burden': ['B', '保護者の同行が必要で、事前予約が必要'], 'cost': ['A', '操作編は500円'], 'reservation': ['B', '事前予約制'], 'family_value': ['B', 'ものづくりと技術への興味を親子で広げられる']}, 'strengths': ['本物のロボットを操作できる', '500円と手頃'], 'limitations': ['小学3〜6年生に限られる', '事前予約が必要'], 'comparison': '総合B（11/21〜22）：本物のロボットを動かせて参加費も手頃だが、対象学年が限られ事前予約が必要。', 'pos': ['official_date_confirmed', 'child_activity_confirmed'], 'override': '', 'pf': 'pass', 'overall': 'B', 'child': True}, {'id': 'verified-20261213-adachi-shikahama-ohanashi', 'week': '2026-12-12', 'ward': '足立区', 'page': 'adachi_shikahama_ohanashi.html', 'name': 'おはなし会（足立区立鹿浜図書館・12月）', 'url': 'https://kodomo-smile.metro.tokyo.lg.jp/events/3381', 'date': '2026-12-13', 'period': '12/13(日)（毎月第2日曜）', 'time': '14:00〜14:30', 'venue': '足立区立鹿浜図書館（足立区鹿浜6-8-1）', 'price': '無料', 'description': '絵本の読み聞かせなどのおはなし会。小学生以下の子どもと保護者が対象で、当日受付・定員10人。', 'cats': ['絵本・読み聞かせ', '図書館'], 'io': '屋内', 'res': {'required': False, 'note': '当日受付。定員10人。'}, 'quotes': ['2026年8月9日（日）原則毎月第2日曜日14:00～14:30', '小学生以下の子どもと保護者', '足立区立鹿浜図書館住所：東京', '受付方法：当日受付■定員：10人'], 'basis': 'child_program', 'reason': '原則毎月第2日曜日に開かれる、小学生以下の子どもと保護者のためのおはなし会。当日受付で、定員は10人。', 'axes': {'child_target': ['A', '小学生以下の子どもと保護者を対象にしたおはなし会'], 'interactivity': ['B', '聞いて楽しむ読み聞かせが中心'], 'age_fit': ['A', '対象が小学生以下と明記'], 'stay_flexibility': ['B', '14:00〜14:30の30分のみ'], 'burden': ['A', '近所の図書館で、当日受付'], 'cost': ['A', '参加費の記載なし（公共図書館の行事）'], 'reservation': ['A', '当日受付で予約不要'], 'family_value': ['B', '絵本の時間を親子で過ごせる']}, 'strengths': ['当日受付で気軽', '小学生以下が対象'], 'limitations': ['定員10人と少ない', '30分だけの短い行事'], 'comparison': '総合B：当日受付で気軽に参加できる小学生以下向けの会だが、定員10人で時間も短い。', 'pos': ['official_date_confirmed', 'child_activity_confirmed'], 'override': '', 'pf': 'pass', 'overall': 'B', 'child': True}, {'id': 'verified-20261121-meguro-shinobu-waiwai', 'week': '2026-11-21', 'ward': '目黒区', 'page': 'meguro_shinobu_1121.html', 'name': '志のぶわいわいパーク28 創立115周年記念コンサート（志のぶ幼稚園）', 'url': 'https://shinobu-kg.com/1121-2/', 'date': '2026-11-21', 'period': '11/21(土)', 'time': '9:30〜11:30', 'venue': '志のぶ幼稚園 第1園庭＆第2園庭（志のぶセンス・オブ・ワンダーランド）', 'price': '無料', 'description': '幼稚園の園庭で開かれる地域向けのコンサート。地域の方なら誰でも予約なしで参加でき、小学生以下の来場者にはステッカーの特典がある。', 'cats': ['音楽', '地域イベント', '園庭'], 'io': '屋外', 'res': {'required': False, 'note': '予約不要。'}, 'quotes': ['○実施日：2026年11月21日(土)', '○開催時間：9時30分〜11時30分', '○場所：志のぶ幼稚園第1園庭＆第2園庭(志のぶセンス・オブ・ワンダーランド)', '○入場料：無料(予約は必要ありません)', '小学生以下来場者特典：Won'], 'basis': 'all_ages', 'reason': '幼稚園の園庭で開かれる無料のコンサート。地域の人なら予約なしで参加でき、小学生以下の来場者には特典がある。', 'axes': {'child_target': ['B', '小学生以下の来場者特典があり、幼稚園の園庭で開催'], 'interactivity': ['B', 'コンサートを聴いて楽しむのが中心'], 'age_fit': ['unknown', '対象年齢の目安は明記がない'], 'stay_flexibility': ['B', '9:30〜11:30の時間内に参加できる'], 'burden': ['B', '屋外の園庭での開催'], 'cost': ['A', '入場無料'], 'reservation': ['A', '予約は必要ありません'], 'family_value': ['B', '地域の親子で音楽を楽しめる']}, 'strengths': ['無料・予約不要', '小学生以下の特典あり'], 'limitations': ['屋外の園庭での開催', '対象年齢の目安がない'], 'comparison': '総合B：無料・予約不要で子どもの来場特典もあるが、聴くのが中心で屋外開催。', 'pos': ['official_date_confirmed', 'child_activity_confirmed'], 'override': '', 'pf': 'pass', 'overall': 'B', 'child': True}, {'id': 'verified-20261123-shibuya-cocolon-xmas', 'week': '2026-11-21', 'ward': '渋谷区', 'page': 'cocolon_xmas_1123.html', 'name': 'COCOLONクリスマスコンサート2026（東京ウィメンズプラザ）', 'url': 'https://co-co-lon.com/event/xmas_concert26/', 'date': '2026-11-23', 'period': '11/23(月・祝)', 'time': '1部13:00開演／2部15:30開演', 'venue': '東京ウィメンズプラザ（渋谷区神宮前5-53-67）', 'price': 'おとな2,000円／こども1,000円', 'description': '障がいがあってもなくても、きょうだいも、パパママも楽しめるクリスマスコンサート。1部・2部の入れ替え制で、各回30組120名、先着の申込制。', 'cats': ['音楽', 'クリスマス', 'インクルーシブ'], 'io': '屋内', 'res': {'required': True, 'note': '先着の申込制。各回30組120名。'}, 'quotes': ['日時：2026年11月23日(月・祝)', '1部：12:15開場/13:00開演', '場所：東京ウィメンズプラザ', '定員：各回30組120名', '障がいがあってもなくても、きょうだいも、パパママも楽しめるコンサート！', 'こども：1000円【COCO'], 'basis': 'all_ages', 'reason': '障がいの有無やきょうだい・保護者も一緒に楽しめるクリスマスコンサート。こども1,000円で、各回30組の先着申込制。', 'axes': {'child_target': ['B', '障がいの有無を問わず、きょうだいも一緒に楽しめるコンサート'], 'interactivity': ['B', 'コンサートを聴いて楽しむのが中心'], 'age_fit': ['unknown', '対象年齢の目安は明記がない'], 'stay_flexibility': ['B', '1部・2部の入れ替え制で、時間が決まっている'], 'burden': ['B', '先着の申込制で、各回30組'], 'cost': ['C', 'おとな2,000円、こども1,000円'], 'reservation': ['B', '先着の申込制'], 'family_value': ['B', '家族そろってクリスマスの音楽を楽しめる']}, 'strengths': ['家族みんなで楽しめる', '障がいのある子も参加しやすい'], 'limitations': ['先着の申込制で各回30組', '参加費がかかる'], 'comparison': '総合B：家族そろって参加しやすいクリスマスコンサートだが、先着申込制で参加費もかかる。', 'pos': ['official_date_confirmed', 'child_activity_confirmed'], 'override': '', 'pf': 'pass', 'overall': 'B', 'child': True}, {'id': 'verified-20261128-chuo-fes-contest', 'week': '2026-11-28', 'ward': '中央区', 'page': 'fes_contest_1128.html', 'name': '第4回FESコンテスト 小学生審査員の募集（KABUTO ONE）', 'url': 'https://faincation.com/news/21129', 'date': '2026-11-28', 'period': '11/28(土)', 'time': '14:00〜17:00', 'venue': 'KABUTO ONE（中央区日本橋兜町7-1）', 'price': '無料', 'description': '小学1〜6年生の児童とその保護者が対象の、コンテスト表彰式への参加。ゆうちょ銀行の特別体験ブースもある。参加は事前の申込が必要。', 'cats': ['体験', '金融教育', 'イベント'], 'io': '屋内', 'res': {'required': True, 'note': '定員に達し次第締切。公式LINEの友だち追加が必要。'}, 'quotes': ['2026年11月28日（土）14:00～17:00', '小学1年生から6年生までの児童とその保護者', '表彰式：ホール（4階）交流会', 'KABUTOONE（東京都中央区日本橋兜町7-1）'], 'basis': 'child_program', 'reason': '小学1〜6年生の児童とその保護者を対象にした、コンテストの表彰式と特別体験ブース。参加費は無料で、事前の申込が必要。', 'axes': {'child_target': ['A', '小学1〜6年生の児童とその保護者を対象にしたイベント'], 'interactivity': ['B', '表彰式への参加と体験ブースが中心'], 'age_fit': ['A', '対象が小学1〜6年生と明記'], 'stay_flexibility': ['B', '14:00〜17:00の時間が決まっている'], 'burden': ['B', '事前の申込と公式LINEの友だち追加が必要'], 'cost': ['A', '参加費無料'], 'reservation': ['B', '事前申込。定員に達し次第締切'], 'family_value': ['B', '親子でお金や社会について学ぶきっかけになる']}, 'strengths': ['小学生と保護者が対象で無料', '特別体験ブースがある'], 'limitations': ['事前申込が必要', '表彰式が中心で参加型の内容は限られる'], 'comparison': '総合B：小学生と保護者向けで無料だが、表彰式が中心で事前申込も必要。', 'pos': ['official_date_confirmed', 'child_activity_confirmed'], 'override': '', 'pf': 'pass', 'overall': 'B', 'child': True}, {'id': 'verified-20261219-shibuya-funsportnexus', 'week': '2026-12-19', 'ward': '渋谷区', 'page': 'funsportnexus_1219.html', 'name': 'fun sport nexus（国立オリンピック記念青少年総合センター）', 'url': 'https://funsportnexus.org/202612orisen/', 'date': '2026-12-19', 'period': '12/19(土)', 'time': '10:00〜16:00ごろ（プログラムにより異なる）', 'venue': '国立オリンピック記念青少年総合センター（渋谷区代々木神園町3-1）', 'price': '無料', 'description': 'あそびをキーワードに、かけっこ、ぱん食い競走、バスケットボール、ダンス、柔道の転び方教室、将棋などを無料で体験できるスポーツイベント。自由参加と事前申込制のプログラムがある。', 'cats': ['スポーツ', '体験', '無料'], 'io': '屋内・屋外', 'res': {'required': None, 'note': '自由参加（申込不要）と事前申込制のプログラムがある。申込制も定員に達していなければ当日参加可能。'}, 'quotes': ['2026.12.19（土）-20（日）／国立オリンピック記念青少年総合センター', '参加費無料なのでお気軽にご参加ください！', '事前申込制のプログラムもあります。', 'スポあんぱん食い競走スポーツ安全協会／ぱん食い競走協会10:00-11:00／13:00-14:00中央広場', 'サンロッカーズ11:30-12:30'], 'basis': 'all_ages', 'reason': '12/19に、かけっこ教室やぱん食い競走、バスケットボールなどのスポーツ体験を無料で楽しめる。自由参加のプログラムが多く、事前申込制のものもある。', 'axes': {'child_target': ['B', '学年を示した子ども向けプログラムも含む全年齢向けのスポーツ体験'], 'interactivity': ['A', '走る、踊る、球技など体を動かす体験が中心'], 'age_fit': ['unknown', 'プログラムごとに対象学年が異なり、全体の目安はない'], 'stay_flexibility': ['A', '自由参加のプログラムが多く、好きな時間に参加できる'], 'burden': ['B', 'プログラムによって事前申込が必要'], 'cost': ['A', '参加費無料'], 'reservation': ['B', '自由参加と事前申込制が混在'], 'family_value': ['A', '親子で多彩なスポーツを無料で体験できる']}, 'strengths': ['参加費無料', '自由参加のプログラムが多い'], 'limitations': ['プログラムにより事前申込が必要', '対象学年がプログラムごとに異なる'], 'comparison': '総合B（12/19）：無料で多彩なスポーツ体験ができ自由参加も多いが、一部は事前申込で対象学年も異なる。', 'pos': ['official_date_confirmed', 'child_activity_confirmed'], 'override': '', 'pf': 'pass', 'overall': 'B', 'child': True}, {'id': 'verified-20261220-shibuya-funsportnexus', 'week': '2026-12-19', 'ward': '渋谷区', 'page': 'funsportnexus_1219.html', 'name': 'fun sport nexus（国立オリンピック記念青少年総合センター）', 'url': 'https://funsportnexus.org/202612orisen/', 'date': '2026-12-20', 'period': '12/20(日)', 'time': '10:00〜16:00ごろ（プログラムにより異なる）', 'venue': '国立オリンピック記念青少年総合センター（渋谷区代々木神園町3-1）', 'price': '無料', 'description': 'あそびをキーワードに、かけっこ、ぱん食い競走、バスケットボール、ダンス、柔道の転び方教室、将棋などを無料で体験できるスポーツイベント。自由参加と事前申込制のプログラムがある。', 'cats': ['スポーツ', '体験', '無料'], 'io': '屋内・屋外', 'res': {'required': None, 'note': '自由参加（申込不要）と事前申込制のプログラムがある。申込制も定員に達していなければ当日参加可能。'}, 'quotes': ['2026.12.19（土）-20（日）／国立オリンピック記念青少年総合センター', '参加費無料なのでお気軽にご参加ください！', '事前申込制のプログラムもあります。', 'スポあんぱん食い競走スポーツ安全協会／ぱん食い競走協会10:00-11:00／13:00-14:00中央広場', 'サンロッカーズ11:30-12:30'], 'basis': 'all_ages', 'reason': '12/20に、かけっこ教室やぱん食い競走、バスケットボールなどのスポーツ体験を無料で楽しめる。自由参加のプログラムが多く、事前申込制のものもある。', 'axes': {'child_target': ['B', '学年を示した子ども向けプログラムも含む全年齢向けのスポーツ体験'], 'interactivity': ['A', '走る、踊る、球技など体を動かす体験が中心'], 'age_fit': ['unknown', 'プログラムごとに対象学年が異なり、全体の目安はない'], 'stay_flexibility': ['A', '自由参加のプログラムが多く、好きな時間に参加できる'], 'burden': ['B', 'プログラムによって事前申込が必要'], 'cost': ['A', '参加費無料'], 'reservation': ['B', '自由参加と事前申込制が混在'], 'family_value': ['A', '親子で多彩なスポーツを無料で体験できる']}, 'strengths': ['参加費無料', '自由参加のプログラムが多い'], 'limitations': ['プログラムにより事前申込が必要', '対象学年がプログラムごとに異なる'], 'comparison': '総合B（12/20）：無料で多彩なスポーツ体験ができ自由参加も多いが、一部は事前申込で対象学年も異なる。', 'pos': ['official_date_confirmed', 'child_activity_confirmed'], 'override': '', 'pf': 'pass', 'overall': 'B', 'child': True}]
RAW = SPECS_RAW
SPECS = []
for _r in RAW:
    _s = dict(_r)
    _s['categories'] = _s.pop('cats'); _s['indoor_outdoor'] = _s.pop('io'); _s['reservation'] = _s.pop('res')
    _s['child_activity'] = _s.pop('child'); _s['price_field'] = _s.pop('pf'); _s['positive'] = _s.pop('pos')
    SPECS.append(_s)
NEW_IDS = [s['id'] for s in SPECS]
SHARDS = {w: f'{w}-events-lead22-20261120.json' for w in ('2026-11-21', '2026-11-28', '2026-12-05', '2026-12-12', '2026-12-19')}
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
        run['lead22_addition_20261120'] = {
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
        'run_id': 'lead22-addition-20261120', 'run_type': 'manual_verified_lead22_addition',
        'status': 'verified_subset_publication', 'as_of_jst': '2026-11-20', 'executed_at': m['generated'],
        'base_data_production_sha': BASE, 'target_weekends': sorted(derived),
        'prior_active_week_records': 649, 'candidate_active_week_records': 658, 'added_weekly_records': 9,
        'new_event_ids': NEW_IDS, 'held_not_published': sorted(HELD),
        'existing_event_records_physically_deleted': 0, 'image_only_updates': 0,
        'source_failures_remain_unverified': True, 'global_source_audit_complete': False,
        'full_23_ward_25_source_audit_complete': False,
        'note': '東京都の公園管理者・東京都こども向け行事ポータル・ちひろ美術館・足立区立図書館・各主催者の公式ページで日付・時間・会場・条件を確認できた9件のみ追加。',
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
