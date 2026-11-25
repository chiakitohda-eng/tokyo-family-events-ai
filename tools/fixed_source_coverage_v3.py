#!/usr/bin/env python3
"""Phase 3: safe, read-only status evidence for ALL registered fixed sources.

A checked URL is not a verified list of dated events. Discovery link counts
are not a complete candidate census. This audit never alters event records.
"""
import argparse
import concurrent.futures
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
from urllib.parse import urlsplit

try:
    from .holiday_after_collect import fetch_url, html_links, public_row, tamemap_new_arrival_leads, tamemap_calendar_leads
    from .source_coverage_reconcile import load_published, canonical_url
except ImportError:
    from holiday_after_collect import fetch_url, html_links, public_row, tamemap_new_arrival_leads, tamemap_calendar_leads
    from source_coverage_reconcile import load_published, canonical_url

JST = dt.timezone(dt.timedelta(hours=9))
SOURCE_GROUPS = {
    "nerima_district_festivals_2026": "年間日程",
    "nerima_forest_festa_2026": "公式企画表",
    "suginami_calendar_all": "日別カレンダー",
    "suginami_festival": "月別カレンダー",
    "tamemap_nakano": "地域カレンダー",
    "nakano_official_tourism": "記事・一覧",
    "itabashi_times_event": "記事・一覧",
    "nerimakanko": "記事・月別",
    "itabashi_official_festival": "区公式",
    "itabashi_tourism_festival": "観光協会",
}
DETAIL_ADAPTERS = {
    "nerima_district_festivals_2026": "第一弾：年間公式日程",
    "suginami_calendar_all": "第一弾：公式日別カレンダー",
    "nerima_forest_festa_2026": "個別企画・日付照合",
    "nakano_official_tourism": "第二弾：記事・一覧",
    "itabashi_times_event": "第二弾：記事・一覧",
    "nerimakanko": "第二弾：月別・記事",
}
MAX_URLS_PER_SOURCE = 9
MAX_STORED_LEADS = 20


def months(start, end):
    current = start.replace(day=1)
    while current <= end:
        yield current
        current = (current.replace(day=28) + dt.timedelta(days=4)).replace(day=1)


def expand_urls(source, start, end):
    urls = []
    templates = source.get("search_urls") or [source["base_url"]]
    for template in templates:
        if not template.startswith("https://"):
            raise ValueError("non-HTTPS registered URL " + source["id"])
        substitutions = list(months(start, end)) if any(x in template for x in
                        ("{YYYY}", "{YYYY-MM}", "{MM}", "{M}")) else [start]
        for month in substitutions:
            url = (template.replace("{YYYY-MM}", month.strftime("%Y-%m"))
                    .replace("{YYYY}", str(month.year))
                    .replace("{MM}", f"{month.month:02d}")
                    .replace("{M}", str(month.month)))
            if "{" in url or "}" in url:
                raise ValueError("unexpanded URL placeholder " + source["id"])
            if url not in urls:
                urls.append(url)
    if not urls or len(urls) > MAX_URLS_PER_SOURCE:
        raise ValueError("invalid URL expansion cardinality " + source["id"])
    return urls


def probe(url, fetcher=None):
    response = fetch_url(url, fetcher=fetcher, attempts=1)
    entry = public_row(response)
    if response.get("status") == "checked":
        content_type = (entry.get("content_type") or "").lower()
        if "html" not in content_type and "xml" not in content_type:
            entry.update(status="error", error="unsupported content type; no HTML event discovery proof")
            return entry, []
        try:
            if (urlsplit(url).hostname == "pc.tamemap.net" and
                    urlsplit(url).path == "/1311401/new_arrival"):
                discovered = tamemap_new_arrival_leads(response["body"], url)
                entry["page_title"] = "ためまっぷなかの・新着投稿一覧（日時未確認）"
                entry["observed_new_arrival_title_leads"] = len(discovered)
                entry["new_arrival_title_samples"] = [
                    {"candidate_id": c["candidate_id"], "name": c["name"],
                     "poster": c.get("poster", ""), "date_verified": False,
                     "detail_url": c["discovery_url"] if c.get("detail_link_observed") else None}
                    for c in discovered[:20]]
                entry["event_date_verified"] = False
                entry["not_a_calendar_replacement"] = True
                return entry, []
            if (urlsplit(url).hostname == "pc.tamemap.net" and
                    urlsplit(url).path.startswith("/1311401/calendar/")):
                leads = tamemap_calendar_leads(response["body"], url)
                entry["page_title"] = "ためまっぷなかの・月別カレンダー"
                entry["observed_event_link_leads"] = len(leads)
                entry["event_date_verified"] = False
                return entry, leads
            page_title, leads = html_links(response["body"], url)
            entry["page_title"] = page_title
            entry["observed_event_link_leads"] = len(leads)
            return entry, leads
        except ValueError as error:
            entry.update(status="error", error="parse: " + str(error))
    return entry, []


def source_audit(source, start, end, fetcher=None, max_workers=8):
    urls = expand_urls(source, start, end)
    with concurrent.futures.ThreadPoolExecutor(max_workers=max(1, min(max_workers, 8))) as ex:
        outputs = list(ex.map(lambda url: probe(url, fetcher=fetcher), urls))
    checks = [entry for entry, _ in outputs]
    failures = [{"url": c["url"], "error": c.get("error", "unknown")}
                for c in checks if c.get("status") != "checked"]
    # A repeated article on several pages is one observed URL lead, not one
    # different event card per source page.
    seen = {}
    for check, leads in outputs:
        for lead in leads:
            url = canonical_url(lead.get("discovery_url"))
            if not url:
                continue
            if url not in seen:
                seen[url] = {"url": url, "name": lead.get("name", ""),
                             "observed_in": [check["url"]]}
            elif check["url"] not in seen[url]["observed_in"]:
                seen[url]["observed_in"].append(check["url"])
    ok = sum(c.get("status") == "checked" for c in checks)
    retrieval = "checked" if ok == len(checks) else ("partial_error" if ok else "source_error")
    # Explicitly do not derive candidate census, inclusion/exclusion,
    # publication parity or coverage completeness from navigational links.
    status = "要個別照合" if retrieval == "checked" else ("一部取得失敗" if ok else "取得失敗")
    return {
        "source_id": source["id"], "label": source["label"], "origin": source["origin"],
        "required": bool(source.get("required")), "group": SOURCE_GROUPS.get(source["id"], "固定サイト"),
        "detail_adapter": DETAIL_ADAPTERS.get(source["id"]),
        "base_url": source["base_url"], "retrieval_status": retrieval,
        "status_label": status, "pages_expected": len(checks), "pages_checked": ok,
        "pages_failed": len(failures), "observed_distinct_link_leads": len(seen),
        "example_leads": list(seen.values())[:MAX_STORED_LEADS],
        "new_arrival_post_leads_observed": sum(c.get("observed_new_arrival_title_leads", 0)
                                               for c in checks),
        "new_arrival_post_leads_are_unverified": True,
        "new_arrival_samples": [item for c in checks
                                 for item in c.get("new_arrival_title_samples", [])][:MAX_STORED_LEADS],
        "event_candidates_total": None, "candidate_publication_parity": "未検証",
        "published_count_from_source": None, "excluded_count_from_source": None,
        "duplicate_count_from_source": None, "unreviewed_count_from_source": None,
        "unverified_due_to_source_error": bool(failures),
        "source_checks": checks, "errors": failures,
        "audit_method": "registered URLs; HTML link lead observation; no inferred event dates",
        "caveat": "接続成功は候補・掲載の全件照合完了を意味しません。",
    }


def build_report(registry, start, end, *, fetcher=None, workers=8, checked_at=None):
    sources = registry.get("explicit_sources", [])
    if not isinstance(sources, list) or len(sources) < 26:
        raise ValueError("expected the original registrations plus any newly registered sources")
    ids = [s.get("id") for s in sources]
    if any(not s.get("enabled", False) for s in sources) or len(set(ids)) != len(sources):
        raise ValueError("disabled or duplicate fixed source ID")
    if not set(registry.get("protected_source_ids", [])).issubset(ids):
        raise ValueError("protected source registration missing")
    protected = set(registry.get("protected_legacy_source_ids", []))
    if len(protected) != 18 or not protected.issubset(ids):
        raise ValueError("protected 18 legacy sources missing")
    output = [None] * len(sources)
    with concurrent.futures.ThreadPoolExecutor(max_workers=max(1, min(workers, 12))) as ex:
        futures = {ex.submit(source_audit, s, start, end, fetcher, 3): i
                   for i, s in enumerate(sources)}
        for fut in concurrent.futures.as_completed(futures):
            i = futures[fut]
            s = sources[i]
            try:
                output[i] = fut.result()
            except (OSError, ValueError, KeyError, TypeError) as e:
                output[i] = {
                    "source_id": s["id"], "label": s["label"], "origin": s["origin"],
                    "required": bool(s.get("required")), "group": SOURCE_GROUPS.get(s["id"], "固定サイト"),
                    "base_url": s["base_url"], "detail_adapter": DETAIL_ADAPTERS.get(s["id"]),
                    "retrieval_status": "source_error", "status_label": "取得失敗",
                    "pages_expected": None, "pages_checked": 0, "pages_failed": None,
                    "observed_distinct_link_leads": None, "example_leads": [],
                    "event_candidates_total": None, "candidate_publication_parity": "未検証",
                    "published_count_from_source": None, "excluded_count_from_source": None,
                    "duplicate_count_from_source": None, "unreviewed_count_from_source": None,
                    "errors": [{"url": s.get("base_url"), "error": str(e)[:220]}],
                    "unverified_due_to_source_error": True, "source_checks": [],
                    "audit_method": "registered URL fetch error",
                    "caveat": "取得失敗は0件を意味しません。",
                }
    # Never conceal the tourism source 503 merely because the separate
    # municipal official festival source is accessible. Only connect evidence.
    known = {x["source_id"]: x for x in output}
    for src, state in zip(sources, output):
        fallback_ids = src.get("fallback_source_ids") or []
        if not fallback_ids:
            continue
        if not isinstance(fallback_ids, list) or any(
                x not in known or x == src["id"] for x in fallback_ids):
            raise ValueError("invalid registered fallback source mapping")
        state["official_alternatives"] = [
            {"source_id": sid,
             "retrieval_status": known[sid]["retrieval_status"],
             "base_url": known[sid]["base_url"],
             "source_coverage_not_transferred": True}
            for sid in fallback_ids]
        state["official_alternative_can_be_used_for_event_verification"] = any(
            known[sid]["retrieval_status"] == "checked" for sid in fallback_ids)
        state["failed_primary_source_stays_failed"] = True
    statuses = [s["retrieval_status"] for s in output]
    generated = checked_at or dt.datetime.now(JST).isoformat(timespec="seconds")
    return {
        "schema_version": 1, "kind": "registered_fixed_source_retrieval_and_link_leads",
        "generated_at_jst": generated, "horizon": [str(start), str(end)],
        "execution_environment": "github_actions" if os.environ.get("GITHUB_ACTIONS") == "true" else "current_execution_environment",
        "registered_source_count": len(output), "protected_legacy_source_count": len(protected),
        "source_registry_digest": hashlib.sha256(json.dumps(
            registry["explicit_sources"], sort_keys=True, ensure_ascii=False).encode()).hexdigest(),
        "summary": {
            "registered": len(output), "reachable_all_registered_urls": statuses.count("checked"),
            "partial_errors": statuses.count("partial_error"), "source_errors": statuses.count("source_error"),
            "full_event_row_parity_verified_by_this_report": 0,
            "event_candidates_count": None,
            "publication_gaps_confirmed": None,
        },
        "sources": output, "read_only": True,
        "disclaimer": f"全{len(output)}サイトのURL取得監査。記事候補やリンク数は全件候補数ではなく、公式開催日・採否・公開整合性の検証は別に必要。エラーは0件に変換しません。",
    }


def validate(report, registry):
    if report.get("read_only") is not True or report.get("schema_version") != 1:
        raise ValueError("invalid report")
    original = registry["explicit_sources"]
    ids = [s["source_id"] for s in report["sources"]]
    if ids != [s["id"] for s in original]:
        raise ValueError("source register drift or order changed")
    if report["summary"]["registered"] != len(original) or report["summary"]["full_event_row_parity_verified_by_this_report"] != 0:
        raise ValueError("unsafe audit scope or false parity claim")
    if any(s["event_candidates_total"] is not None or
           s["candidate_publication_parity"] != "未検証" for s in report["sources"]):
        raise ValueError("cannot assert event coverage from registered URL probes")
    if any(s["retrieval_status"] == "checked" and
           s["pages_expected"] != s["pages_checked"] for s in report["sources"]):
        raise ValueError("false checked status")
    return True


def main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument("--registry", default="site/data/discovery_sources.json")
    p.add_argument("--manifest", required=True)
    p.add_argument("--output", required=True)
    p.add_argument("--workers", type=int, default=8)
    a = p.parse_args(argv)
    registry = json.loads(Path(a.registry).read_text(encoding="utf-8"))
    from source_fallback_policy import apply_fallback_overlay
    registry = apply_fallback_overlay(registry)
    manifest = json.loads(Path(a.manifest).read_text(encoding="utf-8"))
    weeks = manifest["weekends"]
    start, end = dt.date.fromisoformat(weeks[0]["sat"]), dt.date.fromisoformat(weeks[-1]["sun"])
    result = build_report(registry, start, end, workers=a.workers)
    validate(result, registry)
    output = Path(a.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"checked_at": result["generated_at_jst"], "summary": result["summary"],
                      "errors": [(s["source_id"], s["retrieval_status"])
                                 for s in result["sources"] if s["retrieval_status"] != "checked"]},
                     ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
