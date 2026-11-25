import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
import {prepareIssues,validateCatalog,validateAudit,retrievalStatus} from '../site/pending-issues-model.mjs';
const read=p=>fs.readFileSync(p,'utf8');
const catalog=JSON.parse(read('site/audit/pending_issues_catalog.json'));
const audit={schema_version:1,read_only:true,registered_source_count:26,generated_at_jst:'2026-11-14T21:00:00+09:00',summary:{full_event_row_parity_verified_by_this_report:0},sources:Array.from({length:26},(_,i)=>({source_id:i===0?'tamemap_nakano':i===1?'itabashi_tourism_festival':'fixture_'+i,retrieval_status:i===0?'source_error':'checked',candidate_publication_parity:'未検証'}))};
assert.equal(validateCatalog(catalog),true);assert.equal(validateAudit(audit),true);
const model=prepareIssues(catalog,audit);
assert.equal(model.entries.length,5);
assert.deepEqual(model.counts,{total:2,pending:1,deferred:1,completed:3,connection:1,verification:1});
assert.deepEqual(model.remaining.map(e=>e.id),['tamemap-nakano','article-leads']);
assert.deepEqual(model.completed.map(e=>e.id),['itabashi-tourism','suginami-candidates','weekly-update']);
assert.ok(model.remaining.every(e=>e.work_status!=='completed'));
assert.ok(model.completed.every(e=>e.completed_at && e.completed_scope && e.status.label==='対応完了'));
assert.match(model.remaining[0].status.label,/保留/);
assert.equal(model.remaining[0].retrieval_status.label,'自動取得できません');
assert.equal(model.remaining[1].status.label,'公式根拠の確認待ち');
// An HTTP success must not complete a deferred investigation or an unverified event.
const healed=structuredClone(audit);healed.sources[0].retrieval_status='checked';
const next=prepareIssues(catalog,healed);
assert.deepEqual(next.counts,model.counts);
assert.equal(next.remaining[0].work_status,'deferred');
assert.equal(next.remaining[0].retrieval_status.label,'登録ページの接続を確認');
assert.doesNotMatch(next.remaining[0].retrieval_status.label,/照合待ち/);
// Failure to load the audit never erases the manually reviewed completion/holds.
const unavailable=prepareIssues(catalog,null);
assert.deepEqual(unavailable.counts,model.counts);
assert.equal(unavailable.is_audit_current,false);
assert.equal(unavailable.remaining[0].retrieval_status.label,'取得状況を確認できません');
const allDone=structuredClone(catalog);
for(const e of allDone.issues)Object.assign(e,{work_status:'completed',completed_at:'2026-11-14',completed_scope:'Fixture scope only'});
assert.equal(prepareIssues(allDone,null).counts.total,0);
assert.equal(prepareIssues(allDone,null).completed.length,5);
// Missing/unknown work status fails closed instead of silently looking complete.
for(const mutate of [c=>delete c.issues[0].work_status,c=>c.issues[0].work_status='unknown',c=>delete c.issues[1].completed_scope,c=>c.issues[1].completed_at='',c=>c.issues[0].issue_url='https://example.com/ads']){
 const invalid=structuredClone(catalog);mutate(invalid);assert.throws(()=>validateCatalog(invalid));
}
const page=read('site/pending-issues.html'),js=read('site/pending-issues.js');
assert.doesNotMatch(page,/id="completedIssues"/);
assert.match(js,/textNode\("details"/);
assert.match(page,/完了分は残課題の件数に含めません/);
assert.match(js,/model\.entries\.filter/);assert.match(js,/pendingStatusFilter/);
assert.match(js,/textContent/);assert.doesNotMatch(js,/\.innerHTML\s*=/);
assert.match(read('site/index.html'),/href="pending-issues\.html"/);
for(const id of ['pendingIssueList','pendingCategoryFilter','pendingStatusFilter'])assert.ok(page.includes(`id="${id}"`));
console.log('PASS: remaining/completed counts, explicit holds, independent audit changes, missing evidence and safe rendering');

// Exercise the actual asynchronous load-failure handler, not only model fixtures.
const nodes=new Map();
const node=()=>({textContent:'—',children:[],replaceChildren(...children){this.children=children;}});
const document={getElementById(id){if(!nodes.has(id))nodes.set(id,node());return nodes.get(id);},createElement:node};
const context=vm.createContext({document,fetch:async()=>({ok:false,status:503}),console:{error(){},warn(){}}});
const runtime=js.replace(/^import[^\n]+\n/,'').replace(/\ninit\(\);\s*$/,'\nglobalThis.initStatusPage=init;');
vm.runInContext(runtime,context);await context.initStatusPage();
assert.equal(nodes.get('pendingVisibleCount').textContent,'未確認');


assert.match(nodes.get('pendingIssueList').children[0].textContent,/取得できません/);
console.log('PASS: actual load failure keeps both lists unknown and does not access a missing model');

assert.doesNotMatch(page,/全体の状況|id="pendingTotal"|id="pendingCompleted"|class="pending-issues-stats"/);
assert.doesNotMatch(js,/model\.counts\./);
console.log("PASS: no aggregate dashboard; direct task list with explicit status and preserved details");
