#!/usr/bin/env python3
"""6 weekly records (Tama expansion: Tama x3, Higashikurume x1, Musashino x2) from committed official pages (2026-11-21).

Raw official pages are committed unchanged under research/2026-11-20-thin-wards/pages/. The gate validator re-derives every record and requires exact equality.
"""
import argparse, hashlib, json, pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import suginami_addition_20261118 as S

BASE = '4670dda5202bc21529e0744163f87a444bf062d1'   # data-production after lead25 (729 active week records)
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
    {'id': 'verified-20261128-tama-karakida-tatsukids-wreath', 'week': '2026-11-28', 'ward': '多摩市', 'page': 'tama_karakida_tatsukids_20261128.html',
     'name': 'たつきっずDAY どんぐりリースづくり（唐木田児童館）', 'url': _TAMA + '/1011290/1009612/1017988.html', 'date': '2026-11-28', 'period': '11/28(土)', 'time': '15:00〜16:00',
     'venue': '唐木田児童館 工作室（多摩市鶴牧6-14）', 'price': '費用不要（無料）',
     'description': '中央大学の学生サークル「たつきっず」のお兄さんお姉さんと、どんぐりや落ち葉を使ってリースを作る工作。対象は未就学児から高校生。先着20名で、当日児童館に来てください。',
     'cats': ['体験・ワークショップ', '工作'], 'io': '屋内',
     'res': {'required': True, 'note': '申込必要。当日児童館に来てください。先着20名。'},
     'quotes': ['2026年11月28日（土曜日） 開催時間 午後3時から午後4時まで', '開催場所 児童館 工作室', '対象 未就学児、小学生、中学生、高校生', 'どんぐりや落ち葉を使って可愛いリースを作ろう！！', '当日児童館に来てください。先着20名です。 費用 不要'],
     'overall': 'A', 'basis': 'child_program', 'child': True,
     'reason': '未就学児から高校生が対象の無料のリース工作。先着20名で、当日児童館に来て申し込む。',
     'axes': _ax(['A', '対象は未就学児から高校生で、児童館の子ども向け企画'], ['A', 'どんぐりや落ち葉でリースを作る工作体験'], ['A', '未就学児から高校生と対象年齢が明記されている'], ['B', '15:00〜16:00の1時間枠'], ['B', '先着20名で、当日児童館に来て申し込む'], ['A', '費用は不要'], ['B', '申込必要（当日児童館で、先着20名）'], ['A', '学生と一緒に季節の工作を無料で楽しめる']),
     'strengths': ['無料で、どんぐりのリース作りを体験できる', '未就学児から高校生まで参加できる'], 'limitations': ['先着20名で、定員になり次第終了の可能性', '1時間の枠で、時間が限られる'],
     'comparison': '総合A：子ども向けの無料の工作体験。先着20名で当日申込という点が制約。',
     'pf': 'pass', 'pos': ['official_date_confirmed', 'child_activity_confirmed']},
    {'id': 'verified-20261128-tama-suwa-zarigani-outdoor', 'week': '2026-11-28', 'ward': '多摩市', 'page': 'tama_suwa_zarigani_20261128.html',
     'name': 'あつまれ！！ザリガニ団（諏訪児童館・小学1〜4年生）', 'url': _TAMA + '/1011287/1010680/1015937.html', 'date': '2026-11-28', 'period': '11/28(土)', 'time': '14:00〜19:00',
     'venue': '諏訪児童館 遊戯室・前庭・児童館周辺（多摩市諏訪2-8）', 'price': '参加費200円（食材料費など）',
     'description': '小学1〜4年生対象のアウトドアイベント。謎解きミッションや火起こしなどに、家族から少し離れてグループで挑戦する。定員30名（先着）、終了が19:00のため必ずお迎えが必要。',
     'cats': ['体験・ワークショップ', '自然・公園'], 'io': '屋外',
     'res': {'required': True, 'note': '申込必要（11/4から受付、先着30名）。「じどうかんだより」の申込書に記入し、参加費200円を添えて本人が持参。'},
     'quotes': ['2026年11月28日（土曜日） 開催時間 午後2時 から 午後7時 まで', '開催場所 諏訪児童館遊戯室 前庭 児童館周辺', '対象 小学1～4年生 定員30名（申込み先着順）', '謎解きミッションや火起こしなど、楽しいこといっぱいです！', '※終了時間が午後7時のため、必ずお迎えが必要です。', '参加費200円を添えて、必ず参加する本人が持ってきてください。'],
     'overall': 'B', 'basis': 'child_program', 'child': True,
     'reason': '小学1〜4年生向けのアウトドア企画で、謎解きや火起こしなど体験が中心。申込（先着30名）と参加費200円が必要で、19:00終了のため保護者のお迎えがいる。',
     'axes': _ax(['A', '対象は小学1〜4年生で、児童館の子ども向け企画'], ['A', '謎解きミッションや火起こしなど体験が中心'], ['A', '小学1〜4年生と対象年齢が明記されている'], ['C', '14:00〜19:00の長時間で、家族から離れて参加する形式'], ['B', '先着30名の申込と、19:00のお迎えが必要'], ['B', '参加費200円（食材料費など）'], ['B', '11/4から受付の先着制で、申込書の持参が必要'], ['A', 'アウトドアの体験を子どもだけで挑戦できる']),
     'strengths': ['火起こしや謎解きなどの体験が中心', '参加費が200円と少額'], 'limitations': ['先着30名で、申込書の持参が必要', '19:00終了で必ずお迎えが必要', '家族から離れて参加する形式'],
     'comparison': '総合B：体験の質は高いが、先着の申込と長時間のお迎えが必要で、家族連れで気軽に行く形式ではない。',
     'pf': 'pass', 'pos': ['official_date_confirmed', 'child_activity_confirmed']},
    {'id': 'verified-20261129-higashikurume-snow-white-musical', 'week': '2026-11-28', 'ward': '東久留米市', 'page': 'higashikurume_snowwhite_musical_20261129.html',
     'name': 'ミュージカル「白雪姫」（生涯学習センター）', 'url': 'https://www.city.higashikurume.lg.jp/eventinfo/1029503.html', 'date': '2026-11-29', 'period': '11/29(日)', 'time': '14:30〜16:30（14:00開場）',
     'venue': '東久留米市生涯学習センター ホール', 'price': '全席指定・前売り2,800円（中学生以下1,300円）、3歳未満の膝上鑑賞は無料',
     'description': 'グリム童話の「白雪姫」を、こどもから大人まで楽しめる本格的な創作ミュージカルとして上演。チケット購入者の先着30人限定でバックステージツアーがある。定員は先着500人。',
     'cats': ['舞台・音楽', 'まつり・イベント'], 'io': '屋内',
     'res': {'required': True, 'note': '9/18から電話または生涯学習センターの窓口で申込。先着500人。売り切れ状況は公式ページに記載なし。'},
     'quotes': ['令和8年11月29日(日曜日)', '午後2時30分 から 午後4時30分 まで 午後2時 開場', '会場 生涯学習センター ホール', 'グリム童話で有名な白雪姫のこどもから大人まで楽しめる本格的な創作ミュージカルをお楽しみください。', '定員 先着500人 費用 【全席指定】 前売り 2,800円（中学生以下1,300円） ※3歳未満の膝上鑑賞は無料', '9月18日(金曜日)午前9時から電話または直接同センターへ'],
     'overall': 'B', 'basis': 'all_ages', 'child': False,
     'reason': '「こどもから大人まで楽しめる」ミュージカルで、中学生以下の料金と3歳未満の膝上無料がある。鑑賞が中心で、全席指定・有料・事前申込が必要。',
     'axes': _ax(['B', '「こどもから大人まで楽しめる」とあるが、子ども専用ではない'], ['C', '鑑賞が中心のミュージカル'], ['B', '中学生以下の料金設定があり、3歳未満は膝上で鑑賞できる'], ['C', '全席指定で、上演時間（約2時間）席に座って鑑賞する'], ['B', '全席指定の前売り券が必要で、売り切れの可能性がある'], ['B', '前売り2,800円、中学生以下1,300円'], ['B', '電話または窓口でチケットを購入（9/18から先着500人）'], ['B', '親子で本格的な舞台を楽しめる']),
     'strengths': ['中学生以下は1,300円で、3歳未満は膝上無料', '親しみやすい白雪姫の舞台'], 'limitations': ['有料の全席指定で、事前にチケット購入が必要', '鑑賞が中心で、約2時間座って見る形式', '売り切れ状況は公式ページに記載がない'],
     'comparison': '総合B：親子向けの有名な物語の舞台だが、有料・事前購入・鑑賞中心の条件がある。',
     'pf': 'pass', 'pos': ['official_date_confirmed']},
    {'id': 'verified-20261205-tama-ichinomiya-asobitai', 'week': '2026-12-05', 'ward': '多摩市', 'page': 'tama_ichinomiya_asobitai_20261205.html',
     'name': 'あそび隊がやってくる！クリスマス（一ノ宮児童館）', 'url': _TAMA + '/1011281/1009115/1020209.html', 'date': '2026-12-05', 'period': '12/5(土)', 'time': '14:00〜15:30',
     'venue': '一ノ宮児童館（多摩市一ノ宮1-18-7）', 'price': '費用不要（無料）',
     'description': '明星大学初等教育研究会「どろんこの会」のお兄さんお姉さんと、クリスマスをテーマにした6つのブースで遊ぶ。対象はどなたでも（幼児も参加可だが小学生向けの遊び）。申込不要・費用不要。',
     'cats': ['体験・ワークショップ', 'まつり・イベント'], 'io': '屋内',
     'res': {'required': False, 'note': '申込不要。'},
     'quotes': ['2026年12月5日（土曜日） 開催時間 午後2時 から 午後3時30分 まで', '開催場所 一ノ宮児童館 対象 どなたでも 幼児も参加できますが、対象は小学生の遊びです。', '「どろんこ」のお兄さんお姉さんと一緒に楽しく遊ぼう！今回のテーマは「クリスマス」です。', '申込み 不要 費用 不要 イベント情報をiPhone・iPad端末のカレンダーに取り込めます。'],
     'overall': 'A', 'basis': 'child_program', 'child': True,
     'reason': '小学生向けの遊びを大学生と楽しむ、無料・申込不要の児童館イベント。幼児も参加できる。',
     'axes': _ax(['A', '児童館の企画で、対象は小学生の遊び（幼児も参加可）'], ['A', '6つのブースで遊ぶ参加型の企画'], ['B', '小学生向けの遊びで、幼児も参加できるが年齢別の案内はない'], ['A', '14:00〜15:30の間に自由に遊べる形式'], ['A', '申込不要で、そのまま行ける'], ['A', '費用は不要'], ['A', '申込不要'], ['A', 'クリスマスのあそびを無料で楽しめる']),
     'strengths': ['無料・申込不要で、小学生向けの遊びを楽しめる', '幼児も参加できる'], 'limitations': ['遊びの内容は小学生向けで、幼児には難しい場合がある', 'ブースの詳細は「企画中」と記載'],
     'comparison': '総合A：無料・申込不要で、対象が子ども。ブースの内容は企画中。',
     'pf': 'pass', 'pos': ['official_date_confirmed', 'child_activity_confirmed']},
    {'id': 'verified-20261205-musashino-family-xmas-concert', 'week': '2026-12-05', 'ward': '武蔵野市', 'page': 'musashino_family_xmas_concert_20261205.html',
     'name': 'ファミリー・クリスマスコンサート（武蔵野市民文化会館 小ホール）', 'url': 'https://www.musashino.or.jp/bunka/1002092/1009902.html', 'date': '2026-12-05', 'period': '12/5(土)', 'time': '14:00開演（13:30開場）',
     'venue': '武蔵野市民文化会館 小ホール', 'price': '全席指定・一般2,500円／友の会2,250円／U25 1,500円／小学生1,000円',
     'description': 'オルガンとアルトの歌声で楽しむクリスマスコンサート。対象は小学生から大人まで。バッハ、ブラームス、アンダーソンなどのクリスマス曲を演奏する。',
     'cats': ['舞台・音楽', 'まつり・イベント'], 'io': '屋内',
     'res': {'required': True, 'note': '10/3(土)10:00からチケット発売、全席指定。売り切れ状況は公式ページに記載なし。'},
     'quotes': ['開催日 2026年12月5日（土曜日） 開催時間 午後2時開演（午後1時30分開場）', '開催場所 武蔵野市民文化会館 小ホール', '対象 小学生、中学生・高校生・大学生、大人', '一般 2,500円 友の会 2,250円 U25（25歳以下） 1,500円 小学生 1,000円', '一足早いクリスマスのひと時を、素敵な歌声とオルガンと共に楽しみましょう！', '主催 (一社)オルガン芸術振興会 共催 (公財)武蔵野文化生涯学習事業団'],
     'overall': 'B', 'basis': 'age_eligible', 'child': False,
     'reason': '小学生から参加でき、小学生料金（1,000円）があるクリスマスコンサート。鑑賞中心の有料・全席指定で、未就学児の対象かどうかは公式ページに記載がない。',
     'axes': _ax(['B', '「ファミリー」と題し、対象は小学生から大人（子ども専用ではない）'], ['C', 'コンサート鑑賞が中心'], ['B', '小学生以上が対象で、未就学児の可否は記載なし'], ['C', '全席指定で、開演から終演まで座って鑑賞する'], ['B', '有料のチケット購入が必要'], ['B', '一般2,500円、小学生1,000円'], ['B', 'チケット購入が必要（10/3発売）'], ['B', 'クリスマスの音楽を親子で楽しめる']),
     'strengths': ['小学生料金（1,000円）があり、クリスマス曲を家族で楽しめる'], 'limitations': ['有料・全席指定で、鑑賞が中心', '未就学児の入場可否は公式ページに記載がない'],
     'comparison': '総合B：小学生から楽しめるが、鑑賞が中心の有料公演で、小さな子連れには向きにくい。',
     'pf': 'pass', 'pos': ['official_date_confirmed']},
    {'id': 'verified-20261219-musashino-santa-oyako-undokai', 'week': '2026-12-19', 'ward': '武蔵野市', 'page': 'musashino_santa_oyako_undokai_20261219.html',
     'name': 'サンタさんと親子運動会（武蔵野総合体育館）', 'url': 'https://www.musashino.or.jp/sports/1001545/1001549/1010161.html', 'date': '2026-12-19', 'period': '12/19(土)', 'time': '（1）3・4歳の部 10:00〜11:30／（2）5・6歳の部 14:00〜15:45',
     'venue': '武蔵野総合体育館 1階 メインアリーナ', 'price': '1組1,500円（保護者1名に子ども2名の場合は2,300円）',
     'description': '8つの動物チームに分かれて、体操や障害物競争などを行う親子運動会。3・4歳の部（2022年4月2日〜2024年4月1日生まれ）と5・6歳の部（2020年4月2日〜2022年4月1日生まれ）があり、各80組。抽選申込制。託児付事業で一時保育（有料）もある。',
     'cats': ['スポーツ', '親子運動'], 'io': '屋内',
     'res': {'required': True, 'note': '抽選申込制（インターネット・はがき）。定員を超えた場合は武蔵野市内在住・在園の方を優先して抽選。申込期間は公式ページに記載がなく要確認。'},
     'quotes': ['開催日 2026年12月19日（土曜日）', '（1）3・4歳の部 10：00～11：30（90分）', '開催場所 武蔵野総合体育館 1階 メインアリーナ', '8つの動物チームに分かれて体操や障害物競争などを行う親子運動会です。', '費用 1組/1,500円 ※保護者1名に子ども2名（双子など）の場合は2,300円', '抽選申込制 インターネット・はがき', '※定員超えた場合は、武蔵野市内に在住・在園の方を優先して抽選を行います。', '募集人数 （1）（2）各80組'],
     'overall': 'B', 'basis': 'child_program', 'child': True,
     'reason': '3〜6歳の親子が対象の運動会で、体操や障害物競争を親子で楽しめる。参加費1組1,500円、抽選申込制で、定員超過時は市内在住・在園者が優先される。',
     'axes': _ax(['A', '3〜6歳の親子が対象の運動会'], ['A', '体操や障害物競争を親子で体験する'], ['A', '生まれ年で年齢別の2部制（3・4歳／5・6歳）'], ['B', '各部90〜105分の枠で参加'], ['B', '抽選申込制で、対象年齢外の子連れ参加はできない'], ['B', '1組1,500円'], ['C', '抽選申込制で、市内在住・在園者が優先される'], ['A', '親子で体を動かして一緒に楽しめる']),
     'strengths': ['年齢別の2部制で、親子で運動を楽しめる', '一時保育（有料）が付く部がある'], 'limitations': ['抽選申込制で、定員超過時は市内在住・在園者が優先', '申込期間は公式ページに記載がなく要確認', '対象年齢外の子の同伴はできない'],
     'comparison': '総合B：対象が合う親子向け企画だが、抽選と市内優先、申込期間の未記載が制約。',
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
SHARDS = {w: f'{w}-events-lead26-20261121.json' for w in ('2026-11-21', '2026-11-28', '2026-12-05', '2026-12-12', '2026-12-19', '2026-12-26')}
HELD = {
    'musashino-asobi-mini-school-20261128': '武蔵野市 遊びのミニ学校（11/28）：対象が市内在住・在学の小学生と保護者に限られるため保留。',
    'musashino-nogyo-kyoshitsu-20261129': '武蔵野市 農業ふれあい公園 子ども向け農業教室：市内在住・在学の小学3〜6年で全日程参加者に限られるため保留。',
    'musashino-hakkentai-20261206': '武蔵野市 むさしの発見隊（12/6）：市内在住・在学の小学3〜6年とその保護者に限られるため保留。',
    'musashino-noasobi-1122-1123': '武蔵野市 親子野あそびクラブ（11/22・11/23）：11/23は申込終了、11/22は申込の締切や状況を公式ページで確認できず保留。',
    'musashino-harp-20261206': '武蔵野市 プレイスコンサート（ハープ、12/6）：申込は11/20に終了済みのため保留。',
    'tama-aoi-ritmic-20261125': '多摩市 親子リトミック（愛宕、11/25）：平日開催のため、週末・祝日のみを掲載する現行の範囲外で保留。',
    'tama-yakiimo-20261202': '多摩市 やきいも（永山児童館、12/2）：平日開催のため保留。',
    'tama-soratomo-20261214': '多摩市 SORATOMO ふたご座流星群（12/14）：平日開催のため保留。',
    'tama-atago-nature-20261128': '多摩市 愛宕の自然探検隊（11/28）：公式ページに費用の記載がなく保留。',
    'tama-renkoji-science-20261212': '多摩市 子ども科学実験教室（連光寺、12/12）：公式ページに費用の記載がなく保留。',
    'tama-fitness-hijiri-20261201': '多摩市 親子で楽しむフィットネス（12/1）：平日開催で、費用の記載もなく保留。',
    'higashikurume-xmas-ohanashi-1212-1219-1220-1221': '東久留米市 図書館のクリスマスおはなし会等（12/12・12/19・12/20・12/21）：公式ページに費用の記載がなく保留（12/21は平日）。',
    'kiyose-takeoka-demae-jidokan': '清瀬市 竹丘出前児童館（12/12ほか）：費用・申込の記載が確認できず保留。',
    'remaining-cities': '武蔵野・東久留米・多摩・清瀬・国立以外の市（立川・三鷹・調布・小金井・小平・国分寺・西東京・東村山・昭島・日野・狛江・稲城・町田・八王子）：カレンダーの元データの所在を確認中で、個別ページに届いていない市がある（未解消）。',
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
        run['lead26_addition_20261121'] = {
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
        'run_id': 'lead26-addition-20261121', 'run_type': 'manual_verified_lead26_addition',
        'status': 'verified_subset_publication', 'as_of_jst': '2026-11-21', 'executed_at': m['generated'],
        'base_data_production_sha': BASE, 'target_weekends': sorted(derived),
        'prior_active_week_records': 729, 'candidate_active_week_records': 735, 'added_weekly_records': 6,
        'new_event_ids': NEW_IDS, 'held_not_published': sorted(HELD),
        'existing_event_records_physically_deleted': 0, 'image_only_updates': 0,
        'source_failures_remain_unverified': True, 'global_source_audit_complete': False,
        'full_23_ward_25_source_audit_complete': False,
        'note': '多摩拡張の第2弾として、多摩市の児童館イベント（唐木田・諏訪・一ノ宮）、東久留米市のミュージカル、武蔵野市の親子運動会とクリスマスコンサートの公式ページを確認し、6件を追加。市内在住限定・費用未記載・平日開催のものは保留。',
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
