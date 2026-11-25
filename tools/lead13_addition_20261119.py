#!/usr/bin/env python3
"""5 weekly records (5 events) found by reading the remaining pool pages and calendar detail pages (2026-11-19).

Raw official pages are committed unchanged under research/2026-11-19-audit/pages/
(fetched by read-only workflows, HTTP 200). Quotes must occur verbatim in those pages.
The gate validator re-derives every record from this module and requires exact equality.
"""
import argparse, hashlib, json, pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import suginami_addition_20261118 as S

BASE = 'a871cce168c683fb37eb07d898b8c5f481f019ad'   # data-production after the lead13 addition (547 records)
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


SPECS_RAW = [{'id': 'verified-20261128-ota-takahata-undo-asobi', 'week': '2026-11-28', 'ward': '大田区', 'page': 'ota_takahata_1309.pdf.txt', 'name': '高畑児童館 子育て講座「乳幼親子で一緒に楽しく！～社会性を育む運動遊び～」', 'url': 'https://www.city.ota.tokyo.jp/event/jidoukan/takahatajidoukan_1309.files/134.pdf', 'date': '2026-11-28', 'period': '11/28(土)', 'time': '1部10:00〜10:45／2部11:00〜11:45', 'venue': '高畑児童館（大田区西六郷）', 'price': '参加費の記載なし', 'description': '運動教室の講師と一緒に、乳幼児と保護者が体を動かして遊ぶ子育て講座。1部は5か月〜1歳未満、2部は1歳以上の未就学児が対象。', 'cats': ['親子', '体験・ワークショップ'], 'io': '屋内', 'res': {'required': True, 'note': '11/2から来館、11/9から電話で申込。1部15組・2部12組まで。'}, 'quotes': ['大田区立高畑児童館11月のおしらせ（乳幼児向け）', '高畑児童館子育て講座「乳幼親子で一緒に楽しく！～社会性を育む運動遊び～」', '日時：定員11月28日(土)1部10:00～10:45(対象概ね5か月から1歳未満)15組まで2部11:00～11:45', '申込制：11月２日(月)～来館にて申込み開始'], 'overall': 'B', 'basis': 'child_program', 'child': True, 'reason': '運動教室の講師と一緒に、乳幼児と保護者が体を動かして遊ぶ子育て講座。参加費の記載なし。事前の申込が必要。', 'axes': {'child_target': ['A', '乳幼児と保護者が対象'], 'interactivity': ['A', '講師と一緒に運動遊びをする'], 'age_fit': ['A', '5か月〜1歳未満と1歳以上で部を分けている'], 'stay_flexibility': ['B', '1部10:00〜10:45／2部11:00〜11:45'], 'burden': ['C', '申込制で、1部15組・2部12組まで'], 'cost': ['unknown', '参加費の記載がない'], 'reservation': ['C', '11/2から来館、11/9から電話で申込'], 'family_value': ['B', '親子で体を動かして交流できる']}, 'strengths': ['年齢別の2部制', '講師つき'], 'limitations': ['申込制で少人数', '参加費の記載なし'], 'comparison': '総合B：11/28(土)の高畑児童館で1部10:00〜10:45／2部11:00〜11:45の開催。参加費の記載なし。申込が必要で、定員がある。', 'extra': [], 'pf': 'unknown', 'pos': ['official_date_confirmed', 'child_activity_confirmed']}, {'id': 'verified-20261128-ota-minamimagome3-undo-asobi', 'week': '2026-11-28', 'ward': '大田区', 'page': 'ota_minamimagome3_1309.pdf.txt', 'name': '南馬込三丁目児童館 子育て講座「親子で運動遊び～育児中の心とからだをケア～」', 'url': 'https://www.city.ota.tokyo.jp/event/jidoukan/minamimagome3tyoume_jidou_1309.files/110.pdf', 'date': '2026-11-28', 'period': '11/28(土)', 'time': '①10:00〜10:40／②11:00〜11:40', 'venue': '南馬込三丁目児童館（遊戯室）', 'price': '参加費の記載なし', 'description': '親子で体を動かして、触れ合い方や遊び方を学ぶ子育て講座。①は8か月〜2歳、②は2歳〜6歳が対象。', 'cats': ['親子', '体験・ワークショップ'], 'io': '屋内', 'res': {'required': True, 'note': '申込み受付中。各回10組（2部制）。'}, 'quotes': ['南馬込三丁目児童館開館時間／月～土午前9時～午後5時', '25日(水)計測会28日(土)子育て講座もうしこみ', '親子で運動遊び◆場所遊戯室◆場所学童保育室'], 'overall': 'B', 'basis': 'child_program', 'child': True, 'reason': '親子で体を動かして、触れ合い方や遊び方を学ぶ子育て講座。参加費の記載なし。事前の申込が必要。', 'axes': {'child_target': ['A', '乳幼児と保護者が対象'], 'interactivity': ['A', '親子で運動遊びをする'], 'age_fit': ['A', '8か月〜2歳と2歳〜6歳で部を分けている'], 'stay_flexibility': ['B', '①10:00〜10:40／②11:00〜11:40'], 'burden': ['C', '申込制で、各回10組'], 'cost': ['unknown', '参加費の記載がない'], 'reservation': ['C', '申込み受付中（方法は児童館へ）'], 'family_value': ['B', '親子で体を動かして交流できる']}, 'strengths': ['年齢別の2部制'], 'limitations': ['各回10組と少人数', '参加費の記載なし'], 'comparison': '総合B：11/28(土)の南馬込三丁目児童館で①10:00〜10:40／②11:00〜11:40の開催。参加費の記載なし。申込が必要で、定員がある。', 'extra': [{'page': 'ota_minamimagome3_1309.pdf.plain.txt', 'url': 'https://www.city.ota.tokyo.jp/event/jidoukan/minamimagome3tyoume_jidou_1309.files/110.pdf', 'q': '①10:00～10:40（8か月～2歳）②11:00～11:40（2歳～6歳）'}, {'page': 'ota_minamimagome3_1309.pdf.plain.txt', 'url': 'https://www.city.ota.tokyo.jp/event/jidoukan/minamimagome3tyoume_jidou_1309.files/110.pdf', 'q': '乳幼児ファミリー各回10組（2部制）※申込み受付中'}], 'pf': 'unknown', 'pos': ['official_date_confirmed', 'child_activity_confirmed']}, {'id': 'verified-20261121-ota-ikegami-densha-asobo', 'week': '2026-11-21', 'ward': '大田区', 'page': 'ota_ikegami_1310.pdf.txt', 'name': '池上児童館 電車で遊ぼう', 'url': 'https://www.city.ota.tokyo.jp/event/jidoukan/ikegamijidoukan_1310.files/114.pdf', 'date': '2026-11-21', 'period': '11/21(土)', 'time': '10:30〜11:30', 'venue': '池上児童館（遊戯室）', 'price': '参加費の記載なし', 'description': 'たくさんの電車のおもちゃで遊べる、乳幼児ファミリー向けの遊び場。', 'cats': ['親子', '子ども'], 'io': '屋内', 'res': {'required': False, 'note': '申込の案内はない。'}, 'quotes': ['大田区池上5-9-9電話・ＦＡＸ/03-3751-6603', '電車で遊ぼう(遊戯室)木曜日9:00～11:3021日土曜日10:30～11:30', 'たくさんの電車のおもちゃで遊べます☆'], 'overall': 'B', 'basis': 'child_program', 'child': True, 'reason': 'たくさんの電車のおもちゃで遊べる、乳幼児ファミリー向けの遊び場。参加費の記載なし。申込の案内はなく、当日参加できる。', 'axes': {'child_target': ['A', '乳幼児ファミリーが対象'], 'interactivity': ['A', '電車のおもちゃで自由に遊ぶ'], 'age_fit': ['A', '乳幼児ファミリーと明記'], 'stay_flexibility': ['B', '10:30〜11:30'], 'burden': ['A', '申込の案内はなく、気軽に行ける'], 'cost': ['unknown', '参加費の記載がない'], 'reservation': ['A', '申込の案内はない'], 'family_value': ['B', '電車好きの子が遊べる']}, 'strengths': ['電車のおもちゃ', '申込の案内なし'], 'limitations': ['参加費の記載なし'], 'comparison': '総合B：11/21(土)の池上児童館で10:30〜11:30の開催。参加費の記載なし。申込不要で気軽に参加できる。', 'extra': [], 'pf': 'unknown', 'pos': ['official_date_confirmed', 'child_activity_confirmed']}, {'id': 'verified-20261121-ota-tokumochi-ohanashi', 'week': '2026-11-21', 'ward': '大田区', 'page': 'ota_tokumochi_1309.pdf.txt', 'name': '徳持児童館 ファミリータイム「おはなし会」', 'url': 'https://www.city.ota.tokyo.jp/event/jidoukan/tokumoti_1309.files/115.pdf', 'date': '2026-11-21', 'period': '11/21(土)', 'time': '11:00〜11:30', 'venue': '徳持児童館', 'price': '参加費の記載なし', 'description': 'ボランティアによる読み聞かせを楽しむ、どなたでも参加できるおはなし会。', 'cats': ['絵本', '親子'], 'io': '屋内', 'res': {'required': True, 'note': '11/2から来館で申込。定員15組程度。'}, 'quotes': ['大田区池上8-13-4徳持児童館電話・ＦＡＸ/03-3751-9914', 'ファミリータイム「おはなし会」', '21日(土)11：00～11：30', '11/2（月）から来館にて申込み受付定員15組程度ボランティアによる読み聞かせ'], 'overall': 'B', 'basis': 'child_program', 'child': True, 'reason': 'ボランティアによる読み聞かせを楽しむ、どなたでも参加できるおはなし会。参加費の記載なし。事前の申込が必要。', 'axes': {'child_target': ['A', '乳幼児ファミリーが参加できる'], 'interactivity': ['A', '読み聞かせを聞く'], 'age_fit': ['unknown', '対象年齢の目安は明記がない'], 'stay_flexibility': ['B', '11:00〜11:30'], 'burden': ['B', '定員15組程度で来館申込'], 'cost': ['unknown', '参加費の記載がない'], 'reservation': ['B', '11/2から来館で申込'], 'family_value': ['B', '絵本の時間を親子で楽しめる']}, 'strengths': ['読み聞かせ'], 'limitations': ['定員15組程度', '参加費の記載なし'], 'comparison': '総合B：11/21(土)の徳持児童館で11:00〜11:30の開催。参加費の記載なし。申込が必要で、定員がある。', 'extra': [], 'pf': 'unknown', 'pos': ['official_date_confirmed', 'child_activity_confirmed']}, {'id': 'verified-20261121-ota-minamimagome-family-time', 'week': '2026-11-21', 'ward': '大田区', 'page': 'ota_minamimagome_1310.pdf.txt', 'name': '南馬込児童館 ファミリータイム（土曜日）', 'url': 'https://www.city.ota.tokyo.jp/event/jidoukan/minamimagome_1310.files/109.pdf', 'date': '2026-11-21', 'period': '11/21(土)', 'time': '11:00〜11:20', 'venue': '南馬込児童館', 'price': '参加費の記載なし', 'description': '体操・手遊び・ふれあい遊びなどを楽しむ、乳幼児ファミリー向けの土曜の活動。', 'cats': ['親子', '子ども'], 'io': '屋内', 'res': {'required': False, 'note': '定例行事はいつでもどなたでも参加できる。'}, 'quotes': ['南馬込児童館乳幼児向け１１月号大田区南馬込1-59-21', 'ファミリータイム21日（土曜日）時間：11：00～11：20対象：乳幼児ファミリー', '内容：体操・手遊び・ふれあい遊び等', '定例行事はいつでもどなたでも参加できます！'], 'overall': 'B', 'basis': 'child_program', 'child': True, 'reason': '体操・手遊び・ふれあい遊びなどを楽しむ、乳幼児ファミリー向けの土曜の活動。参加費の記載なし。申込の案内はなく、当日参加できる。', 'axes': {'child_target': ['A', '乳幼児ファミリーが対象'], 'interactivity': ['A', '体操・手遊び・ふれあい遊び'], 'age_fit': ['A', '乳幼児ファミリーと明記'], 'stay_flexibility': ['B', '11:00〜11:20'], 'burden': ['A', '定例行事はいつでも参加できる'], 'cost': ['unknown', '参加費の記載がない'], 'reservation': ['A', '申込の案内はない'], 'family_value': ['B', '土曜に親子で参加できる']}, 'strengths': ['土曜開催', '申込の案内なし'], 'limitations': ['短時間（20分）', '参加費の記載なし'], 'comparison': '総合B：11/21(土)の南馬込児童館で11:00〜11:20の開催。参加費の記載なし。申込不要で気軽に参加できる。', 'extra': [], 'pf': 'unknown', 'pos': ['official_date_confirmed', 'child_activity_confirmed']}]
RAW = SPECS_RAW
SPECS = []
for _r in RAW:
    _s = dict(_r)
    _s['categories'] = _s.pop('cats'); _s['indoor_outdoor'] = _s.pop('io'); _s['reservation'] = _s.pop('res')
    _s['child_activity'] = _s.pop('child'); _s['price_field'] = _s.pop('pf'); _s['positive'] = _s.pop('pos')
    SPECS.append(_s)
NEW_IDS = [s['id'] for s in SPECS]
SHARDS = {w: f'{w}-events-lead13-20261119.json' for w in ('2026-11-21', '2026-11-28', '2026-12-05', '2026-12-12', '2026-12-19')}
HELD = {'ota-jidokan-others': '大田区の児童館の月間PDFのうち、定例の短い活動・回収・計測会・母乳相談会など子ども向け体験として弱いものは掲載対象外', 'shinagawa-koto-event-lists': '品川・江東は取得できた公式一覧に、週末・祝日の日付付きの個別イベントが見つからなかった'}


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
        run['lead13_addition_20261119'] = {
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
        'run_id': 'lead13-addition-20261119', 'run_type': 'manual_verified_lead13_addition',
        'status': 'verified_subset_publication', 'as_of_jst': '2026-11-19', 'executed_at': m['generated'],
        'base_data_production_sha': BASE, 'target_weekends': sorted(derived),
        'prior_active_week_records': 547, 'candidate_active_week_records': 552, 'added_weekly_records': 5,
        'new_event_ids': NEW_IDS, 'held_not_published': sorted(HELD),
        'existing_event_records_physically_deleted': 0, 'image_only_updates': 0,
        'source_failures_remain_unverified': True, 'global_source_audit_complete': False,
        'full_23_ward_25_source_audit_complete': False,
        'note': '大田区の児童館の月間おしらせPDF（原本と本文抽出を保存）で日付と内容を確認できた5件の週別レコードのみ追加。',
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
