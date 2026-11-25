#!/usr/bin/env python3
"""6 weekly records (Tama expansion: Chofu x2, Higashimurayama x2, Tachikawa x1, Hachioji x1) from committed official pages (2026-11-21).

Raw official pages are committed unchanged under research/2026-11-20-thin-wards/pages/. The gate validator re-derives every record and requires exact equality.
"""
import argparse, hashlib, json, pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import suginami_addition_20261118 as S

BASE = 'cdfa4b5ae52314182f3de0d13c51c07c337145dc'   # data-production after lead27 (735 active week records)
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
    {'id': 'verified-20261121-chofu-jindai-rose-festa', 'week': '2026-11-21', 'ward': '調布市', 'page': 'chofu_jindai_rose_festa_20261121.html',
     'name': '神代植物公園「秋のバラフェスタ」', 'url': 'https://www.city.chofu.lg.jp/040040/p023399.html', 'date': '2026-11-21', 'end': '2026-11-23', 'period': '11/21(土)〜11/23(月・祝)', 'time': '9:30〜17:00（最終入園16:00）',
     'venue': '神代植物公園（調布市）', 'price': '入園料 一般500円、中学生200円、65歳以上250円。小学生以下と、都内在住・在学の中学生は無料',
     'description': '神代植物公園で開催中の秋のバラフェスタ。早朝開園、ばらコンサート、ばら園シャボン玉の魔法、秋のバラ展、ミニバラ盆栽展、バラのカフェテラス、ガイドツアーなどがある（雨天・荒天中止の催しあり）。11/21〜11/23は会期の最終の連休にあたる。',
     'cats': ['自然・公園', 'まつり・イベント'], 'io': '屋外',
     'res': {'required': False, 'note': '公式ページに事前申込の記載はない（入園料を支払って入園）。'},
     'quotes': ['イベント開催日時 2026年10月6日（火曜日）から2026年11月23日（月曜日） 日程・時間 午前9時30分から午後5時まで(最終入園は午後4時)',
                '会場名称 神代植物公園 内容 早朝開園 ばらコンサート (注)雨天中止 ばら園シャボン玉の魔法 (注)雨天中止',
                '入園料 一般:500円 65歳以上:250円 中学生:200円 (注)小学生以下、都内在住・在学の中学生は無料',
                '現在、神代植物公園で「秋のバラフェスタ」が開催されています。 春とは違う秋のバラをぜひご覧ください。'],
     'overall': 'B', 'basis': 'all_ages', 'child': False,
     'reason': '小学生以下は入園無料の植物公園で、ばら園シャボン玉の魔法やコンサートなど家族で楽しめる催しがある。子ども専用ではなく、催しの一部は雨天中止。',
     'axes': _ax(['B', '子ども専用ではないが、小学生以下は無料で入園できる'], ['B', 'シャボン玉の魔法やコンサートなど、見て参加できる催しがある'], ['B', '年齢の限定はなく、小学生以下は無料'], ['A', '屋外の公園で、出入りや滞在時間を自由に決められる'], ['B', '雨天中止の催しがあり、天候の影響を受ける'], ['A', '小学生以下は無料。大人は500円'], ['A', '事前申込の記載はなく、入園料を払って入る'], ['B', '秋のバラを見ながら公園を散策できる']),
     'strengths': ['小学生以下は入園無料', '早朝開園やシャボン玉の魔法など、家族で楽しめる催しがある'], 'limitations': ['子ども専用の企画ではない', '催しの一部は雨天・荒天中止'],
     'comparison': '総合B：家族で散策できる公園イベント。子ども向けの企画が中心ではなく、天候の影響を受ける。',
     'pf': 'pass', 'pos': ['official_date_confirmed']},
    {'id': 'verified-20261128-higashimurayama-akitsu-chirorin-shukakusai', 'week': '2026-11-28', 'ward': '東村山市', 'page': 'higashimurayama_chirorin_shukakusai_20261128.html',
     'name': '秋津ちろりん村「収穫祭」', 'url': 'https://www.city.higashimurayama.tokyo.jp/event/main/omatsuri/tirorinsyuukakusai.html', 'date': '2026-11-28', 'period': '11/28(土)', 'time': '10:00〜12:00',
     'venue': '秋津ちろりん村（東村山市秋津町1-9）', 'price': '品目ごとに数百円程度（野菜の種類により金額が異なる）',
     'description': 'ボランティアが育てた大根や白菜などの収穫体験と野菜の販売。対象はどなたでも。申込不要で当日直接行ける。小雨決行で、荒天時は12/5に延期。駐車場は20台程度。',
     'cats': ['体験・ワークショップ', '自然・公園'], 'io': '屋外',
     'res': {'required': False, 'note': '申込不要。当日直接現地へ。'},
     'quotes': ['日時 令和8年11月28日（土曜） 午前10時から正午まで （注記1）事前の申し込みは不要です。当日直接現地にお越しください。',
                '場所 秋津ちろりん村 住所：東村山市秋津町1丁目9番地',
                'ちろりん村のボランティアが丹精込めて作った大根や白菜等の収穫体験や、野菜の販売を行います。',
                '参加対象者 どなたでも 費用 品目ごと数百円程度 （注記）野菜の種類により金額が異なります。'],
     'overall': 'B', 'basis': 'all_ages', 'child': False,
     'reason': '大根や白菜の収穫体験ができる、申込不要・どなたでも参加できる農園のイベント。2時間の枠で、費用は購入する野菜の分。',
     'axes': _ax(['B', '対象はどなたでも。子ども専用ではない'], ['A', '大根や白菜の収穫を体験できる'], ['B', '年齢の限定はなく、子どもも参加できる'], ['B', '10:00〜12:00の2時間枠'], ['A', '申込不要で、当日直接行ける'], ['A', '野菜の購入分のみ。品目ごとに数百円程度'], ['A', '申込不要'], ['B', '野菜の収穫を家族で体験できる']),
     'strengths': ['申込不要で、当日直接行ける', '収穫を体験でき、野菜を買って帰れる'], 'limitations': ['子ども専用の企画ではない', '2時間の枠で、荒天時は12/5に延期'],
     'comparison': '総合B：気軽に行ける収穫体験。子ども向けの企画ではないが、家族で参加しやすい。',
     'pf': 'pass', 'pos': ['official_date_confirmed']},
    {'id': 'verified-20261205-tachikawa-takamatsu-xmas-eigakai', 'week': '2026-12-05', 'ward': '立川市', 'page': 'tachikawa_takamatsu_xmas_eigakai_20261205.html',
     'name': 'クリスマスたかまつり（クリスマス映画会「パンダコパンダ」・高松学習館）', 'url': 'https://www.city.tachikawa.lg.jp/event/e-kodomo/1028344.html', 'date': '2026-12-05', 'period': '12/5(土)', 'time': '第1回 11:00〜11:35／第2回 13:30〜14:05',
     'venue': '高松学習館（立川市高松町3-22-5）', 'price': '無料（費用なし）',
     'description': 'クリスマス映画会として「パンダコパンダ」を上映する。1日2回（各回約35分）で、対象はどなたでも。各回30人で、電子申請または電話の申込が必要。',
     'cats': ['舞台・音楽', '体験・ワークショップ'], 'io': '屋内',
     'res': {'required': True, 'note': '申込必要。11/10 9:00から電子申請または電話（高松学習館 042-527-0014）。各回30人。申込状況は公式ページに記載なし。'},
     'quotes': ['開催日 2026年12月5日（土曜日） 開催時間 上映時間（2回上映） 第1回目 午前11時から11時35分 第2回目 午後1時30分から2時5分',
                '開催場所 高松学習館 所在地 立川市高松町3-22-5',
                '対象 どなたでも ハッシュタグ #人気、#無料',
                '「クリスマス映画会」を12月5日（土曜日）午前11時から11時35分と午後1時30分から2時5分に開催します。 上映作品は「パンダコパンダ」です。',
                '費用 なし 定員 各回30人'],
     'overall': 'A', 'basis': 'child_program', 'child': True,
     'reason': '子ども向けの映画会で、1回約35分と短く、無料。申込が必要で各回30人と少人数。',
     'axes': _ax(['A', '「パンダコパンダ」を上映する子ども向けの映画会（対象はどなたでも）'], ['B', '映画の鑑賞が中心'], ['A', '1回約35分と短く、小さな子も見やすい'], ['A', '各回約35分で、2回から選べる'], ['B', '申込が必要で、各回30人'], ['A', '無料'], ['B', '申込必要（電子申請または電話）。状況は記載なし'], ['A', 'クリスマスの時期に、親子で短い映画を無料で楽しめる']),
     'strengths': ['無料で、1回約35分と短い', '2回から時間を選べる'], 'limitations': ['申込が必要で各回30人と少ない', '申込の受付状況は公式ページに記載がない'],
     'comparison': '総合A：短くて無料の子ども向け映画会。申込と少人数が制約。',
     'pf': 'pass', 'pos': ['official_date_confirmed', 'child_activity_confirmed']},
    {'id': 'verified-20261206-higashimurayama-kodomo-festa-oyako-kangeki', 'week': '2026-12-05', 'ward': '東村山市', 'page': 'higashimurayama_kodomofesta_kangeki_20261206.html',
     'name': '児童館子どもフェスタ 親子観劇会 人形劇「霧のむこうのふしぎな町」（中央公民館ホール）', 'url': 'https://www.city.higashimurayama.tokyo.jp/kosodate/jidokan/jidoukan_info/yatteru/kodomofesta/oshirase/mousikomi2019.html', 'date': '2026-12-06', 'period': '12/6(日)', 'time': '午前の部 10:30〜11:50／午後の部 14:00〜15:20',
     'venue': '東村山市立中央公民館ホール（東村山市本町2-33-2）', 'price': '1人800円',
     'description': '人形劇団ひとみ座による人形劇「霧のむこうのふしぎな町」の親子観劇会。対象は3歳以上18歳未満と保護者、妊娠中の方とご家族。3歳未満は膝上鑑賞ができる。座席は指定。申込はLoGoフォームまたは市内児童館で、12/4正午まで（チケットが無くなり次第終了）。',
     'cats': ['舞台・音楽', 'まつり・イベント'], 'io': '屋内',
     'res': {'required': True, 'note': '申込必要。LoGoフォームまたは市内児童館で10/19 9:30〜12/4正午。チケットが無くなり次第終了。座席指定、キャンセル・変更不可。'},
     'quotes': ['日時 令和8年12月6日(日曜） 午前の部：午前10時30分から11時50分まで 午後の部：午後2時から3時20分まで',
                '会場 東村山市立中央公民館ホール（東村山市本町2丁目33番地2）',
                '対象 3歳以上18歳未満のかたと保護者。妊娠中のかたとご家族。 （注記）3歳未満のお子さんは膝上鑑賞が可能です。',
                '定員 午前の部 400名 午後の部 400名 費用 1人 800円',
                '申込み LoGoフォームからの申込み 10月19日（月曜）午前9時30分から12月4日（金曜）正午まで'],
     'overall': 'B', 'basis': 'child_program', 'child': True,
     'reason': '3歳以上の子どもと保護者が対象の人形劇の観劇会で、3歳未満は膝上で見られる。有料（1人800円）・座席指定・事前申込で、鑑賞が中心。',
     'axes': _ax(['A', '3歳以上18歳未満と保護者が対象の、児童館の子ども向け観劇会'], ['C', '人形劇の鑑賞が中心'], ['A', '3歳以上が対象で、3歳未満は膝上鑑賞が可能'], ['B', '各部約80分（休憩10分を含む）で、午前・午後から選べる'], ['B', '事前申込が必要で、座席は指定'], ['B', '1人800円'], ['B', '申込必要（12/4正午まで、チケットが無くなり次第終了）'], ['A', '家族で人形劇を楽しめる']),
     'strengths': ['午前・午後の2回から選べる', '3歳未満は膝上で鑑賞できる'], 'limitations': ['1人800円で、事前申込・座席指定', '鑑賞が中心で、キャンセル・変更ができない'],
     'comparison': '総合B：子ども向けの人形劇だが、有料・事前申込・鑑賞中心の条件がある。',
     'pf': 'pass', 'pos': ['official_date_confirmed', 'child_activity_confirmed']},
    {'id': 'verified-20261212-hachioji-keihachi-xmas-market-beeswax-wrap', 'week': '2026-12-12', 'ward': '八王子市', 'page': 'hachioji_keihachi_xmas_market_20261212.html',
     'name': 'ケイハチクリスマスマーケット2026 みつろうラップづくりワークショップ（東京たま未来メッセ）', 'url': 'https://www.city.hachioji.tokyo.jp/kurashi/life/005/001/007/p038184.html', 'date': '2026-12-12', 'period': '12/12(土)', 'time': '10:00〜16:00',
     'venue': '東京たま未来メッセ 第2会議室（八王子市明神町3-19-2）', 'price': '無料（材料はすべて会場で用意）',
     'description': 'ケイハチクリスマスマーケットで開く、みつろうラップづくりのワークショップ。会場で用意した布を使うか、好きな布を持参して作る。対象は小学生以上（小学生は保護者同伴）で、アイロンを使うため未就学児は参加できない。事前申込または当日参加（申込多数の場合は抽選）。',
     'cats': ['体験・ワークショップ', '工作'], 'io': '屋内',
     'res': {'required': False, 'note': '事前申込（12/6まで、申込多数の場合は抽選）または当日参加。'},
     'quotes': ['日時 令和8年（2026年）12月12日（土） 10：00～16：00',
                '会場 東京たま未来メッセ（八王子市明神町3丁目19-2）（京王八王子駅から徒歩2分） 第2会議室',
                '対象 小学生以上 ※小学生は保護者同伴でご参加ください。 ※アイロンを使用するため、未就学児の参加はご遠慮ください。',
                '参加費 無料 持ち物 不要（材料はすべて会場で用意します。）',
                '参加方法 事前申込みもしくは当日参加にてご参加いただけます。'],
     'overall': 'B', 'basis': 'age_eligible', 'child': True,
     'reason': '小学生以上（小学生は保護者同伴）が無料でみつろうラップを作れるワークショップ。当日参加もできる。アイロンを使うため未就学児は参加できない。',
     'axes': _ax(['B', '小学生以上が対象のワークショップ（子ども専用ではない）'], ['A', '布にみつろうを使ってラップを作る工作体験'], ['B', '小学生以上。未就学児は参加できない'], ['A', '10:00〜16:00の間に参加できる'], ['A', '当日参加もでき、材料は会場で用意される'], ['A', '参加費は無料'], ['A', '事前申込または当日参加（申込多数の場合は抽選）'], ['B', 'エコ体験を親子で楽しめる']),
     'strengths': ['無料で、材料はすべて会場で用意される', '当日参加ができる'], 'limitations': ['未就学児は参加できない', '事前申込は申込多数の場合に抽選'],
     'comparison': '総合B：小学生以上の親子向けの無料の工作体験。未就学児は不可。',
     'pf': 'pass', 'pos': ['official_date_confirmed', 'child_activity_confirmed']},
    {'id': 'verified-20261219-chofu-family-concert-0sai-classic', 'week': '2026-12-19', 'ward': '調布市', 'page': 'chofu_family_concert_20261219.html',
     'name': 'ファミリーコンサート「0歳児からのクラシック音楽会 - もうすぐクリスマス」（東部公民館）', 'url': 'https://www.city.chofu.lg.jp/100060/p059321.html', 'date': '2026-12-19', 'period': '12/19(土)', 'time': 'A公演 10:15〜10:45／B公演 11:30〜12:00',
     'venue': '東部公民館 学習室（調布市若葉町1-29-21 2階）', 'price': '無料',
     'description': '女性4人の弦楽四重奏によるコンサート。0歳から参加でき、リズムに合わせて踊ったり歌ったりも楽しめる。「そりすべり」「ジングルベル」「おもちゃのチャチャチャ」などを演奏。A・B公演は同内容で各回40人。多数の場合は抽選（市民優先）で、申込は11/21 9:00〜11/29 21:00。',
     'cats': ['舞台・音楽', 'まつり・イベント'], 'io': '屋内',
     'res': {'required': True, 'note': '申込必要。11/21 9:00〜11/29 21:00に申込フォーム。多数の場合は抽選（市民優先）、結果は12/1にメール。'},
     'quotes': ['イベント開催日時 2026年12月19日（土曜日） 日程・時間 (A公演)午前10時15分から10時45分まで(開場:午前10時) (B公演)午前11時30分から正午まで(開場:午前11時15分)',
                '会場名称 東部公民館 学習室 会場住所 調布市若葉町1-29-21 2階',
                '0歳から参加できるので、リズムに合わせて踊ったり、歌ったりも楽しめます。',
                '「そりすべり」 「みんなで鳴らそう ジングルベル」 「おもちゃのチャチャチャ」 ほか',
                '費用 無料 定員 各回40人(多数抽選。市民優先) 申込 11月21日(土曜日)午前9時から29日(日曜日)午後9時に、申込フォーム(外部リンク)で受付'],
     'overall': 'A', 'basis': 'child_program', 'child': True,
     'reason': '0歳から参加できる30分の親子向けコンサートで、踊ったり歌ったりも楽しめる無料の企画。申込が必要で、多数の場合は抽選（市民優先）。',
     'axes': _ax(['A', '「0歳児からのクラシック音楽会」と題した親子向けのコンサート'], ['A', 'リズムに合わせて踊ったり歌ったりできる'], ['A', '0歳から参加できる'], ['A', '各回30分で、A・Bの2公演から選べる'], ['B', '申込が必要で、多数の場合は抽選（市民優先）'], ['A', '無料'], ['B', '申込必要（11/21〜11/29、抽選）'], ['A', 'クリスマス曲を0歳から親子で楽しめる']),
     'strengths': ['0歳から参加でき、無料', '各回30分と短く、踊ったり歌ったりできる'], 'limitations': ['多数の場合は抽選（市民優先）で、参加できない可能性がある', '各回40人と少人数'],
     'comparison': '総合A：0歳から参加できる無料の親子コンサート。抽選（市民優先）が制約。',
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
SHARDS = {w: f'{w}-events-lead27-20261121.json' for w in ('2026-11-21', '2026-11-28', '2026-12-05', '2026-12-12', '2026-12-19', '2026-12-26')}
HELD = {
    'tachikawa-jump-20261129': '立川市 子どものジャンプ力向上プロジェクト（11/29）：公式ページに費用の記載がなく保留。',
    'koganei-jidofes-20261129': '小金井市 じどうかんフェスティバル2026・子どもの権利の日のつどい（11/29）：公式ページに費用の記載がなく保留（案内PDFは未取得）。',
    'komae-ohanashi-20261129': '狛江市 親子で楽しむおはなし会（11/29）：公式ページに費用の記載がなく保留。',
    'higashimurayama-kotsu-anzen-fesuta-20261205': '東村山市 親子で楽しく学ぶ！交通安全フェスタ（12/5）：公式ページに費用の記載がなく保留。',
    'higashimurayama-minamidai-marche-20261205': '東村山市 南台公園あおぞらマルシェ（12/5）：公式ページに費用の記載がなく保留。',
    'hachioji-hatchikko-kitchen-festa-20261128': '八王子市 はちっこキッチン フェスタ（11/28）：公式ページに入場や体験の費用の記載がなく保留。',
    'hachioji-recycle-hiroba-20261128-29': '八王子市 リサイクルひろば（11/28・11/29）：取得したページに内容と費用の記載がなく保留。',
    'hachioji-ryonan-mizube-matsuri-20261205': '八王子市 陵南水辺活用まつり（12/5）：公式ページに費用の記載がなく保留。',
    'chofu-marche-de-chofu-20261205-06': '調布市 マルシェ ドゥ 調布（12/5・12/6）：公式ページに費用の記載がなく保留。',
    'kodaira-fc-tokyo-oyako-soccer-20261220': '小平市 小平二水会・FC東京 親子サッカー教室（12/20）：市内在住の4〜5歳に限られるため保留。',
    'kodaira-ogawanishi-mobile-20261129': '小平市 ジュニア講座 モビールワークショップ（11/29）：市内在住・在学の小学生に限られるため保留。',
    'koganei-mini4kuu-20261128': '小金井市 親子でミニ四駆（11/28）：市内在住・在勤・在学に限られ、申込も終了しているため保留。',
    'kunitachi-marche-20261213': '国立市 くにたちマルシェ2026（12/13）：公式ページに費用の記載がなく、更新日表記も古いため保留。',
    'nishitokyo-yagifes-20261121-22': '西東京市 ヤギフェス（11/21・11/22）：子ども向けの内容と費用が公式ページで確認できず保留。',
    'nishitokyo-ekimae-festa-20261128-29': '西東京市 保谷駅前フェスタ（11/28・11/29）：子ども向けの内容と入場の費用が公式ページで確認できず保留。',
    'machida-event-pages': '町田市 まちだイベントなび掲載のイベント（親子陶芸、3Rまなびフェスタ、薬師池公園ほか）：掲載ページは日時と会場だけで、費用と詳細は外部サイトのため保留。',
    'remaining-cities': '三鷹・小金井・小平・国分寺・西東京・昭島・日野・狛江・稲城・町田・国立・清瀬は、週末の個別イベントの公式根拠（日付・場所・費用）を引き続き調査中。',
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
        run['lead27_addition_20261121'] = {
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
        'run_id': 'lead27-addition-20261121', 'run_type': 'manual_verified_lead27_addition',
        'status': 'verified_subset_publication', 'as_of_jst': '2026-11-21', 'executed_at': m['generated'],
        'base_data_production_sha': BASE, 'target_weekends': sorted(derived),
        'prior_active_week_records': 735, 'candidate_active_week_records': 741, 'added_weekly_records': 6,
        'new_event_ids': NEW_IDS, 'held_not_published': sorted(HELD),
        'existing_event_records_physically_deleted': 0, 'image_only_updates': 0,
        'source_failures_remain_unverified': True, 'global_source_audit_complete': False,
        'full_23_ward_25_source_audit_complete': False,
        'note': '多摩拡張の第3弾として、調布市（神代植物公園・0歳児からのクラシック音楽会）、東村山市（ちろりん村収穫祭・親子観劇会）、立川市（クリスマス映画会）、八王子市（みつろうラップ体験）を公式の個別ページで確認して追加。'
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
