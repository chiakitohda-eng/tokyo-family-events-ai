#!/usr/bin/env python3
"""7 weekly records (7 events) found by reading the remaining pool pages and calendar detail pages (2026-11-19).

Raw official pages are committed unchanged under research/2026-11-19-audit/pages/
(fetched by read-only workflows, HTTP 200). Quotes must occur verbatim in those pages.
The gate validator re-derives every record from this module and requires exact equality.
"""
import argparse, hashlib, json, pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import suginami_addition_20261118 as S

BASE = '003709fe1fdce9af71fb83da6fe3ff2c225b4ba3'   # data-production after the lead14 addition (552 records)
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


SPECS_RAW = [{'id': 'verified-20261123-koto-midori-kosodate-kameido', 'week': '2026-11-21', 'ward': '江東区', 'page': 'koto_kuho_1101_3.html', 'name': 'みどりの子育てひろば「秋の自然たんけん隊@亀戸」', 'url': 'https://www.city.koto.lg.jp/011501/kuse/koho/kuho/r08/text/110103.html', 'date': '2026-11-23', 'period': '11/23(月・祝)', 'time': '10:00〜11:30', 'venue': '亀戸中央公園B地区', 'price': '参加費の記載なし', 'description': '公園を探検しながら秋の自然を見つける、1歳以上の幼児と保護者向けのおさんぽ会。講師はNPOマザーツリー自然学校。', 'cats': ['公園・自然', '親子'], 'io': '屋外', 'res': {'required': True, 'note': '11/5から申込フォームで。定員50人程度（申込順）。'}, 'quotes': ['みどりの子育てひろば「秋の自然たんけん隊@亀戸」自然の中でこどもを育む「みどりの子育てひろば」のおさんぽ会です。公園を探検しながら秋の自然を見つけましょう。【日時】11月23日（月曜日・祝日）10時00分～11時30分', '【日時】11月23日（月曜日・祝日）10時00分～11時30分', '【場所】亀戸中央公園B地区（亀戸8丁目22番）【対象】1歳以上の幼児と保護者', '【対象】1歳以上の幼児と保護者【定員】50人程度（申込順）', '【申し込み】11月5日（木曜日）から申込フォーム（外部サイトへリンク）（別ウィンドウで開きます）で'], 'overall': 'B', 'basis': 'child_program', 'child': True, 'reason': '公園を探検しながら秋の自然を見つける、1歳以上の幼児と保護者向けのおさんぽ会。参加費の記載なし。事前の申込が必要。', 'axes': {'child_target': ['A', '1歳以上の幼児と保護者が対象'], 'interactivity': ['A', '公園を探検して自然を探す'], 'age_fit': ['A', '1歳以上の幼児と明記'], 'stay_flexibility': ['B', '10:00〜11:30'], 'burden': ['B', '定員50人程度で、申込フォームから申込'], 'cost': ['unknown', '参加費の記載がない'], 'reservation': ['B', '11/5から申込フォーム'], 'family_value': ['A', '自然の中で親子で歩ける']}, 'strengths': ['自然たんけん', '講師つき'], 'limitations': ['申込フォーム', '参加費の記載なし'], 'comparison': '総合B：11/23(月・祝)の亀戸中央公園B地区で10:00〜11:30の開催。参加費の記載なし。申込が必要で、定員がある。', 'extra': [], 'pf': 'unknown', 'pos': ['official_date_confirmed', 'child_activity_confirmed']}, {'id': 'verified-20261129-koto-higashisuna-nyanmatsuri', 'week': '2026-11-28', 'ward': '江東区', 'page': 'koto_kuho_1111_2.html', 'name': '東砂児童館 ひがしすにゃんまつり -冬-', 'url': 'https://www.city.koto.lg.jp/011501/kuse/koho/kuho/r08/text/111102.html', 'date': '2026-11-29', 'period': '11/29(日)', 'time': '10:00〜15:00', 'venue': '東砂児童館（区報に会場の明記なし）', 'price': '参加費の記載なし', 'description': 'おばけやしき、リサイクル市、舞台発表がある児童館のまつり。乳幼児から高校生世代まで。当日直接参加。', 'cats': ['祭り', '子ども'], 'io': '屋内', 'res': {'required': False, 'note': '当日直接会場へ。'}, 'quotes': ['東砂児童館ひがしすにゃんまつり-冬-', '【日時】11月29日（日曜日）10時00分～15時00分【対象】乳幼児（0歳）～小・中学生、高校生世代', '【内容】おばけやしき、リサイクル市、舞台発表【申し込み】当日直接会場へ'], 'overall': 'B', 'basis': 'child_program', 'child': True, 'reason': 'おばけやしき、リサイクル市、舞台発表がある児童館のまつり。参加費の記載なし。申込の案内はなく、当日参加できる。', 'axes': {'child_target': ['A', '乳幼児から高校生世代までが対象'], 'interactivity': ['A', 'おばけやしき・リサイクル市・舞台発表'], 'age_fit': ['A', '乳幼児（0歳）〜高校生世代と明記'], 'stay_flexibility': ['B', '10:00〜15:00'], 'burden': ['A', '当日直接参加でき、出入り自由'], 'cost': ['unknown', '参加費の記載がない'], 'reservation': ['A', '申込不要'], 'family_value': ['B', '児童館のまつりを親子で楽しめる']}, 'strengths': ['当日直接', 'おばけやしき'], 'limitations': ['会場の明記なし', '参加費の記載なし'], 'comparison': '総合B：11/29(日)の東砂児童館で10:00〜15:00の開催。参加費の記載なし。申込不要で気軽に参加できる。', 'extra': [], 'pf': 'unknown', 'pos': ['official_date_confirmed', 'child_activity_confirmed']}, {'id': 'verified-20261205-koto-tatsumi-family-day-crystal', 'week': '2026-12-05', 'ward': '江東区', 'page': 'koto_kuho_1111_2.html', 'name': '辰巳児童館 ファミリーデー「科学工作～結晶をそだてよう～」', 'url': 'https://www.city.koto.lg.jp/011501/kuse/koho/kuho/r08/text/111102.html', 'date': '2026-12-05', 'period': '12/5(土)', 'time': '10:30〜11:30', 'venue': '辰巳児童館（区報に会場の明記なし）', 'price': '参加費の記載なし', 'description': '結晶についての話を聞き、結晶がそだつセットを工作する、年長児〜高校生世代向けのファミリーデー。', 'cats': ['体験・ワークショップ', '工作'], 'io': '屋内', 'res': {'required': True, 'note': '11/21 9時から辰巳児童館に電話・窓口で申込。定員20人（申込順）。'}, 'quotes': ['辰巳児童館ファミリーデー「科学工作～結晶をそだてよう～」', '【日時】12月5日（土曜日）10時30分～11時30分【対象】年長児～小・中学生、高校生世代（注釈）小学生以下は要保護者同伴', '【定員】20人（申込順）【内容】結晶についての話と、結晶がそだつセットの工作', '【申し込み】11月21日（土曜日）9時00分から辰巳児童館に電話・窓口で'], 'overall': 'B', 'basis': 'child_program', 'child': True, 'reason': '結晶についての話を聞き、結晶がそだつセットを工作する、年長児〜高校生世代向けのファミリーデー。参加費の記載なし。事前の申込が必要。', 'axes': {'child_target': ['A', '年長児〜高校生世代が対象（小学生以下は保護者同伴）'], 'interactivity': ['A', '結晶の話を聞いて工作する'], 'age_fit': ['A', '年長児以上と明記'], 'stay_flexibility': ['B', '10:30〜11:30'], 'burden': ['C', '定員20人で、申込が必要'], 'cost': ['unknown', '参加費の記載がない'], 'reservation': ['C', '11/21から電話・窓口で申込'], 'family_value': ['B', '親子で科学工作ができる']}, 'strengths': ['科学工作', '保護者同伴'], 'limitations': ['定員20人', '参加費の記載なし'], 'comparison': '総合B：12/5(土)の辰巳児童館で10:30〜11:30の開催。参加費の記載なし。申込が必要で、定員がある。', 'extra': [], 'pf': 'unknown', 'pos': ['official_date_confirmed', 'child_activity_confirmed']}, {'id': 'verified-20261219-koto-minamisuna-xmas-concert', 'week': '2026-12-19', 'ward': '江東区', 'page': 'koto_kuho_1111_2.html', 'name': '南砂児童館 クリスマスミニコンサート', 'url': 'https://www.city.koto.lg.jp/011501/kuse/koho/kuho/r08/text/111102.html', 'date': '2026-12-19', 'period': '12/19(土)', 'time': '11:00〜11:30（開場10:30）', 'venue': '南砂児童館（区報に会場の明記なし）', 'price': '参加費の記載なし', 'description': '金管楽器アンサンブルによるクリスマス曲の演奏を楽しむ、乳幼児から高校生世代向けのコンサート。', 'cats': ['音楽', 'ショー・観劇'], 'io': '屋内', 'res': {'required': True, 'note': '12/5 9時からこうとうおやこ手帳または窓口で申込。定員100人。'}, 'quotes': ['南砂児童館Teen’sBase（中高生支援館）クリスマスミニコンサート', '【日時】12月19日（土曜日）11時00分～11時30分（開場10時30分）【対象】乳幼児（0歳）～小・中学生、高校生世代', '【定員】100人（オンライン申し込み50人、窓口50人。付き添いを含む。申込順）', '【内容】金管楽器アンサンブルによるクリスマス曲の演奏'], 'overall': 'B', 'basis': 'child_program', 'child': True, 'reason': '金管楽器アンサンブルによるクリスマス曲の演奏を楽しむ、乳幼児から高校生世代向けのコンサート。参加費の記載なし。事前の申込が必要。', 'axes': {'child_target': ['A', '乳幼児から高校生世代が対象'], 'interactivity': ['B', '演奏を鑑賞する'], 'age_fit': ['A', '乳幼児（0歳）〜高校生世代と明記'], 'stay_flexibility': ['B', '11:00〜11:30（開場10:30）'], 'burden': ['C', '定員100人（付き添いを含む）で申込が必要'], 'cost': ['unknown', '参加費の記載がない'], 'reservation': ['C', '12/5からおやこ手帳または窓口で申込'], 'family_value': ['B', '親子でクリスマスの生演奏を楽しめる']}, 'strengths': ['生演奏', '30分と短い'], 'limitations': ['申込が必要', '参加費の記載なし'], 'comparison': '総合B：12/19(土)の南砂児童館で11:00〜11:30（開場10:30）の開催。参加費の記載なし。申込が必要で、定員がある。', 'extra': [], 'pf': 'unknown', 'pos': ['official_date_confirmed', 'child_activity_confirmed']}, {'id': 'verified-20261219-koto-onagigawa-winter-festival', 'week': '2026-12-19', 'ward': '江東区', 'page': 'koto_kuho_1111_2.html', 'name': '小名木川児童館 ウィンターフェスティバル', 'url': 'https://www.city.koto.lg.jp/011501/kuse/koho/kuho/r08/text/111102.html', 'date': '2026-12-19', 'period': '12/19(土)', 'time': '10:30〜13:30', 'venue': '小名木川児童館（区報に会場の明記なし）', 'price': '参加費の記載なし', 'description': 'クリスマス工作やミニコンサートなどが楽しめる、乳幼児から高校生世代向けの冬のイベント。当日直接参加。', 'cats': ['祭り', '工作'], 'io': '屋内', 'res': {'required': False, 'note': '当日直接会場へ。定員200人（先着順）。'}, 'quotes': ['小名木川児童館ウィンターフェスティバル', '【日時】12月19日（土曜日）10時30分～13時30分', '【定員】200人（先着順）【内容】クリスマス工作やミニコンサートなどのウィンターイベント', '【内容】クリスマス工作やミニコンサートなどのウィンターイベント【申し込み】当日直接会場へ'], 'overall': 'B', 'basis': 'child_program', 'child': True, 'reason': 'クリスマス工作やミニコンサートなどが楽しめる、乳幼児から高校生世代向けの冬のイベント。参加費の記載なし。申込の案内はなく、当日参加できる。', 'axes': {'child_target': ['A', '乳幼児から高校生世代が対象'], 'interactivity': ['A', 'クリスマス工作やミニコンサート'], 'age_fit': ['A', '乳幼児（0歳）〜高校生世代と明記'], 'stay_flexibility': ['B', '10:30〜13:30'], 'burden': ['A', '当日直接参加'], 'cost': ['unknown', '参加費の記載がない'], 'reservation': ['A', '申込不要（先着200人）'], 'family_value': ['B', '工作とコンサートを親子で楽しめる']}, 'strengths': ['当日直接', 'クリスマス工作'], 'limitations': ['先着200人', '参加費の記載なし'], 'comparison': '総合B：12/19(土)の小名木川児童館で10:30〜13:30の開催。参加費の記載なし。申込不要で気軽に参加できる。', 'extra': [], 'pf': 'unknown', 'pos': ['official_date_confirmed', 'child_activity_confirmed']}, {'id': 'verified-20261219-koto-oshima-xmas-party', 'week': '2026-12-19', 'ward': '江東区', 'page': 'koto_kuho_1111_2.html', 'name': '大島児童館 クリスマスパーティー2026', 'url': 'https://www.city.koto.lg.jp/011501/kuse/koho/kuho/r08/text/111102.html', 'date': '2026-12-19', 'period': '12/19(土)', 'time': '①10:30〜11:20（乳幼児と保護者）／②14:00〜14:50（小学生〜高校生世代）', 'venue': '大島児童館（区報に会場の明記なし）', 'price': '参加費の記載なし', 'description': 'クリスマス気分を味わいながらゲームなどを楽しむパーティー。午前は乳幼児と保護者、午後は小学生〜高校生世代。', 'cats': ['祭り', '子ども'], 'io': '屋内', 'res': {'required': True, 'note': '11/28 9時から大島児童館窓口で申込（空きがあれば12/5から電話可）。①40人②60人。'}, 'quotes': ['大島児童館クリスマスパーティー2026', '【日時】12月19日（土曜日）（1）10時30分～11時20分（2）14時00分～14時50分【対象】（1）乳幼児と保護者（2）小・中学生～高校生世代', '【定員】（1）40人（2）60人（申込順）【内容】クリスマス気分を味わいながらゲームなどを楽しむ', '【申し込み】11月28日（土曜日）9時00分から大島児童館窓口で'], 'overall': 'B', 'basis': 'child_program', 'child': True, 'reason': 'クリスマス気分を味わいながらゲームなどを楽しむパーティー。参加費の記載なし。事前の申込が必要。', 'axes': {'child_target': ['A', '午前は乳幼児と保護者、午後は小学生〜高校生世代'], 'interactivity': ['A', 'ゲームなどを楽しむ'], 'age_fit': ['A', '年齢別に2部に分けている'], 'stay_flexibility': ['B', '①10:30〜11:20（乳幼児と保護者）／②14:00〜14:50（小学生〜高校生世代）'], 'burden': ['C', '申込順で定員40人・60人'], 'cost': ['unknown', '参加費の記載がない'], 'reservation': ['C', '11/28から窓口で申込'], 'family_value': ['B', 'クリスマス気分でゲームを楽しめる']}, 'strengths': ['年齢別の2部制', 'ゲーム'], 'limitations': ['申込が必要', '参加費の記載なし'], 'comparison': '総合B：12/19(土)の大島児童館で①10:30〜11:20（乳幼児と保護者）／②14:00〜14:50（小学生〜高校生世代）の開催。参加費の記載なし。申込が必要で、定員がある。', 'extra': [], 'pf': 'unknown', 'pos': ['official_date_confirmed', 'child_activity_confirmed']}, {'id': 'verified-20261213-koto-papa-happy-xmas-tree-art', 'week': '2026-12-12', 'ward': '江東区', 'page': 'koto_kuho_1101_3.html', 'name': 'パパのハッピー子育て講座 親子で楽しむクリスマスツリーアート', 'url': 'https://www.city.koto.lg.jp/011501/kuse/koho/kuho/r08/text/110103.html', 'date': '2026-12-13', 'period': '12/13(日)', 'time': '10:00〜11:30', 'venue': '男女共同参画推進センター', 'price': '参加費の記載なし', 'description': '「臨床美術」で素材の感触や色を楽しみながらクリスマスツリーを表現する、3〜5歳のこどもと父親向けの講座。', 'cats': ['体験・ワークショップ', 'アート'], 'io': '屋内', 'res': {'required': True, 'note': '11/5 9時から区ホームページ申込または電話・窓口。定員16組（申込順）。幼児の一時保育は要予約。'}, 'quotes': ['パパのハッピー子育て講座親子で楽しむクリスマスツリーアート', '【日時】12月13日（日曜日）10時00分～11時30分', '【場所】男女共同参画推進センター', '【対象】3～5歳のこどもと父親【定員】16組（申込順）（注釈）父親1人につきこども1人', '【申し込み】11月5日（木曜日）から申込フォーム（外部サイトへリンク）（別ウィンドウで開きます）で【問い合わせ】施設保全課庶務係'], 'overall': 'B', 'basis': 'child_program', 'child': True, 'reason': '「臨床美術」で素材の感触や色を楽しみながらクリスマスツリーを表現する、3〜5歳のこどもと父親向けの講座。参加費の記載なし。事前の申込が必要。', 'axes': {'child_target': ['A', '3〜5歳のこどもと父親が対象'], 'interactivity': ['A', '臨床美術でクリスマスツリーを作る'], 'age_fit': ['A', '3〜5歳と明記'], 'stay_flexibility': ['B', '10:00〜11:30'], 'burden': ['C', '定員16組で、申込が必要'], 'cost': ['unknown', '参加費の記載がない'], 'reservation': ['C', '11/5から区ホームページまたは電話・窓口'], 'family_value': ['A', '父子で作品づくりができる']}, 'strengths': ['父子向け', '臨床美術'], 'limitations': ['定員16組', '父親1人につきこども1人', '参加費の記載なし'], 'comparison': '総合B：12/13(日)の男女共同参画推進センターで10:00〜11:30の開催。参加費の記載なし。申込が必要で、定員がある。', 'extra': [], 'pf': 'unknown', 'pos': ['official_date_confirmed', 'child_activity_confirmed']}]
RAW = SPECS_RAW
SPECS = []
for _r in RAW:
    _s = dict(_r)
    _s['categories'] = _s.pop('cats'); _s['indoor_outdoor'] = _s.pop('io'); _s['reservation'] = _s.pop('res')
    _s['child_activity'] = _s.pop('child'); _s['price_field'] = _s.pop('pf'); _s['positive'] = _s.pop('pos')
    SPECS.append(_s)
NEW_IDS = [s['id'] for s in SPECS]
SHARDS = {w: f'{w}-events-lead14-20261119.json' for w in ('2026-11-21', '2026-11-28', '2026-12-05', '2026-12-12', '2026-12-19')}
HELD = {'koto-teens-and-weekday': '江東区の児童館冬イベントのうち、平日開催・中高生のみ・2027年開催・抽選で区内在住限定のもの（星空教室など）は掲載対象外', 'shinagawa-koho-pages': '品川区の広報しながわ（2026-11-01・11-15号）のWebページURLは取得できず（404）、品川区は日付付きの個別イベントが未確認'}


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
    for x in spec.get('extra', []):
        t2 = _page_text(pathlib.Path(pages_dir) / x['page'])
        if S._strip(x['q']) not in t2:
            raise ValueError(f"{spec['id']}: calendar quote not found verbatim in the committed official calendar page: {x['q']}")
        out.append({'url': x['url'], 'quote': x['q'], 'checked_at': CHECKED,
                    'sha256': hashlib.sha256(x['q'].encode('utf-8')).hexdigest(),
                    'hash_scope': 'quoted_text_only_not_HTTP_response_hash',
                    'description': f"{spec['ward']}公式資料PDF（2026-11-19にHTTP200で取得、原本と本文抽出をresearch/2026-11-19-audit/pages/に不変保存）の本文引用。"})
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
        run['lead14_addition_20261119'] = {
            'kind': 'individually_verified_official_events_from_lead_triage', 'added_ids': [i[0]['id'] for i in items],
            'held_not_published': sorted(HELD), 'pages_committed_at': 'research/2026-11-19-audit/pages/',
            'base_data_production_sha': BASE, 'global_source_audit_complete': False}
        S.jdump(d / f'{week}-run.json', run)
        for x in m['weekends']:
            if x['sat'] == week:
                x['count'] += n
    m['generated'] = '2026-11-20T02:00:00+09:00'
    S.jdump(d / 'manifest.json', m)
    h = S.jload(d / 'update_history.json')
    h['history'].append({
        'run_id': 'lead14-addition-20261119', 'run_type': 'manual_verified_lead14_addition',
        'status': 'verified_subset_publication', 'as_of_jst': '2026-11-19', 'executed_at': m['generated'],
        'base_data_production_sha': BASE, 'target_weekends': sorted(derived),
        'prior_active_week_records': 552, 'candidate_active_week_records': 559, 'added_weekly_records': 7,
        'new_event_ids': NEW_IDS, 'held_not_published': sorted(HELD),
        'existing_event_records_physically_deleted': 0, 'image_only_updates': 0,
        'source_failures_remain_unverified': True, 'global_source_audit_complete': False,
        'full_23_ward_25_source_audit_complete': False,
        'note': '江東区報（令和8年11月1日号・11日号）の公式テキスト版で日付と内容を確認できた7件の週別レコードのみ追加。',
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
