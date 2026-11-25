"""Frozen 2026-11-14 additive release. Preserve every old fact and source-error multiset."""
import argparse
from collections import Counter
import copy
import hashlib
import json
from pathlib import Path
import subprocess
from validate_official_schedule_audit import validate

BASE = 'd05e78f3550ec0f302ab5a3c6550414e7dce5391'
SPEC = Path(__file__).resolve().parents[1] / 'research/all_non_tamemap_review_20261114/publishable.json'
SPEC_SHA256 = '08a1d94a1bef380103d33dbda07b7f6d047dc211e383f05f208516352cfcab5f'
COUNTS = {'2026-11-14': 22, '2026-11-21': 29, '2026-11-28': 24, '2026-12-05': 23, '2026-12-12': 20}
WEEKS = tuple(COUNTS)
KEY = 'all_non_tamemap_review_20261114'


def load_spec():
    raw = SPEC.read_bytes()
    if hashlib.sha256(raw).hexdigest() != SPEC_SHA256:
        raise ValueError('frozen reviewed facts changed')
    spec = json.loads(raw)
    rows = spec['records']
    if spec['base_data_production_sha'] != BASE or Counter(r['week'] for r in rows) != Counter(COUNTS):
        raise ValueError('wrong frozen review batch')
    return rows


def expected_outputs(read_old, rows, stamp):
    manifest = copy.deepcopy(read_old('manifest.json'))
    manifest['generated'] = stamp
    outputs = {'manifest.json':manifest}
    ids = []
    for week in WEEKS:
        batch = [r for r in rows if r['week'] == week]
        if len(batch) != COUNTS[week]:
            raise ValueError('wrong per-week addition count')
        new_ids = [r['event']['id'] for r in batch]
        ids.extend(new_ids)
        shard = week + '-events-all-non-tamemap-20261114.json'
        outputs[shard] = [r['event'] for r in batch]
        next(w for w in manifest['weekends'] if w['sat'] == week)['count'] += len(batch)
        doc = copy.deepcopy(read_old(week + '.json'))
        doc['generated'] = stamp
        doc['event_files'].append(shard)
        for field in ('published_count','candidate_count'):
            doc['coverage'][field] += len(batch)
            for ward, count in Counter(r['event']['ward'] for r in batch).items():
                next(w for w in doc['coverage']['wards'] if w['ward'] == ward)[field] += count
        outputs[week + '.json'] = doc
        ver = copy.deepcopy(read_old(week + '-verification.json'))
        ver['events'].extend(r['verification'] for r in batch)
        for field in ('total','verified'):
            ver['summary'][field] += len(batch)
        outputs[week + '-verification.json'] = ver
        dec = copy.deepcopy(read_old(week + '-decisions.json'))
        for row in batch:
            audit = copy.deepcopy(row['decision'])
            if dec.get('rubric_version') == 'family-fit-v1':
                audit['canonical_family_fit_v2'] = copy.deepcopy(audit['family_fit'])
                audit['family_fit']['rubric_version'] = 'family-fit-v1'
                audit['family_fit']['evaluation_rubric_version'] = 'family-fit-v2'
                audit['compatibility_note'] = 'Historical v1 envelope; canonical_family_fit_v2 and public event preserve the actual v2 evaluation.'
            dec['decisions'].append(audit)
        for field in ('candidate_total','published'):
            dec['summary'][field] += len(batch)
        outputs[week + '-decisions.json'] = dec
        run = copy.deepcopy(read_old(week + '-run.json'))
        for field in ('published','verified'):
            run['summary'][field] += len(batch)
        run[KEY] = {'new_event_ids':new_ids,'base_data_production_sha':BASE,
                    'prompt':{'version':'v1.15','path':'prompts/tokyo_family_events_complete_prompt_v1.15.txt','resolved':True},
                    'reviewed_on':'2026-11-14','source_failures_remain_unverified':True,
                    'old_events_changed':0,'old_events_removed':0,'whole_source_parity_complete':False,'fixed_851_adjudication_complete':True}
        outputs[week + '-run.json'] = run
    history = copy.deepcopy(read_old('update_history.json'))
    history['history'].append({'run_id':'all-non-tamemap-20261114','run_type':'manual_official_add_only',
        'status':'verified_subset','as_of_jst':'2026-11-14','executed_at':stamp,
        'base_data_production_sha':BASE,'target_weekends':list(WEEKS),'added_weekly_records':len(rows),
        'new_event_ids':ids,'removed_weekly_records':0,'changed_existing_records':0,
        'source_failures_remain_unverified':True,'content_review_complete':False,'fixed_851_adjudication_complete':True,'unreviewed_candidates':0,
        'official_evidence_urls':sorted({r['event']['official_url'] for r in rows}),
        'note':'本文照合したためまっぷを除く追加分のみ公開。週をまたぐ企画は各週に掲載し、休館日をまたがない。既存480個票・履歴・取得失敗を保持。固定851候補の判定は完了。取得不能46本文・保留24候補を保持し、全本文確認成功とは主張しない。'})
    outputs['update_history.json'] = history
    return outputs


def compare_outputs(actual, expected):
    if actual != expected:
        raise ValueError('unapproved data, old evidence, or changed paths')


def check(base, directory):
    if base != BASE:
        raise ValueError('only the exact pre-review production baseline is permitted')
    directory = Path(directory)
    old = lambda name:json.loads(subprocess.check_output(['git','show',BASE + ':site/data/' + name]))
    current = lambda name:json.loads((directory/name).read_text())
    stamp = current('manifest.json')['generated']
    if stamp <= old('manifest.json')['generated']:
        raise ValueError('manifest timestamp must advance')
    expected = expected_outputs(old,load_spec(),stamp)
    changed = subprocess.check_output(['git','diff','--name-only',BASE,'HEAD'],text=True).splitlines()
    if set(changed) != {'site/data/' + p for p in expected}:
        raise ValueError('only the exact reviewed data files may change')
    compare_outputs({p:current(p) for p in expected},expected)
    before,after = Counter(),Counter()
    config = current('discovery_sources.json')
    for w in old('manifest.json')['weekends']:
        d = w['sat']
        before.update(validate(old(d+'-run.json'),old(d+'.json'),old(d+'-decisions.json'),config,()))
        after.update(validate(current(d+'-run.json'),current(d+'.json'),current(d+'-decisions.json'),config,()))
    if before != after:
        raise ValueError('historical source failures changed')
    print('ALL NON TAMEMAP ADDITION GATE PASS: frozen additions; old 480 records/history/source debt unchanged')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base-ref',required=True)
    parser.add_argument('--data-dir',default='site/data')
    args = parser.parse_args()
    check(args.base_ref,args.data_dir)
