#!/usr/bin/env python3
"""Seven individually verified official events found by the 2026-11-19 six-week lead audit.

Raw official pages are committed unchanged under research/2026-11-19-audit/pages/
(fetched by read-only workflows, HTTP 200). Quotes must occur verbatim in those pages.
The gate validator re-derives every record from this module and requires exact equality.
"""
import argparse, hashlib, json, pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import suginami_addition_20261118 as S

BASE = '455be3b3979e68bef0af70b5785cbac0edaec8ab'   # data-production after the 2026-11-18 lead-triage addition
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


SPECS_RAW = [{'id': 'verified-20261121-sumida-smile-festival', 'week': '2026-11-21', 'ward': '墨田区', 'page': 'sumida_smile.html', 'name': '令和8年度すみだスマイル・フェスティバル', 'url': 'https://www.city.sumida.lg.jp/kenko_fukushi/syougai/rikai_sokushin/syougaisya-syuukan/smile2026.html', 'date': '2026-11-21', 'period': '11/21(土)', 'time': '10:00〜15:00', 'venue': 'すみだ生涯学習センター（墨田区東向島）', 'price': None, 'description': '障害者週間のフェスティバル。工作・ポチ袋ワークショップ、補助犬ふれあい、ダンス教室、ステージなど。一部は事前申込。', 'cats': ['体験・ワークショップ', '地域交流'], 'io': '屋内', 'res': {'required': None, 'note': 'ワークショップや体験コーナーはどなたでも参加可。コンサート・ダンス教室・ポチ袋などは事前申込。'}, 'quotes': ['■日時：11月21日（土曜日）10時～15時', '■実施場所：すみだ生涯学習センター', 'ワークショップや体験コーナーはどなたでも参加が可能です。', '誰でもコンサート（お子さんから大人まで）', 'かんたん工作ワークショップクリスマスリースのブローチや手作りおもちゃを作ります。', '補助犬（盲導犬、介助犬、聴導犬）とふれあえる！一緒に写真撮影も可'], 'overall': 'B', 'basis': 'all_ages', 'child': True, 'reason': '誰でも参加できるフェスティバルで、工作・補助犬ふれあい・お子さん向けダンス教室などがある。費用の記載はなく、一部は事前申込。', 'axes': {'child_target': ('B', '障害者週間のフェスティバルで、お子さん向けのコーナーがある'), 'interactivity': ('A', '工作ワークショップ・補助犬ふれあい・ダンス教室など参加型が多い'), 'age_fit': ('unknown', '対象年齢は公式案内に明記がない'), 'stay_flexibility': ('A', '10時〜15時で、各コーナーは12時〜15時の間に自由に回れる'), 'burden': ('B', 'コンサート・ダンス教室・ポチ袋は事前申込が必要'), 'cost': ('unknown', '参加費は公式案内に明記がない'), 'reservation': ('B', '一部のみ事前申込。それ以外は当日参加可'), 'family_value': ('B', '工作や補助犬ふれあいを家族で体験できる区の催し')}, 'strengths': ['工作・補助犬ふれあいなど家族で参加できるコーナー'], 'limitations': ['費用が未記載', '一部は事前申込'], 'comparison': '総合B：参加型コーナーは多いが、費用が未記載で一部は事前申込が必要。', 'pf': 'unknown', 'pos': ['official_date_confirmed', 'child_activity_confirmed']}, {'id': 'verified-20261128-suginami-narita-shukakusai', 'week': '2026-11-28', 'ward': '杉並区', 'page': 'suginami_shukakusai.html', 'name': '成田西ふれあい農業公園「収穫祭」', 'url': 'https://www.city.suginami.tokyo.jp/s121/event/29068.html', 'date': '2026-11-28', 'period': '11/28(土)', 'time': '10:30〜12:30', 'venue': '成田西ふれあい農業公園（杉並区成田西3丁目18番9号）', 'price': '無料（けんちん汁・焼きイモは各200円）', 'description': '収穫を感謝する収穫祭。けんちん汁や焼きいもの販売、野菜の即売、くわ体験やワークショップ、なみすけも登場。', 'cats': ['体験・ワークショップ', '自然・農体験'], 'io': '屋外', 'res': {'required': False, 'note': '当日直接会場へ。小学生以下は保護者同伴。'}, 'quotes': ['2026年11月28日（土曜日）開催時間午前10時30分から午後0時30分まで', '成田西ふれあい農業公園杉並区成田西3丁目18番9号', '対象者どなたでも小学生以下は保護者同伴', '当日直接会場へお越しください。費用無料', 'けんちん汁や焼いもの販売、野菜の即売会、くわ体験やワークショップ', 'なみすけもやって来ます！'], 'overall': 'A', 'basis': 'child_program', 'child': True, 'reason': '農業公園の収穫祭で、くわ体験やワークショップがあり、小学生以下は保護者同伴。入場無料・申込不要。', 'axes': {'child_target': ('B', 'どなたでも参加でき、小学生以下は保護者同伴と案内されている'), 'interactivity': ('A', 'くわ体験・ワークショップなど参加型の体験がある'), 'age_fit': ('B', '小学生以下は保護者同伴。年齢の下限は明記がない'), 'stay_flexibility': ('B', '開催は2時間。サツマイモ焼きなどは時間・整理券あり'), 'burden': ('B', '野菜販売は先着・整理券の回がある'), 'cost': ('A', '入場無料（飲食は各200円）'), 'reservation': ('A', '当日直接会場へ（申込不要）'), 'family_value': ('A', '農体験と地域の収穫祭を無料で家族で楽しめる')}, 'strengths': ['無料・申込不要で農体験とワークショップ'], 'limitations': ['開催は2時間', '焼きイモ等は整理券あり'], 'comparison': '総合A：参加型の農体験が無料・申込不要。時間が短く、一部は整理券制。', 'pf': 'pass', 'pos': ['official_date_confirmed', 'child_activity_confirmed']}, {'id': 'verified-20261128-taito-uguisudani-imohori', 'week': '2026-11-28', 'ward': '台東区', 'page': 'taito_uguisudani.html', 'name': '鶯谷公園アーバンファーミング「おいもで お・も・い・で」みんなでお芋掘り', 'url': 'https://www.city.taito.lg.jp/kenchiku/koumin/katsuyou/torikumi.html', 'date': '2026-11-28', 'period': '11/28(土)', 'time': '第一部10:00集合／第二部11:00集合', 'venue': '区立鶯谷公園（台東区根岸1丁目3番17号）', 'price': '無料', 'description': 'ご家族でお芋掘り。サツマイモ・大根・かぶ・ミズナを収穫（持ち帰り可）。サツマイモのつるでリース作りも。申込制（抽選）。', 'cats': ['体験・ワークショップ', '自然・農体験'], 'io': '屋外', 'res': {'required': True, 'note': '申込締切11/20、定員を超えた場合は抽選（結果11/24通知）。家族2〜4人、17歳以下のみの参加不可。'}, 'quotes': ['令和8年11月28日（土曜日）第一部午前10時集合第二部午前11時集合', '区立鶯谷公園台東区根岸1丁目3番17号', 'ご家族で、お芋掘りにご参加しませんか。', 'サツマイモのツルを使ったクリスマスリース作りのワークショップ', '申込定員：各部15組、計30組', '申込締切は11月20日（金曜日）です。'], 'overall': 'B', 'basis': 'child_program', 'child': True, 'reason': '家族で参加するお芋掘りとリース作り。無料だが、申込制（締切11/20・定員超過は抽選）で家族2〜4人の条件がある。', 'axes': {'child_target': ('A', '「ご家族で」お芋掘りに参加する企画で、17歳以下のみの参加は不可'), 'interactivity': ('A', 'お芋掘り・リース作りワークショップなど体験が中心'), 'age_fit': ('B', '家族2〜4人での参加が条件。年齢の目安は明記がない'), 'stay_flexibility': ('B', '第一部・第二部の集合時刻が決まっている'), 'burden': ('C', '申込制で、定員30組・抽選。雨天は29日に延期予定'), 'cost': ('A', '参加費無料'), 'reservation': ('C', '事前申込が必要（締切11/20、抽選）'), 'family_value': ('A', '農体験を無料で家族で楽しめる')}, 'strengths': ['無料で家族向けの農体験', '収穫物のプレゼントあり'], 'limitations': ['事前申込・抽選', '申込締切は11/20', '雨天は翌日延期'], 'comparison': '総合B：内容と費用は良いが、事前申込・抽選で当日参加できない。', 'pf': 'pass', 'pos': ['official_date_confirmed', 'child_activity_confirmed']}, {'id': 'verified-20261128-nerima-hikarigaoka-park-festa', 'week': '2026-11-28', 'ward': '練馬区', 'page': 'nerima_hikarigaoka_festa.html', 'name': '光が丘公園フェスタ', 'url': 'https://www.nerimakanko.jp/event/detail.php?event_id=e000003035', 'date': '2026-11-28', 'end': '2026-11-29', 'period': '11/28(土)・11/29(日)', 'time': '10:00〜16:00', 'venue': '都立光が丘公園 けやき広場（練馬区光が丘4丁目1-1）', 'price': '参加無料', 'image': 'https://www.nerimakanko.jp/img_data/e000003035.jpg', 'description': '落葉やどんぐりを使った遊び・工作、はたらく車大集合、動物とのふれあい、名物のメロンパン。28日・29日で内容が一部異なる。雨天決行。', 'cats': ['体験・ワークショップ', '公園・自然'], 'io': '屋外', 'res': {'required': False, 'note': '申込の記載なし。雨天決行。'}, 'quotes': ['2026年11月28日（土）、11月29日（日）10：00～16：00', '都立光が丘公園けやき広場', '落葉やどんぐりを使った遊びや工作で秋の公園をたのしもう！', 'はたらく車大集合のほか、かわいい動物たちにも会えるよ。', '料金参加無料主催者光が丘公園サービスセンター'], 'overall': 'A', 'basis': 'child_program', 'child': True, 'reason': '落葉やどんぐりの工作、はたらく車、動物とのふれあいがある子ども・家族向けの公園イベント。参加無料・雨天決行で、2日間の開催。', 'axes': {'child_target': ('A', '子ども・家族向けのカテゴリで、工作や遊び、はたらく車、動物がある'), 'interactivity': ('A', '落葉やどんぐりを使った遊びや工作などの体験'), 'age_fit': ('unknown', '対象年齢は公式案内に明記がない'), 'stay_flexibility': ('A', '10時〜16時の2日間で、都合のよい時間に参加できる'), 'burden': ('B', '屋外開催。雨天決行。28日・29日で内容が一部異なる'), 'cost': ('A', '参加無料'), 'reservation': ('A', '申込の記載なし（当日参加できる見込み）'), 'family_value': ('A', '工作・はたらく車・動物を無料で家族で楽しめる')}, 'strengths': ['無料で2日間開催、工作・はたらく車・動物'], 'limitations': ['屋外・雨天決行', '28日と29日で内容が異なる'], 'comparison': '総合A：家族向けの内容が豊富で、無料・2日間開催。屋外のため天候の影響がある。', 'pf': 'pass', 'pos': ['official_date_confirmed', 'child_activity_confirmed']}, {'id': 'verified-20261205-suginami-ochiba-kanshasai', 'week': '2026-12-05', 'ward': '杉並区', 'page': 'suginami_ochiba.html', 'name': '落ち葉感謝祭2026（落ち葉掃き・おたのしみイベント）', 'url': 'https://www.city.suginami.tokyo.jp/s100/event/23008.html', 'date': '2026-12-05', 'period': '12/5(土)', 'time': '9:00〜15:00（会場ごとに異なる）', 'venue': '区内の公園（井草森公園ほか）', 'price': None, 'description': '公園の落ち葉掃きと、どんぐりなどを使った工作・草木のおたのしみイベント。どなたでも参加可、当日直接会場へ。雨天は落ち葉掃き中止。', 'cats': ['体験・ワークショップ', '公園・自然'], 'io': '屋外', 'res': {'required': False, 'note': '当日直接会場へ。軍手・ほうき・ちりとりを持参。'}, 'quotes': ['開催時間午前9時から午後3時まで会場ごとに開催時間が異なります。', '対象者どなたでも開催場所', '内容落ち葉掃き、おたのしみイベント', '当日直接会場へお越しください。', 'どんぐりなどを使った工作、草木', '雨天の場合は「落ち葉掃き」は中止し、井草森公園の「おたのしみイベント」は規模を縮小して実施します。'], 'overall': 'B', 'basis': 'all_ages', 'child': True, 'reason': 'どなたでも参加できる公園の落ち葉掃きと、どんぐり工作などのおたのしみイベント。申込不要だが、会場・時間が会場ごとに異なり、雨天は縮小・中止。', 'axes': {'child_target': ('B', 'どなたでも参加できる。工作などの子ども向けの催しもある'), 'interactivity': ('A', '落ち葉掃きと、どんぐり等を使った工作の体験'), 'age_fit': ('unknown', '対象年齢は公式案内に明記がない'), 'stay_flexibility': ('B', '会場ごとに開催時間が異なる'), 'burden': ('B', '雨天は落ち葉掃き中止・イベントは縮小。持ち物あり'), 'cost': ('unknown', '費用は公式案内に明記がない'), 'reservation': ('A', '当日直接会場へ（申込不要）'), 'family_value': ('B', '公園で自然に触れる体験を家族で楽しめる')}, 'strengths': ['申込不要で公園の体験と工作'], 'limitations': ['会場・時間が会場ごとに異なる', '雨天は縮小・中止'], 'comparison': '総合B：申込不要で体験できるが、会場・時間の確認が必要で雨天の影響がある。', 'pf': 'unknown', 'pos': ['official_date_confirmed']}, {'id': 'verified-20261206-suginami-fureai-festa', 'week': '2026-12-05', 'ward': '杉並区', 'page': 'suginami_fureai_festa.html', 'name': '令和8年度障害者週間事業 ふれあいフェスタ2026（セシオン杉並）', 'url': 'https://www.city.suginami.tokyo.jp/s036/event/23030.html', 'date': '2026-12-06', 'period': '12/6(日)', 'time': '10:00〜15:00', 'venue': 'セシオン杉並（杉並区梅里1丁目22番32号）', 'price': '無料', 'description': '障害者週間のフェスタ。スポレク種目体験、似顔絵・バルーンアート、模擬店、キッチンカー、ダンス・手話・エイサーのステージなど。', 'cats': ['体験・ワークショップ', '地域交流'], 'io': '屋内・屋外', 'res': {'required': False, 'note': '当日直接会場へ。雨天は中庭イベント中止の可能性あり。'}, 'quotes': ['2026年12月6日（日曜日）開催時間午前10時から午後3時まで', 'セシオン杉並杉並区梅里1丁目22番32号', '対象者どなたでも開催場所', 'お子様から大人まで気軽にチャレンジできる内容ばかりで', '似顔絵コーナーバルーンアート', '当日直接会場へお越しください。費用無料'], 'overall': 'B', 'basis': 'all_ages', 'child': True, 'reason': 'どなたでも参加できる無料のフェスタ。スポーツ体験、似顔絵・バルーンアート、模擬店があり、お子様から大人まで楽しめると案内されている。', 'axes': {'child_target': ('B', 'どなたでも参加でき、お子様から大人まで気軽に体験できると案内'), 'interactivity': ('A', 'スポレク種目体験や似顔絵・バルーンアートなど参加できる体験が多い'), 'age_fit': ('B', 'お子様から大人までと案内。細かな年齢条件は明記がない'), 'stay_flexibility': ('A', '10時〜15時の間、好きな時間に回れる'), 'burden': ('B', '雨天は中庭イベント中止の可能性あり。室内履き持参のコーナーがある'), 'cost': ('A', '費用無料（模擬店は購入）'), 'reservation': ('A', '当日直接会場へ（申込不要）'), 'family_value': ('B', '体験と模擬店を家族で無料で回れる区の催し')}, 'strengths': ['無料・申込不要で体験コーナーが多い'], 'limitations': ['子ども専用ではない', '一部は雨天中止の可能性'], 'comparison': '総合B：無料・申込不要で体験が多い。子ども専用ではない。', 'pf': 'pass', 'pos': ['official_date_confirmed', 'child_activity_confirmed']}, {'id': 'verified-20261213-suginami-cesion-christmas', 'week': '2026-12-12', 'ward': '杉並区', 'page': 'suginami_cesion_xmas.html', 'name': 'セシオンクリスマス会（セシオン杉並）', 'url': 'https://www.city.suginami.tokyo.jp/s024/event/29061.html', 'date': '2026-12-13', 'period': '12/13(日)', 'time': '11:00〜15:00', 'venue': 'セシオン杉並 展示室（杉並区梅里1丁目22番32号）', 'price': None, 'description': 'ゴスペルクワイヤの演奏、子どもたちのダンス・チアダンス、人形劇を友達や家族と楽しむクリスマス会。入退場自由・申込不要。', 'cats': ['音楽・ステージ', '地域交流'], 'io': '屋内', 'res': {'required': False, 'note': '入退場自由（事前申し込み不要）。'}, 'quotes': ['2026年12月13日（日曜日）開催時間午前11時から午後3時まで', 'セシオン杉並展示室杉並区梅里1丁目22番32号', 'ゴスペルクワイヤの演奏、子どもたちによるパフォーマンス、人形劇', '入退場自由（事前申し込み不要）', '当日直接会場へお越しください。'], 'overall': 'B', 'basis': 'all_ages', 'child': True, 'reason': 'ゴスペルや子どものダンス、人形劇を楽しむクリスマス会。入退場自由で申込不要。費用の記載はない。', 'axes': {'child_target': ('B', '子どもたちの出演や人形劇があり、家族で楽しめる'), 'interactivity': ('B', '主に鑑賞型のステージ'), 'age_fit': ('unknown', '対象年齢は公式案内に明記がない'), 'stay_flexibility': ('A', '入退場自由で、休憩中も展示室に入れる'), 'burden': ('A', '室内で、申込不要'), 'cost': ('unknown', '費用は公式案内に明記がない'), 'reservation': ('A', '入退場自由（事前申し込み不要）'), 'family_value': ('B', 'クリスマスのステージを家族で気軽に見られる')}, 'strengths': ['入退場自由・申込不要の室内ステージ'], 'limitations': ['鑑賞型が中心', '費用が未記載'], 'comparison': '総合B：気軽に立ち寄れる室内ステージ。体験要素は少ない。', 'pf': 'unknown', 'pos': ['official_date_confirmed']}]
RAW = SPECS_RAW
SPECS = []
for _r in RAW:
    _s = dict(_r)
    _s['categories'] = _s.pop('cats'); _s['indoor_outdoor'] = _s.pop('io'); _s['reservation'] = _s.pop('res')
    _s['child_activity'] = _s.pop('child'); _s['price_field'] = _s.pop('pf'); _s['positive'] = _s.pop('pos')
    SPECS.append(_s)
NEW_IDS = [s['id'] for s in SPECS]
SHARDS = {w: f'{w}-events-audit-20261119.json' for w in ('2026-11-21', '2026-11-28', '2026-12-05', '2026-12-12')}
HELD = {
    'bunkyo-craft-festival-20261121': '区内在住・在勤・在学者限定',
    'suginami-oyako-sports-challenge-20261129': '区内在住・在園の未就学児限定',
    'adachi-hime-fes-20261205': '謎解き・観光周遊型で子ども向けではない',
    'suginami-minor-registration-events': '申込締切済み・居住者限定の杉並区主催講座等',
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
                    'description': f"{spec['ward']}公式ページ（2026-11-19にHTTP200で取得、research/2026-11-19-audit/pages/に不変保存）の本文引用。引用文字列だけのUTF-8 SHA-256。"})
    return out


def derive(pages_dir):
    out = {}
    for s in SPECS:
        ev = evidence(s, pages_dir)
        if s.get('image'):
            _raw = (pathlib.Path(pages_dir) / s['page']).read_text(encoding='utf-8', errors='ignore')
            if s['image'] not in _raw:
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
        run['audit_addition_20261119'] = {
            'kind': 'individually_verified_official_events_from_lead_triage', 'added_ids': [i[0]['id'] for i in items],
            'held_not_published': sorted(HELD), 'pages_committed_at': 'research/2026-11-19-audit/pages/',
            'base_data_production_sha': BASE, 'global_source_audit_complete': False}
        S.jdump(d / f'{week}-run.json', run)
        for x in m['weekends']:
            if x['sat'] == week:
                x['count'] += n
    m['generated'] = '2026-11-19T10:00:00+09:00'
    S.jdump(d / 'manifest.json', m)
    h = S.jload(d / 'update_history.json')
    h['history'].append({
        'run_id': 'audit-addition-20261119', 'run_type': 'manual_verified_audit_addition',
        'status': 'verified_subset_publication', 'as_of_jst': '2026-11-19', 'executed_at': m['generated'],
        'base_data_production_sha': BASE, 'target_weekends': sorted(derived),
        'prior_active_week_records': 437, 'candidate_active_week_records': 444, 'added_weekly_records': 7,
        'new_event_ids': NEW_IDS, 'held_not_published': sorted(HELD),
        'existing_event_records_physically_deleted': 0, 'image_only_updates': 0,
        'source_failures_remain_unverified': True, 'global_source_audit_complete': False,
        'full_23_ward_25_source_audit_complete': False,
        'note': '未確認リンクの仕分けで公式個別ページを確認できた3件のみ追加。条件が合わない4件は掲載せず理由を保存。',
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
