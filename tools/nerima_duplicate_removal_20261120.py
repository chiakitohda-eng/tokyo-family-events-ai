#!/usr/bin/env python3
"""Remove 5 duplicate Nerima forest-festival listings (user-approved option A, 2026-11-20).

Each of these events was published twice: once by an earlier forest-schedule shard (kept) and once by a later
individually-verified lead shard (removed from the published list). Every removal is recorded as an auditable
`duplicate` decision (duplicate_of, reasons, official evidence URL); no record is erased from the decision audit."""
import argparse, pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import suginami_addition_20261118 as S

BASE = 'f7e1a6b97f97e26542c204f9dcdb119eae1f24d0'   # data-production after the Nakano image alignment (629 active week records)
RUN_ID = 'nerima-duplicate-removal-20261120'
# week -> shard -> [(removed id, kept id)]
REMOVALS = {
    '2026-11-21': {'2026-11-21-events-lead3-20261119.json': [('verified-20261121-nerima-nomori-ochiba-asobi', 'nerima-forest-20261121-minamitakamatsu')]},
    '2026-11-28': {'2026-11-28-events-lead8-20261119.json': [('verified-20261129-nerima-molkky', 'nerima-forest-20261129-kitappara')]},
    '2026-12-05': {'2026-12-05-events-lead8-20261119.json': [
        ('verified-20261205-nerima-ochiba-matsuri', 'v15-20261205-nerima-mori-leaf'),
        ('verified-20261205-nerima-oshigoto-minamitakamatsu', 'v15-20261205-nerima-mori-takamatsu'),
        ('verified-20261205-nerima-oshigoto-oozekiyama', 'v15-20261205-nerima-mori-otaka')]},
}
REMOVED_IDS = sorted(r for w in REMOVALS.values() for s in w.values() for r, _ in s)
REASON = '練馬区「ねりまの森こどもフェスタ」の同一イベントが既掲載のレコードと二重に掲載されていたため、後から追加した側を重複として取り下げた（日付・会場・企画が一致）。'


def evidence_url(ev):
    for k in ('official_url', 'url', 'source_url', 'source'):
        v = ev.get(k)
        if isinstance(v, str) and v.startswith('http'):
            return v
    raise ValueError('no official url for ' + str(ev.get('id')))


def build(data_dir):
    d = pathlib.Path(data_dir)
    m = S.jload(d / 'manifest.json')
    for week, shards in REMOVALS.items():
        k = sum(len(v) for v in shards.values())
        removed_events = {}
        for sh, pairs in shards.items():
            rows = S.jload(d / sh)
            ids = {r for r, _ in pairs}
            for r in rows:
                if r.get('id') in ids:
                    removed_events[r['id']] = r
            if set(removed_events) < ids:
                raise ValueError('record not found in ' + sh)
            S.jdump(d / sh, [r for r in rows if r.get('id') not in ids])
        w = S.jload(d / f'{week}.json')
        c = w['coverage']
        c['published_count'] -= k
        c['duplicate_removed'] = (c.get('duplicate_removed') or 0) + k
        for row in c['wards']:
            if row['ward'] == '練馬区':
                row['published_count'] -= k
                row['note'] = (row.get('note') or '') + f' 2026-11-20 同一イベントの二重掲載{k}件を重複として取り下げ（決定記録あり）。'
        S.jdump(d / f'{week}.json', w)
        v = S.jload(d / f'{week}-verification.json')
        v['events'] = [e for e in v['events'] if e.get('id') not in removed_events]
        v['summary'] = dict(v['summary'], total=v['summary']['total'] - k, verified=v['summary']['verified'] - k)
        S.jdump(d / f'{week}-verification.json', v)
        dec = S.jload(d / f'{week}-decisions.json')
        kept = {r: kk for pairs in shards.values() for r, kk in pairs}
        for row in dec['decisions']:
            cid = row.get('candidate_id')
            if cid in removed_events:
                ev = removed_events[cid]
                row['decision'] = 'duplicate'
                row['duplicate_of'] = kept[cid]
                row['reasons'] = [REASON]
                row['evidence'] = [{'url': evidence_url(ev), 'kind': 'official_event_page', 'checked_at': '2026-11-20'}]
                row.pop('family_fit', None)
        dec['summary'] = dict(dec['summary'], published=dec['summary']['published'] - k, duplicate=dec['summary'].get('duplicate', 0) + k)
        S.jdump(d / f'{week}-decisions.json', dec)
        run = S.jload(d / f'{week}-run.json')
        run['summary'] = dict(run['summary'], published=run['summary']['published'] - k, verified=run['summary']['verified'] - k)
        S.jdump(d / f'{week}-run.json', run)
        for x in m['weekends']:
            if x['sat'] == week:
                x['count'] -= k
    m['generated'] = '2026-11-20T18:00:00+09:00'
    S.jdump(d / 'manifest.json', m)
    h = S.jload(d / 'update_history.json')
    h['history'].append({
        'run_id': RUN_ID, 'run_type': 'manual_duplicate_removal', 'status': 'duplicate_decisions_recorded', 'as_of_jst': '2026-11-20',
        'executed_at': m['generated'], 'base_data_production_sha': BASE, 'target_weekends': sorted(REMOVALS),
        'prior_active_week_records': 629, 'candidate_active_week_records': 624, 'added_weekly_records': 0,
        'new_event_ids': [], 'duplicate_decisions_recorded': REMOVED_IDS,
        'duplicate_of': {r: kk for w in REMOVALS.values() for s in w.values() for r, kk in s},
        'existing_event_records_physically_deleted': 0, 'global_source_audit_complete': False,
        'note': '練馬区「ねりまの森こどもフェスタ」の二重掲載5件を、決定記録（duplicate・重複元ID・理由・公式URL）付きで公開リストから取り下げた。'})
    S.jdump(d / 'update_history.json', h)


if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('--data-dir', required=True); a = ap.parse_args()
    try: build(a.data_dir)
    except ValueError as e: print('ERROR:', e, file=sys.stderr); sys.exit(1)
