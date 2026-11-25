#!/usr/bin/env python3
"""6 weekly records (Tama expansion: Tachikawa x4, Akishima x2) from committed official pages (2026-11-21).

Raw official pages are committed unchanged under research/2026-11-20-thin-wards/pages/. The gate validator re-derives every record and requires exact equality.
"""
import argparse, hashlib, json, pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import suginami_addition_20261118 as S

BASE = 'c6cb6fe929bf0a3e80c0c18366a297631b261b4a'   # data-production after lead27 (741 active week records)
CHECKED = '2026-11-21'
AXES = S.AXES
NOTE_AUDIT = '週別全源照合は未完（ためまっぷ403等）。この6件は多摩各市の公式ページの個別確認に基づく。'
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

SPECS_RAW = [
    {'id': 'verified-20261129-tachikawa-takamatsu-neo-akimatsuri', 'week': '2026-11-28', 'ward': '立川市', 'page': 'tachikawa_takamatsu_neo_akimatsuri_20261129.html',
     'name': 'たかまつり～みんなでつくろうネオあきまつり～（高松学習館）', 'url': 'https://www.city.tachikawa.lg.jp/event/e-kouza/1028617.html', 'date': '2026-11-29', 'period': '11/29(日)', 'time': '13:00〜16:00（内容により異なる）',
     'venue': '高松学習館（立川市高松町3-22-5）', 'price': '無料（費用なし）',
     'description': '東京学芸大学の学生が企画した秋のイベント。ぷくぷくシールづくり、ボッチャ体験、むかしあそび・どうぶつしょうぎ、巨大神経衰弱、立川音頭（NEO）、縁日などがある。フォトスポットとスタンプラリーもある。対象はどなたでも。申込不要で、当日先着順に案内される。',
     'cats': ['まつり・イベント', '体験・ワークショップ'], 'io': '屋内',
     'res': {'required': False, 'note': '申込不要。当日先着順に案内。'},
     'quotes': ['開催日 2026年11月29日（日曜日） 開催時間 午後1時 から 午後4時 まで 開催場所 高松学習館',
                '対象 どなたでも 内容によって時間帯が異なります。',
                '東京学芸大学の学生が企画したさまざまなイベントに一緒に参加して秋を楽しみます。',
                'ぷくぷくシールづくり：午後1時～、午後2時～、午後3時～ ボッチャ体験：午後1時～、午後1時30分～、午後2時～、午後2時30分～',
                'むかしあそび・どうぶつしょうぎ：午後1時～午後3時30分 巨大神経衰弱：午後1時30分～午後2時、午後2時30分～午後3時',
                '申込み 不要 当日先着順にご案内いたします。',
                '費用 なし 定員 内容によって異なります。'],
     'overall': 'A', 'basis': 'child_program', 'child': True,
     'reason': '大学生が企画した、シール作り・ボッチャ・むかしあそび・縁日などを楽しむ無料の学習館イベント。申込不要で、子どもが遊べるコーナーが多い。',
     'axes': _ax(['A', '学習館の「子ども・子育て」カテゴリのイベントで、遊びのコーナーが中心'], ['A', 'シール作り、ボッチャ、むかしあそび、縁日などの参加型'], ['B', '年齢の限定はなく、コーナーごとに時間が異なる'], ['A', '13:00〜16:00の間に好きなコーナーを選んで参加できる'], ['A', '申込不要で、当日先着順に案内'], ['A', '費用はなし'], ['A', '申込不要'], ['A', '無料で、親子で体験しながら遊べる']),
     'strengths': ['無料・申込不要で、複数の体験コーナーがある', '好きな時間に出入りでき、いろいろ遊べる'], 'limitations': ['コーナーごとに時間と定員が異なる', '詳しい時間割は案内のチラシで確認が必要'],
     'comparison': '総合A：無料・申込不要で、子どもが遊べる体験コーナーが多い。コーナーごとの時間割に注意。',
     'pf': 'pass', 'pos': ['official_date_confirmed', 'child_activity_confirmed']},
    {'id': 'verified-20261206-tachikawa-pre-nishiki-matsuri', 'week': '2026-12-05', 'ward': '立川市', 'page': 'tachikawa_pre_nishiki_matsuri_20261206.html',
     'name': '第17回プレ錦まつり（錦学習館）', 'url': 'https://www.city.tachikawa.lg.jp/event/e-kouza/1028609.html', 'date': '2026-12-06', 'period': '12/6(日)', 'time': '10:00〜15:00',
     'venue': '錦学習館（立川市錦町3-12-25）', 'price': '無料',
     'description': '東京学芸大学の学生と、クイズやゲームを通して地域を楽しく学ぶまつり。「ものれーるつくれーる」（小学2年生まで）など、つくって遊ぶコーナーがある。一部の催しは事前申込が必要で、定員は各回7〜10人。ステージ出演もある。',
     'cats': ['まつり・イベント', '体験・ワークショップ'], 'io': '屋内',
     'res': {'required': True, 'note': '一部の催しは事前申込が必要（11/10 9:00から電子申請）。それ以外は申込不要の随時参加。'},
     'quotes': ['開催日 2026年12月6日（日曜日） 開催時間 午前10時 から 午後3時 まで 開催場所 錦学習館',
                '対象 どなたでも 一部の催しは対象年齢の設定がございます。 ハッシュタグ #無料',
                '東京学芸大学の学生と、クイズやゲームなどを通して楽しく地域について学びます。',
                '【ものれーるつくれーる（要事前申込）】 対象：小学2年生まで',
                '申込み 一部必要 事前申し込みが必要な催しは、11月10日（火曜日）午前9時から下記のフォームから電子申請でお申し込みください。'],
     'overall': 'B', 'basis': 'all_ages', 'child': True,
     'reason': 'クイズやゲーム、工作など、子どもが楽しめるコーナーがある無料のまつり。一部の催しは事前申込（定員各回7〜10人）が必要で、対象年齢が決まっているものがある。',
     'axes': _ax(['B', '対象はどなたでも。小学2年生までなど、子ども向けのコーナーがある'], ['A', 'クイズ、ゲーム、工作などの参加型のコーナー'], ['B', 'コーナーごとに対象年齢が異なる'], ['A', '10:00〜15:00の間に随時参加できるコーナーがある'], ['B', '一部は事前申込が必要で、定員が少ない'], ['A', '無料'], ['B', '一部の催しは事前申込が必要'], ['A', '地域の学生と遊びながら学べる']),
     'strengths': ['無料で、クイズやゲーム、工作など体験コーナーが多い', '随時参加できるコーナーがある'], 'limitations': ['一部の催しは事前申込が必要で、定員が7〜10人と少ない', 'コーナーごとに対象年齢が決まっている'],
     'comparison': '総合B：無料で遊べるまつり。事前申込が必要なコーナーは定員が少ない。',
     'pf': 'pass', 'pos': ['official_date_confirmed', 'child_activity_confirmed']},
    {'id': 'verified-20261212-tachikawa-kunitachi-ongaku-special-concert', 'week': '2026-12-12', 'ward': '立川市', 'page': 'tachikawa_special_concert_20261212.html',
     'name': '未来の大人たちへのスペシャルコンサート（国立音楽大学ブラスオルケスター・立川ステージガーデン）', 'url': 'https://www.city.tachikawa.lg.jp/event/e-bunka/1028372.html', 'date': '2026-12-12', 'period': '12/12(土)', 'time': '16:00開演（15:00開場）',
     'venue': 'TACHIKAWA STAGE GARDEN（立川ステージガーデン、立川市緑町3-3 N1）', 'price': '一般1,500円、高校生以下500円（3歳以上有料。2歳以下は保護者1名につき1名まで膝上鑑賞が無料）',
     'description': '国立音楽大学ブラスオルケスターによる、ベートーヴェンの交響曲第9番の第4楽章、バレエ「くるみ割り人形」、ロシアのクリスマス音楽などの演奏会。次世代を担う子どもたちの育成を目的に開催。全席指定でチケットが必要。対象はどなたでも。',
     'cats': ['舞台・音楽', 'まつり・イベント'], 'io': '屋内',
     'res': {'required': True, 'note': '申込必要。チケットの購入が必要（全席指定、チケットぴあ、9/26発売）。売り切れ状況は公式ページに記載なし。'},
     'quotes': ['開催日 2026年12月12日（土曜日） 開催時間 午後4時00分開演（午後3時00分開場） 開催場所 TACHIKAWA STAGE GARDEN（立川ステージガーデン）',
                '対象 どなたでも 内容 ベートーヴェン /保科 洋 編曲：交響曲第9番 ニ短調 作品125「合唱付き」より 第4楽章',
                '芸術文化の振興と次世代を担う子どもたちの育成を目的に実施するもので',
                'チャイコフスキー / 足立 正 編曲：バレエ《くるみ割り人形》より',
                '申込み 必要 チケットの購入が必要です。（全席指定） 料金/税込 一般：1,500円 高校生以下：500円 ※3歳以上有料。2歳以下のお子様は保護者1名につきお子様1名まで、膝上鑑賞の場合無料。'],
     'overall': 'B', 'basis': 'all_ages', 'child': False,
     'reason': '高校生以下は500円で、くるみ割り人形やクリスマス音楽など、子どもにも親しみやすい曲の演奏会。全席指定・有料・チケット購入が必要で、鑑賞が中心。',
     'axes': _ax(['B', '子どもたちの育成を目的にしたコンサートで、対象はどなたでも'], ['C', '演奏の鑑賞が中心'], ['B', '3歳以上は有料。2歳以下は膝上鑑賞が無料'], ['C', '全席指定で、開演から終演まで座って鑑賞する'], ['B', '有料のチケット購入が必要'], ['B', '一般1,500円、高校生以下500円'], ['B', 'チケット購入が必要（全席指定）'], ['B', 'くるみ割り人形やクリスマス音楽を家族で楽しめる']),
     'strengths': ['高校生以下は500円で、くるみ割り人形などの親しみやすい曲がある', '2歳以下は膝上鑑賞が無料'], 'limitations': ['全席指定の有料公演で、チケット購入が必要', '鑑賞が中心で、小さな子には長く感じる場合がある'],
     'comparison': '総合B：子どもの育成を目的にした演奏会だが、鑑賞中心の有料公演で、小さな子連れには向きにくい。',
     'pf': 'pass', 'pos': ['official_date_confirmed']},
    {'id': 'verified-20261213-akishima-oyako-money-course', 'week': '2026-12-12', 'ward': '昭島市', 'page': 'akishima_oyako_money_course_20261213.html',
     'name': '親子向け消費生活講座「おやこで学ぶ！お金の役割と大切さ」（市役所市民ホール）', 'url': 'https://www.city.akishima.lg.jp/kurashi/sumai/1001875/1001929/1013015.html', 'date': '2026-12-13', 'period': '12/13(日)', 'time': '10:00〜11:30',
     'venue': '昭島市役所1階 市民ホール', 'price': '無料',
     'description': 'クイズや貯金箱づくりを通して、お金の使い方を親子で楽しく学ぶ講座。対象は小学生と保護者で、低学年にもわかりやすい内容。定員20組（申込順）。申込は11/27（金）まで、LoGoフォームで受け付ける。',
     'cats': ['体験・ワークショップ', '学び'], 'io': '屋内',
     'res': {'required': True, 'note': '申込必要。11/2〜11/27にLoGoフォーム。20組（申込順）。'},
     'quotes': ['開催日 2026年12月13日（日曜日） 開催時間 午前10時 から 午前11時30分 まで 開催場所 市役所1階市民ホール',
                '対象 小学生と保護者 内容 低学年にもわかりやすい内容となっています！',
                'クイズや貯金箱づくりをとおして、お金の使いかたなどを親子で楽しく学びましょう！',
                '定員 20組（申込順） 参加費 無料 申込み 必要 11月2日（月曜日）から11月27日（金曜日）まで下記サイトにて申し込みが可能です。'],
     'overall': 'A', 'basis': 'child_program', 'child': True,
     'reason': '小学生と保護者が対象の、クイズや貯金箱づくりでお金を学ぶ無料の講座。低学年にもわかりやすい内容。定員20組で、11/27までの申込が必要。',
     'axes': _ax(['A', '対象は小学生と保護者の親子向け講座'], ['A', 'クイズや貯金箱づくりの参加型'], ['A', '低学年にもわかりやすい内容と明記'], ['B', '10:00〜11:30の1回のみ'], ['B', '事前申込が必要で、定員20組'], ['A', '参加費は無料'], ['B', '申込必要（11/27まで、申込順）'], ['A', '親子でお金について楽しく学べる']),
     'strengths': ['無料で、クイズや貯金箱づくりを親子で体験できる', '低学年にもわかりやすい内容'], 'limitations': ['定員20組で、事前申込が必要（11/27まで）', '開催は1回のみ'],
     'comparison': '総合A：親子向けの無料の体験講座。申込（11/27まで）と20組の定員が制約。',
     'pf': 'pass', 'pos': ['official_date_confirmed', 'child_activity_confirmed']},
    {'id': 'verified-20261226-akishima-shiki-family-musical-hajimari-no-ki', 'week': '2026-12-26', 'ward': '昭島市', 'page': 'akishima_shiki_family_musical_20261226.html',
     'name': '劇団四季ファミリーミュージカル『はじまりの樹の神話』（FOSTERホール）', 'url': 'https://www.city.akishima.lg.jp/bunka/shogaigakushu/1007496/1002968/1002972/1012429.html', 'date': '2026-12-26', 'period': '12/26(土)', 'time': '16:00〜18:00（15:15開場）',
     'venue': 'FOSTERホール（昭島市民会館）', 'price': '大人7,000円、小学生以下4,500円（税込）。3歳未満は保護者1名につき1名まで膝上鑑賞が無料',
     'description': '岡田淳の「こそあどの森の物語」シリーズ第6巻を題材にしたファミリーミュージカル。上演時間は休憩を含めて約2時間。全席指定（1,139席）。チケットは窓口、電話予約、SHIKI ON-LINE TICKET、チケットぴあで販売。',
     'cats': ['舞台・音楽', 'まつり・イベント'], 'io': '屋内',
     'res': {'required': True, 'note': '申込必要。チケットを購入（窓口は9/26 9:00から、電話予約は9/26 14:00から、ほかにSHIKI ON-LINE TICKETとチケットぴあ）。売り切れ状況は公式ページに記載なし。'},
     'quotes': ['開催日 2026年12月26日（土曜日） 開催時間 午後4時 から 午後6時 まで 開場は午後3時15分からとなります。上演時間は休憩含め、約2時間となります。',
                '開催場所 FOSTERホール（昭島市民会館） 対象 どなたでも',
                '3歳未満のお子様が保護者1名につき、1名まで膝上で観劇する場合には無料となります。',
                '参加費 チケット代金は大人7,000円、小学生以下4,500円（全て税込価格）となります。'],
     'overall': 'B', 'basis': 'all_ages', 'child': False,
     'reason': '児童文学「こそあどの森の物語」を題材にした、小学生以下の料金（4,500円）がある家族向けのミュージカル。全席指定・有料で、鑑賞が中心。3歳未満は膝上で見られる。',
     'axes': _ax(['B', '「ファミリーミュージカル」と題するが、対象はどなたでも（子ども専用ではない）'], ['C', 'ミュージカルの鑑賞が中心'], ['B', '対象はどなたでも。3歳未満は膝上鑑賞が可能'], ['C', '約2時間の全席指定の観劇'], ['B', '有料のチケット購入が必要'], ['C', '大人7,000円、小学生以下4,500円と高額'], ['B', 'チケット購入が必要（全席指定）'], ['B', '人気の児童文学を家族で観劇できる']),
     'strengths': ['小学生以下の料金があり、家族向けの演目', '3歳未満は膝上で鑑賞できる'], 'limitations': ['料金が大人7,000円、小学生以下4,500円と高い', '約2時間の全席指定の観劇で、小さな子には長い'],
     'comparison': '総合B：家族向けの人気ミュージカルだが、高額で約2時間の鑑賞中心の公演。',
     'pf': 'pass', 'pos': ['official_date_confirmed']},
    {'id': 'verified-20261226-tachikawa-nishiki-xmas-eigakai', 'week': '2026-12-26', 'ward': '立川市', 'page': 'tachikawa_nishiki_xmas_eigakai_20261226.html',
     'name': '地域活性にしきクリスマス映画会（錦学習館）', 'url': 'https://www.city.tachikawa.lg.jp/event/e-other/1028669.html', 'date': '2026-12-26', 'period': '12/26(土)', 'time': '10:30〜11:30',
     'venue': '錦学習館（立川市錦町3-12-25）', 'price': '無料',
     'description': 'アニメーション「赤毛のアン クリスマスのコンサート」と「ペリーヌ物語 忘れられないクリスマス」の2作品を上映する。対象はどなたでも。申込不要で、当日直接会場へ。定員30人。',
     'cats': ['舞台・音楽', '体験・ワークショップ'], 'io': '屋内',
     'res': {'required': False, 'note': '申込不要。当日直接会場へ。定員30人。'},
     'quotes': ['開催日 2026年12月26日（土曜日） 開催時間 午前10時30分 から 午前11時30分 まで 開催場所 錦学習館',
                '対象 どなたでも ハッシュタグ #無料',
                '「赤毛のアン クリスマスのコンサート」 「ペリーヌ物語 忘れられないクリスマス」 アニメーション2作品を上映します。',
                '申込み 不要 当日は直接会場へお越しください。 定員30人 費用 無料'],
     'overall': 'B', 'basis': 'all_ages', 'child': True,
     'reason': 'クリスマスのアニメ2作品を無料で上映する学習館の映画会。申込不要で当日直接行ける。定員30人。',
     'axes': _ax(['B', '対象はどなたでも。「子ども・子育て」カテゴリのアニメ上映'], ['C', '映画の鑑賞が中心'], ['B', '年齢の限定はない'], ['B', '約1時間の上映'], ['A', '申込不要で、当日直接行ける'], ['A', '無料'], ['A', '申込不要（定員30人）'], ['B', 'クリスマスのアニメを無料で楽しめる']),
     'strengths': ['無料・申込不要', 'クリスマスのアニメ2作品を上映'], 'limitations': ['定員30人で、満席の場合は入れない', '映画の鑑賞が中心'],
     'comparison': '総合B：無料・申込不要の短いアニメ上映会。鑑賞中心で、定員が少ない。',
     'pf': 'pass', 'pos': ['official_date_confirmed', 'child_activity_confirmed']},
]
RAW = SPECS_RAW
SPECS = []
for _r in RAW:
    _s = dict(_r)
    _s['categories'] = _s.pop('cats'); _s['indoor_outdoor'] = _s.pop('io'); _s['reservation'] = _s.pop('res')
    _s['child_activity'] = _s.pop('child'); _s['price_field'] = _s.pop('pf'); _s['positive'] = _s.pop('pos')
    SPECS.append(_s)
NEW_IDS = [s['id'] for s in SPECS]
SHARDS = {w: f'{w}-events-lead28-20261121.json' for w in ('2026-11-21', '2026-11-28', '2026-12-05', '2026-12-12', '2026-12-19', '2026-12-26')}
HELD = {
    'tachikawa-jump-20261129': '立川市 子どものジャンプ力向上プロジェクト（11/29）：公式ページに費用の記載がなく保留。',
    'tachikawa-dodgeball-20261123': '立川市 児童館対抗ドッジボール大会（11/23）：児童館単位の参加で、申込期限（9/30）も過ぎているため保留。',
    'tachikawa-dream-gakuen-yumematsuri-20261206': '立川市 ドリーム学園 夢まつり（12/6）：児童発達支援施設の活動展示が中心で、一般の家族向けの体験の記載が少ないため保留。',
    'tachikawa-jinken-message-20261128': '立川市 こどもからの人権メッセージ発表会（11/28）：子どもの発表を聞く会で、家族向けの遊び・体験の記載が少ないため保留。',
    'akishima-oyako-sports-day-20261205': '昭島市 親子ふれあいスポーツデー（12/5）：公式ページに費用の記載がなく保留。',
    'akishima-seishonen-festival-20261129': '昭島市 青少年フェスティバル（11/29）：公式ページに費用の記載がなく保留。',
    'akishima-pre-kominkan-matsuri-20261206': '昭島市 ただいま、おかえりプレ公民館まつり（12/6）：対象が「市民のかた」で、在住要件か不明のため保留。',
    'inagi-kyodo-geino-festival-20261206': '稲城市 多摩川流域郷土芸能フェスティバル＆物産展（12/6）：開催場所は狛江市で、公式ページに費用の記載がなく保留。',
    'inagi-kirakira-festa-20261128': '稲城市 矢野口駅前きらきらフェスタ（11/28）：公式ページに費用の記載がなく保留。',
    'koganei-jidofes-20261129': '小金井市 じどうかんフェスティバル2026（11/29）：公式ページに費用の記載がなく保留（案内PDFは未取得）。',
    'komae-ohanashi-20261129': '狛江市 親子で楽しむおはなし会（11/29）：公式ページに費用の記載がなく保留。',
    'higashimurayama-kotsu-anzen-fesuta-20261205': '東村山市 親子で楽しく学ぶ！交通安全フェスタ（12/5）：公式ページに費用の記載がなく保留。',
    'hachioji-hatchikko-kitchen-festa-20261128': '八王子市 はちっこキッチン フェスタ（11/28）：公式ページに入場や体験の費用の記載がなく保留。',
    'machida-event-pages': '町田市 まちだイベントなび掲載のイベント：掲載ページは日時と会場だけで、費用と詳細は外部サイトのため保留。',
    'remaining-cities': '三鷹・小金井・小平・国分寺・西東京・日野・狛江・稲城・町田・国立・清瀬は、週末の個別イベントの公式根拠（日付・場所・費用）を引き続き調査中。',
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
                    'description': f"公式ページ（2026-11-21にHTTP200で取得、research/2026-11-20-thin-wards/pages/に不変保存）の本文引用。引用文字列だけのUTF-8 SHA-256。"})
    for x in spec.get('extra', []):
        t2 = _page_text(pathlib.Path(pages_dir) / x['page'])
        if S._strip(x['q']) not in t2:
            raise ValueError(f"{spec['id']}: calendar quote not found verbatim in the committed official calendar page: {x['q']}")
        out.append({'url': x['url'], 'quote': x['q'], 'checked_at': CHECKED,
                    'sha256': hashlib.sha256(x['q'].encode('utf-8')).hexdigest(),
                    'hash_scope': 'quoted_text_only_not_HTTP_response_hash',
                    'description': f"公式ページ（2026-11-21にHTTP200で取得、research/2026-11-20-thin-wards/pages/に不変保存）の本文引用。"})
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
               'evidence': [{'url': s['url'], 'basis': '2026-11-21 official individual event page (HTTP200); 23 ward completeness not asserted'}],
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
            row = next((r for r in munis if r['ward'] == ward), None)
            if row is None:
                row = {'ward': ward, 'candidate_count': 0, 'published_count': 0, 'note': '多摩拡張（v1.41）の初回。'}
                munis.append(row)
            row['candidate_count'] += k
            row['published_count'] += k
            row['note'] += f' 2026-11-21 公式個別ページ確認済み{k}件を非破壊追加。'
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
        run['lead28_addition_20261121'] = {
            'kind': 'individually_verified_official_events_from_lead_triage', 'added_ids': [i[0]['id'] for i in items],
            'held_not_published': sorted(HELD), 'pages_committed_at': 'research/2026-11-20-thin-wards/pages/',
            'base_data_production_sha': BASE, 'global_source_audit_complete': False}
        S.jdump(d / f'{week}-run.json', run)
        for x in m['weekends']:
            if x['sat'] == week:
                x['count'] += n
    m['generated'] = '2026-11-21T20:00:00+09:00'
    S.jdump(d / 'manifest.json', m)
    h = S.jload(d / 'update_history.json')
    h['history'].append({
        'run_id': 'lead28-addition-20261121', 'run_type': 'manual_verified_lead28_addition',
        'status': 'verified_subset_publication', 'as_of_jst': '2026-11-21', 'executed_at': m['generated'],
        'base_data_production_sha': BASE, 'target_weekends': sorted(derived),
        'prior_active_week_records': 741, 'candidate_active_week_records': 747, 'added_weekly_records': 6,
        'new_event_ids': NEW_IDS, 'held_not_published': sorted(HELD),
        'existing_event_records_physically_deleted': 0, 'image_only_updates': 0,
        'source_failures_remain_unverified': True, 'global_source_audit_complete': False,
        'full_23_ward_25_source_audit_complete': False,
        'note': '多摩拡張の第4弾として、立川市（たかまつり・プレ錦まつり・スペシャルコンサート・クリスマス映画会）、昭島市（親子向けお金の講座・劇団四季ファミリーミュージカル）を公式の個別ページで確認して追加。'
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
