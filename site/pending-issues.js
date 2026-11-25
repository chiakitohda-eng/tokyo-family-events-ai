import {prepareIssues,formatJst} from "./pending-issues-model.mjs?v=20261115-remaining-clarity-1";
const byId=id=>document.getElementById(id);
function textNode(tag,text,className){
  const node=document.createElement(tag);
  if(className)node.className=className;
  node.textContent=String(text??"");
  return node;
}
function statusLine(title,value){
  const elem=textNode("div","","pending-issue-part");
  elem.appendChild(textNode("strong",title));
  elem.appendChild(textNode("p",value));
  return elem;
}
function renderReviewRow(row){
  const item=textNode("details","","pending-review-item");
  item.dataset.reviewStatus=row.status;
  const summary=textNode("summary","","pending-review-summary");
  summary.appendChild(textNode("span",row.name,"pending-review-name"));
  if(row.pending_detail){
    summary.appendChild(textNode("span",row.pending_detail.publication_status+" ／ "+row.pending_detail.blocker,"pending-review-state"));
  }else{
    summary.appendChild(textNode("span",row.status==="assessment_reconfirmed"?"既存評価を再確認":"終了・期間対象外で見送り","pending-review-state"));
  }
  item.appendChild(summary);
  if(row.pending_detail){
    const d=row.pending_detail;
    for(const [title,value]of [["確認できたこと",d.confirmed],["残っている確認",d.missing],["掲載への影響",d.publication_impact],["確認に必要な資料",d.needed_evidence]]){
      item.appendChild(statusLine(title,value));
    }
  }else{
    item.appendChild(textNode("p",row.reason));
  }
  const links=textNode("p","");
  row.sources.forEach((url,i)=>{
    const a=textNode("a","参照資料"+(i+1));a.href=url;a.target="_blank";a.rel="noopener noreferrer";
    links.appendChild(a);links.appendChild(document.createTextNode("　"));
  });
  item.appendChild(links);
  return item;
}
function renderCard(entry){
  const article=textNode("details","","pending-issue-card");
  article.dataset.workStatus=entry.work_status;
  article.id=entry.id;
  const summary=textNode("summary","","pending-issue-summary");
  const head=textNode("div","","pending-issue-card-top");
  head.appendChild(textNode("span",entry.category==="connection"?"サイトの取得に関する問題":"イベント情報の確認作業","pending-issue-kind"));
  head.appendChild(textNode("span",entry.status.label,"pending-issue-status"));
  summary.appendChild(textNode("h3",entry.title));
  summary.appendChild(head);
  article.appendChild(summary);
  const content=textNode("div","","pending-issue-content");
  const body=textNode("div","","pending-issue-parts");
  if(entry.work_status==="completed"){
    body.appendChild(statusLine("完了した対応",entry.now));
    body.appendChild(statusLine("完了とした範囲",entry.completed_scope));
    body.appendChild(statusLine("確認日",entry.completed_at));
  }else if(entry.review_results){
    body.appendChild(statusLine("残っている確認",entry.now));
  }else{
    body.appendChild(statusLine("どんな影響がある？",entry.impact));
    body.appendChild(statusLine("現在残っていること",entry.now));
    body.appendChild(statusLine("代わりの対応",entry.workaround));
    body.appendChild(statusLine("今後の対応",entry.next));
  }
  content.appendChild(body);
  if(entry.review_results){
    const unresolved=entry.review_results.filter(row=>row.status==="withheld_insufficient_evidence");
    const reviewed=entry.review_results.filter(row=>row.status!=="withheld_insufficient_evidence");
    const remaining=textNode("section","","pending-unresolved-results");
    remaining.appendChild(textNode("h4","未解決の"+unresolved.length+"件"));
    if(entry.followup_policy)remaining.appendChild(textNode("p",entry.followup_policy,"pending-followup-policy"));
    for(const row of unresolved)remaining.appendChild(renderReviewRow(row));
    content.appendChild(remaining);
    if(reviewed.length){
      const history=textNode("details","","pending-reviewed-history");
      history.appendChild(textNode("summary","確認済みの記録（"+reviewed.length+"件）"));
      history.appendChild(textNode("p","終了・期間対象外を確認した候補と、根拠を再確認した既存評価です。未解決の9件には含めません。"));
      for(const row of reviewed)history.appendChild(renderReviewRow(row));
      content.appendChild(history);
    }
  }
  if(entry.retrieval_status){
    content.appendChild(statusLine("サイトへの接続（作業状況とは別）",
      entry.retrieval_status.label+"。"+entry.retrieval_status.detail));
  }
  const footer=textNode("div","","pending-issue-card-footer");
  const a=textNode("a","詳しい対応記録を見る（GitHub）");
  a.href=entry.issue_url;
  a.target="_blank";
  a.rel="noopener noreferrer";
  footer.appendChild(a);
  content.appendChild(footer);
  article.appendChild(content);
  return article;
}
function render(model){
  const f=byId("pendingCategoryFilter").value;
  const work=byId("pendingStatusFilter").value;
  const items=model.entries.filter(x=>(f==="all"||x.category===f)&&(work==="all"||x.work_status===work));
  const list=byId("pendingIssueList");
  list.replaceChildren();
  for(const item of items)list.appendChild(renderCard(item));
  if(!items.length)list.appendChild(textNode("p","選択した条件に当てはまる項目はありません。"));
  byId("pendingVisibleCount").textContent=
    f==="all"&&work==="all" ? "すべての対応状況を表示しています。" : "選択した条件の対応状況を表示しています。";
}
async function getJson(path){
  const res=await fetch(path,{cache:"no-store"});
  if(!res.ok)throw new Error("HTTP "+res.status);
  return res.json();
}
async function init(){
  let model;
  try {
    const catalog=await getJson("audit/pending_issues_catalog.json");
    let audit=null;
    try{audit=await getJson("audit/fixed_sources.json");}
    catch(e){console.warn("サイト取得状況の最新監査は未取得です",e);}
    model=prepareIssues(catalog,audit);
  } catch(err){
    console.error("残課題一覧の読み込み失敗",err);
    byId("pendingIntro").textContent="現在の残課題一覧を読み込めませんでした。";
    byId("pendingCheckedAt").textContent="確認ができていないため、残課題が0件とは表示していません。";
    byId("pendingIssueList").replaceChildren(textNode("p","現在一覧を取得できません。時間をおいてもう一度お試しください。"));
    byId("pendingVisibleCount").textContent="未確認";
    return;
  }
  byId("pendingIntro").textContent="残課題・保留・完了を一覧で表示します。各項目を開くと、対応内容や確認できた範囲をご覧いただけます。";
  byId("pendingCheckedAt").textContent=
    "取得状況の最終監査："+(model.is_audit_current?formatJst(model.audit_checked_at):"最新結果は取得できませんでした")+
    "　／　対応リストの確認日："+(model.catalog_reviewed_at||"未確認")+
    "。掲載内容の確認はアクセス成功と別に実施します。";
  byId("pendingStatusFilter").addEventListener("change",()=>render(model));
  byId("pendingCategoryFilter").addEventListener("change",()=>render(model));
  render(model);
}
init();
