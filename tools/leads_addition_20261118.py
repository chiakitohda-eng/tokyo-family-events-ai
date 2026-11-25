#!/usr/bin/env python3
"""Three individually verified official events found by the 2026-11-18 lead triage.

Raw official pages are committed unchanged under research/2026-11-18-leads-triage/pages/
(fetched by read-only workflows, HTTP 200). Quotes must occur verbatim in those pages.
The gate validator re-derives every record from this module and requires exact equality.
"""
import argparse, hashlib, json, pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import suginami_addition_20261118 as S

BASE = 'cae532ddf582dccec739404e8a3a2324d411898a'   # data-production after the Suginami addition
CHECKED = '2026-11-18'
AXES = S.AXES
NOTE_AUDIT = '週別全源照合は未完（ためまっぷ403等）。この1件は各区公式ページの個別確認に基づく。'
S.CHECKED = CHECKED

SPECS = [
    {
        'id': 'verified-20261123-toshima-wanpaku-matsuri', 'week': '2026-11-21', 'ward': '豊島区',
        'page': 'toshima_wanpaku.html',
        'name': '第54回としま子どものつどい「ワンパクまつり」', 'url': 'https://www.city.toshima.lg.jp/231/2609151435.html',
        'date': '2026-11-23', 'period': '11/23(月・祝)', 'time': '10:00〜14:30',
        'venue': '豊島区立総合体育場', 'price': '入場・体験無料（一部有料）',
        'description': 'はしご車体験・白バイ体験・木工教室・世界遺産クイズ・サッカー体験・防災コーナーなどを楽しむ子ども向けまつり。対象は18歳まで。雨天縮小。',
        'categories': ['体験・ワークショップ', '親子・地域体験'], 'indoor_outdoor': '屋内・屋外',
        'reservation': {'required': False, 'note': '当日直接会場へ。コーナーにより整理券・年齢制限あり。'},
        'quotes': ['11月23日(祝)※雨天縮小', '午前10時～午後2時30分', '場所豊島区立総合体育場内容', 'はしご車体験、白バイ体験、木工教室', '対象18歳まで費用入場・体験無料（一部有料）', '申込み方法当日直接会場へ'],
        'overall': 'A', 'basis': 'child_program', 'child_activity': True,
        'reason': '18歳までを対象に、はしご車・白バイ・木工などを体験できる子ども向けまつり。入場無料・申込不要で、コーナーにより整理券や年齢制限がある。',
        'axes': {
            'child_target': ('A', '「としま子どものつどい」で対象は18歳まで。子ども向けの体験が中心'),
            'interactivity': ('A', 'はしご車体験・白バイ体験・木工教室・サッカー体験など参加型が中心'),
            'age_fit': ('B', '18歳までが対象だが、コーナーごとに年齢制限がある'),
            'stay_flexibility': ('A', '10:00〜14:30のあいだ、当日直接会場へ行ける'),
            'burden': ('B', 'コーナーにより整理券が必要。雨天は縮小開催'),
            'cost': ('A', '入場・体験無料（一部有料）'),
            'reservation': ('A', '当日直接会場へ（申込不要）'),
            'family_value': ('A', '消防・警察・防災などの体験を無料で家族で楽しめる区内の子ども向けまつり'),
        },
        'strengths': ['子ども向けの体験が豊富で入場無料・申込不要'], 'limitations': ['コーナーにより整理券・年齢制限', '雨天縮小'],
        'comparison': '総合A：子ども向け体験が中心で無料・申込不要。整理券や年齢制限は一部コーナーに限られる。',
        'price_field': 'pass', 'positive': ['official_date_confirmed', 'child_activity_confirmed'],
    },
    {
        'id': 'verified-20261123-arakawa-film-rocket-stars', 'week': '2026-11-21', 'ward': '荒川区',
        'page': 'arakawa_rocket.html',
        'name': '星空観察会とフィルムロケット工作（荒川自然公園）', 'url': 'https://www.city.arakawa.tokyo.jp/a042/koen/koen/sizenkouen2.html',
        'date': '2026-11-23', 'period': '11/23(月・祝)', 'time': '工作13:00〜16:00／観察会17:30〜19:30',
        'venue': '荒川自然公園野球場', 'price': '工作200円／観察会無料',
        'description': 'フィルムケースでロケットを作って飛ばす工作と、望遠鏡で月や惑星を見る星空観察会。誰でも自由参加で申込不要。',
        'categories': ['体験・ワークショップ', '自然・科学'], 'indoor_outdoor': '屋外',
        'reservation': {'required': False, 'note': '申込不要。工作は定員80名。中止時は荒川自然公園ホームページで案内。'},
        'quotes': ['2026年11月23日（月曜日）13時00分から2026年11月23日（月曜日）19時30分', '場所荒川自然公園野球場内容', 'フィルムケースを使ってロケットを作り、飛ばします。', '誰でも自由参加定員工作：80名', '費用工作：200円観察会：無料', '申し込み不要問合せ荒川自然公園'],
        'overall': 'A', 'basis': 'child_program', 'child_activity': True,
        'reason': 'ロケット工作と望遠鏡での天体観察を体験できる公園イベント。誰でも自由参加・申込不要で、工作は200円・定員80名。',
        'axes': {
            'child_target': ('B', '対象は「誰でも自由参加」。工作・観察は子どもが楽しめる内容'),
            'interactivity': ('A', 'ロケットを作って飛ばす工作と、望遠鏡での観察が体験できる'),
            'age_fit': ('unknown', '対象年齢は公式案内に明記がない'),
            'stay_flexibility': ('A', '工作13:00〜16:00と観察会17:30〜19:30が別枠で、都合のよい時間帯に参加できる'),
            'burden': ('B', '観察会は夕方〜夜間。工作は定員80名で、中止の場合がある'),
            'cost': ('A', '工作200円・観察会無料'),
            'reservation': ('A', '申込不要'),
            'family_value': ('A', '工作と星空観察を低価格で親子で体験できる'),
        },
        'strengths': ['工作と天体観察を低価格・申込不要で体験'], 'limitations': ['工作は定員80名', '観察会は夜間・天候により中止の場合あり', '対象年齢は未記載'],
        'comparison': '総合A：体験内容と費用・申込の条件が良好。対象年齢が未記載で夜間枠がある点が制約。',
        'price_field': 'pass', 'positive': ['official_date_confirmed', 'child_activity_confirmed'],
    },
    {
        'id': 'verified-20261205-nerima-shogaisha-festival', 'week': '2026-12-05', 'ward': '練馬区',
        'page': 'nerima_shogai_festival.html',
        'name': '2026障害者フェスティバル（練馬区・光が丘）', 'url': 'https://www.city.nerima.tokyo.jp/hokenfukushi/shogai/koryu/syogai_festival.html',
        'date': '2026-12-05', 'period': '12/5(土)', 'time': '10:00〜15:00',
        'venue': '光が丘区民センター・光が丘公園ふれあいの径（練馬区光が丘2-9-6）', 'price': None,
        'description': '障害者週間にちなむ区のフェスティバル。24団体の模擬店・工作・ゲームコーナー、10団体のコンサート、作品展示など。',
        'categories': ['文化・地域イベント', '地域交流'], 'indoor_outdoor': '屋内・屋外',
        'reservation': {'required': None, 'note': '申込の記載なし。公式ページで確認。'},
        'quotes': ['令和8年12月5日（土曜）午前10時から午後3時', '光が丘区民センター、光が丘公園ふれあいの径', '24団体が模擬店を出店します。', '子育て支援SANの会018物品販売、工作コーナー', '10団体が歌やダンスなどを披露します。', '富士見台聴こえとことばの教室綿あめ販売、ゲームコーナー'],
        'overall': 'B', 'basis': 'all_ages', 'child_activity': False,
        'reason': '誰でも立ち寄れる地域フェスティバルで、模擬店・工作・ゲーム・コンサートがある。子ども専用ではなく、入場料や申込の記載はない。',
        'axes': {
            'child_target': ('B', '子ども専用ではない地域フェスティバルだが、工作・ゲームコーナーがある'),
            'interactivity': ('B', '工作コーナー・ゲームコーナー・コンサートなど参加・鑑賞が混在'),
            'age_fit': ('unknown', '対象年齢は公式案内に明記がない'),
            'stay_flexibility': ('A', '10:00〜15:00の開催で、模擬店・展示・コンサートを自由に回れる構成'),
            'burden': ('B', '光が丘駅から区民センターに直結。公共交通機関の利用を案内'),
            'cost': ('unknown', '入場料の記載なし。模擬店の購入は有料の見込み'),
            'reservation': ('unknown', '申込の要否は公式案内に明記がない'),
            'family_value': ('B', '模擬店・工作・コンサートを家族で回れる地域イベント'),
        },
        'strengths': ['光が丘駅直結で模擬店・工作・コンサートを一度に楽しめる'], 'limitations': ['子ども専用ではない', '入場料・申込の記載なし'],
        'comparison': '総合B：地域の公式フェスで立ち寄りやすいが、子ども向けの比重は小さく費用等が未記載。',
        'price_field': 'unknown', 'positive': ['official_date_confirmed'],
    },
]
NEW_IDS = [s['id'] for s in SPECS]
SHARDS = {'2026-11-21': '2026-11-21-events-leads-20261118.json', '2026-12-05': '2026-12-05-events-leads-20261118.json'}
HELD = {
    'nakano-dinosaur-diorama-20261121': 'ひとり親家庭限定・受付終了（11/16）',
    'arakawa-hanga-20261123': '小学5年生以上の成人向け講習・受付終了（11/14）',
    'nerima-daikon-20261206': '区内在住限定・受付終了（11/14）',
    'nerima-sibling-dance-20261205': 'きょうだい児と家族限定の申込制（定員10組）',
}


def evidence(spec, pages_dir):
    text = S.page_text(pathlib.Path(pages_dir) / spec['page'])
    out = []
    for q in spec['quotes']:
        if S._strip(q) not in text:
            raise ValueError(f"{spec['id']}: quote not found verbatim in the committed official page: {q}")
        out.append({'url': spec['url'], 'quote': q, 'checked_at': CHECKED,
                    'sha256': hashlib.sha256(q.encode('utf-8')).hexdigest(),
                    'hash_scope': 'quoted_text_only_not_HTTP_response_hash',
                    'description': f"{spec['ward']}公式ページ（2026-11-18にHTTP200で取得、research/2026-11-18-leads-triage/pages/に不変保存）の本文引用。引用文字列だけのUTF-8 SHA-256。"})
    return out


def derive(pages_dir):
    out = {}
    for s in SPECS:
        ev = evidence(s, pages_dir)
        fit = S.family_fit(s, ev)
        event = {
            'id': s['id'], 'ward': s['ward'], 'name': s['name'], 'url': s['url'], 'official_url': s['url'], 'source': s['url'],
            'image': '', 'period': s['period'], 'date_start': s['date'], 'date_end': s['date'], 'time': s['time'],
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
               'evidence': [{'url': s['url'], 'basis': '2026-11-18 official individual event page (HTTP200); 23 ward completeness not asserted'}],
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
                    row['note'] += f' 2026-11-18 公式個別ページ確認済み{k}件を非破壊追加。'
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
        run['leads_addition_20261118'] = {
            'kind': 'individually_verified_official_events_from_lead_triage', 'added_ids': [i[0]['id'] for i in items],
            'held_not_published': sorted(HELD), 'pages_committed_at': 'research/2026-11-18-leads-triage/pages/',
            'base_data_production_sha': BASE, 'global_source_audit_complete': False}
        S.jdump(d / f'{week}-run.json', run)
        for x in m['weekends']:
            if x['sat'] == week:
                x['count'] += n
    m['generated'] = '2026-11-18T10:00:00+09:00'
    S.jdump(d / 'manifest.json', m)
    h = S.jload(d / 'update_history.json')
    h['history'].append({
        'run_id': 'leads-triage-addition-20261118', 'run_type': 'manual_verified_leads_addition',
        'status': 'verified_subset_publication', 'as_of_jst': '2026-11-18', 'executed_at': m['generated'],
        'base_data_production_sha': BASE, 'target_weekends': sorted(derived),
        'prior_active_week_records': 434, 'candidate_active_week_records': 437, 'added_weekly_records': 3,
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
    ap.add_argument('--pages-dir', default='research/2026-11-18-leads-triage/pages')
    a = ap.parse_args()
    try:
        build(a.data_dir, a.pages_dir)
    except ValueError as exc:
        print('ERROR:', exc, file=sys.stderr)
        sys.exit(1)
