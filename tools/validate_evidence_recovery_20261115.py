"""Frozen manual evidence recovery for staging review; preserve all 598 old event facts and source errors."""
import argparse
from collections import Counter
import copy
import hashlib
import json
from pathlib import Path
import subprocess
from validate_official_schedule_audit import validate

BASE = '847e388e65b99e38a0f108ecc96009778b3fdcd2'
SPEC = Path(__file__).resolve().parents[1] / 'research/evidence_recovery_20261115/publishable.json'
SPEC_SHA256 = '573adaaa6b2c8a393409cea03dcfd71d018bd64105416dc184111f981d977256'
COUNTS = {'2026-11-21': 3, '2026-11-28': 1}
WEEKS = tuple(COUNTS)
KEY = 'evidence_recovery_20261115'


def load_spec():
    raw = SPEC.read_bytes()
    if hashlib.sha256(raw).hexdigest() != SPEC_SHA256:
        raise ValueError('frozen reviewed facts changed')
    spec = json.loads(raw)
    rows = spec['records']
    if spec['base_data_production_sha'] != BASE or Counter(r['week'] for r in rows) != Counter(COUNTS):
        raise ValueError('wrong frozen review batch')
    if len(spec['assessment_reviews']) != 6:
        raise ValueError('wrong assessment scope')
    return spec


def expected_additions(read_old, rows, stamp):
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
        shard = week + '-events-evidence-recovery-20261115.json'
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
                    'reviewed_on':'2026-11-15','source_failures_remain_unverified':True,
                    'old_events_changed':0,'old_events_removed':0,'whole_source_parity_complete':False,'fixed_851_adjudication_complete':True}
        outputs[week + '-run.json'] = run
    history = copy.deepcopy(read_old('update_history.json'))
    history['history'].append({'run_id':'evidence-recovery-20261115','run_type':'manual_official_add_only',
        'status':'verified_subset','as_of_jst':'2026-11-15','executed_at':stamp,
        'base_data_production_sha':BASE,'target_weekends':list(WEEKS),'added_weekly_records':len(rows),
        'new_event_ids':ids,'removed_weekly_records':0,'changed_existing_records':0,
        'source_failures_remain_unverified':True,'content_review_complete':False,'fixed_851_adjudication_complete':True,'unreviewed_candidates':0,
        'official_evidence_urls':sorted({r['event']['official_url'] for r in rows}),
        'note':'公式代替根拠で3企画・週別4件を追加、既存6件の8軸を再確認（総合A/B変更なし）。既存598件の開催事実・過去履歴・取得失敗は保持。手動変更はユーザーのステージング確認後だけ本番反映する。'})
    outputs['update_history.json'] = history
    return outputs


def expected_outputs(old, spec, stamp):
    out = expected_additions(old, spec['records'], stamp)
    rows = spec['assessment_reviews']
    weeks = sorted({r['week'] for r in rows})
    def doc(n):
        if n not in out:
            out[n] = copy.deepcopy(old(n))
        return out[n]
    for r in rows:
        w, eid = r['week'], r['id']
        e = next(e for e in doc(r['event_file']) if e['id'] == eid)
        if e['family_fit'] != r['before_family_fit']:
            raise ValueError('old assessment mismatch '+eid)
        fit = copy.deepcopy(r['after_family_fit'])
        e['family_fit'] = copy.deepcopy(fit)
        dec = doc(w+'-decisions.json')
        d = next(d for d in dec['decisions'] if d['candidate_id'] == r['decision_candidate_id'])
        if dec['rubric_version'] == 'family-fit-v1':
            d['canonical_family_fit_v2'] = copy.deepcopy(fit)
            fit['rubric_version'] = 'family-fit-v1'
            fit['evaluation_rubric_version'] = 'family-fit-v2'
        d['published_event_id'] = eid
        d['family_fit'] = fit
        d['reasons'].append('2026-11-15公式代替根拠の再確認：'+r['after_family_fit']['reason'])
        d['evidence'].append({'url':r['after_family_fit']['review']['evidence'][0]['url'], 'basis':'8軸の個別根拠・強み・留保点をresearch/evidence_recovery_20261115/publishable.jsonで照合。'})
        if 'individual_evidence_review' not in d.setdefault('positive_signals',[]):
            d['positive_signals'].append('individual_evidence_review')
        v = next(v for v in doc(w+'-verification.json')['events'] if v['id'] == eid)
        v['assessment_review'] = {'reviewed_on':'2026-11-15','from':r['before_family_fit']['overall'],'to':r['after_family_fit']['overall'],'reason':r['after_family_fit']['reason'],'source':r['after_family_fit']['review']['evidence'][0]['url']}
    for w in weeks:
        doc(w+'.json')['generated'] = stamp
        doc(w+'-run.json')[KEY] = {'base_data_production_sha':BASE,'reviewed_ids':[r['id'] for r in rows if r['week']==w],'assessment_only':True,'event_facts_changed':False,'source_checks_changed':False}
    h = out['update_history.json']['history'][-1]
    h.update(run_type='manual_evidence_recovery',target_weekends=sorted(set(WEEKS)|set(weeks)),reviewed_weekly_records=6,reviewed_programs=6,grade_changes=0,changed_existing_records=6,changed_event_ids=[r['id'] for r in rows],event_facts_changed=False)
    return out


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
    print('EVIDENCE RECOVERY GATE PASS: 4 additions, 6 assessments; 598 old event facts/history/source errors preserved')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base-ref',required=True)
    parser.add_argument('--data-dir',default='site/data')
    args = parser.parse_args()
    check(args.base_ref,args.data_dir)
