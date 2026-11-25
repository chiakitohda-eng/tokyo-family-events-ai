#!/usr/bin/env python3
"""三角広場のクリスマス (新宿住友ビル三角広場, 2026/11/20-12/13), four weekend records.

User-approved special case (2026-11-19): the official events page gives the period, the free movie screenings
(closure days exist), the paid kids park (age limit) and says the detailed schedule is on the official Instagram.
Hours and closure days are NOT published on any readable page, so records carry no invented time: they point to the
official Instagram. The raw official page is committed unchanged; quotes must occur verbatim in it.
The gate validator re-derives every record from this module and requires exact equality.
"""
import argparse, hashlib, pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import suginami_addition_20261118 as S
from audit_addition_20261119 import _page_text

BASE = 'd32b8dbe18b04e41791cf88801bec57d5ace0aaa'   # data-production after the 2026-11-19 audit addition (444 records)
CHECKED = '2026-11-19'
AXES = S.AXES
S.CHECKED = CHECKED
INSTAGRAM = 'https://www.instagram.com/sankakuhiroba_srd/'
OFFICIAL = 'https://www.sumitomo-sankakuhiroba.jp/event/'
IMAGE = 'https://www.sumitomo-sankakuhiroba.jp/wp-content/uploads/2026/11/TOP★最終稿クリスマスキッズ-e1794967373142.jpg'
PAGE = 'sankaku_events.html'
NOTE = ('開催時間・休演日は公式ページに記載がなく、公式Instagramの参照が案内されている。時間は推測せず、'
        '公式Instagramを参照先として掲載（ユーザー承認の特例）。週別全源照合は未完。')
QUOTES = ['2026/11/20(金)〜12/13(日)',
          'ご家族で楽しめる無料映画上映会*にふわふわ遊具のキッズパーク**',
          'クリスマススペシャルのクラシックライブまで、芝生広場でクリスマスを満喫！',
          '詳細スケジュールは公式インスタグラムをご確認ください。',
          '*休演日有。**有料・年齢制限有']
BASE_DESC = ('ご家族で楽しめる無料映画上映会（休演日あり）、ふわふわ遊具のキッズパーク（有料・年齢制限あり）、'
             'クリスマススペシャルのクラシックライブを芝生広場で開催。開催時間・休演日は公式案内になく、公式Instagram'
             f'（{INSTAGRAM}）で確認してください。')
LATE_DESC = BASE_DESC + '※Instagramの11月カレンダー上の「第一弾」表示は11/20〜11/27。以降の実施日も公式Instagramで確認してください。'
WEEKS = {  # sat -> (sun, id, description)
    '2026-11-21': ('2026-11-22', 'verified-20261121-sankaku-christmas', BASE_DESC),
    '2026-11-28': ('2026-11-29', 'verified-20261128-sankaku-christmas', LATE_DESC),
    '2026-12-05': ('2026-12-06', 'verified-20261205-sankaku-christmas', LATE_DESC),
    '2026-12-12': ('2026-12-13', 'verified-20261212-sankaku-christmas', LATE_DESC),
}
SHARDS = {w: f'{w}-events-sankaku-20261119.json' for w in WEEKS}
NEW_IDS = [v[1] for v in WEEKS.values()]
HELD = {}
AX = {'child_target': ('A', 'ご家族で楽しめる映画上映会とキッズパークがある'),
      'interactivity': ('B', 'ふわふわ遊具のキッズパークで遊べる（有料）。映画上映は鑑賞型'),
      'age_fit': ('unknown', 'キッズパークに年齢制限があるが、具体的な年齢は公式ページにない'),
      'stay_flexibility': ('unknown', '開催時間・休演日は公式ページになく、公式Instagramで確認する必要がある'),
      'burden': ('unknown', '時間・休演日が未確認のため、行く前に公式Instagramで確認が必要'),
      'cost': ('B', '映画上映会は無料。キッズパークは有料（金額は公式ページにない）'),
      'reservation': ('unknown', '申込の要否は公式ページに記載がない'),
      'family_value': ('B', '無料の映画上映とクリスマスの雰囲気を家族で楽しめる')}


def spec(week):
    sun, sid, desc = WEEKS[week]
    return {'id': sid, 'week': week, 'ward': '新宿区', 'page': PAGE, 'name': '三角広場のクリスマス', 'url': OFFICIAL,
            'date': week, 'end': sun, 'period': '11/20(金)〜12/13(日)', 'time': '公式Instagramで確認（映画上映会は休演日あり）',
            'venue': '新宿住友ビル 三角広場（芝生広場）', 'price': '映画上映会は無料／キッズパークは有料', 'image': IMAGE,
            'description': desc, 'categories': ['体験・ワークショップ', '音楽・ステージ'], 'indoor_outdoor': '屋内',
            'reservation': {'required': None, 'note': '申込の要否は公式案内に記載なし。詳細は公式Instagramを確認。'},
            'quotes': QUOTES, 'overall': 'B', 'basis': 'child_program', 'child_activity': True,
            'reason': 'ご家族向けの無料映画上映会とキッズパークがあるクリスマス企画。開催時間・休演日は公式Instagramでの確認が必要。',
            'axes': AX, 'strengths': ['無料の映画上映会とキッズパーク（有料）を家族で楽しめる'],
            'limitations': ['開催時間・休演日が公式ページにない', 'キッズパークは有料・年齢制限あり'],
            'comparison': '総合B：家族向けの内容だが、時間・休演日・年齢制限の詳細は公式Instagramで要確認。',
            'price_field': 'unknown', 'positive': ['official_date_confirmed', 'child_activity_confirmed']}


def evidence(s, pages_dir):
    text = _page_text(pathlib.Path(pages_dir) / s['page'])
    out = []
    for q in s['quotes']:
        if S._strip(q) not in text:
            raise ValueError(f"{s['id']}: quote not found verbatim in the committed official page: {q}")
        out.append({'url': s['url'], 'quote': q, 'checked_at': CHECKED,
                    'sha256': hashlib.sha256(q.encode('utf-8')).hexdigest(),
                    'hash_scope': 'quoted_text_only_not_HTTP_response_hash',
                    'description': '三角広場公式イベントページ（2026-11-19にHTTP200で取得、research/2026-11-19-audit/pages/に不変保存）の本文引用。引用文字列だけのUTF-8 SHA-256。'})
    return out


def derive(pages_dir):
    out = {}
    raw = (pathlib.Path(pages_dir) / PAGE).read_text(encoding='utf-8', errors='ignore')
    if IMAGE not in raw:
        raise ValueError('image URL is not declared on the committed official page')
    for week in WEEKS:
        s = spec(week)
        ev = evidence(s, pages_dir)
        fit = S.family_fit(s, ev)
        event = {'id': s['id'], 'ward': s['ward'], 'name': s['name'], 'url': s['url'], 'official_url': s['url'], 'source': s['url'],
                 'image': s['image'], 'period': s['period'], 'date_start': s['date'], 'date_end': s['end'], 'time': s['time'],
                 'venue': s['venue'], 'price': s['price'], 'description': s['description'], 'categories': s['categories'],
                 'indoor_outdoor': s['indoor_outdoor'], 'reservation': s['reservation'], 'family_fit': fit,
                 'audit': {'checked_on': CHECKED, 'calendar_index_url': None, 'source_claim': 'verified',
                           'global_23_ward_source_audit_complete': False}}
        ver = {'id': s['id'], 'status': 'verified', 'source': s['url'], 'source_kind': 'public_official', 'verified_on': CHECKED,
               'fields': {'name': 'pass', 'date': 'pass', 'venue': 'pass', 'time': 'unknown', 'price': 'unknown',
                          'reservation': 'unknown', 'official_url': 'pass'},
               'corrections': {}, 'note': NOTE, 'evidence': ev}
        dec = {'candidate_id': s['id'], 'name': s['name'], 'ward': s['ward'], 'decision': 'published', 'family_fit': fit,
               'positive_signals': s['positive'], 'negative_signals': ['global_source_audit_pending', 'hours_unconfirmed_instagram_only'],
               'hard_exclusion': None, 'exclusion_type': None, 'primary_reason_code': 'family_value_high',
               'reason_codes': ['family_value_high'], 'reasons': [s['reason']],
               'evidence': [{'url': s['url'], 'basis': '2026-11-19 official events page (HTTP200); hours only on official Instagram; 23 ward completeness not asserted'}],
               'override_reason': ''}
        out[week] = [(event, ver, dec)]
    return out


def build(data_dir, pages_dir):
    d = pathlib.Path(data_dir)
    derived = derive(pages_dir)
    m = S.jload(d / 'manifest.json')
    for week, items in derived.items():
        n = 1
        S.jdump(d / SHARDS[week], [i[0] for i in items])
        w = S.jload(d / f'{week}.json')
        w['event_files'] = list(w['event_files']) + [SHARDS[week]]
        cov = w['coverage']
        cov['candidate_count'] += n
        cov['published_count'] += n
        for row in cov['wards']:
            if row['ward'] == '新宿区':
                row['candidate_count'] += 1
                row['published_count'] += 1
                row['note'] += ' 2026-11-19 公式イベントページ確認済み1件を非破壊追加（時間は公式Instagram参照）。'
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
        run['sankaku_addition_20261119'] = {
            'kind': 'user_approved_official_page_event_with_instagram_reference', 'added_ids': [i[0]['id'] for i in items],
            'held_not_published': sorted(HELD), 'pages_committed_at': 'research/2026-11-19-audit/pages/',
            'instagram_reference': INSTAGRAM, 'hours_published': False,
            'base_data_production_sha': BASE, 'global_source_audit_complete': False}
        S.jdump(d / f'{week}-run.json', run)
        for x in m['weekends']:
            if x['sat'] == week:
                x['count'] += n
    m['generated'] = '2026-11-19T11:00:00+09:00'
    S.jdump(d / 'manifest.json', m)
    h = S.jload(d / 'update_history.json')
    h['history'].append({
        'run_id': 'sankaku-addition-20261119', 'run_type': 'manual_verified_sankaku_addition',
        'status': 'verified_subset_publication', 'as_of_jst': '2026-11-19', 'executed_at': m['generated'],
        'base_data_production_sha': BASE, 'target_weekends': sorted(derived),
        'prior_active_week_records': 444, 'candidate_active_week_records': 448, 'added_weekly_records': 4,
        'new_event_ids': NEW_IDS, 'held_not_published': sorted(HELD),
        'existing_event_records_physically_deleted': 0, 'image_only_updates': 0,
        'source_failures_remain_unverified': True, 'global_source_audit_complete': False,
        'full_23_ward_25_source_audit_complete': False,
        'note': '三角広場のクリスマス（11/20〜12/13）を4週末レコードで追加。開催時間・休演日は公式Instagram参照とし、推測値は載せない（ユーザー承認の特例）。',
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
