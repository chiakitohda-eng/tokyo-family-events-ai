#!/usr/bin/env python3
"""Four individually verified Suginami official events for the 12/19-12/20 weekend.

Source of truth: raw official pages fetched on 2026-11-18 by the read-only workflow
fetch-live-and-suginami-20261118.yml and committed unchanged under
research/2026-11-18-suginami-pages/. Every quote below must occur verbatim in the
committed page text; the quote hash is the SHA-256 of the quote text only (stated in
`hash_scope`), exactly like earlier evidence. The gate validator re-derives all
records from this module and requires exact equality, so data cannot drift.
"""
import argparse
import hashlib
import html
import json
import pathlib
import re
import sys

BASE = '06888a9239c86436c4a499b4268847fa34f4dd2c'   # data-production after the 11/21 rollover
WEEK = '2026-12-19'
SHARD = '2026-12-19-events-suginami-official-20261118.json'
CHECKED = '2026-11-18'
AXES = ('child_target', 'interactivity', 'age_fit', 'stay_flexibility', 'burden', 'cost', 'reservation', 'family_value')
NOTE_AUDIT = '週別全源照合は未完（ためまっぷ403等）。この1件は杉並区公式ページの個別確認に基づく。'

# Events decided NOT to publish (recorded in research/2026-11-18-suginami-dispositions.json).
HELD = {
    'suginami-official-29120': '区内在住限定・抽選・申込は11/23まで。広域の子連れ外出向け掲載には条件が合わない。',
    'suginami-official-29334': '区内在住・在勤・在学限定で、子ども向けの体験企画ではなく玩具修理の相談窓口。',
    'suginami-official-29192': '未就学児不可・参加費3,000円・定員15名の成人向け吟行会。子連れ外出向けではない。',
    'suginami-official-29029': '区内在住/在校の経験者（中高生）限定で申込は11/20まで。一般の子連れ向けではない。',
}

SPECS = [
    {
        'id': 'verified-20261219-suginami-29249', 'page': 's022_event_29249.html',
        'name': '科学で遊ぼう！さいえんす縁日', 'url': 'https://www.city.suginami.tokyo.jp/s022/event/29249.html',
        'date': '2026-12-19', 'period': '12/19', 'time': '12:00〜15:00',
        'venue': '荻窪地域区民センター（杉並区荻窪2-34-20）', 'price': '無料',
        'description': 'ホバークラフト乗車・スライム・紙ひこうき大会・科学読み聞かせなど、科学で遊ぶ縁日。対象は小学生以上で未就学児は保護者同伴。',
        'categories': ['体験・ワークショップ', '親子・地域体験'], 'indoor_outdoor': '屋内',
        'reservation': {'required': False, 'note': '申込不要・当日直接会場へ。モーターカーは限定50台、日時計は当日正午に受講券を配布（定員制）。'},
        'quotes': ['2026年12月19日（土曜日）', '午後0時から午後3時まで', '開催場所 荻窪地域区民センター', '当日直接会場へお越しください。', '小学生以上（未就学児は保護者同伴）'],
        'overall': 'A', 'basis': 'child_program', 'child_activity': True,
        'reason': '小学生以上（未就学児は保護者同伴）が体験して遊ぶ区内の科学縁日。無料・申込不要で、一部の出し物は台数や定員の制限がある。',
        'axes': {
            'child_target': ('A', '対象者は未就学児・小学生・中学生で、子ども向けの科学あそびが中心'),
            'interactivity': ('A', 'ホバークラフト乗車・スライム・紙ひこうき大会など参加型の出し物が中心'),
            'age_fit': ('A', '小学生以上を主対象とし、未就学児も保護者同伴で参加できる'),
            'stay_flexibility': ('unknown', '途中の出入りや滞在時間の自由度は公式案内に明記がない'),
            'burden': ('A', '申込不要で当日直接会場へ行ける。モーターカー（50台）や日時計は定員制'),
            'cost': ('A', '費用は無料'),
            'reservation': ('A', '申込不要・当日直接会場へ'),
            'family_value': ('A', '子どもが科学を体験して遊べる区主催の縁日で、無料で参加できる'),
        },
        'strengths': ['子ども向けの参加型出し物が多く無料・申込不要'], 'limitations': ['モーターカー限定50台など一部は数量・定員の制限', '滞在の自由度は未記載'],
        'comparison': '総合A：子ども向けの参加型体験が中心で、無料・申込不要。制限は一部の出し物に限られる。',
        'status': 'verified', 'price_field': 'pass', 'positive': ['official_date_confirmed', 'child_activity_confirmed'],
    },
    {
        'id': 'verified-20261219-suginami-28963', 'page': 's023_event_28963.html',
        'name': 'クリスマス交流会 アフリカハープ コラ演奏会', 'url': 'https://www.city.suginami.tokyo.jp/s023/event/28963.html',
        'date': '2026-12-19', 'period': '12/19', 'time': '17:30〜19:00（開場17:00）',
        'venue': 'コミュニティふらっと成田（杉並区成田西1-28-18）',
        'price': '大人1,500円／中高生750円／小学生500円／乳幼児無料（サンタ衣装の大人は750円）',
        'description': 'アフリカの伝統楽器「コラ」の演奏会に、ゲームや合唱を加えた地域のクリスマス交流会。子どもから大人まで参加できる。',
        'categories': ['文化・地域イベント', '親子・地域体験'], 'indoor_outdoor': '屋内',
        'reservation': {'required': True, 'note': '電話または施設窓口で申込。12/19まで・申込順・定員45名。'},
        'quotes': ['2026年12月19日（土曜日）', '午後5時30分から午後7時まで', '子どもから大人まで楽しめる交流クリスマス会です。', '中高生750円 小学生500円 乳幼児無料', '2026年12月19日まで 定員 45名'],
        'overall': 'B', 'basis': 'all_ages', 'child_activity': False,
        'reason': '「どなたでも」参加でき乳幼児も無料の地域クリスマス会。演奏鑑賞が中心で、夕方開催・申込必須・定員45名の条件がある。',
        'axes': {
            'child_target': ('B', '対象は「どなたでも」で、子どもから大人まで楽しめる交流会（子ども専用ではない）'),
            'interactivity': ('B', '演奏鑑賞に加えゲームや合唱がある'),
            'age_fit': ('A', '乳幼児は無料、小学生・中高生の料金区分があり子連れ参加を前提とした設定'),
            'stay_flexibility': ('unknown', '途中の出入りの可否は公式案内に明記がない'),
            'burden': ('B', '17:30〜19:00の夕方開催で、電話または窓口での申込が必要'),
            'cost': ('B', '大人1,500円・中高生750円・小学生500円・乳幼児無料'),
            'reservation': ('B', '電話または施設窓口で申込、申込順・定員45名'),
            'family_value': ('B', '異文化の楽器演奏に触れる地域交流会。体験の中心は鑑賞'),
        },
        'strengths': ['乳幼児無料で子連れ参加を想定した料金設定'], 'limitations': ['夕方開催・申込必須・定員45名', '体験の中心は演奏鑑賞'],
        'comparison': '総合B：子連れで参加しやすい料金設定だが、対象は全年齢向けで申込・夕方開催の条件がある。',
        'status': 'verified', 'price_field': 'pass', 'positive': ['official_date_confirmed'],
    },
    {
        'id': 'verified-20261219-suginami-29140', 'page': 's025_event_29140.html',
        'name': '天文講座「ドーム型プラネタリウムで星空体験」', 'url': 'https://www.city.suginami.tokyo.jp/s025/event/29140.html',
        'date': '2026-12-19', 'period': '12/19',
        'time': '4回入替制（各回約45分）：10:00／11:00／13:00／14:00開始',
        'venue': '高井戸地域区民センター体育室（杉並区高井戸東3-7-5）', 'price': '公式案内に金額明記なし（申込前に要確認）',
        'description': '直径5メートルのドーム型プラネタリウムで星空を見上げる体験。4歳以上、未就学児は保護者の付き添いが必要。',
        'categories': ['体験・ワークショップ', '親子・地域体験'], 'indoor_outdoor': '屋内',
        'reservation': {'required': True, 'note': '往復はがきまたは協議会ホームページから12/6必着。各回20名・抽選。1件につき4名まで。'},
        'quotes': ['2026年12月19日（土曜日）', '4歳以上。未就学児は保護者の付き添いが必要です。', '5メートルのドーム型プラネタリウム', '2026年12月6日まで 定員 各20名', '申し込み1件につき、4名まで記入できます。'],
        'overall': 'B', 'basis': 'age_eligible', 'child_activity': False,
        'reason': '4歳以上が参加できるドーム型プラネタリウム体験。各回約45分の入替制・途中退席不可で、往復はがき等の申込と抽選（各回20名）が必要。',
        'axes': {
            'child_target': ('B', '「どなたでも」参加できる講座で、4歳以上が参加対象（子ども専用ではない）'),
            'interactivity': ('B', '星空を観賞する体験型の講座'),
            'age_fit': ('B', '4歳以上。未就学児は保護者の付き添いが必要'),
            'stay_flexibility': ('C', '各回入れ替え制・途中退席不可'),
            'burden': ('B', '体育室での約45分の入替制で、申込と抽選がある'),
            'cost': ('unknown', '費用欄に金額の記載がない'),
            'reservation': ('C', '往復はがきまたはホームページで12/6必着、各回20名の抽選'),
            'family_value': ('B', '子どもが星空を身近に体験できる区民センターの講座'),
        },
        'strengths': ['4歳から参加でき星空を体験できる'], 'limitations': ['抽選・申込必須（12/6必着）', '途中退席不可の入替制で費用は未記載'],
        'comparison': '総合B：4歳から体験できるが、申込・抽選・入替制の制約がある。',
        'status': 'verified', 'price_field': 'unknown', 'positive': ['official_date_confirmed'],
    },
    {
        'id': 'verified-20261220-suginami-29174', 'page': 's116_event_29174.html',
        'name': '【絵本ライブ】親と子でたのしむおはなし会28', 'url': 'https://www.city.suginami.tokyo.jp/s116/event/29174.html',
        'date': '2026-12-20', 'period': '12/20', 'time': '10:30〜11:10（10:20開場）',
        'venue': '杉並区立中央図書館 地下ホール（杉並区荻窪3-40-23）', 'price': '公式案内に金額明記なし（申込前に要確認）',
        'description': '絵本の読み聞かせを楽しみながら、絵本による子育ての方法を紹介する親子向けのおはなし会。乳幼児から参加できる。',
        'categories': ['絵本', '親子・地域体験'], 'indoor_outdoor': '屋内',
        'reservation': {'required': True, 'note': 'Eメールで12/16まで。申込順・20組40名。定員到達で受付終了、キャンセル待ちあり。'},
        'quotes': ['2026年12月20日（日曜日）', '午前10時30分から午前11時10分まで', '子供（乳幼児から）、大人（保護者、教育関係者、絵本に関心のある方）', '絵本の読み聞かせを楽しむとともに、絵本による子育ての方法を紹介します。', '2026年12月16日まで 定員 各回20組40名'],
        'overall': 'A', 'basis': 'child_program', 'child_activity': True,
        'reason': '乳幼児から親子で参加できる図書館の絵本読み聞かせ会。約40分で参加しやすい一方、Eメール申込（12/16まで）と20組の定員がある。',
        'axes': {
            'child_target': ('A', '「親と子でたのしむ」絵本の読み聞かせ会で、対象に乳幼児を明記'),
            'interactivity': ('B', '読み聞かせを聴く形式で、親子で絵本を楽しむ'),
            'age_fit': ('A', '乳幼児から参加できる'),
            'stay_flexibility': ('unknown', '途中の出入りの可否は公式案内に明記がない'),
            'burden': ('A', '約40分と短く、図書館のホールで開催'),
            'cost': ('unknown', '費用欄に金額の記載がない'),
            'reservation': ('B', 'Eメールで12/16まで。申込順・20組40名でキャンセル待ちあり'),
            'family_value': ('A', '乳幼児と保護者が絵本を一緒に楽しめ、子育ての方法も紹介される'),
        },
        'strengths': ['乳幼児から参加でき約40分で参加しやすい'], 'limitations': ['Eメール申込（12/16まで）と20組の定員', '費用は未記載'],
        'comparison': '総合A：乳幼児から親子で参加でき短時間。申込と定員の制約はあるが対象適合性が高い。',
        'status': 'verified', 'price_field': 'unknown', 'positive': ['official_date_confirmed', 'child_activity_confirmed'],
    },
]
NEW_IDS = [s['id'] for s in SPECS]


def page_text(path):
    raw = pathlib.Path(path).read_text(encoding='utf-8', errors='ignore')
    raw = raw[raw.find('<h1'):]
    raw = re.sub(r'<(script|style).*?</\1>', '', raw, flags=re.S)
    raw = re.sub(r'<br\s*/?>|</(p|li|tr|dt|dd|h\d|div|th|td)>', '\n', raw)
    return re.sub(r'\s+', '', html.unescape(re.sub(r'<[^>]+>', '', raw)))


def _strip(s):
    return re.sub(r'\s+', '', s)


def evidence(spec, pages_dir):
    text = page_text(pathlib.Path(pages_dir) / spec['page'])
    out = []
    for quote in spec['quotes']:
        key = _strip(quote).replace('|', '')
        if key not in text.replace('|', ''):
            raise ValueError(f"{spec['id']}: quote not found verbatim in the committed official page: {quote}")
        out.append({'url': spec['url'], 'quote': quote, 'checked_at': CHECKED,
                    'sha256': hashlib.sha256(quote.encode('utf-8')).hexdigest(),
                    'hash_scope': 'quoted_text_only_not_HTTP_response_hash',
                    'description': '杉並区公式ページ（2026-11-18にHTTP200で取得、research/2026-11-18-suginami-pages/に不変保存）の本文引用。引用文字列だけのUTF-8 SHA-256。'})
    return out


def family_fit(spec, ev):
    axes = {k: {'grade': spec['axes'][k][0], 'reason': spec['axes'][k][1]} for k in AXES}
    return {
        'grade': spec['overall'], 'overall': spec['overall'], 'rubric_version': 'family-fit-v2', 'reason': spec['reason'],
        'axes': axes,
        'review': {
            'schema_version': 1, 'method': 'individual_evidence_review', 'reviewed_on': CHECKED,
            'axes_checked': list(AXES), 'audience_basis': spec['basis'], 'child_activity_confirmed': spec['child_activity'],
            'strengths': spec['strengths'], 'limitations': spec['limitations'], 'grade_comparison': spec['comparison'],
            'unsupported_axes': [k for k in AXES if spec['axes'][k][0] == 'unknown'],
            'evidence': ev,
        },
    }


def derive(pages_dir):
    events, verification, decisions = [], [], []
    for s in SPECS:
        ev = evidence(s, pages_dir)
        fit = family_fit(s, ev)
        events.append({
            'id': s['id'], 'ward': '杉並区', 'name': s['name'], 'url': s['url'], 'official_url': s['url'], 'source': s['url'],
            'image': '', 'period': s['period'], 'date_start': s['date'], 'date_end': s['date'], 'time': s['time'],
            'venue': s['venue'], 'price': s['price'], 'description': s['description'], 'categories': s['categories'],
            'indoor_outdoor': s['indoor_outdoor'], 'reservation': s['reservation'], 'family_fit': fit,
            'audit': {'checked_on': CHECKED, 'calendar_index_url': None, 'source_claim': 'verified',
                      'global_23_ward_source_audit_complete': False},
        })
        verification.append({
            'id': s['id'], 'status': 'verified', 'source': s['url'], 'source_kind': 'public_official', 'verified_on': CHECKED,
            'fields': {'name': 'pass', 'date': 'pass', 'venue': 'pass', 'time': 'pass', 'price': s['price_field'],
                       'reservation': 'pass', 'official_url': 'pass'},
            'corrections': {}, 'note': NOTE_AUDIT, 'evidence': ev,
        })
        decisions.append({
            'candidate_id': s['id'], 'name': s['name'], 'ward': '杉並区', 'decision': 'published', 'family_fit': fit,
            'positive_signals': s['positive'], 'negative_signals': ['global_source_audit_pending'],
            'hard_exclusion': None, 'exclusion_type': None, 'primary_reason_code': 'family_value_high',
            'reason_codes': ['family_value_high'], 'reasons': [s['reason']],
            'evidence': [{'url': s['url'], 'basis': '2026-11-18 official individual event page (HTTP200); 23 ward completeness not asserted'}],
            'override_reason': '',
        })
    return events, verification, decisions


def jload(p):
    return json.loads(pathlib.Path(p).read_text(encoding='utf-8'))


def jdump(p, obj):
    pathlib.Path(p).write_text(json.dumps(obj, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def build(data_dir, pages_dir):
    d = pathlib.Path(data_dir)
    events, verification, decisions = derive(pages_dir)
    jdump(d / SHARD, events)
    week = jload(d / f'{WEEK}.json')
    week['event_files'] = list(week['event_files']) + [SHARD]
    cov = week['coverage']
    cov['candidate_count'] += 4
    cov['published_count'] += 4
    for row in cov['wards']:
        if row['ward'] == '杉並区':
            row['candidate_count'] = 4
            row['published_count'] = 4
            row['note'] += ' 杉並区公式の個別ページ確認済み4件を掲載（2026-11-18）。'
    jdump(d / f'{WEEK}.json', week)
    v = jload(d / f'{WEEK}-verification.json')
    v['events'] += verification
    v['summary'] = dict(v['summary'], total=v['summary']['total'] + 4, verified=v['summary']['verified'] + 4)
    jdump(d / f'{WEEK}-verification.json', v)
    dec = jload(d / f'{WEEK}-decisions.json')
    dec['decisions'] += decisions
    dec['summary'] = dict(dec['summary'], candidate_total=dec['summary']['candidate_total'] + 4,
                          published=dec['summary']['published'] + 4)
    jdump(d / f'{WEEK}-decisions.json', dec)
    run = jload(d / f'{WEEK}-run.json')
    run['summary'] = dict(run['summary'], candidates=run['summary']['candidates'] + 4,
                          published=run['summary']['published'] + 4, verified=run['summary']['verified'] + 4)
    run['suginami_addition_20261118'] = {
        'kind': 'four_individually_verified_official_events', 'added_ids': NEW_IDS,
        'held_not_published': sorted(HELD), 'pages_committed_at': 'research/2026-11-18-suginami-pages/',
        'base_data_production_sha': BASE, 'global_source_audit_complete': False,
    }
    jdump(d / f'{WEEK}-run.json', run)
    m = jload(d / 'manifest.json')
    for w in m['weekends']:
        if w['sat'] == WEEK:
            w['count'] += 4
    m['generated'] = '2026-11-18T09:00:00+09:00'
    jdump(d / 'manifest.json', m)
    h = jload(d / 'update_history.json')
    h['history'].append({
        'run_id': 'suginami-december-addition-20261118', 'run_type': 'manual_verified_suginami_december_addition',
        'status': 'verified_subset_publication', 'as_of_jst': '2026-11-18', 'executed_at': m['generated'],
        'base_data_production_sha': BASE, 'target_weekends': [WEEK],
        'prior_active_week_records': 430, 'candidate_active_week_records': 434, 'added_weekly_records': 4,
        'new_event_ids': NEW_IDS, 'held_not_published': sorted(HELD),
        'existing_event_records_physically_deleted': 0, 'image_only_updates': 0,
        'source_failures_remain_unverified': True, 'global_source_audit_complete': False,
        'full_23_ward_25_source_audit_complete': False,
        'note': '杉並区公式の個別ページで日付・会場・対象・申込を確認できた4件のみ追加。条件が合わない4件は掲載せず理由を保存。',
    })
    jdump(d / 'update_history.json', h)


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--data-dir', required=True)
    ap.add_argument('--pages-dir', default='research/2026-11-18-suginami-pages')
    a = ap.parse_args()
    try:
        build(a.data_dir, a.pages_dir)
    except ValueError as exc:
        print('ERROR:', exc, file=sys.stderr)
        sys.exit(1)
