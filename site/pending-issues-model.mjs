/** Source-grounded status labels for the public outstanding-work page. */
export const ALLOWED_CATEGORIES = Object.freeze(["connection", "verification"]);
const ISSUE_PREFIX = "https://github.com/toodataa-ai/tokyo-family-events-ai/issues/";

export function validateCatalog(catalog) {
  if (!catalog || catalog.schema_version !== 1 || !Array.isArray(catalog.issues) ||
      catalog.issues.length === 0 || catalog.issues.length > 30) {
    throw new Error("残課題の一覧データが不正です");
  }
  const seen = new Set();
  for (const entry of catalog.issues) {
    if (!["pending","deferred","completed"].includes(entry.work_status) ||
        (entry.work_status === "completed" && (!entry.completed_scope || !/^\d{4}-\d{2}-\d{2}$/.test(entry.completed_at || ""))) ||
        !entry.id || seen.has(entry.id) || !ALLOWED_CATEGORIES.includes(entry.category) ||
        !entry.title || !entry.impact || !entry.now || !entry.workaround ||
        !entry.next || !entry.issue_url?.startsWith(ISSUE_PREFIX) ||
        !/^https:\/\/github\.com\/toodataa-ai\/tokyo-family-events-ai\/issues\/[0-9]+$/.test(entry.issue_url)) {
      throw new Error("残課題の内容・追跡リンクが不正です");
    }
    if ((entry.category === "connection") !== Boolean(entry.source_id)) {
      throw new Error("取得課題に紐づく参照元がありません");
    }
    seen.add(entry.id);
  }
  return true;
}

export function validateAudit(audit) {
  return Boolean(audit && audit.schema_version === 1 && audit.read_only === true &&
    audit.registered_source_count === 26 && Array.isArray(audit.sources) &&
    audit.sources.length === 26 &&
    audit.summary?.full_event_row_parity_verified_by_this_report === 0 &&
    audit.sources.every(x => typeof x.source_id === "string" &&
      ["checked", "partial_error", "source_error"].includes(x.retrieval_status) &&
      x.candidate_publication_parity === "未検証"));
}

export function retrievalStatus(entry, audit) {
  if (entry.category !== "connection") {
    return null;
  }
  if (!validateAudit(audit)) {
    return {label:"取得状況を確認できません",detail:"最新の監査情報が取得できていません。解消したとは判定しません。"};
  }
  const row = audit.sources.find(x => x.source_id === entry.source_id);
  if (!row) {
    return {label:"取得状況を確認できません",detail:"対象サイトの監査結果が見つかりません。"};
  }
  if (row.retrieval_status === "checked") {
    return {label:"登録ページの接続を確認",detail:"監査時点で登録ページを取得できました。作業の完了・保留とは別の接続結果です。"};
  }
  const alternatives = (row.official_alternatives || []).filter(x =>
    x.retrieval_status === "checked");
  if (row.retrieval_status === "partial_error") {
    return {label:"一部のページが取得できません",
      detail:"補助ページから情報を確認できる場合がありますが、取得に失敗したページの確認は残っています。"};
  }
  return {label:"自動取得できません",
    detail:alternatives.length
      ? "対象サイトは取得できませんが、別の自治体公式サイトへの接続は確認できています。"
      : "自動でページを取得できていません。既存イベントが消えたという意味ではありません。"};
}

export function issueStatus(entry) {
  if (entry.work_status === "completed") return {label:"対応完了",detail:entry.completed_scope};
  if (entry.work_status === "deferred") return {label:"保留（指定により対象外）",detail:entry.next};
  return {label:"公式根拠の確認待ち",detail:entry.next};
}

export function prepareIssues(catalog, audit) {
  validateCatalog(catalog);
  const report = validateAudit(audit) ? audit : null;
  const entries = catalog.issues.map(e => ({...e, status:issueStatus(e),
    retrieval_status:e.category === "connection" ? retrievalStatus(e,report) : null}));
  const remaining = entries.filter(e => e.work_status !== "completed");
  return {
    entries, remaining, completed:entries.filter(e => e.work_status === "completed"),
    is_audit_current:Boolean(report), audit_checked_at:report?.generated_at_jst || null,
    catalog_reviewed_at:catalog.reviewed_at_jst || null,
    counts:{total:remaining.length, pending:remaining.filter(e => e.work_status === "pending").length,
      deferred:remaining.filter(e => e.work_status === "deferred").length,
      completed:entries.length-remaining.length,
      connection:remaining.filter(e => e.category === "connection").length,
      verification:remaining.filter(e => e.category === "verification").length}
  };
}

export function formatJst(raw) {
  if (!raw) return "未確認";
  const date = new Date(raw);
  return Number.isNaN(date.getTime()) ? "未確認" :
    date.toLocaleString("ja-JP", {timeZone:"Asia/Tokyo",year:"numeric",month:"long",
                                 day:"numeric",hour:"2-digit",minute:"2-digit"});
}
