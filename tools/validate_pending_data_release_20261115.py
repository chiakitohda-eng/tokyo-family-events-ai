"""Exact combined proof for the two already reviewed pending data batches."""
import argparse,json,subprocess
from pathlib import Path
import validate_evidence_recovery_20261115 as first
import validate_aipaku_addition_20261115 as second
BASE='847e388e65b99e38a0f108ecc96009778b3fdcd2'
INTERMEDIATE='6fb1abd131411ba64bbb175667c3d8a0fc922d69'
CANDIDATE='e9886705d9c6ce2cc21fdd276553df2a34849fd4'

def check(base,directory='site/data'):
    if base!=BASE or subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()!=CANDIDATE:
        raise ValueError('only the exact reviewed production baseline and 603-record candidate are permitted')
    old=lambda n:json.loads(subprocess.check_output(['git','show',BASE+':site/data/'+n]))
    previous=lambda n:json.loads(subprocess.check_output(['git','show',INTERMEDIATE+':site/data/'+n]))
    expected=first.expected_outputs(old,first.load_spec(),previous('manifest.json')['generated'])
    changed=subprocess.check_output(['git','diff','--name-only',BASE,INTERMEDIATE],text=True).splitlines()
    if set(changed)!={'site/data/'+n for n in expected}:
        raise ValueError('intermediate review changed paths')
    first.compare_outputs({n:previous(n)for n in expected},expected)
    # This freezes the second batch and preserves the entire first batch, its
    # history and the original source-error multiset. No missing-source waiver.
    second.check(BASE,directory)
    print('PENDING DATA RELEASE PASS: exact 5 additions + 6 evidence reviews; all 598 old event facts and source failures retained')

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--base-ref',required=True);p.add_argument('--data-dir',default='site/data');a=p.parse_args();check(a.base_ref,a.data_dir)
