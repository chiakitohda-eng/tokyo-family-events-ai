#!/usr/bin/env python3
"""Require individually evidenced explanations for new/changed published assessments.

This is a review gate, not a grade calculator. It never averages axes, promotes
by A-count, or lowers grades just because an unrelated field is unknown.
Unchanged legacy assessments are retained and are not silently reclassified.
"""
import argparse,json,re,sys,unicodedata
from pathlib import Path
from validate_non_regression import CurrentStore,GitStore,load_bundle,read_json
AXES=('child_target','interactivity','age_fit','stay_flexibility','burden','cost','reservation','family_value')
AUDIENCES={'child_program','all_ages','age_eligible','accompaniment_only','performers_are_children','unspecified'}
GENERIC_REASONS={'公式または主催者提供の詳細本文で日付・会場・参加条件を確認。','詳細本文の日時・会場・参加条件を確認。','公式情報を確認。','家族で楽しめる。','総合評価はB。'}

def inspect_assessment(fit):
 errors=[]
 if not isinstance(fit,dict):return ['missing family_fit']
 grade=fit.get('overall')
 if grade not in ('A','B','C','D') or fit.get('grade')!=grade:errors.append('overall and grade must agree')
 reason=str(fit.get('reason') or '').strip()
 if len(reason)<25 or reason in GENERIC_REASONS:errors.append('overall reason must explain this activity, not verification completion')
 axes=fit.get('axes') or {};review=fit.get('review') or {}
 if review.get('schema_version')!=1 or review.get('method')!='individual_evidence_review':errors.append('individual evidence review required; no default grade')
 if set(review.get('axes_checked') or [])!=set(AXES):errors.append('all eight axes must be reviewed')
 if not re.fullmatch(r'\d{4}-\d{2}-\d{2}',str(review.get('reviewed_on') or '')):errors.append('review date required')
 if not review.get('strengths') or not review.get('limitations'):errors.append('specific strengths and limitations required')
 comparison=str(review.get('grade_comparison') or '')
 if len(comparison)<25 or comparison in GENERIC_REASONS:errors.append('explain why this overall grade was chosen')
 evidence=review.get('evidence') or []
 if not evidence:errors.append('primary/organizer evidence required')
 for r in evidence:
  if not isinstance(r,dict) or not str(r.get('url','')).startswith('https://') or len(str(r.get('quote','')))<12 or not re.fullmatch('[0-9a-f]{64}',str(r.get('sha256',''))) or not r.get('checked_at'):errors.append('evidence needs URL, exact excerpt, capture date and content hash')
 basis=review.get('audience_basis')
 if basis not in AUDIENCES:errors.append('explicit audience basis required')
 if basis in {'all_ages','age_eligible','accompaniment_only','performers_are_children','unspecified'} and axes.get('child_target',{}).get('grade')=='A':errors.append('general admission, age eligibility, accompanying children or child performers do not establish a child-targeted program')
 if basis=='accompaniment_only' and review.get('child_activity_confirmed') is not True and axes.get('interactivity',{}).get('grade')=='A':errors.append('adult activity cannot be credited as the accompanying child activity')
 for axis in review.get('unsupported_axes') or []:
  if axes.get(axis,{}).get('grade')!='unknown':errors.append('unsupported axis must stay unknown: '+axis)
 if axes.get('burden',{}).get('grade')=='A' and re.search('駅.*近|駅直近',str(axes['burden'].get('reason',''))) and not review.get('burden_evidence'):errors.append('near a station alone does not establish low safety/crowding burden')
 return errors

def normalized_identity(value):
 return re.sub(r'\s+','',unicodedata.normalize('NFKC',str(value or '')))

def decision_index(rows):
 """Keep historical candidate IDs; resolve only explicit, unique published aliases."""
 result={}
 for row in rows:
  for key in {row.get('candidate_id'),row.get('published_event_id')} - {None,''}:
   if not isinstance(key,str):raise ValueError('invalid explicit decision identity')
   if key in result and result[key] is not row:raise ValueError('ambiguous published decision identity: '+key)
   result[key]=row
 return result

def bundles(store,prefix):
 manifest=read_json(store,prefix+'/manifest.json')
 if not isinstance(manifest,dict):raise ValueError('manifest missing')
 return {w['sat']:load_bundle(store,prefix,w['file']) for w in manifest['weekends']}

def check(base,directory):
 prefix=Path(directory).as_posix().rstrip('/');before=bundles(GitStore(base),prefix);after=bundles(CurrentStore(),prefix);old={};by_id={}
 for w,b in before.items():
  if not b:raise ValueError('old bundle missing '+w)
  for e in b['events']:old[w,e['id']]=e;by_id.setdefault(e['id'],[]).append(e)
 errors=[];reviewed=0;comparisons={}
 for week,bundle in after.items():
  if not bundle:raise ValueError('candidate bundle missing '+week)
  decisions=decision_index(bundle['decisions'])
  for e in bundle['events']:
   previous=old.get((week,e['id']));fit=e.get('family_fit');unchanged=previous and previous.get('family_fit')==fit
   # Exact same-ID, same-assessment carryover is not a new rating decision.
   carried=not previous and any(p.get('family_fit')==fit for p in by_id.get(e['id'],[]))
   if unchanged or carried:continue
   reviewed+=1;key=week+'/'+e['id'];errors.extend(key+': '+s for s in inspect_assessment(fit))
   decision=decisions.get(e['id']) or {}
   if decision.get('published_event_id'):
    if any(normalized_identity(decision.get(k))!=normalized_identity(e.get(k)) for k in ['name','ward']):errors.append(key+': explicit published alias does not match event identity')
   d_fit=decision.get('canonical_family_fit_v2') or decision.get('family_fit') or {}
   if any(d_fit.get(k)!=fit.get(k) for k in ['grade','overall','reason','axes','review']):errors.append(key+': published and decision assessments disagree')
   if fit.get('overall') in ('C','D') and not str(decision.get('override_reason') or '').strip():errors.append(key+': conditional publication requires a specific override')
   review=fit.get('review') or {};comparison=review.get('grade_comparison');identity=(e.get('name'),e.get('official_url'),e.get('venue'))
   if comparison:
    if comparison in comparisons and comparisons[comparison]!=identity:errors.append(key+': explanation reused for a different program')
    comparisons[comparison]=identity
 if errors:raise ValueError('\n'.join(errors))
 print(f'FAMILY FIT QUALITY PASS: {reviewed} new/changed assessments individually reviewed; unchanged ratings retained')
 return reviewed
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--base-ref',required=True);p.add_argument('--data-dir',default='site/data');a=p.parse_args()
 try:check(a.base_ref,a.data_dir)
 except (ValueError,KeyError,TypeError) as e:print('FAMILY FIT QUALITY BLOCKER: '+str(e),file=sys.stderr);sys.exit(2)
