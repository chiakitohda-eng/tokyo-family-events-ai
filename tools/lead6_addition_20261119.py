#!/usr/bin/env python3
"""Seven weekly records (three events) found by reading the remaining pool pages and calendar detail pages (2026-11-19).

Raw official pages are committed unchanged under research/2026-11-19-audit/pages/
(fetched by read-only workflows, HTTP 200). Quotes must occur verbatim in those pages.
The gate validator re-derives every record from this module and requires exact equality.
"""
import argparse, hashlib, json, pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import suginami_addition_20261118 as S

BASE = 'db9501b3a8dcd9c11c06c8b4f058061b8a248263'   # data-production after the lead4 addition (469 records)
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


SPECS_RAW = [{'id': 'verified-20261123-arakawa-hoshizora-rocket', 'week': '2026-11-21', 'ward': '荒川区', 'page': 'arakawa_hoshizora_rocket.html', 'name': '星空観察会とフィルムロケット工作（荒川自然公園）', 'url': 'https://www.city.arakawa.tokyo.jp/a042/koen/koen/sizenkouen2.html', 'date': '2026-11-23', 'period': '11/23(月・祝)', 'time': '工作13:00〜16:00／観察会17:30〜19:30', 'venue': '荒川自然公園野球場（荒川区荒川2丁目）', 'price': '工作200円／観察会無料', 'description': 'フィルムケースでロケットを作って飛ばす工作と、望遠鏡で月や惑星を見る観察会。誰でも自由参加、申込不要。工作は定員80名。', 'cats': ['体験・ワークショップ', '公園・自然'], 'io': '屋外', 'res': {'required': False, 'note': '申し込み不要。工作は定員80名。'}, 'quotes': ['ロケット工作と星空観察会を楽しもう！！', 'フィルムロケット工作13時00分～16時00分星空観察会17時30分～19時30分場所荒川自然公園野球場', 'フィルムケースを使ってロケットを作り、飛ばします。', '望遠鏡で月や惑星を観察します。', '対象者誰でも自由参加定員工作：80名観察会：なし費用工作：200円観察会：無料'], 'overall': 'B', 'basis': 'child_program', 'child': True, 'reason': 'ロケット工作と星空観察ができる。誰でも自由参加で申込不要。工作は有料（200円）で定員80名。', 'axes': {'child_target': ('B', '誰でも自由参加。工作と観察は子どもも楽しめる内容'), 'interactivity': ('A', 'ロケットを作って飛ばす工作と、望遠鏡での観察'), 'age_fit': ('unknown', '対象年齢の目安は明記がない'), 'stay_flexibility': ('B', '工作と観察会で時間帯が分かれ、夜まで開催'), 'burden': ('B', '屋外の開催で、中止の場合は公園のホームページで案内'), 'cost': ('B', '工作は200円、観察会は無料'), 'reservation': ('A', '申し込み不要'), 'family_value': ('A', '工作と星空を一日で体験できる')}, 'strengths': ['ロケット工作と星空観察を体験できる', '申込不要'], 'limitations': ['工作は200円で定員80名', '屋外開催で中止の場合がある'], 'comparison': '総合B：体験内容が充実し申込不要だが、工作は有料で定員がある。', 'pf': 'pass', 'pos': ['official_date_confirmed', 'child_activity_confirmed']}, {'id': 'verified-20261205-adachi-seibutsuen-hotaru', 'week': '2026-12-05', 'ward': '足立区', 'page': 'adachi_seibutsuen_hotaru.html', 'name': '足立区生物園 冬のホタル観賞会（夜間特別開園）', 'url': 'https://www.city.adachi.tokyo.jp/k-iji/event/seibutsuen_huyuhotaru.html', 'date': '2026-12-05', 'end': '2026-12-06', 'period': '11/28〜12/20の土日', 'time': '18:00〜21:00（20分ごと9回、最終回20:40開始）', 'venue': '足立区生物園（足立区保木間2丁目17番1号 元渕江公園内）', 'price': '無料（別途入園料が必要）', 'description': '室内の水槽で光るヘイケボタルを観賞できる夜間特別開園。各回40人の先着順で、事前申込は不要。就学前の子どもは保護者同伴。', 'cats': ['体験・ワークショップ', '公園・自然'], 'io': '屋内', 'res': {'required': False, 'note': '事前の申し込みは不要。直接会場へ。'}, 'quotes': ['室内に置かれた水槽の中で輝くヘイケボタルの幻想的な光を観賞できます。', '各日、午後6時から午後9時※最終回は午後8時40分開始。20分ごとに9回実施。', '対象どなたでも※就学前の子どもは保護者の同伴が必要です。', '募集人数各40人（先着順）費用無料※入園料が必要です。申込方法事前の申し込みは不要です。'], 'overall': 'B', 'basis': 'all_ages', 'child': False, 'reason': '冬のホタルを水槽で観賞できる夜の特別開園。どなたでも入れ、就学前は保護者同伴。各回40人の先着で、事前申込は不要。', 'axes': {'child_target': ('B', 'どなたでも入れ、就学前の子どもは保護者同伴と案内'), 'interactivity': ('B', 'ホタルの観賞が中心'), 'age_fit': ('unknown', '対象年齢の目安は明記がない'), 'stay_flexibility': ('B', '20分ごと9回の入れ替え制で、各回40人の先着'), 'burden': ('B', '夜の開催で、生体の状況により中止になる場合がある'), 'cost': ('B', '費用無料だが、別途入園料が必要'), 'reservation': ('A', '事前の申し込みは不要'), 'family_value': ('B', '冬にホタルを家族で観賞できる')}, 'strengths': ['申込不要で冬のホタルを観賞できる'], 'limitations': ['各回40人の先着順', '別途入園料が必要', '生体の状況により中止になる場合がある'], 'comparison': '総合B：申込不要で珍しい観賞ができるが、各回の定員が40人で入園料が別に必要。', 'pf': 'unknown', 'pos': ['official_date_confirmed']}, {'id': 'verified-20261212-adachi-seibutsuen-hotaru', 'week': '2026-12-12', 'ward': '足立区', 'page': 'adachi_seibutsuen_hotaru.html', 'name': '足立区生物園 冬のホタル観賞会（夜間特別開園）', 'url': 'https://www.city.adachi.tokyo.jp/k-iji/event/seibutsuen_huyuhotaru.html', 'date': '2026-12-12', 'end': '2026-12-13', 'period': '11/28〜12/20の土日', 'time': '18:00〜21:00（20分ごと9回、最終回20:40開始）', 'venue': '足立区生物園（足立区保木間2丁目17番1号 元渕江公園内）', 'price': '無料（別途入園料が必要）', 'description': '室内の水槽で光るヘイケボタルを観賞できる夜間特別開園。各回40人の先着順で、事前申込は不要。就学前の子どもは保護者同伴。', 'cats': ['体験・ワークショップ', '公園・自然'], 'io': '屋内', 'res': {'required': False, 'note': '事前の申し込みは不要。直接会場へ。'}, 'quotes': ['室内に置かれた水槽の中で輝くヘイケボタルの幻想的な光を観賞できます。', '各日、午後6時から午後9時※最終回は午後8時40分開始。20分ごとに9回実施。', '対象どなたでも※就学前の子どもは保護者の同伴が必要です。', '募集人数各40人（先着順）費用無料※入園料が必要です。申込方法事前の申し込みは不要です。'], 'overall': 'B', 'basis': 'all_ages', 'child': False, 'reason': '冬のホタルを水槽で観賞できる夜の特別開園。どなたでも入れ、就学前は保護者同伴。各回40人の先着で、事前申込は不要。', 'axes': {'child_target': ('B', 'どなたでも入れ、就学前の子どもは保護者同伴と案内'), 'interactivity': ('B', 'ホタルの観賞が中心'), 'age_fit': ('unknown', '対象年齢の目安は明記がない'), 'stay_flexibility': ('B', '20分ごと9回の入れ替え制で、各回40人の先着'), 'burden': ('B', '夜の開催で、生体の状況により中止になる場合がある'), 'cost': ('B', '費用無料だが、別途入園料が必要'), 'reservation': ('A', '事前の申し込みは不要'), 'family_value': ('B', '冬にホタルを家族で観賞できる')}, 'strengths': ['申込不要で冬のホタルを観賞できる'], 'limitations': ['各回40人の先着順', '別途入園料が必要', '生体の状況により中止になる場合がある'], 'comparison': '総合B：申込不要で珍しい観賞ができるが、各回の定員が40人で入園料が別に必要。', 'pf': 'unknown', 'pos': ['official_date_confirmed']}, {'id': 'verified-20261219-adachi-seibutsuen-hotaru', 'week': '2026-12-19', 'ward': '足立区', 'page': 'adachi_seibutsuen_hotaru.html', 'name': '足立区生物園 冬のホタル観賞会（夜間特別開園）', 'url': 'https://www.city.adachi.tokyo.jp/k-iji/event/seibutsuen_huyuhotaru.html', 'date': '2026-12-19', 'end': '2026-12-20', 'period': '11/28〜12/20の土日', 'time': '18:00〜21:00（20分ごと9回、最終回20:40開始）', 'venue': '足立区生物園（足立区保木間2丁目17番1号 元渕江公園内）', 'price': '無料（別途入園料が必要）', 'description': '室内の水槽で光るヘイケボタルを観賞できる夜間特別開園。各回40人の先着順で、事前申込は不要。就学前の子どもは保護者同伴。', 'cats': ['体験・ワークショップ', '公園・自然'], 'io': '屋内', 'res': {'required': False, 'note': '事前の申し込みは不要。直接会場へ。'}, 'quotes': ['室内に置かれた水槽の中で輝くヘイケボタルの幻想的な光を観賞できます。', '各日、午後6時から午後9時※最終回は午後8時40分開始。20分ごとに9回実施。', '対象どなたでも※就学前の子どもは保護者の同伴が必要です。', '募集人数各40人（先着順）費用無料※入園料が必要です。申込方法事前の申し込みは不要です。'], 'overall': 'B', 'basis': 'all_ages', 'child': False, 'reason': '冬のホタルを水槽で観賞できる夜の特別開園。どなたでも入れ、就学前は保護者同伴。各回40人の先着で、事前申込は不要。', 'axes': {'child_target': ('B', 'どなたでも入れ、就学前の子どもは保護者同伴と案内'), 'interactivity': ('B', 'ホタルの観賞が中心'), 'age_fit': ('unknown', '対象年齢の目安は明記がない'), 'stay_flexibility': ('B', '20分ごと9回の入れ替え制で、各回40人の先着'), 'burden': ('B', '夜の開催で、生体の状況により中止になる場合がある'), 'cost': ('B', '費用無料だが、別途入園料が必要'), 'reservation': ('A', '事前の申し込みは不要'), 'family_value': ('B', '冬にホタルを家族で観賞できる')}, 'strengths': ['申込不要で冬のホタルを観賞できる'], 'limitations': ['各回40人の先着順', '別途入園料が必要', '生体の状況により中止になる場合がある'], 'comparison': '総合B：申込不要で珍しい観賞ができるが、各回の定員が40人で入園料が別に必要。', 'pf': 'unknown', 'pos': ['official_date_confirmed']}, {'id': 'verified-20261205-edogawa-fuyusakura', 'week': '2026-12-05', 'ward': '江戸川区', 'page': 'edogawa_fuyusakura.html', 'name': '新川さくら館 冬ざくらイルミネーション', 'url': 'https://www.city.edogawa.tokyo.jp/event/26fuyusakura.html', 'date': '2026-12-05', 'end': '2026-12-06', 'period': '11/21〜12/25', 'time': '16:30〜21:30', 'venue': '新川さくら館広場（江戸川区船堀7丁目15番12号）', 'price': '無料', 'description': '新川さくら館の広場で開催するイルミネーション。冬の夜を彩る光を楽しめる。無料・申込不要。', 'cats': ['公園・自然', '地域交流'], 'io': '屋外', 'res': {'required': False, 'note': '申し込み不要。'}, 'quotes': ['きらめく光に包まれた幻想的な冬のお花見をお楽しみください。', '開催日時2026年11月21日（土曜日）から2026年12月25日（金曜日）16時30分～21時30分', '申し込み不要場所新川さくら館広場住所江戸川区船堀7丁目15番12号', '冬の夜を彩るイルミネーションを、ぜひお楽しみください。', '費用無料問合せ新川さくら館'], 'overall': 'B', 'basis': 'all_ages', 'child': False, 'reason': '冬の夜のイルミネーション。無料・申込不要で、5時間の開催。子ども向けとは明記されていない。', 'axes': {'child_target': ('unknown', '子ども向けとは明記されていない'), 'interactivity': ('B', 'イルミネーションの観賞が中心'), 'age_fit': ('unknown', '対象年齢は明記がない'), 'stay_flexibility': ('A', '16時30分〜21時30分の間、好きな時間に立ち寄れる'), 'burden': ('B', '夜の屋外での開催'), 'cost': ('A', '費用無料'), 'reservation': ('A', '申し込み不要'), 'family_value': ('B', '冬の夜の光を家族で楽しめる')}, 'strengths': ['無料・申込不要で5週間にわたり開催'], 'limitations': ['子ども向けとは明記されていない', '夜の屋外開催'], 'comparison': '総合B：無料・申込不要で気軽に行けるが、子ども向けの内容は明記がない。', 'pf': 'unknown', 'pos': ['official_date_confirmed']}, {'id': 'verified-20261212-edogawa-fuyusakura', 'week': '2026-12-12', 'ward': '江戸川区', 'page': 'edogawa_fuyusakura.html', 'name': '新川さくら館 冬ざくらイルミネーション', 'url': 'https://www.city.edogawa.tokyo.jp/event/26fuyusakura.html', 'date': '2026-12-12', 'end': '2026-12-13', 'period': '11/21〜12/25', 'time': '16:30〜21:30', 'venue': '新川さくら館広場（江戸川区船堀7丁目15番12号）', 'price': '無料', 'description': '新川さくら館の広場で開催するイルミネーション。冬の夜を彩る光を楽しめる。無料・申込不要。', 'cats': ['公園・自然', '地域交流'], 'io': '屋外', 'res': {'required': False, 'note': '申し込み不要。'}, 'quotes': ['きらめく光に包まれた幻想的な冬のお花見をお楽しみください。', '開催日時2026年11月21日（土曜日）から2026年12月25日（金曜日）16時30分～21時30分', '申し込み不要場所新川さくら館広場住所江戸川区船堀7丁目15番12号', '冬の夜を彩るイルミネーションを、ぜひお楽しみください。', '費用無料問合せ新川さくら館'], 'overall': 'B', 'basis': 'all_ages', 'child': False, 'reason': '冬の夜のイルミネーション。無料・申込不要で、5時間の開催。子ども向けとは明記されていない。', 'axes': {'child_target': ('unknown', '子ども向けとは明記されていない'), 'interactivity': ('B', 'イルミネーションの観賞が中心'), 'age_fit': ('unknown', '対象年齢は明記がない'), 'stay_flexibility': ('A', '16時30分〜21時30分の間、好きな時間に立ち寄れる'), 'burden': ('B', '夜の屋外での開催'), 'cost': ('A', '費用無料'), 'reservation': ('A', '申し込み不要'), 'family_value': ('B', '冬の夜の光を家族で楽しめる')}, 'strengths': ['無料・申込不要で5週間にわたり開催'], 'limitations': ['子ども向けとは明記されていない', '夜の屋外開催'], 'comparison': '総合B：無料・申込不要で気軽に行けるが、子ども向けの内容は明記がない。', 'pf': 'unknown', 'pos': ['official_date_confirmed']}, {'id': 'verified-20261219-edogawa-fuyusakura', 'week': '2026-12-19', 'ward': '江戸川区', 'page': 'edogawa_fuyusakura.html', 'name': '新川さくら館 冬ざくらイルミネーション', 'url': 'https://www.city.edogawa.tokyo.jp/event/26fuyusakura.html', 'date': '2026-12-19', 'end': '2026-12-20', 'period': '11/21〜12/25', 'time': '16:30〜21:30', 'venue': '新川さくら館広場（江戸川区船堀7丁目15番12号）', 'price': '無料', 'description': '新川さくら館の広場で開催するイルミネーション。冬の夜を彩る光を楽しめる。無料・申込不要。', 'cats': ['公園・自然', '地域交流'], 'io': '屋外', 'res': {'required': False, 'note': '申し込み不要。'}, 'quotes': ['きらめく光に包まれた幻想的な冬のお花見をお楽しみください。', '開催日時2026年11月21日（土曜日）から2026年12月25日（金曜日）16時30分～21時30分', '申し込み不要場所新川さくら館広場住所江戸川区船堀7丁目15番12号', '冬の夜を彩るイルミネーションを、ぜひお楽しみください。', '費用無料問合せ新川さくら館'], 'overall': 'B', 'basis': 'all_ages', 'child': False, 'reason': '冬の夜のイルミネーション。無料・申込不要で、5時間の開催。子ども向けとは明記されていない。', 'axes': {'child_target': ('unknown', '子ども向けとは明記されていない'), 'interactivity': ('B', 'イルミネーションの観賞が中心'), 'age_fit': ('unknown', '対象年齢は明記がない'), 'stay_flexibility': ('A', '16時30分〜21時30分の間、好きな時間に立ち寄れる'), 'burden': ('B', '夜の屋外での開催'), 'cost': ('A', '費用無料'), 'reservation': ('A', '申し込み不要'), 'family_value': ('B', '冬の夜の光を家族で楽しめる')}, 'strengths': ['無料・申込不要で5週間にわたり開催'], 'limitations': ['子ども向けとは明記されていない', '夜の屋外開催'], 'comparison': '総合B：無料・申込不要で気軽に行けるが、子ども向けの内容は明記がない。', 'pf': 'unknown', 'pos': ['official_date_confirmed']}]
RAW = SPECS_RAW
SPECS = []
for _r in RAW:
    _s = dict(_r)
    _s['categories'] = _s.pop('cats'); _s['indoor_outdoor'] = _s.pop('io'); _s['reservation'] = _s.pop('res')
    _s['child_activity'] = _s.pop('child'); _s['price_field'] = _s.pop('pf'); _s['positive'] = _s.pop('pos')
    SPECS.append(_s)
NEW_IDS = [s['id'] for s in SPECS]
SHARDS = {w: f'{w}-events-lead6-20261119.json' for w in ('2026-11-21', '2026-11-28', '2026-12-05', '2026-12-12', '2026-12-19')}
HELD = {'adachi-seibutsuen-hotaru-20261128': '条件は合うが11/28週の画像率が70%を割るため、11/28・29は保留（12/5以降は掲載）', 'edogawa-fuyusakura-20261121': '11/21週の画像の余裕が荒川の工作に使われたため、11/21〜22は保留（12/5以降は掲載）', 'meguro-gohongi-oyako-asobo-20261128': '条件は合うが11/28週の画像率が70%を割るため保留', 'suginami-unesco-tsudoi-20261128': 'キッズコーナーは条件に合うが11/28週の画像率のため保留', 'taito-asakusabashi-kosaku-20261122': '申込不要・無料だが定員8組。11/21週の画像率のため保留', 'adachi-ouka-hakoniwa-20261128': '材料費3,300円・先着10人で申込が必要', 'chiyoda-first-bicycle-20261129': '千代田区在住者のみが対象', 'suginami-nazo-sanpo-20261116': '区内在住・在勤・在学の方が対象', 'suginami-futago-ryuseigun-20261212': '抽選で、申込が12/1までに終了', 'itabashi-shimizu-berezza-20261123': '公式ページに内容が「準備中」'}


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
        run['lead6_addition_20261119'] = {
            'kind': 'individually_verified_official_events_from_lead_triage', 'added_ids': [i[0]['id'] for i in items],
            'held_not_published': sorted(HELD), 'pages_committed_at': 'research/2026-11-19-audit/pages/',
            'base_data_production_sha': BASE, 'global_source_audit_complete': False}
        S.jdump(d / f'{week}-run.json', run)
        for x in m['weekends']:
            if x['sat'] == week:
                x['count'] += n
    m['generated'] = '2026-11-19T16:00:00+09:00'
    S.jdump(d / 'manifest.json', m)
    h = S.jload(d / 'update_history.json')
    h['history'].append({
        'run_id': 'lead6-addition-20261119', 'run_type': 'manual_verified_lead6_addition',
        'status': 'verified_subset_publication', 'as_of_jst': '2026-11-19', 'executed_at': m['generated'],
        'base_data_production_sha': BASE, 'target_weekends': sorted(derived),
        'prior_active_week_records': 469, 'candidate_active_week_records': 476, 'added_weekly_records': 7,
        'new_event_ids': NEW_IDS, 'held_not_published': sorted(HELD),
        'existing_event_records_physically_deleted': 0, 'image_only_updates': 0,
        'source_failures_remain_unverified': True, 'global_source_audit_complete': False,
        'full_23_ward_25_source_audit_complete': False,
        'note': '残りの候補プールとカレンダーの個別ページを精読し、公式個別ページで条件を確認できた3イベント（7週別レコード）のみ追加。条件が合わないものは掲載せず理由を保存。',
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
