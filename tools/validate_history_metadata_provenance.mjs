#!/usr/bin/env node
// Narrow, fail-closed audit for the historical 2026-11-08 count-only provenance correction.
// No event, verification, decision, discovery, or source-check content may change.
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {execFileSync} from 'node:child_process';
import {join} from 'node:path';

const args=process.argv.slice(2);
const arg=name=>args[args.indexOf(name)+1];
assert(args.includes('--base-ref')&&args.includes('--data-dir'),
  'Required: --base-ref <40-char-data-production-sha> --data-dir site/data');
const base=arg('--base-ref'),dir=arg('--data-dir');
assert(/^[0-9a-f]{40}$/.test(base),'Expected exact production data commit SHA');
const git=(...cmd)=>execFileSync('git',cmd,{encoding:'utf8',maxBuffer:8*1024*1024}).trim();
const changed=git('diff','--name-only',base,'HEAD').split('\n').filter(Boolean);
assert.deepEqual(changed,['site/data/update_history.json'],
  'Only the already-published update_history metadata may change');
const old=JSON.parse(git('show',base+':site/data/update_history.json'));
const now=JSON.parse(readFileSync(join(dir,'update_history.json'),'utf8'));
assert.equal(now.schema_version,old.schema_version,'History schema immutable');
assert.equal(now.history.length,old.history.length,'History entries immutable');
let touched=0;
for(let i=0;i<old.history.length;i++){
  const oldRow=old.history[i], newRow=structuredClone(now.history[i]);
  if(oldRow.run_type==='verified_current_horizon_subset'&&oldRow.as_of_jst==='2026-11-08'){
    assert(!Object.hasOwn(oldRow,'new_event_ids'),'Baseline must not already claim new IDs');
    assert(Array.isArray(newRow.new_event_ids),'New IDs must be an explicit array');
    delete newRow.new_event_ids; touched++;
  }
  assert.deepEqual(newRow,oldRow,'Historical facts or source failure states changed at history index '+i);
}
assert.equal(touched,1,'Exactly one identified 2026-11-08 rollover record allowed');
const row=now.history.find(r=>r.run_type==='verified_current_horizon_subset'&&r.as_of_jst==='2026-11-08');
assert.equal(row.added_weekly_records,18);
assert.equal(row.protected_carryover_records,13);
assert.equal(row.newly_verified_or_announced_records,5);
const week=JSON.parse(readFileSync(join(dir,'2026-12-12.json'),'utf8'));
assert.deepEqual(week.event_files,['2026-12-12-events-current-verified.json'],
  'Unexpected event shard layout: independently re-review before changing proof');
const events=JSON.parse(readFileSync(join(dir,week.event_files[0]),'utf8'));
const ver=JSON.parse(readFileSync(join(dir,'2026-12-12-verification.json'),'utf8'));
const dec=JSON.parse(readFileSync(join(dir,'2026-12-12-decisions.json'),'utf8'));
const run=JSON.parse(readFileSync(join(dir,'2026-12-12-run.json'),'utf8'));
assert.equal(events.length,18,'Published 12/12 original record count cannot change');
assert.equal(run.summary?.protected_carryover,13);
assert.equal(run.summary?.new_official_published,5);
const independentlyAdded=events.slice(13);
const ids=independentlyAdded.map(e=>e.id);
assert.equal(new Set(ids).size,5,'All five event IDs must be distinct');
assert.deepEqual([...row.new_event_ids].sort(),[...ids].sort(),
  'Added IDs must correspond exactly to the five published independent event records');
const decisions=new Map(dec.decisions.map(x=>[x.candidate_id,x]));
const verified=new Map(ver.events.map(x=>[x.id,x]));
for(const event of independentlyAdded){
  assert(['2026-12-12','2026-12-13'].includes(event.date_start),
    'New ID must be held in the current added week');
  assert(event.official_url?.startsWith('https://'),'Each new event must retain official source');
  assert.equal(decisions.get(event.id)?.decision,'published','New identity lacks published decision');
  assert(['verified','announced'].includes(verified.get(event.id)?.status),
    'New identity lacks original verification/announcement provenance');
}
assert(events.slice(0,13).every(e=>!row.new_event_ids.includes(e.id)),
  'Protected carryover must never appear in added IDs');
assert.equal(now.history.at(-1).run_type,'manual_official_add_only',
  'The eleven previously verified gap-recovery additions must remain the newest history row');
assert.equal(now.history.at(-1).new_event_ids.length,11);
console.log('PASS exact provenance-only correction: 13 preserved + 5 independently added + 11 gap recovery');
console.log('UNCHANGED_SOURCE_AUDIT_DEBT: 844 unverified links, 3 Tamemap required-source 403s,');
console.log('and incomplete per-candidate event-row audit remain open; NO full-source parity is claimed.');
