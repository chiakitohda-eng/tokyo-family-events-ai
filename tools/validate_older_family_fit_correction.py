"""Exact 2026-11-14 weekly assessment review; all 448 event facts and old source debt preserved."""
import argparse,copy,hashlib,json,subprocess
from pathlib import Path
from collections import Counter
from validate_official_schedule_audit import validate
BASE='9dce04230d9a8a257f8ce6d035f66122250d5d69'
SPEC=Path(__file__).resolve().parents[1]/'research/older_family_fit_review_20261114/review.json'
SPEC_SHA256='dd2b62f94e9cc67d754588b1953f515beca8b705285c1ecb1c4baa04c2a789dc'
SOURCE=SPEC.with_name('source_evidence.json')
SOURCE_SHA256='6093f1b070548871b52ed18adc71ac2ca28cf6bc7c0322e71e828ada8dc82704'
def load_spec():
 raw=SPEC.read_bytes()
 if hashlib.sha256(raw).hexdigest()!=SPEC_SHA256:raise ValueError('individual review changed')
 if hashlib.sha256(SOURCE.read_bytes()).hexdigest()!=SOURCE_SHA256:raise ValueError('reviewed source evidence changed')
 s=json.loads(raw)
 if s['base_data_production_sha']!=BASE or len(s['records'])!=196 or s['program_count']!=116:raise ValueError('wrong reviewed scope')
 return s

def expected_outputs(old,s,stamp):
 out={};rows=s['records'];weeks=sorted({r['week'] for r in rows})
 for n in ['manifest.json','update_history.json']+[r['event_file'] for r in rows]+[w+suffix for w in weeks for suffix in ['.json','-decisions.json','-verification.json','-run.json']]:
  if n not in out:out[n]=copy.deepcopy(old(n))
 out['manifest.json']['generated']=stamp
 changes=[]
 for r in rows:
  w=r['week'];eid=r['id'];event=next(e for e in out[r['event_file']] if e['id']==eid)
  if event['family_fit']!=r['before_family_fit']:raise ValueError('old assessment mismatch '+eid)
  event['family_fit']=copy.deepcopy(r['after_family_fit'])
  d=next(d for d in out[w+'-decisions.json']['decisions'] if d['candidate_id']==r['decision_candidate_id']);fit=copy.deepcopy(r['after_family_fit'])
  if out[w+'-decisions.json']['rubric_version']=='family-fit-v1':
   d['canonical_family_fit_v2']=copy.deepcopy(fit);fit['rubric_version']='family-fit-v1';fit['evaluation_rubric_version']='family-fit-v2'
  d['published_event_id']=eid;d['family_fit']=fit;d['override_reason']=r['override_reason'];d['reasons'].append('2026-11-14週次再評価：'+r['after_family_fit']['reason'])
  d['evidence'].append({'url':r['after_family_fit']['review']['evidence'][0]['url'],'basis':'8軸を個別確認し総合評価の強み・留保点・出典を記録。research/older_family_fit_review_20261114/review.json'})
  for signal in ['individual_evidence_review']:
   if signal not in d.setdefault('positive_signals',[]):d['positive_signals'].append(signal)
  if fit['overall']=='C' and 'conditional_age_fit' not in d.setdefault('negative_signals',[]):d['negative_signals'].append('conditional_age_fit')
  v=next(v for v in out[w+'-verification.json']['events'] if v['id']==eid);v['assessment_review']={'reviewed_on':'2026-11-14','from':r['before_family_fit']['overall'],'to':r['after_family_fit']['overall'],'reason':r['after_family_fit']['reason'],'source':r['after_family_fit']['review']['evidence'][0]['url']}
  changes.append({'week':w,'id':eid,'from':r['before_family_fit']['overall'],'to':r['after_family_fit']['overall']})
 for w in weeks:
  out[w+'.json']['generated']=stamp
  out[w+'-run.json']['older_family_fit_review_20261114']={'base_data_production_sha':BASE,'reviewed_ids':[r['id'] for r in rows if r['week']==w],'assessment_only':True,'event_facts_changed':False,'source_checks_changed':False,'review':'research/older_family_fit_review_20261114/review.json'}
 out['update_history.json']['history'].append({'run_id':'older-family-fit-review-20261114','run_type':'manual_assessment_correction','status':'verified_correction','as_of_jst':'2026-11-14','executed_at':stamp,'base_data_production_sha':BASE,'target_weekends':weeks,'reviewed_weekly_records':196,'reviewed_programs':116,'grade_changes':sum(c['from']!=c['to'] for c in changes),'upgraded_to_A':sum(c['from']=='B' and c['to']=='A' for c in changes),'changed_to_C':sum(c['from']!='C' and c['to']=='C' for c in changes),'changed_event_ids':[r['id'] for r in rows],'added_weekly_records':0,'removed_weekly_records':0,'changed_existing_records':196,'assessment_only':True,'event_facts_changed':False,'source_failures_remain_unverified':True,'note':'既存208個票のうち、ためまっぷ2個票を対象外とし、196個票116企画を本文で8軸再評価。10個票は過去の公式詳細再取得待ちとして据置。日時・会場・料金・予約等の事実、他252個票・更新履歴・取得失敗を保持。'})
 return out

def compare_outputs(actual,expected):
 if actual!=expected:raise ValueError('unreviewed file, event fact, assessment or evidence changed')

def check(base,directory):
 if base!=BASE:raise ValueError('only exact reviewed baseline permitted')
 directory=Path(directory);old=lambda n:json.loads(subprocess.check_output(['git','show',BASE+':site/data/'+n]));cur=lambda n:json.loads((directory/n).read_text());stamp=cur('manifest.json')['generated']
 if stamp<=old('manifest.json')['generated']:raise ValueError('timestamp must advance')
 expected=expected_outputs(old,load_spec(),stamp);changed=subprocess.check_output(['git','diff','--name-only',BASE,'HEAD'],text=True).splitlines()
 if set(changed)!={'site/data/'+n for n in expected}:raise ValueError('wrong changed file set')
 compare_outputs({n:cur(n) for n in expected},expected)
 before=Counter();after=Counter();config=cur('discovery_sources.json')
 for w in old('manifest.json')['weekends']:
  d=w['sat'];before.update(validate(old(d+'-run.json'),old(d+'.json'),old(d+'-decisions.json'),config,()));after.update(validate(cur(d+'-run.json'),cur(d+'.json'),cur(d+'-decisions.json'),config,()))
 if before!=after:raise ValueError('historical source errors changed')
 print('OLDER ASSESSMENT GATE PASS: 196 records individually reviewed; 448 event facts and source debt unchanged')
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--base-ref',required=True);p.add_argument('--data-dir',default='site/data');a=p.parse_args();check(a.base_ref,a.data_dir)
