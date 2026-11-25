#!/usr/bin/env python3
"""Six individually verified official events found by reading the 79 unread dated leads (2026-11-19).

Raw official pages are committed unchanged under research/2026-11-19-audit/pages/
(fetched by read-only workflows, HTTP 200). Quotes must occur verbatim in those pages.
The gate validator re-derives every record from this module and requires exact equality.
"""
import argparse, hashlib, json, pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import suginami_addition_20261118 as S

BASE = 'b4154af0d152a613f408fae94f40b4de9b2ed34c'   # data-production after the Sankaku Plaza Christmas addition (448 records)
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


SPECS_RAW = [{'id': 'verified-20261121-meguro-kodomo-ongakusai', 'week': '2026-11-21', 'ward': '目黒区', 'page': 'meguro_ongakusai.html', 'name': '令和8年度めぐろ子ども音楽祭', 'url': 'https://www.city.meguro.tokyo.jp/bunka/event/ongakusai-.html', 'date': '2026-11-21', 'period': '11/21(土)', 'time': '13:00〜16:00（開場12:30・2部制）', 'venue': 'めぐろパーシモンホール 大ホール（目黒区八雲1丁目1番1号）', 'price': '入場無料', 'description': '区立小学校7校7団体の合唱・合奏の発表会。子どもたちの歌声や演奏を聴きに来場できる。入場無料・整理券なし、直接会場へ。', 'cats': ['音楽・ステージ', '地域交流'], 'io': '屋内', 'res': {'required': False, 'note': '入場整理券はなく、直接会場へ。'}, 'quotes': ['令和8年11月21日（土曜日）開場12時30分、開演13時、終演予定16時予定（2部制）', 'めぐろパーシモンホール大ホール（目黒区八雲一丁目1番1号区民キャンパス内）', '区立小学校7校7団体が出演をし、日頃練習を行っている合唱や合奏などの成果を披露します。', 'ぜひ、子どもたちの歌声や演奏を聴きにお越しください！', '入場は無料です。入場整理券はございませんので、直接会場へお越しください。'], 'overall': 'B', 'basis': 'all_ages', 'child': True, 'reason': '小学生の合唱・合奏の発表会。入場無料・整理券なしで直接行ける。鑑賞型で、撮影はご遠慮いただく。', 'axes': {'child_target': ('B', '小学生が出演する発表会で、子どもの歌声や演奏を聴きに来場できる'), 'interactivity': ('B', '主に鑑賞型のステージ'), 'age_fit': ('unknown', '対象年齢は公式案内に明記がない'), 'stay_flexibility': ('unknown', '入退場の扱いは公式案内に明記がない'), 'burden': ('B', '撮影ご遠慮・駐車場に限りがあり、公共交通機関での来場が案内されている'), 'cost': ('A', '入場無料'), 'reservation': ('A', '整理券なし・直接会場へ'), 'family_value': ('B', '子どもの演奏を家族で無料で聴ける')}, 'strengths': ['入場無料・整理券なしで直接行ける子どもの発表会'], 'limitations': ['鑑賞型が中心', '撮影不可'], 'comparison': '総合B：無料で気軽に聴けるが、鑑賞型で体験要素は少ない。', 'pf': 'pass', 'pos': ['official_date_confirmed', 'child_activity_confirmed']}, {'id': 'verified-20261123-edogawa-kasai-super-fes', 'week': '2026-11-21', 'ward': '江戸川区', 'page': 'edogawa_kasai_superfes.html', 'name': 'KASAI Super Fes（共育プラザ葛西の館まつり）', 'url': 'https://www.city.edogawa.tokyo.jp/event/super_fes.html', 'date': '2026-11-23', 'period': '11/23(月・祝)', 'time': '10:30〜15:00', 'venue': '共育プラザ葛西（江戸川区宇喜田町175番地）', 'price': '無料（模擬店等は一部有料・現金のみ）', 'description': '共育プラザ葛西の年に1度の館まつり。ゲームコーナー、キッチンカー、ポニー体験などがある。申込不要。', 'cats': ['体験・ワークショップ', '地域交流'], 'io': '屋内・屋外', 'res': {'required': False, 'note': '申し込み不要。'}, 'quotes': ['2026年11月23日（月曜日）10時30分から15時00分', 'さまざまなゲームコーナーやキッチンカー、ポニー体験など', '申し込み不要場所共育プラザ葛西住所江戸川区宇喜田町175番地', '対象どなたでも参加可費用無料一部、模擬店等は有料現金のみ', '年に1度の共育プラザ葛西の館まつり♪'], 'overall': 'B', 'basis': 'child_program', 'child': True, 'reason': 'ゲームコーナーやポニー体験がある、共育プラザ葛西の館まつり。参加無料（模擬店等は一部有料）・申込不要。', 'axes': {'child_target': ('B', 'どなたでも参加でき、ゲームコーナーやポニー体験など子ども向けの内容がある'), 'interactivity': ('A', 'ゲームコーナーやポニー体験などの参加型'), 'age_fit': ('unknown', '対象年齢は公式案内に明記がない'), 'stay_flexibility': ('A', '10時30分〜15時の間、好きな時間に回れる'), 'burden': ('B', '模擬店は現金のみ。会場は共育プラザ葛西'), 'cost': ('A', '参加無料（一部の模擬店等は有料）'), 'reservation': ('A', '申し込み不要'), 'family_value': ('B', 'ゲームやポニー体験を家族で楽しめる館まつり')}, 'strengths': ['無料・申込不要でゲームやポニー体験'], 'limitations': ['模擬店は現金のみ', '詳細な内容は公式ページにない'], 'comparison': '総合B：参加型で無料・申込不要。内容の詳細は公式ページに少ない。', 'pf': 'pass', 'pos': ['official_date_confirmed', 'child_activity_confirmed']}, {'id': 'verified-20261121-suginami-suginoko-nouen-matsuri', 'week': '2026-11-21', 'ward': '杉並区', 'page': 'suginami_suginoko.html', 'name': 'すぎのこ農園まつり2026', 'url': 'https://www.city.suginami.tokyo.jp/s121/event/28512.html', 'date': '2026-11-21', 'period': '11/21(土)', 'time': '10:00〜12:00', 'venue': '農福連携農園すぎのこ農園（杉並区井草3丁目19番23号）', 'price': None, 'description': '杉並産野菜などのマルシェ、展示、クワ体験やリース作りなどの体験コーナー。なみすけも遊びに来る。どなたでも参加可。', 'cats': ['体験・ワークショップ', '自然・農体験'], 'io': '屋外', 'res': {'required': None, 'note': '申込に関する記載なし。'}, 'quotes': ['開催日2026年11月21日（土曜日）開催時間午前10時から午後0時まで', '対象者どなたでも開催場所農福連携農園すぎのこ農園杉並区井草3丁目19番23号', 'クワ体験やリース作りなどを予定', '当日はなみすけも遊びにきます！', '杉並産野菜、草花等の販売、区内障害者施設の利用者が作ったパン'], 'overall': 'B', 'basis': 'all_ages', 'child': True, 'reason': '農園のまつりで、クワ体験やリース作りなどの体験コーナーがあり、どなたでも参加できる。時間が2時間で、費用・申込は記載がない。', 'axes': {'child_target': ('B', 'どなたでも参加でき、体験コーナーやなみすけが登場する'), 'interactivity': ('A', 'クワ体験やリース作りなどの体験を予定'), 'age_fit': ('unknown', '対象年齢は公式案内に明記がない'), 'stay_flexibility': ('B', '開催は午前の2時間'), 'burden': ('B', '内容は都合により変更になる場合がある'), 'cost': ('unknown', '費用は公式案内に明記がない'), 'reservation': ('unknown', '申込の要否は公式案内に明記がない'), 'family_value': ('B', '農体験と地域のまつりを家族で楽しめる')}, 'strengths': ['クワ体験やリース作りなどの体験コーナー'], 'limitations': ['開催は2時間', '費用・申込の記載がない'], 'comparison': '総合B：体験コーナーがあるが、時間が短く費用・申込の記載がない。', 'pf': 'unknown', 'pos': ['official_date_confirmed', 'child_activity_confirmed']}, {'id': 'verified-20261122-suginami-koukaido-tree-tento', 'week': '2026-11-21', 'ward': '杉並区', 'page': 'suginami_koukaido_tree.html', 'name': '杉並公会堂クリスマスツリー点灯式2026', 'url': 'https://www.city.suginami.tokyo.jp/s030/event/28892.html', 'date': '2026-11-22', 'period': '11/22(日)', 'time': '18:00〜18:40', 'venue': '杉並公会堂 正面特設ステージ（杉並区上荻1丁目23番15号）', 'price': '無料', 'description': 'メタセコイアのイルミネーション点灯と、木管五重奏・パワーコーラスなどのステージ。来場した子どもにプレゼントがある。雨天は大ホールホワイエ。', 'cats': ['音楽・ステージ', '地域交流'], 'io': '屋外', 'res': {'required': False, 'note': '当日直接会場へ。'}, 'quotes': ['杉並公会堂のシンボルであるメタセコイアの木に、イルミネーションを点灯します。', '木管五重奏やパワーコーラスなどのパフォーマンスステージも開催します', '来場したお子さんにはプレゼントを準備しています。', '開催日2026年11月22日（日曜日）開催時間午後6時から午後6時40分まで', '申し込み当日直接会場へお越しください。費用無料'], 'overall': 'B', 'basis': 'all_ages', 'child': True, 'reason': 'イルミネーション点灯とステージを楽しめる。来場した子どもにプレゼントがあり、無料・申込不要。夕方の短時間の催し。', 'axes': {'child_target': ('B', 'どなたでも参加でき、来場した子どもにプレゼントがある'), 'interactivity': ('B', '主に鑑賞型の点灯式とステージ'), 'age_fit': ('unknown', '対象年齢は公式案内に明記がない'), 'stay_flexibility': ('C', '18時〜18時40分の短時間'), 'burden': ('B', '夕方の開催で、雨天は会場が変わる'), 'cost': ('A', '費用無料'), 'reservation': ('A', '当日直接会場へ'), 'family_value': ('B', 'クリスマスの点灯を家族で無料で楽しめる')}, 'strengths': ['無料・申込不要でクリスマスのイルミネーション'], 'limitations': ['夕方の40分間のみ', '鑑賞型'], 'comparison': '総合B：無料・申込不要で気軽に行けるが、開催時間が短く鑑賞型。', 'pf': 'pass', 'pos': ['official_date_confirmed', 'child_activity_confirmed']}, {'id': 'verified-20261121-nerima-minamioizumi-nofesta', 'week': '2026-11-21', 'ward': '練馬区', 'page': 'nerima_minamioizumi_nofesta.html', 'name': '南大泉with農フェスタ2026', 'url': 'https://www.nerimakanko.jp/event/detail.php?event_id=e000003013', 'date': '2026-11-21', 'end': '2026-11-22', 'period': '11/21(土)・11/22(日)', 'time': '10:00〜12:00／13:00〜15:00', 'venue': '南大泉農の風景育成地区内（練馬区南大泉3・4丁目）', 'price': 'クイズラリー等は無料（収穫体験は参加費200円）', 'image': 'https://www.nerimakanko.jp/img_data/e000003013.png', 'description': '農の風景が残る地区を歩いて楽しむ2日間。スマートフォンを使ったクイズラリーや収穫体験、マルシェ、キッチンカー。', 'cats': ['体験・ワークショップ', '自然・農体験'], 'io': '屋外', 'res': {'required': None, 'note': '申込に関する記載なし。詳細はチラシまたはHP。'}, 'quotes': ['スマートフォンを使ったクイズラリーや収穫体験をはじめ、マルシェやキッチンカーなど', '2026年11月21日（土）22日（日）10:00〜12:00／13:00〜15:00', '場所南大泉農の風景育成地区内', '東京都練馬区南大泉３丁目・４丁目', 'クイズラリー等の参加は無料。クイズラリーでスタンプを集めると収穫体験補助券が発行され、参加費２００円で収穫体験に参加できます。'], 'overall': 'B', 'basis': 'child_program', 'child': True, 'reason': 'クイズラリーや収穫体験（200円）がある農のイベント。2日間・各日午前午後の開催で、まちを歩いて楽しむ形式。', 'axes': {'child_target': ('B', 'クイズラリーや収穫体験があり家族で参加しやすい'), 'interactivity': ('A', 'クイズラリー・収穫体験などの参加型'), 'age_fit': ('unknown', '対象年齢は公式案内に明記がない'), 'stay_flexibility': ('B', '午前・午後の2枠で、まちを歩いて回る'), 'burden': ('B', '屋外開催。スマートフォンを使うクイズラリー'), 'cost': ('A', 'クイズラリー等は無料、収穫体験は200円'), 'reservation': ('unknown', '申込の要否は公式案内に明記がない'), 'family_value': ('A', '農体験とマルシェを家族で安く楽しめる')}, 'strengths': ['無料のクイズラリーと200円の収穫体験'], 'limitations': ['屋外開催', '申込の記載がない'], 'comparison': '総合B：体験が安く楽しめるが、申込・対象年齢の記載がない。', 'pf': 'pass', 'pos': ['official_date_confirmed', 'child_activity_confirmed']}, {'id': 'verified-20261121-nerima-nomori-ochiba-asobi', 'week': '2026-11-21', 'ward': '練馬区', 'page': 'nerima_nomori_kodomofesta.html', 'name': 'ねりまの森こどもフェスタ「落ち葉と森の素材あそび」（南高松の森緑地）', 'url': 'https://www.city.nerima.tokyo.jp/kurashi/shigoto/midori/shokai/nerimanomori.html', 'date': '2026-11-21', 'period': '11/21(土)', 'time': '13:30〜15:30', 'venue': '南高松の森緑地（練馬区高松2丁目14番4号）', 'price': None, 'description': 'ねりまの森こどもフェスタの1回。落ち葉プールや森の素材のおもちゃ遊び。主催は南高松もりファンクラブ。イベント参加でオリジナルグッズのプレゼントがある。', 'cats': ['体験・ワークショップ', '公園・自然'], 'io': '屋外', 'res': {'required': None, 'note': '申込に関する記載なし。'}, 'quotes': ['令和8年11月21日（土曜）午後1時30分から午後3時30分まで', '落ち葉と森の素材あそび（落ち葉プール、森の素材のおもちゃ遊び）', '南高松の森緑地（高松2丁目14番4号）南高松もりファンクラブ', 'イベント参加でオリジナルグッズをプレゼントします。'], 'overall': 'B', 'basis': 'child_program', 'child': True, 'reason': 'こども向けのフェスタの1回で、落ち葉プールや森の素材のおもちゃ遊びがある。費用・申込・雨天時の扱いは記載がない。', 'axes': {'child_target': ('A', '「こどもフェスタ」の企画で、落ち葉プールなど子ども向けの遊びがある'), 'interactivity': ('A', '落ち葉プールや森の素材のおもちゃ遊びの参加型'), 'age_fit': ('unknown', '対象年齢は公式案内に明記がない'), 'stay_flexibility': ('B', '開催は2時間'), 'burden': ('B', '屋外の森での開催'), 'cost': ('unknown', '費用は公式案内に明記がない'), 'reservation': ('unknown', '申込の要否は公式案内に明記がない'), 'family_value': ('A', '森で子どもが遊べ、参加でグッズがもらえる')}, 'strengths': ['落ち葉プールなど子ども向けの森あそび', '参加でオリジナルグッズ'], 'limitations': ['開催は2時間', '費用・申込・雨天時の記載がない'], 'comparison': '総合B：子ども向けの内容だが、費用・申込・雨天時の記載がない。', 'pf': 'unknown', 'pos': ['official_date_confirmed', 'child_activity_confirmed']}]
RAW = SPECS_RAW
SPECS = []
for _r in RAW:
    _s = dict(_r)
    _s['categories'] = _s.pop('cats'); _s['indoor_outdoor'] = _s.pop('io'); _s['reservation'] = _s.pop('res')
    _s['child_activity'] = _s.pop('child'); _s['price_field'] = _s.pop('pf'); _s['positive'] = _s.pop('pos')
    SPECS.append(_s)
NEW_IDS = [s['id'] for s in SPECS]
SHARDS = {w: f'{w}-events-lead3-20261119.json' for w in ('2026-11-21',)}
HELD = {'asuka-oyako-challenge-kita-20261129': '原則区内在住・在学の親子が対象。公式ページ未確認（取得できたのは配信サイトのみ）', 'meguro-ajimi-club-20261121': '目黒区在住・在学の小学生限定の申込制', 'nerima-nomori-moruk-20261129': '11/28週の画像率が70%を割るため保留（画像宣言なし）。公式ページの内容は確認済み', 'toshima-kumin-hiroba-fes-20261121': '子ども向けの内容が公式ページから確認できない', 'suginami-cesion-xmas-family-concert-20261213': 'チケット制で募集終了'}


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
        run['lead3_addition_20261119'] = {
            'kind': 'individually_verified_official_events_from_lead_triage', 'added_ids': [i[0]['id'] for i in items],
            'held_not_published': sorted(HELD), 'pages_committed_at': 'research/2026-11-19-audit/pages/',
            'base_data_production_sha': BASE, 'global_source_audit_complete': False}
        S.jdump(d / f'{week}-run.json', run)
        for x in m['weekends']:
            if x['sat'] == week:
                x['count'] += n
    m['generated'] = '2026-11-19T12:00:00+09:00'
    S.jdump(d / 'manifest.json', m)
    h = S.jload(d / 'update_history.json')
    h['history'].append({
        'run_id': 'lead3-addition-20261119', 'run_type': 'manual_verified_lead3_addition',
        'status': 'verified_subset_publication', 'as_of_jst': '2026-11-19', 'executed_at': m['generated'],
        'base_data_production_sha': BASE, 'target_weekends': sorted(derived),
        'prior_active_week_records': 448, 'candidate_active_week_records': 454, 'added_weekly_records': 6,
        'new_event_ids': NEW_IDS, 'held_not_published': sorted(HELD),
        'existing_event_records_physically_deleted': 0, 'image_only_updates': 0,
        'source_failures_remain_unverified': True, 'global_source_audit_complete': False,
        'full_23_ward_25_source_audit_complete': False,
        'note': '未読の日付つき候補79件のうち、公式個別ページで条件を確認できた6件のみ追加。条件が合わないものは掲載せず理由を保存。',
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
