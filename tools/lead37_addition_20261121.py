#!/usr/bin/env python3
"""2 weekly records (Jindai Botanical Garden x2, Yoyogi Park) from committed official pages (2026-11-21).

Raw official pages are committed unchanged under research/2026-11-20-thin-wards/pages/. The gate validator re-derives every record and requires exact equality.
"""
import argparse, hashlib, json, pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import suginami_addition_20261118 as S

BASE = '73951929654233560abe8d64fc175cfb323af829'   # data-production after lead36 (768 active week records)
CHECKED = '2026-11-21'
AXES = S.AXES
NOTE_AUDIT = '週別全源照合は未完（ためまっぷ403等）。この4件は多摩各市の公式ページの個別確認に基づく。'
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
    {'id': 'verified-20261121-chofu-jindai-konomi-kusanomi-ten-2026', 'week': '2026-11-21', 'ward': '調布市', 'page': 'jindai_konomi_2026.html',
     'name': '木の実・草の実展（神代植物公園）', 'url': 'https://www.tokyo-park.or.jp/park/jindai/news/2026/11_19_12_6.html', 'date': '2026-11-21', 'end': '2026-12-06',
     'period': '11/19(木)〜12/6(日)（開催中）', 'time': '神代植物公園の開園時間（9:30〜17:00）',
     'venue': '神代植物公園 植物会館展示室（調布市深大寺元町）', 'price': '展示の別料金の記載なし。入園料が必要（大人500円・65歳以上250円・中学生200円、小学生以下無料）',
     'description': 'さまざまな種類のドングリや、珍しい木の実・草の実を展示する、神代植物公園の毎年人気の展示。大人から子どもまで楽しめる内容。',
     'cats': ['展示', '公園・自然'], 'io': '屋内',
     'res': {'required': False, 'note': '予約の記載なし。'},
     'quotes': ['期間：11月19日(木)～12月6日(日)', '場所：植物会館展示室（画像をクリックすると拡大できます）', '大人から子どもまで楽しめる内容となっています。', 'さまざまな種類のドングリや、珍しい木の実・草の実の数々を展示します！'],
     'extra': [{'page': 'jindai_park_top_2026.html', 'url': 'https://www.tokyo-park.or.jp/park/jindai/', 'q': '入園料一般・大人500円（団体：400円）'}, {'page': 'jindai_park_top_2026.html', 'url': 'https://www.tokyo-park.or.jp/park/jindai/', 'q': '開園時間午前9時30分～午後5時'}],
     'overall': 'B', 'basis': 'all_ages', 'child': True,
     'reason': 'ドングリや木の実・草の実を並べた展示で、大人から子どもまで楽しめる。屋内の展示室で見られ、小学生以下は入園料が無料。展示のための別料金の記載はない。',
     'axes': _ax(['B', '大人から子どもまでが対象'], ['C', '展示を見て楽しむ内容が中心'], ['B', '年齢の限定はない'], ['A', '約3週間と長く、開園時間内で好きな時間に行ける'], ['B', '公園内を歩く必要がある'], ['B', '入園料が必要（小学生以下は無料）'], ['A', '予約の記載なし'], ['B', '公園の散策と合わせて、季節の自然を学べる']),
     'strengths': ['小学生以下は入園料が無料', '屋内の展示で、天候に左右されない'], 'limitations': ['展示を見る内容が中心で、体験は少ない', '大人には入園料が必要'],
     'comparison': '総合B：季節の自然を見て学べる展示。小学生以下は無料だが、体験は少ない。',
     'pf': 'pass', 'pos': ['official_date_confirmed']},
    {'id': 'verified-20261205-chofu-jindai-winter-forest-tanken-2026', 'week': '2026-12-05', 'ward': '調布市', 'page': 'jindai_winterforest_20261206.html',
     'name': '「自然」と友達になろう！冬の森たんけん（神代植物公園）', 'url': 'https://www.tokyo-park.or.jp/park/jindai/news/2026/12_6.html', 'date': '2026-12-06', 'end': '2026-12-06',
     'period': '12/6(日)', 'time': '午前の部10:30〜11:40・午後の部13:30〜14:40（各70分）',
     'venue': '神代植物公園 植物会館前集合（調布市深大寺元町）', 'price': '参加費50円（レクリエーション保険料・ひとり）。保護者は入園料が別途必要',
     'description': '神代植物公園の職員（ネイチャーゲームリーダー）といっしょに、目で見て、耳で聞いて、手で触って、においを感じながら冬の森をたんけんする親子向けの体験。対象は5歳以上〜小学4年生（保護者同伴）で、各回親子5組10人ほど。事前申込制・先着順。',
     'cats': ['体験・ワークショップ', '公園・自然'], 'io': '屋外',
     'res': {'required': True, 'note': '事前申込制・先着順。申込フォームから申し込む。小雨決行・雨天中止。'},
     'quotes': ['【実施日】2026年12月6日（日）', '【集合場所】神代植物公園植物会館前', '【対象】5歳以上～小学校4年生（保護者同伴）', '【参加費】50円(レクリエーション保険料)/ひとり', '※保護者は入園料が別途必要です。', '【定員】各回親子5組10人程度（事前申込制・先着順）', '①午前の部10時30分～11時40分（70分）', '②午後の部13時30分～14時40分（70分）'],
     'overall': 'A', 'basis': 'child_program', 'child': True,
     'reason': '5歳から小学4年生の子どもが保護者といっしょに、五感で冬の森を探検する体験。参加費は50円と安い。事前申込制で先着順、各回の定員が少ない。',
     'axes': _ax(['A', '5歳〜小学4年生の子どもと保護者のための体験'], ['A', '見る・聞く・触る・においをかぐ体験型'], ['A', '対象年齢がはっきりしている'], ['B', '午前・午後の2回から選べる（各70分）'], ['B', '屋外で、雨天中止。保護者は入園料が必要'], ['A', '参加費は50円'], ['C', '事前申込制・先着順で、定員が少ない'], ['A', '職員の案内で、子どもが自然に親しめる']),
     'strengths': ['参加費は50円と安い', '5歳〜小学4年生向けで、職員が案内する'], 'limitations': ['事前申込制で、各回の定員が少ない', '雨天中止。保護者は入園料が別に必要'],
     'comparison': '総合A：対象年齢がはっきりした親子向けの自然体験で、参加費も安い。申込と定員の制約がある。',
     'pf': 'pass', 'pos': ['official_date_confirmed']},
    {'id': 'verified-20261205-shibuya-yoyogi-donguri-kosaku-20261206', 'week': '2026-12-05', 'ward': '渋谷区', 'page': 'yoyogi_donguri_20261206.html',
     'name': '日曜日自然教室「どんぐり工作」（代々木公園）', 'url': 'https://www.tokyo-park.or.jp/park/yoyogi/news/2026/12_6_pm.html', 'date': '2026-12-06', 'end': '2026-12-06',
     'period': '12/6(日)', 'time': '13:30〜15:30',
     'venue': '代々木公園 フラワーランド（渋谷区代々木神園町）', 'price': '参加費は無料',
     'description': '代々木公園にあるいろいろな種類のどんぐりや松ぼっくりを使って、自由な発想でオリジナルの置き物を作る工作。申込は不要で、当日自由に参加できる。先着20名で、材料がなくなり次第終了。同じ日に有料のクリスマスリースづくり（要申込）も開く。',
     'cats': ['体験・ワークショップ', '公園・自然'], 'io': '屋外',
     'res': {'required': False, 'note': '申込不要、当日自由参加。先着20名。雨天の場合、どんぐり工作は中止。'},
     'quotes': ['【日時】2026年12月6日（日）13：30～15：30', '【場所】代々木公園内「フラワーランド」', '②日曜日自然教室「どんぐり工作」', '【参加費】無料【定員】先着20名、席に空きがあれば順次ご案内、在庫なくなり次第終了', '【申込み】不要、当日自由参加', '代々木公園にある色々な種類のどんぐりや松ぼっくりを使って工作。'],
     'overall': 'B', 'basis': 'all_ages', 'child': True,
     'reason': 'どんぐりや松ぼっくりで置き物を作る、自由参加の工作教室。参加費は無料で、申込も要らない。先着20名で、雨天は中止。',
     'axes': _ax(['B', '年齢の限定はなく、子どもも参加しやすい工作'], ['A', 'どんぐりや松ぼっくりで自由に作る'], ['B', '年齢の限定はない'], ['B', '13:30〜15:30の間に立ち寄れる'], ['B', '屋外で、雨天は中止。先着20名'], ['A', '参加費は無料'], ['A', '申込不要、当日自由参加'], ['B', '公園で自然の材料を使った工作を楽しめる']),
     'strengths': ['参加費が無料で、申込も要らない', '自然の材料を使って自由に作れる'], 'limitations': ['先着20名で、材料がなくなり次第終了', '雨天の場合は中止'],
     'comparison': '総合B：無料で当日参加できる自然工作。定員が少なく、雨天中止。',
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
SHARDS = {w: f'{w}-events-lead37-20261121.json' for w in ('2026-11-21', '2026-11-28', '2026-12-05', '2026-12-12', '2026-12-19', '2026-12-26')}
HELD = {
    'urayasu-tokyo-disney-resort': '浦安市 東京ディズニーリゾート（ディズニー・クリスマス）：公式サイトがGitHub Actionsから取得できず（https・http・英語ページのいずれもタイムアウト）、本文の引用と入園料の確認ができず保留。入園料は日・券種で変わる。',
    'minato-shiba-zojoji-walk': '港区 芝公園の増上寺ツアー・心を整える時間（11/22・11/29）：大人向けの内容で、子ども向けの記載がなく保留。',
    'tokyo-parks-eight-park-stamp-rally': '8公園を巡るスタンプラリー（10/24〜12/13）：アプリを使うラリーで、会場が複数の区にまたがり、開催場所を1つに決められず保留。',
    'minato-hibiya-sanso-cycling': 'TOKYO散走（12/20）：中学生以上が対象で、子ども向けではなく保留。',
    'tokyo-zoo-association-events': '上野・井の頭・葛西の動物園・水族園：お知らせ一覧（第66回）は取得できたが、イベントの日付・費用が読み取れず保留。',
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
            is_ward = ward.endswith('区')
            row = next((r for r in (cov['wards'] if is_ward else munis) if r['ward'] == ward), None)
            if row is None and is_ward:
                raise SystemExit(f'ward row missing: {ward}')
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
        run['lead37_addition_20261121'] = {
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
        'run_id': 'lead37-addition-20261121', 'run_type': 'manual_verified_lead37_addition',
        'status': 'verified_subset_publication', 'as_of_jst': '2026-11-21', 'executed_at': m['generated'],
        'base_data_production_sha': BASE, 'target_weekends': sorted(derived),
        'prior_active_week_records': 768, 'candidate_active_week_records': 771, 'added_weekly_records': 3,
        'new_event_ids': NEW_IDS, 'held_not_published': sorted(HELD),
        'existing_event_records_physically_deleted': 0, 'image_only_updates': 0,
        'source_failures_remain_unverified': True, 'global_source_audit_complete': False,
        'full_23_ward_25_source_audit_complete': False,
        'note': '都立公園の個別ページ（お知らせ）から、神代植物公園の木の実・草の実展と冬の森たんけん（調布市）、代々木公園のどんぐり工作（渋谷区）を（駒沢ファンタジアは登録済みのため追加せず）公式ページで個別に確認して追加。',
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
