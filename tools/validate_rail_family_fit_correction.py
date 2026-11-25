"""Frozen single-event assessment correction; no event facts or source debt can change."""
import argparse,copy,hashlib,json,subprocess
from pathlib import Path
from collections import Counter
from validate_official_schedule_audit import validate
BASE='033c9e12728f1fca18899b3b47d9a8ca62e3ab48'
SPEC=Path(__file__).resolve().parents[1]/'research/rail_family_fit_review_20261114/review.json'
SPEC_SHA256='eec8829d6cc8e77309671d27debd67f201e0cfd280d93d2bb7a124bac3c7d9ea'
def load_spec():
 raw=SPEC.read_bytes()
 if hashlib.sha256(raw).hexdigest()!=SPEC_SHA256:raise ValueError('reviewed assessment changed')
 s=json.loads(raw)
 if s['base_data_production_sha']!=BASE:raise ValueError('wrong baseline')
 return s

def expected_outputs(old,s,stamp):
 w=s['week'];eid=s['event_id'];out={}
 names=['manifest.json',w+'.json',s['event_file'],w+'-decisions.json',w+'-verification.json',w+'-run.json','update_history.json']
 for n in names:out[n]=copy.deepcopy(old(n))
 for n in ['manifest.json',w+'.json']:out[n]['generated']=stamp
 event=next(e for e in out[s['event_file']] if e['id']==eid)
 if event['family_fit']!=s['before_family_fit']:raise ValueError('old assessment mismatch')
 event['family_fit']=copy.deepcopy(s['after_family_fit'])
 decision=next(r for r in out[w+'-decisions.json']['decisions'] if r['candidate_id']==eid)
 fit=copy.deepcopy(s['after_family_fit']);decision['canonical_family_fit_v2']=copy.deepcopy(fit)
 if out[w+'-decisions.json']['rubric_version']=='family-fit-v1':
  fit['rubric_version']='family-fit-v1';fit['evaluation_rubric_version']='family-fit-v2'
 decision['family_fit']=fit
 decision['reasons'].append(s['reason'])
 decision['evidence'].append({'url':s['evidence']['url'],'basis':s['reason'],'checked_at':s['evidence']['retrieval']['checked_at']})
 for signal in ['child_explicit','hands_on','flexible_visit','learning_value']:
  if signal not in decision['positive_signals']:decision['positive_signals'].append(signal)
 verification=next(r for r in out[w+'-verification.json']['events'] if r['id']==eid)
 verification['verified_on']='2026-11-14'
 verification['assessment_review']={'reviewed_on':'2026-11-14','from':'B','to':'A','reason':s['reason'],'source':s['evidence']['url']}
 verification['evidence'].append({'url':s['evidence']['url'],**{k:s['evidence']['retrieval'][k] for k in ['checked_at','sha256']}})
 out[w+'-run.json']['rail_family_fit_correction_20261114']={'event_id':eid,'old_grade':'B','new_grade':'A','event_facts_changed':False,'source_checks_changed':False,'review':'research/rail_family_fit_review_20261114/review.json'}
 out['update_history.json']['history'].append({'run_id':'rail-family-fit-review-20261114','run_type':'manual_assessment_correction','status':'verified_correction','as_of_jst':'2026-11-14','executed_at':stamp,'base_data_production_sha':BASE,'target_weekends':[w],'changed_event_ids':[eid],'added_weekly_records':0,'removed_weekly_records':0,'changed_existing_records':1,'assessment_only':True,'event_facts_changed':False,'official_evidence_urls':[s['evidence']['url']],'note':'総合評価B→A（星2→3）を公式の子ども向け体験・無料・入退場自由に基づき再評価。日時・会場・料金等の個票事実、他407個票、既存履歴と参照元失敗は不変。年齢適合Bと未記載条件を機械的にAへ引き上げない。'})
 return out

def compare_outputs(actual,expected):
 if actual!=expected:raise ValueError('unreviewed file, event fact, assessment or evidence changed')

def check(base,directory):
 if base!=BASE:raise ValueError('only exact baseline permitted')
 directory=Path(directory);old=lambda n:json.loads(subprocess.check_output(['git','show',BASE+':site/data/'+n]));cur=lambda n:json.loads((directory/n).read_text())
 stamp=cur('manifest.json')['generated']
 if stamp<=old('manifest.json')['generated']:raise ValueError('timestamp must advance')
 expected=expected_outputs(old,load_spec(),stamp)
 changed=subprocess.check_output(['git','diff','--name-only',BASE,'HEAD'],text=True).splitlines()
 if set(changed)!={'site/data/'+n for n in expected}:raise ValueError('wrong changed file set')
 compare_outputs({n:cur(n) for n in expected},expected)
 before=Counter();after=Counter();config=cur('discovery_sources.json')
 for w in old('manifest.json')['weekends']:
  d=w['sat'];before.update(validate(old(d+'-run.json'),old(d+'.json'),old(d+'-decisions.json'),config,()));after.update(validate(cur(d+'-run.json'),cur(d+'.json'),cur(d+'-decisions.json'),config,()))
 if before!=after:raise ValueError('historical source errors changed')
 print('RAIL ASSESSMENT GATE PASS: 408 events retained; only one reviewed family_fit corrected; facts/history/source debt preserved')
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--base-ref',required=True);p.add_argument('--data-dir',default='site/data');a=p.parse_args();check(a.base_ref,a.data_dir)
