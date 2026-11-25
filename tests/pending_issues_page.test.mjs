import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
import {prepareIssues,validateCatalog,validateAudit,retrievalStatus} from '../site/pending-issues-model.mjs';
const read=p=>fs.readFileSync(p,'utf8');
const catalog=JSON.parse(read('site/audit/pending_issues_catalog.json'));
const audit={schema_version:1,read_only:true,registered_source_count:26,generated_at_jst:'2026-11-14T21:00:00+09:00',summary:{full_event_row_parity_verified_by_this_report:0},sources:Array.from({length:26},(_,i)=>({source_id:i===0?'tamemap_nakano':i===1?'itabashi_tourism_festival':'fixture_'+i,retrieval_status:i===0?'source_error':'checked',candidate_publication_parity:'未検証'}))};
assert.equal(validateCatalog(catalog),true);assert.equal(validateAudit(audit),true);
const currentAudit=structuredClone(audit);
currentAudit.sources.push({source_id:'shinjuku_sankaku_hiroba',retrieval_status:'checked',candidate_publication_parity:'未検証'});
currentAudit.registered_source_count=27;
assert.equal(validateAudit(currentAudit),true,'adding the venue source must not hide every connection status');
currentAudit.registered_source_count=26;assert.equal(validateAudit(currentAudit),false,'declared count must match actual rows');
currentAudit.registered_source_count=27;currentAudit.sources[26].source_id=currentAudit.sources[0].source_id;
assert.equal(validateAudit(currentAudit),false,'duplicate source IDs must fail closed');
const model=prepareIssues(catalog,audit);
assert.equal(model.entries.length,5);
assert.deepEqual(model.counts,{total:2,pending:1,deferred:1,completed:3,connection:1,verification:1});
assert.deepEqual(model.remaining.map(e=>e.id),['tamemap-nakano','article-leads']);
assert.deepEqual(model.completed.map(e=>e.id),['itabashi-tourism','suginami-candidates','weekly-update']);
assert.ok(model.remaining.every(e=>e.work_status!=='completed'));
assert.ok(model.completed.every(e=>e.completed_at && e.completed_scope && ['対応完了','全件判定済み（一部見送り）'].includes(e.status.label)));
assert.match(model.remaining[0].status.label,/保留/);
assert.equal(model.remaining[0].retrieval_status.label,'自動取得できません');
const reviewed=model.remaining.find(e=>e.id==='article-leads');
assert.equal(reviewed.status.label,'公式根拠の確認待ち');
assert.equal(reviewed.review_results.length,20);
assert.equal(reviewed.review_results.filter(r=>r.status==='withheld_insufficient_evidence').length,9);
assert.match(reviewed.now,/未解決/);
assert.equal(reviewed.public_information_only,true);
assert.equal(reviewed.outbound_contact_allowed,false);
assert.match(reviewed.followup_policy,/問い合わせは行いません/);
for(const row of reviewed.review_results.filter(r=>r.status==='withheld_insufficient_evidence')){
 assert.ok(row.pending_detail?.confirmed && row.pending_detail?.missing && row.pending_detail?.publication_impact && row.pending_detail?.needed_evidence);
}
for(const change of [c=>delete c.issues[3].review_results[0].pending_detail,c=>c.issues[3].review_results[0].pending_detail.missing='',c=>c.issues[3].outbound_contact_allowed=true]){
 const invalid=structuredClone(catalog);change(invalid);assert.throws(()=>validateCatalog(invalid));
}
const premature=structuredClone(catalog);
Object.assign(premature.issues[3],{work_status:'completed',completed_at:'2026-11-15',completed_scope:'全件を調査して掲載見送りを判定'});
assert.throws(()=>validateCatalog(premature),/完了にできません/,'withholding must not silently complete missing primary evidence');
for(const mutation of [c=>c.issues[3].review_results[0].sources=['javascript:alert(1)'],c=>c.issues[3].review_results[0].status='verified',c=>c.issues[3].review_results.push(c.issues[3].review_results[0])]){const bad=structuredClone(catalog);mutation(bad);assert.throws(()=>validateCatalog(bad));}
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
for(const e of allDone.issues){Object.assign(e,{work_status:'completed',completed_at:'2026-11-14',completed_scope:'Fixture scope only'});delete e.review_results;}
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

// The real renderer must put only unresolved rows before the collapsed history.
class ReviewNode{
 constructor(tag){this.tag=tag;this.children=[];this.dataset={};this.textContent='';this.open=false;}
 appendChild(child){this.children.push(child);return child;}
}
const reviewDocument={createElement:tag=>new ReviewNode(tag),createTextNode:value=>Object.assign(new ReviewNode('#text'),{textContent:value})};
const reviewContext=vm.createContext({document:reviewDocument,entry:reviewed});
vm.runInContext(js.replace(/^import[^\n]+\n/,'').replace(/\ninit\(\);\s*$/,'\nglobalThis.card=renderCard(entry);'),reviewContext);
const findNodes=(node,match)=>[...(match(node)?[node]:[]),...node.children.flatMap(n=>findNodes(n,match))];
const section=findNodes(reviewContext.card,n=>n.className==='pending-unresolved-results')[0];
assert.equal(section.children.filter(n=>n.className==='pending-review-item').length,9);
const history=findNodes(reviewContext.card,n=>n.className==='pending-reviewed-history')[0];
assert.equal(history.open,false);
assert.equal(history.children.filter(n=>n.className==='pending-review-item').length,11);
const row=section.children.find(n=>n.className==='pending-review-item');
assert.equal(row.open,false);
assert.equal(row.children.filter(n=>n.className==='pending-issue-part').length,4);
assert.equal(findNodes(section,n=>n.dataset?.reviewStatus==='assessment_reconfirmed').length,0);
console.log('PASS: nine explicit blockers and four detail fields; eleven reviewed records remain collapsed separately');
