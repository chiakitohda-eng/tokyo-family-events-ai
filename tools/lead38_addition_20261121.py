#!/usr/bin/env python3
"""8 weekly records (Meguro jidokan x6, Edogawa Kodomo Mirai-kan x2) from committed official pages (2026-11-22).

Raw official pages are committed unchanged under research/2026-11-20-thin-wards/pages/. The gate validator re-derives every record and requires exact equality.
"""
import argparse, hashlib, json, pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import suginami_addition_20261118 as S

BASE = '19205b672d01c9c1a26cb2b9a10812035b44bf0b'   # data-production after lead37 (771 active week records)
CHECKED = '2026-11-22'
AXES = S.AXES
NOTE_AUDIT = '週別全源照合は未完（ためまっぷ403等）。この8件は目黒区・江戸川区の公式個別ページの確認に基づく。'
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


_ctrl = '目黒区 児童館 乳幼児のつどい'
SPECS_RAW = [
    {'id': 'verified-20261212-meguro-karasumori-tudoi-xmas-kazari', 'week': '2026-12-12', 'ward': '目黒区', 'page': 'meguro_karasumori_tudoi_20261212.html',
     'name': '烏森住区センター児童館 乳幼児のつどい「クリスマス飾り作り」', 'url': 'https://www.city.meguro.tokyo.jp/houkago/event/karasumori-tudoi1.html', 'date': '2026-12-12', 'end': '2026-12-12',
     'period': '12/12(土)', 'time': '10:30〜11:30',
     'venue': '烏森住区センター児童館 プレイルーム（目黒区）', 'price': '参加費の記載なし',
     'description': '専門の講師や児童館職員による親子体操、工作、遊びなどを、子どもと保護者がいっしょに楽しむ会。12/12はクリスマス飾り作り。0歳児から5歳児とその保護者が対象で、お父さんの参加も歓迎。',
     'cats': ['親子', '体験・ワークショップ'], 'io': '屋内',
     'res': {'required': None, 'note': '申込方法の記載なし。'},
     'quotes': ['乳幼児のつどい「クリスマス飾り作り」', '2026年12月12日（土曜日）', '午前10時30分から11時30分まで', '烏森住区センター児童館プレイルーム', '0歳児から5歳児（令和2年4月2日から令和8年4月1日生まれ）とその保護者', '対象年齢の乳幼児と保護者であれば、どなたでも参加できます。'],
     'overall': 'B', 'basis': 'child_program', 'child': True,
     'reason': '0〜5歳の子どもと保護者がいっしょに工作や遊びを楽しむ児童館の会。区内在住などの限定の記載はなく、どなたでも参加できる。参加費と申込方法の記載はない。',
     'axes': _ax(['A', '0歳児から5歳児とその保護者のための会'], ['A', '工作や遊びを親子で行う'], ['A', '対象は0〜5歳と明記'], ['B', '10:30〜11:30の1時間'], ['B', '申込方法の記載がなく、事前確認が望ましい'], ['unknown', '参加費の記載がない'], ['unknown', '申込方法の記載がない'], ['B', '親子で工作を楽しみ、保護者同士も交流できる']),
     'strengths': ['0〜5歳の親子向けで、どなたでも参加できる', '講師や職員がいっしょに遊ぶ'], 'limitations': ['参加費の記載がない', '申込方法の記載がない'],
     'comparison': '総合B：12/12(土)10:30〜11:30、クリスマス飾り作りの親子の会。参加費・申込方法の記載がなく、確認が必要。',
     'pf': 'unknown', 'pos': ['official_date_confirmed']},
    {'id': 'verified-20261213-meguro-mukaihara-tudoi-kisetsu-kosaku', 'week': '2026-12-12', 'ward': '目黒区', 'page': 'meguro_mukaihara_tudoi_20261213.html',
     'name': '向原住区センター児童館 乳幼児のつどい「季節の工作」', 'url': 'https://www.city.meguro.tokyo.jp/houkago/event/mukaiharakisetu.html', 'date': '2026-12-13', 'end': '2026-12-13',
     'period': '12/13(日)', 'time': '10:30〜11:30',
     'venue': '向原住区センター児童館 地下プレイルーム（目黒区）', 'price': '参加費の記載なし',
     'description': '乳幼児と保護者が、手遊びや歌遊び、工作遊びを楽しむ「乳幼児のつどい」。12/13は季節の工作。0歳児から5歳児の乳幼児とその保護者が対象で、予約は不要。',
     'cats': ['親子', '体験・ワークショップ'], 'io': '屋内',
     'res': {'required': False, 'note': '予約は不要。10:30の開始前までに行く。'},
     'quotes': ['乳幼児のつどい「季節の工作」', '2026年12月13日（日曜日）', '午前10時30分から午前11時30分まで', '向原住区センター児童館　地下プレイルーム', '予約は不要です。午前10時30分の開始前までにお越しください。', '0歳児から5歳児（令和2年4月2日から令和8年4月1日生まれ）の乳幼児とその保護者'],
     'overall': 'B', 'basis': 'child_program', 'child': True,
     'reason': '0〜5歳の乳幼児と保護者が、手遊びや歌遊び、工作を楽しむ児童館の会。予約は不要で、日曜に参加できる。参加費の記載はない。',
     'axes': _ax(['A', '0歳児から5歳児の乳幼児とその保護者が対象'], ['A', '手遊び・歌遊び・工作を親子で行う'], ['A', '対象は0〜5歳と明記'], ['B', '10:30〜11:30の1時間'], ['A', '予約は不要で、開始前に行けばよい'], ['unknown', '参加費の記載がない'], ['A', '予約は不要'], ['B', '親子の工作と保護者同士の交流']),
     'strengths': ['予約不要で、日曜に参加できる', '0〜5歳の親子向け'], 'limitations': ['参加費の記載がない', '汚れてもよい服装が必要'],
     'comparison': '総合B：12/13(日)10:30〜11:30、季節の工作。予約不要で行きやすい。参加費の記載はない。',
     'pf': 'unknown', 'pos': ['official_date_confirmed']},
    {'id': 'verified-20261212-meguro-komaba-tudoi-athletic-kosaku', 'week': '2026-12-12', 'ward': '目黒区', 'page': 'meguro_komaba_tudoi_20261212.html',
     'name': '駒場児童館 乳幼児のつどい「アスレチックと工作」', 'url': 'https://www.city.meguro.tokyo.jp/houkago/event/komaba-tudoi-12.html', 'date': '2026-12-12', 'end': '2026-12-12',
     'period': '12/12(土)', 'time': '10:30〜11:30',
     'venue': '駒場児童館 プレイルーム（目黒区）', 'price': '無料',
     'description': '0歳児から5歳児までを対象に、アスレチック遊びと工作を楽しむ乳幼児のつどい。先着20組で、事前予約制。',
     'cats': ['親子', '体験・ワークショップ'], 'io': '屋内',
     'res': {'required': True, 'note': '事前予約制。先着20組。申込方法は毎月の児童館のお知らせで確認する。'},
     'quotes': ['乳幼児のつどい「アスレチックと工作」', '2026年12月12日（土曜日）', '午前10時30分から午前11時30分まで', '駒場児童館　プレイルーム', '対象0歳児から5歳児まで', '参加人数・定員先着20組料金・費用無料', '事前予約制です。詳しくは毎月の児童館のお知らせでご確認ください。'],
     'overall': 'B', 'basis': 'child_program', 'child': True,
     'reason': '0〜5歳の子どもが、アスレチックと工作を楽しむ児童館の会。参加費は無料。事前予約制で先着20組。',
     'axes': _ax(['A', '0歳児から5歳児までが対象'], ['A', 'アスレチックと工作で体を動かして作る'], ['A', '対象は0〜5歳と明記'], ['B', '10:30〜11:30の1時間'], ['C', '事前予約制で、先着20組'], ['A', '参加費は無料'], ['C', '事前予約制で、定員が少ない'], ['B', '体を動かす遊びと工作を親子で楽しめる']),
     'strengths': ['参加費は無料', '体を動かす遊びと工作が両方ある'], 'limitations': ['事前予約制で先着20組', '申込方法は別のお知らせで確認が必要'],
     'comparison': '総合B：12/12(土)10:30〜11:30、アスレチックと工作。無料だが、事前予約制で先着20組。',
     'pf': 'pass', 'pos': ['official_date_confirmed']},
    {'id': 'verified-20261205-meguro-ishibumi-tudoi-papa-fureai', 'week': '2026-12-05', 'ward': '目黒区', 'page': 'meguro_ishibumi_tudoi_20261205.html',
     'name': '碑住区センター児童館 乳幼児のつどい「パパといっしょにふれあいあそび」', 'url': 'https://www.city.meguro.tokyo.jp/houkago/event/ishibumi-tudoi1205.html', 'date': '2026-12-05', 'end': '2026-12-05',
     'period': '12/5(土)', 'time': '10:30〜11:30',
     'venue': '碑住区センター児童館（目黒区碑文谷二丁目16番6号）', 'price': '参加費の記載なし',
     'description': '体を使ったあそびや絵本の読み語りなど、パパならではのふれあいあそびと、パパ同士の座談会。令和8年4月2日以降生まれの乳児から1歳児までとその保護者が対象で、定員10組（先着順）。',
     'cats': ['親子', '体験・ワークショップ'], 'io': '屋内',
     'res': {'required': True, 'note': '11/1(日)9:00から受付開始。開館時間中に電話（03-3711-6791）または児童館受付へ。定員10組（先着順）。'},
     'quotes': ['乳幼児のつどい「パパといっしょにふれあいあそび」', '令和8年12月5日（土曜日）午前10時30分から午前11時30分まで', '碑住区センター児童館（目黒区碑文谷二丁目16番6号）', '令和8年4月2日以降生まれの乳児から1歳児までとその保護者', '定員10組（先着順）参加方法', '体を使ったあそびや絵本の読み語りなど、パパならではの子どもとのふれあいあそびと、パパ同士の座談会。'],
     'overall': 'B', 'basis': 'child_program', 'child': True,
     'reason': 'パパと乳児〜1歳児がふれあって遊ぶ児童館の会。土曜に参加できる。定員10組の先着順で、電話または児童館で申し込む。参加費の記載はない。',
     'axes': _ax(['A', '乳児から1歳児とその保護者（パパ）が対象'], ['A', 'ふれあいあそびと絵本の読み語り'], ['A', '対象は乳児〜1歳児と明記'], ['B', '10:30〜11:30の1時間'], ['C', '定員10組の先着順で、電話などで申込'], ['unknown', '参加費の記載がない'], ['C', '電話または来館で申込。定員が少ない'], ['B', 'パパと子どものふれあいと、パパ同士の交流']),
     'strengths': ['土曜開催で、パパが参加しやすい', '乳児〜1歳児向けで、座談会もある'], 'limitations': ['定員10組の先着順で、満員の可能性がある', '参加費の記載がない'],
     'comparison': '総合B：12/5(土)10:30〜11:30、パパと乳児〜1歳児のふれあいあそび。定員10組の先着順で、参加費の記載はない。',
     'pf': 'unknown', 'pos': ['official_date_confirmed']},
    {'id': 'verified-20261219-meguro-gohongi-tudoi-santa', 'week': '2026-12-19', 'ward': '目黒区', 'page': 'meguro_gohongi_tudoi_20261219.html',
     'name': '五本木住区センター児童館 乳幼児のつどい「ごほんぎクリスマス サンタさんがやってきた」', 'url': 'https://www.city.meguro.tokyo.jp/houkago/event/8gohongi-tudoi12190.html', 'date': '2026-12-19', 'end': '2026-12-19',
     'period': '12/19(土)', 'time': '10:30〜11:30（10:20から受付）',
     'venue': '五本木住区センター児童館 プレイルーム（目黒区）', 'price': '参加費の記載なし',
     'description': 'みんなでクリスマス会をして楽しむ、ベビーから5歳児までの乳幼児のつどい。クリスマスグッズがあれば持参する。当日来館で参加でき、予約は不要。',
     'cats': ['親子', 'まつり・イベント'], 'io': '屋内',
     'res': {'required': False, 'note': '当日児童館へ行く。予約は不要。'},
     'quotes': ['乳幼児のつどい「ごほんぎクリスマス　サンタさんがやってきた」', '令和8年12月19日（土曜日）午前10時30分から11時30分まで', '五本木住区センター児童館　プレイルーム', '対象ベビーから5歳児まで', '参加希望のかたは、当日児童館へお越しください。予約は不要です。', '今年もあとわずか。みんなでクリスマス会をして楽しみましょう。'],
     'overall': 'B', 'basis': 'child_program', 'child': True,
     'reason': 'ベビーから5歳児までの親子で楽しむ、児童館のクリスマス会。予約は不要で、土曜に参加できる。参加費の記載はない。',
     'axes': _ax(['A', 'ベビーから5歳児までが対象'], ['B', 'クリスマス会として親子で参加する'], ['A', '対象はベビー〜5歳児と明記'], ['B', '10:30〜11:30の1時間'], ['A', '予約不要で、当日行けばよい'], ['unknown', '参加費の記載がない'], ['A', '予約は不要'], ['B', 'クリスマスの季節行事を親子で楽しめる']),
     'strengths': ['予約不要で、土曜に参加できる', 'ベビー〜5歳児まで幅広く参加できる'], 'limitations': ['参加費の記載がない', '体験の内容の詳細は書かれていない'],
     'comparison': '総合B：12/19(土)10:30〜11:30、児童館のクリスマス会。予約不要で行きやすい。参加費の記載はない。',
     'pf': 'unknown', 'pos': ['official_date_confirmed']},
    {'id': 'verified-20261219-meguro-kamimeguro-tudoi-rhythmic', 'week': '2026-12-19', 'ward': '目黒区', 'page': 'meguro_kamimeguro_tudoi_20261219.html',
     'name': '上目黒住区センター児童館 乳幼児のつどい「親子でリトミック遊び」', 'url': 'https://www.city.meguro.tokyo.jp/houkago/event/kamime-tudoi14.html', 'date': '2026-12-19', 'end': '2026-12-19',
     'period': '12/19(土)', 'time': '10:30〜11:30',
     'venue': '上目黒住区センター児童館 2階プレイルーム（目黒区）', 'price': '無料',
     'description': '講師を招いて、親子でリトミック遊びを楽しむ会。1歳児から3歳児とその保護者が対象で、費用は無料。事前予約制で、開催日の2週間前から電話または来館で受け付ける。',
     'cats': ['親子', '音楽・ステージ'], 'io': '屋内',
     'res': {'required': True, 'note': '事前予約制。開催日の2週間前（12/5）から、電話（03-3793-1103）または来館で申し込む。'},
     'quotes': ['乳幼児のつどい「親子でリトミック遊び」', '令和8年12月19日（土曜日）午前10時30分から11時30分まで', '上目黒住区センター児童館　2階プレイルーム', '1歳児から3歳児のお子さんとその保護者費用無料', '事前予約制。開催日の2週間前より受け付けを開始します。', '講師のかたをお招きして、親子でリトミック遊びを楽しみます。'],
     'overall': 'B', 'basis': 'child_program', 'child': True,
     'reason': '1〜3歳の子どもと保護者が、講師といっしょにリトミックを楽しむ児童館の会。費用は無料。事前予約制で、受付は開催の2週間前から。',
     'axes': _ax(['A', '1歳児から3歳児とその保護者が対象'], ['A', '講師とリトミックで体を動かす'], ['A', '対象は1〜3歳と明記'], ['B', '10:30〜11:30の1時間'], ['B', '事前予約制。受付は開催の2週間前から'], ['A', '費用は無料'], ['C', '事前予約制で、電話または来館で申込'], ['B', '音楽に合わせて親子で体を動かせる']),
     'strengths': ['費用は無料', '講師が来て、リトミックを体験できる'], 'limitations': ['事前予約制で、受付は12/5から', '対象は1〜3歳に限られる'],
     'comparison': '総合B：12/19(土)10:30〜11:30、親子のリトミック。無料だが、事前予約制で受付は12/5から。',
     'pf': 'pass', 'pos': ['official_date_confirmed']},
    {'id': 'verified-20261205-edogawa-mirai-xmas-tree-denshi', 'week': '2026-12-05', 'ward': '江戸川区', 'page': 'edogawa_mirai_xmastree_20261205.html',
     'name': 'クリスマスツリーをつくろう（江戸川区子ども未来館）', 'url': 'https://www.city.edogawa.tokyo.jp/event/2612christmas.html', 'date': '2026-12-05', 'end': '2026-12-05',
     'period': '12/5(土)', 'time': '14:00〜16:00',
     'venue': '子ども未来館（江戸川区篠崎町三丁目12番10号）', 'price': '無料',
     'description': '電子部品をはんだごてで組み立てて、電子クリスマスツリーを作る講座。小学校4年生から6年生が対象。定員9人の抽選で、申込はウェブサイトまたは往復はがき（ウェブは11/24まで）。',
     'cats': ['体験・ワークショップ', '科学・ものづくり'], 'io': '屋内',
     'res': {'required': True, 'note': '申込必要・定員9人（抽選）。申込期間は11/13〜11/24（ウェブサイトのしめきり）。往復はがきはしめきり前日までに到着。'},
     'quotes': ['クリスマスツリーをつくろう', '2026年12月5日（土曜日）14時00分から16時00分', '実際に電子部品をはんだごてで組み立て、電子クリスマスツリーを作ってみましょう。', '小学校4年生から6年生まで定員9人（抽選）費用無料', '2026年11月13日（金曜日）から2026年11月24日（火曜日）'],
     'overall': 'B', 'basis': 'child_program', 'child': True,
     'reason': '小学4〜6年生が、はんだごてで電子部品を組み立てて電子ツリーを作る講座。費用は無料だが、定員9人の抽選で、申込は11/24まで。',
     'axes': _ax(['A', '小学校4年生から6年生が対象'], ['A', 'はんだごてで電子部品を組み立てる'], ['A', '対象は小学4〜6年生と明記'], ['B', '14:00〜16:00の2時間'], ['C', '抽選で、申込は11/24まで'], ['A', '費用は無料'], ['C', '申込必要で、定員9人の抽選'], ['A', 'ものづくりを通して電気の仕組みを学べる']),
     'strengths': ['費用は無料', '電子工作でものづくりを体験できる'], 'limitations': ['定員9人の抽選で、申込は11/24まで', '対象は小学4〜6年生に限られる'],
     'comparison': '総合B：12/5(土)14:00〜16:00、小学4〜6年生の電子工作。無料だが、抽選（9人）で申込は11/24まで。',
     'pf': 'pass', 'pos': ['official_date_confirmed']},
    {'id': 'verified-20261219-edogawa-mirai-shimenawa-oyako', 'week': '2026-12-19', 'ward': '江戸川区', 'page': 'edogawa_mirai_shimenawa_20261219.html',
     'name': '親子でしめ縄づくり（江戸川区子ども未来館）', 'url': 'https://www.city.edogawa.tokyo.jp/event/2612shimenawa.html', 'date': '2026-12-19', 'end': '2026-12-19',
     'period': '12/19(土)', 'time': '10:00〜12:00',
     'venue': '子ども未来館（江戸川区篠崎町三丁目12番10号）', 'price': '無料',
     'description': '稲から取れる藁を使って、お正月の玄関かざりのしめ縄を親子で作る講座。小学校3年生から6年生とその保護者が対象。定員8組の抽選で、申込は12/8まで。',
     'cats': ['体験・ワークショップ', '親子'], 'io': '屋内',
     'res': {'required': True, 'note': '申込必要・定員8組（抽選）。申込期間は11/13〜12/8（ウェブサイトのしめきり）。往復はがきはしめきり前日までに到着。'},
     'quotes': ['しめ縄は、正月に歳神様を迎えるための玄関かざりです。', '2026年12月19日（土曜日）10時00分から12時00分', '親子でつくり方を学び、1年の始まりを家族で祝いましょう。', '小学校3年生から6年生までとその保護者', '定員8組（抽選）費用無料', '2026年11月13日（金曜日）から2026年12月8日（火曜日）'],
     'overall': 'B', 'basis': 'child_program', 'child': True,
     'reason': '小学3〜6年生と保護者が、藁でしめ縄を作る伝統の工作講座。費用は無料だが、定員8組の抽選で、申込は12/8まで。',
     'axes': _ax(['A', '小学校3年生から6年生とその保護者が対象'], ['A', '藁でしめ縄を作る'], ['A', '対象は小学3〜6年生と明記'], ['B', '10:00〜12:00の2時間'], ['C', '抽選で、申込は12/8まで'], ['A', '費用は無料'], ['C', '申込必要で、定員8組の抽選'], ['A', '正月かざりの作り方を親子で学べる']),
     'strengths': ['費用は無料', '伝統のしめ縄づくりを親子で体験できる'], 'limitations': ['定員8組の抽選で、申込は12/8まで', '対象は小学3〜6年生と保護者に限られる'],
     'comparison': '総合B：12/19(土)10:00〜12:00、親子のしめ縄づくり。無料だが、抽選（8組）で申込は12/8まで。',
     'pf': 'pass', 'pos': ['official_date_confirmed']},
]
RAW = SPECS_RAW
SPECS = []
for _r in RAW:
    _s = dict(_r)
    _s['categories'] = _s.pop('cats'); _s['indoor_outdoor'] = _s.pop('io'); _s['reservation'] = _s.pop('res')
    _s['child_activity'] = _s.pop('child'); _s['price_field'] = _s.pop('pf'); _s['positive'] = _s.pop('pos')
    SPECS.append(_s)
NEW_IDS = [s['id'] for s in SPECS]
SHARDS = {w: f'{w}-events-lead38-20261121.json' for w in ('2026-11-22', '2026-11-28', '2026-12-05', '2026-12-12', '2026-12-19', '2026-12-26')}
HELD = {
    'setagaya-yamano-puppet-20261209': '世田谷区 山野児童館「ぽんぽこパペット劇場」(12/9)：平日開催のため対象外。',
    'setagaya-ochiai-chibikko-hiroba': '世田谷区 上町児童館ちびっこひろば・山野児童館ぐるりんぱ：火曜（平日）開催のため対象外。',
    'minato-roppongi-nijimi-card-20261206': '港区 親子でエコっとプロジェクト（12/6）：区内在住の親子限定のため対象外。',
    'edogawa-kosodate-festival-20261114': '江戸川区 親子であそぼう 子育てフェスティバル：11/14開催で期間外。',
    'koto-midori-kosodate-toyosu': '江東区 外遊び型みどりの子育てひろば（豊洲公園）：開催日が木曜（平日）のため対象外。',
    'meguro-teens-festa-20261206-20261220': '目黒区 ティーンズ・フェスタ・イン・めぐろ（12/6〜12/20）：中高生向けで、子連れ向けの根拠が弱く保留。',
    'meguro-other-jidokan-weekday': '目黒区 児童館の乳幼児のつどい（11/24〜12/23の平日分）：平日開催のため対象外。',
    'ota-kodomo-calendar-202612': '大田区 子ども・教育カレンダー12月：期間内の週末イベントの掲載なし（12/17の平日講座のみ）。',
    'urayasu-tokyo-disney-resort': '浦安市 東京ディズニーリゾート：公式サイトが取得できず、保留（継続）。',
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
                    'description': f"公式ページ（2026-11-22にHTTP200で取得、research/2026-11-20-thin-wards/pages/に不変保存）の本文引用。引用文字列だけのUTF-8 SHA-256。"})
    for x in spec.get('extra', []):
        t2 = _page_text(pathlib.Path(pages_dir) / x['page'])
        if S._strip(x['q']) not in t2:
            raise ValueError(f"{spec['id']}: calendar quote not found verbatim in the committed official calendar page: {x['q']}")
        out.append({'url': x['url'], 'quote': x['q'], 'checked_at': CHECKED,
                    'sha256': hashlib.sha256(x['q'].encode('utf-8')).hexdigest(),
                    'hash_scope': 'quoted_text_only_not_HTTP_response_hash',
                    'description': f"公式ページ（2026-11-22にHTTP200で取得、research/2026-11-20-thin-wards/pages/に不変保存）の本文引用。"})
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
               'evidence': [{'url': s['url'], 'basis': '2026-11-22 official individual event page (HTTP200); 23 ward completeness not asserted'}],
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
        run['lead38_addition_20261121'] = {
            'kind': 'individually_verified_official_events_from_lead_triage', 'added_ids': [i[0]['id'] for i in items],
            'held_not_published': sorted(HELD), 'pages_committed_at': 'research/2026-11-20-thin-wards/pages/',
            'base_data_production_sha': BASE, 'global_source_audit_complete': False}
        S.jdump(d / f'{week}-run.json', run)
        for x in m['weekends']:
            if x['sat'] == week:
                x['count'] += n
    m['generated'] = '2026-11-22T20:00:00+09:00'
    S.jdump(d / 'manifest.json', m)
    h = S.jload(d / 'update_history.json')
    h['history'].append({
        'run_id': 'lead38-addition-20261121', 'run_type': 'manual_verified_lead38_addition',
        'status': 'verified_subset_publication', 'as_of_jst': '2026-11-22', 'executed_at': m['generated'],
        'base_data_production_sha': BASE, 'target_weekends': sorted(derived),
        'prior_active_week_records': 771, 'candidate_active_week_records': 779, 'added_weekly_records': 8,
        'new_event_ids': NEW_IDS, 'held_not_published': sorted(HELD),
        'existing_event_records_physically_deleted': 0, 'image_only_updates': 0,
        'source_failures_remain_unverified': True, 'global_source_audit_complete': False,
        'full_23_ward_25_source_audit_complete': False,
        'note': '目黒区の児童館の乳幼児のつどい6件と、江戸川区子ども未来館の講座2件を、公式の個別ページで確認して追加（第71〜72回の取得）。',
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
