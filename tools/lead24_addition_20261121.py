#!/usr/bin/env python3
"""6 weekly records (Tokyo metropolitan park events: Shakujii, Shiba, Komazawa x2, Soshigaya, Shinozaki, 6 records) from committed official Tokyo Park Association pages (2026-11-21).

Raw official pages are committed unchanged under research/2026-11-20-thin-wards/pages/. The gate validator re-derives every record and requires exact equality.
"""
import argparse, hashlib, json, pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import suginami_addition_20261118 as S

BASE = '2097dd4aea8c6aa17cf22901caab147f6df17dab'   # data-production after lead23 (720 active week records)
CHECKED = '2026-11-21'
AXES = S.AXES
NOTE_AUDIT = '週別全源照合は未完（ためまっぷ403等）。この4件は各公式ページの個別確認に基づく。'
S.CHECKED = CHECKED


def _page_text(path):
    """Like suginami page_text, but falls back to the whole document when a page has no early <h1>."""
    raw = pathlib.Path(path).read_text(encoding='utf-8', errors='ignore')
    i = raw.find('<h1')
    raw = raw[i:] if 0 <= i < 20000 else raw   # SPA pages (event site) put the only <h1> after the body; use the whole document
    raw = S.re.sub(r'<(script|style).*?</\1>', '', raw, flags=S.re.S)
    raw = S.re.sub(r'<br\s*/?>|</(p|li|tr|dt|dd|h\d|div|th|td)>', '\n', raw)
    return S.re.sub(r'\s+', '', S.html.unescape(S.re.sub(r'<[^>]+>', '', raw)))


_TP = 'https://www.tokyo-park.or.jp'


def _ax(ct, it, af, st, bu, co, re_, fv):
    return {'child_target': ct, 'interactivity': it, 'age_fit': af, 'stay_flexibility': st, 'burden': bu, 'cost': co, 'reservation': re_, 'family_value': fv}


def _komazawa(date, md):
    return {'id': f'verified-{date.replace("-", "")}-setagaya-komazawa-fantasia', 'week': '2026-11-28', 'ward': '世田谷区', 'page': 'tokyopark_komazawa_fantasia_2026.html',
        'name': '駒沢ファンタジア2026（駒沢オリンピック公園）', 'url': _TP + '/event_search/komazawa_fantasia2026.html', 'date': date, 'period': md, 'time': '10:00〜16:00',
        'venue': '駒沢オリンピック公園 中央広場（世田谷区駒沢1-1）', 'price': '参加費無料（ブース等の販売・体験には費用がかかる場合がある）',
        'image': _TP + '/event_search/assets/komazawafantasia2026-8.jpg',
        'description': '駒沢オリンピック公園の開園日に合わせた毎年のイベント。周辺事業者のマルシェ、体験型ワークショップ、キッチンカー、ライブや読み聞かせなどのステージがある。日ごとに内容が一部異なる可能性があるため、詳細は公式ページで確認。',
        'cats': ['まつり・イベント', '体験・ワークショップ'], 'io': '屋外',
        'res': {'required': False, 'note': '「受付等はございません」と記載。小雨決行・荒天中止（前日12:00に公園HP・Xで告知）。'},
        'quotes': ['■日程： 2026 年 11 月 28 日（土）・ 11 月 29 日（日） 10:00 ～ 16:00', '■ 場所：駒沢オリンピック公園（世田谷区駒沢 1-1 ）内 中央広場', '■ 対象：小さい子から大人まで楽しめるコンテンツを多数用意しているイベントです！', '■ 参加費：無料（ ブース等の販売・体験にはお金がかかる場合がございます。）', '〇ステージ ライブや読み聞かせ、ステージパフォーマンスで一緒に会場を沸かせよう！', '〇地域連携ブース 体験型ワークショップや展示・植物の販売などのコンテンツが盛りだくさん！'],
        'overall': 'B', 'basis': 'all_ages', 'child': True,
        'reason': '公式ページに「小さい子から大人まで楽しめる」とあり、体験型ワークショップや読み聞かせのステージがある無料のイベント。ブースの体験は有料の場合がある。',
        'axes': _ax(['B', '「小さい子から大人まで」と明記されるが、子ども専用の企画ではない'], ['B', '体験型ワークショップやステージがあるが、日ごとの内容は公式ページで要確認'], ['B', '対象は「小さい子から大人まで」で、年齢別の案内はない'], ['A', '10:00〜16:00の間、好きなブースを選べる'], ['B', '屋外で小雨決行・荒天中止。駐車場の案内はない'], ['B', '参加費無料だが、ブースの体験や販売は有料の場合がある'], ['A', '受付等なし。当日そのまま参加できる'], ['B', 'マルシェ・ワークショップ・読み聞かせを家族で無料で楽しめる']),
        'strengths': ['参加費無料で、小さな子から大人まで楽しめると明記', '体験型ワークショップや読み聞かせのステージがある'], 'limitations': ['ブースの体験・販売は有料の場合がある', '日ごとの内容が一部異なる可能性があり、公式ページで要確認'],
        'comparison': f'総合B：{md}は無料で入れて小さい子から楽しめるが、子ども専用ではなく、ブースの体験は有料の場合がある。',
        'pf': 'unknown', 'pos': ['official_date_confirmed', 'child_activity_confirmed']}


SPECS_RAW = [
    {'id': 'verified-20261121-nerima-shakujii-book-kaidan', 'week': '2026-11-21', 'ward': '練馬区', 'page': 'tokyopark_shakujii_book_20261121.html',
     'name': '本のくつろぎかいだん（石神井公園）', 'url': _TP + '/park/shakujii/news/2026/park_info_11.html', 'date': '2026-11-21', 'period': '11/21(土)', 'time': '13:00〜16:00',
     'venue': '石神井公園 野外ステージ', 'price': '参加費無料',
     'image': _TP + '/park/shakujii/assets/%E6%9C%AC%E3%81%AE%E3%81%8F%E3%81%A4%E3%82%8D%E3%81%8E%E3%81%8B%E3%81%84%E3%81%A0%E3%82%93_%E3%83%9D%E3%82%B9%E3%82%BF%E3%83%BC.jpg',
     'description': '石神井公園の野外ステージの階段に読書コーナーを設け、練馬おはなしの会などによる楽しいおはなし会を行う1日だけのイベント。予約不要、大人も子供も参加できる。予備日は11/28(土)。',
     'cats': ['本・読み聞かせ', '自然・公園'], 'io': '屋外',
     'res': {'required': False, 'note': '予約不要。予備日11/28(土)。'},
     'quotes': ['令和8年11月21日(土) 午後1時～4時', '場 所 石神井公園野外ステージ', '予約は要りません。大人も子供も大集合！', '階段に読書コーナーを設け、楽しいおはなし会を行います。', '出 演 ねりまおはなしの会、にじのね、石神井図書館スタッフ', '参加費 無料 ■問合せ先 練馬区立石神井図書館'],
     'overall': 'B', 'basis': 'all_ages', 'child': True,
     'reason': '「大人も子供も大集合」とあり、屋外で読書コーナーとおはなし会を無料・予約不要で楽しめる。屋外開催で、天候により予備日になる。',
     'axes': _ax(['B', '「大人も子供も」と明記され、おはなし会がある'], ['B', 'おはなし会を聞く内容で、体験型の企画ではない'], ['B', '年齢別の案内はない'], ['A', '13:00〜16:00の間に自由に立ち寄れる'], ['B', '屋外開催で、荒天時は予備日になる'], ['A', '参加費無料'], ['A', '予約不要'], ['B', '無料で本とおはなし会を楽しめる']),
     'strengths': ['無料・予約不要で、おはなし会と読書コーナーを楽しめる'], 'limitations': ['屋外で天候の影響を受ける（予備日11/28）', '年齢別の案内はない'],
     'comparison': '総合B：無料・予約不要でおはなし会を楽しめるが、年齢別の案内がなく屋外で天候の影響を受ける。',
     'pf': 'pass', 'pos': ['official_date_confirmed', 'child_activity_confirmed']},
    {'id': 'verified-20261121-minato-siba-stargazing', 'week': '2026-11-21', 'ward': '港区', 'page': 'tokyopark_siba_stargazing_20261121.html',
     'name': '星空観望会（芝公園）', 'url': _TP + '/park/siba/news/2026/sibastamprally2026_1.html', 'date': '2026-11-21', 'period': '11/21(土)', 'time': '18:00〜19:30',
     'venue': '芝公園18号地（港区芝公園4-5）', 'price': '参加費無料',
     'image': _TP + '/park/siba/assets/%E6%98%9F%E7%A9%BA%E8%A6%B3%E6%9C%9B%E4%BC%9A%E4%BD%8F%E6%89%80%EF%BC%92.png',
     'description': '芝公園18号地で、天体望遠鏡で秋の星空を眺める観望会。昨年は土星が見えた。どなたでも参加でき、未就学児や小学生も楽しめる。事前申込不要・無料。雨天・曇天中止（当日昼ごろ公式Xで発表）。',
     'cats': ['自然・公園', '体験・ワークショップ'], 'io': '屋外',
     'res': {'required': False, 'note': '事前申込不要。当日、受付場所へ直接。雨天・曇天中止で、可否は当日昼ごろ芝公園公式Xで発表。'},
     'quotes': ['2026年11月21日(土) 18:00～19:30', '受付場所 芝公園18号地 港区芝公園4-5', 'どなたでも、ご参加いただけます。 未就学児や小学生のお子さまも楽しめます。', '事前申込み不要 当日、受付場所へ直接お越しください。', '参加費 無料 ６．内容 天体望遠鏡で星空を眺めてみよう', '※雨天、曇天中止 ※開催の可否は当日お昼ごろ'],
     'overall': 'B', 'basis': 'all_ages', 'child': True,
     'reason': '「未就学児や小学生のお子さまも楽しめます」と明記された、無料・申込不要の天体観望会。夜の開催で、雨天・曇天は中止。',
     'axes': _ax(['B', '「未就学児や小学生のお子さまも楽しめます」と明記されるが、子ども専用ではない'], ['B', '天体望遠鏡で星空を観察する体験'], ['B', '未就学児・小学生も楽しめると記載'], ['B', '18:00〜19:30の枠内で参加'], ['B', '夜間・屋外開催で、雨天・曇天は中止（当日昼に発表）'], ['A', '参加費無料'], ['A', '事前申込不要'], ['B', '無料で望遠鏡で星空を見られる']),
     'strengths': ['無料・申込不要で、未就学児や小学生も楽しめる'], 'limitations': ['夜の屋外開催で雨天・曇天は中止', '開催可否が当日昼まで分からない'],
     'comparison': '総合B：無料・申込不要で子どもも楽しめるが、夜間で天候次第の開催。',
     'pf': 'pass', 'pos': ['official_date_confirmed', 'child_activity_confirmed']},
    _komazawa('2026-11-28', '11/28(土)'),
    _komazawa('2026-11-29', '11/29(日)'),
    {'id': 'verified-20261212-setagaya-soshigaya-xmas-tree', 'week': '2026-12-12', 'ward': '世田谷区', 'page': 'tokyopark_soshigaya_tree_20261212.html',
     'name': 'クリスマスツリー作り（小学生以下・祖師谷公園）', 'url': _TP + '/park/soshigaya/news/2026/park_info_29.html', 'date': '2026-12-12', 'period': '12/12(土)', 'time': '①10:00〜11:00／②13:00〜14:00',
     'venue': '祖師谷公園（世田谷区、詳細な集合場所はポスター・チラシに記載）', 'price': '参加費1回1,500円',
     'image': _TP + '/park/soshigaya/assets/%EF%BC%92%EF%BC%90%EF%BC%92%EF%BC%96%E5%B9%B4%E3%82%AF%E3%83%AA%E3%82%B9%E3%83%9E%E3%82%B9%E3%83%84%E3%83%AA%E3%83%BC%E4%BD%9C%E3%82%8A%EF%BC%86%E3%82%AF%E3%83%AA%E3%82%B9%E3%83%9E%E3%82%B9%E3%83%84%E3%83%AA%E3%83%BC%E4%BD%9C%E3%82%8A%E3%83%81%E3%83%A9%E3%82%B7_1_1.jpg',
     'description': '小学生以下が参加するクリスマスツリー作り（未就学児は保護者同伴）。各回10名で、WEBで申し込み、締切後に抽選（締切は12/3）。同じ公園で12/5にある中学生以上向けのリース作りとは別の企画。',
     'cats': ['体験・ワークショップ', '工作'], 'io': '',
     'res': {'required': True, 'note': 'WEB申込・締切後に抽選。ツリー作りの締切は12/3(木)。'},
     'quotes': ['【クリスマスツリー作り (小学生以下) ※未就学児は保護者同伴】', '12 月 12 日 (土) ① 10 時 00 分 ～ 11 時 00 分 10名 ② 13 時 00 分 ～ 14 時 00 分 10名', '参加費 各回 1,500 円', '※今回、WEBでお申込み ! 締切後抽選となります。', '「クリスマスツリー作り(小学生以下)※未就学児は保護者同伴」 締切 : 12月 3日(木)'],
     'overall': 'A', 'basis': 'child_program', 'child': True,
     'reason': '小学生以下（未就学児は保護者同伴）が対象のクリスマスツリー作りで、参加費1,500円・WEB申込・抽選。各回10名と少人数。',
     'axes': _ax(['A', '対象は小学生以下で、未就学児は保護者同伴'], ['A', 'クリスマスツリーを作る工作体験'], ['A', '小学生以下と対象年齢が明記されている'], ['B', '各回1時間の枠で、開始時刻に参加'], ['B', '事前のWEB申込と抽選が必要で、各回10名と少人数'], ['B', '参加費1回1,500円'], ['B', 'WEB申込・抽選（締切12/3）'], ['A', '子どもが自分でツリーを作って持ち帰れる体験']),
     'strengths': ['小学生以下向けの工作で、未就学児も保護者同伴で参加できる'], 'limitations': ['抽選で各回10名と少人数', '参加費1,500円が必要', '集合場所などの詳細はポスター・チラシに記載'],
     'comparison': '総合A：小学生以下向けの工作で内容が子どもに合うが、有料・抽選・少人数が条件。',
     'pf': 'pass', 'pos': ['official_date_confirmed', 'child_activity_confirmed']},
    {'id': 'verified-20261213-edogawa-shinozaki-fureai-festival', 'week': '2026-12-12', 'ward': '江戸川区', 'page': 'tokyopark_shinozaki_fureai_20261213.html',
     'name': '篠崎公園ふれあいフェスティバル', 'url': _TP + '/park/shinozaki/news/2026/8_12_13.html', 'date': '2026-12-13', 'period': '12/13(日)', 'time': '10:00〜15:00',
     'venue': '篠崎公園', 'price': 'ちゃんこは無料配布（先着200名）。入場料や他のコーナーの費用の記載なし',
     'image': _TP + '/park/shinozaki/assets/%E7%AF%A0%E5%B4%8E%E5%85%AC%E5%9C%92%E3%81%B5%E3%82%8C%E3%81%82%E3%81%84%E3%83%95%E3%82%A7%E3%82%B9%E3%83%86%E3%82%A3%E3%83%90%E3%83%AB2026.png',
     'description': '相撲体験、ちゃんこの無料配布、キッズトレイン、ストラックアウト、公園のはたらく車に乗る体験、消防・警察コーナー（消防ミニカー・パトカー）、親子の靴ひもアクセサリー作りなど。雨天延期は12/20(日)。',
     'cats': ['まつり・イベント', '体験・ワークショップ'], 'io': '屋外',
     'res': {'required': None, 'note': '押し花レジン工作・寄せ植え講座は事前受付制。相撲体験は先着30名（13:00受付）、靴ひもアクセサリーは先着30組。それ以外は申込の記載なし。'},
     'quotes': ['開催日時：令和8年12月13日(日) 10時00分～15時00分', '※雨天延期：延期日12月20 日（日)', '①相撲体験：本物のお相撲さんと相撲をしてみよう。先着30名、受付13：00～', '⑦靴ひもアクセサリー作り：親子で靴ひもを編みキーチャームを作ろう★1組2本まで。(先着30組)', '⑧キッズトレイン：芝山の周りをトレインが走るよ。', '⑩公園のはたらく車：公園の職員とおそろいの制服を着てパワーカートや草刈機に乗ってみよう☆'],
     'overall': 'B', 'basis': 'all_ages', 'child': True,
     'reason': 'キッズトレイン、相撲体験、はたらく車、親子の靴ひもアクセサリー作りなど子どもが体験できるコーナーが多い公園のお祭り。入場料や費用は一部しか記載がない。',
     'axes': _ax(['B', '子ども向けのコーナーが多いが、イベント全体は誰でも参加できるお祭り'], ['A', '相撲体験・はたらく車・ストラックアウト・工作など体験が多い'], ['B', '小学4〜6年生のバスケ大会など年齢指定のコーナーがあり、全体の対象年齢は未記載'], ['A', '10:00〜15:00の間に好きなコーナーを回れる'], ['B', '屋外開催で、一部は先着や事前受付が必要'], ['unknown', 'ちゃんこ無料配布以外の費用の記載がない'], ['B', '一部は事前受付・先着制で、その他は申込の記載なし'], ['B', '相撲・乗り物・工作など子どもが楽しめるコーナーを一度に回れる']),
     'strengths': ['キッズトレインや相撲体験など子ども向けコーナーが多い', 'ちゃんこの無料配布がある'], 'limitations': ['入場料や各コーナーの費用が明記されていない', '一部は先着・事前受付制', '雨天は12/20に延期'],
     'comparison': '総合B：子ども向けコーナーが多い公園のお祭りだが、費用の記載が一部のみで、先着・事前受付のコーナーがある。',
     'pf': 'unknown', 'pos': ['official_date_confirmed', 'child_activity_confirmed']},
]
RAW = SPECS_RAW
SPECS = []
for _r in RAW:
    _s = dict(_r)
    _s['categories'] = _s.pop('cats'); _s['indoor_outdoor'] = _s.pop('io'); _s['reservation'] = _s.pop('res')
    _s['child_activity'] = _s.pop('child'); _s['price_field'] = _s.pop('pf'); _s['positive'] = _s.pop('pos')
    SPECS.append(_s)
NEW_IDS = [s['id'] for s in SPECS]
SHARDS = {w: f'{w}-events-lead24-20261121.json' for w in ('2026-11-21', '2026-11-28', '2026-12-05', '2026-12-12', '2026-12-19', '2026-12-26')}
HELD = {
    'hikarigaoka-fureai-festa-20261128': '光が丘公園フェスタ（練馬区、11/28・29）：どんぐり工作・はたらく車展示などの内容はあるが、参加費の記載がなく費用を推測しないため保留。',
    'ukima-tulip-bulb-20261205': '浮間公園チューリップの球根植え（12/5）：公園が板橋区と北区にまたがり、会場の風車前の区を公式ページで確認できないため保留。',
    'kiba-bousai-festa-20261205': '木場公園防災フェスタ（江東区、12/5）：子ども向けの記載がなく、乗り物展示・防災体験のため、子連れ向けの根拠が不足し保留。',
    'kiba-winter-decor-20261123': '木場公園 冬の飾りつけを作ろう（江東区、11/23）：対象年齢の記載がなく保留。',
    'yoyogi-donguri-20261206': '代々木公園 どんぐり工作（12/6）：対象年齢の記載がなく、子ども向けの根拠が不足し保留。',
    'kasai-rinkai-tours-monthly': '葛西臨海公園 鳥類園ガイドツアー等：毎月第2日曜・第4土曜の定例で、各日付が画像の年間カレンダーでしか確認できず、日付を推測しないため保留。',
    'hibiya-park-terrace-20261219': 'HIBIYA PARK TERRACE（千代田区、12/19・20）：公式ページに詳細（日時別プログラム・費用）が未掲載のため保留。',
    'takaido-wreath-20261205': '高井戸公園クリスマスリース作り教室（12/5）：詳細がチラシ画像のみで本文から確認できず保留。',
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
        for ward in sorted({i[0]['ward'] for i in items}):
            k = sum(1 for i in items if i[0]['ward'] == ward)
            for row in cov['wards']:
                if row['ward'] == ward:
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
        run['lead24_addition_20261121'] = {
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
        'run_id': 'lead24-addition-20261121', 'run_type': 'manual_verified_lead24_addition',
        'status': 'verified_subset_publication', 'as_of_jst': '2026-11-21', 'executed_at': m['generated'],
        'base_data_production_sha': BASE, 'target_weekends': sorted(derived),
        'prior_active_week_records': 720, 'candidate_active_week_records': 726, 'added_weekly_records': 6,
        'new_event_ids': NEW_IDS, 'held_not_published': sorted(HELD),
        'existing_event_records_physically_deleted': 0, 'image_only_updates': 0,
        'source_failures_remain_unverified': True, 'global_source_audit_complete': False,
        'full_23_ward_25_source_audit_complete': False,
        'note': '東京都公園協会の都立公園の公式ページで、石神井公園（11/21）、芝公園（11/21）、駒沢オリンピック公園（11/28・29）、祖師谷公園（12/12）、篠崎公園（12/13）のイベントを確認し、6件を追加。',
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
