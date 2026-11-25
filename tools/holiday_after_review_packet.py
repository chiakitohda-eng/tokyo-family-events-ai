#!/usr/bin/env python3
"""Construct reviewer worklists from published events and *unverified* crawl links.

This is a non-publishable staging artifact.  It never mutates the old manifest,
dated event records, update history or branch references.
"""
import argparse
from collections import defaultdict
import json
from pathlib import Path
import re
import unicodedata


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def norm(value):
    return " ".join(unicodedata.normalize("NFKC", str(value or "")).casefold().split())


def event_identity(ev):
    start, end = ev.get("date_start") or "", ev.get("date_end") or ""
    period = f"{start}|{end}" if start or end else norm(ev.get("period"))
    venue = norm(ev.get("venue"))
    url = ""
    for field in ("official_url", "url"):
        value = ev.get(field)
        if value:
            from urllib.parse import urlsplit
            parsed = urlsplit(value)
            if parsed.scheme == "https":
                url = parsed.hostname.removeprefix("www.") + parsed.path.rstrip("/")
                break
    return f"{norm(ev.get('name'))}|{period}|{('v:' + venue) if venue else ('u:' + url)}"


def is_overlapping(ev, start, end):
    a, b = ev.get("date_start"), ev.get("date_end") or ev.get("date_start")
    return (isinstance(a, str) and isinstance(b, str)
            and bool(re.fullmatch(r"\d{4}-\d{2}-\d{2}", a))
            and bool(re.fullmatch(r"\d{4}-\d{2}-\d{2}", b))
            and a <= end and b >= start)


def attached_weekday_holidays(week, holidays, following_sat=None):
    """Include every registered weekday holiday after Sun until next Sat.

    Do not assume a holiday must be Monday. A 2026-11-03 Tuesday holiday
    belongs to the 2026-10-31 review, never the 2026-11-07 review.
    """
    from datetime import date, timedelta
    sun = date.fromisoformat(week["sun"])
    boundary = (date.fromisoformat(following_sat) if following_sat else
                date.fromisoformat(week["sat"]) + timedelta(days=7))
    days = []
    for holiday in holidays or []:
        day = date.fromisoformat(holiday["date"])
        if sun < day < boundary and day.weekday() < 5:
            days.append(holiday["date"])
    return sorted(set(days))


def discovery_mentions_date(candidate, day):
    via = candidate.get("discovered_via") or {}
    query = str(via.get("query") or "")
    local = day.replace("-", "年", 1).replace("-", "月", 1) + "日"
    return (day in candidate.get("matched_dates", [])
            or day in query or local in query)


def existing_week(data_dir, week):
    main = read_json(data_dir / week["file"])
    events = list(main.get("events") or [])
    for shard in main.get("event_files") or []:
        events.extend(read_json(data_dir / shard))
    return events


def build_packet(plan, published_dir, collected):
    if plan.get("status") != "eligible":
        raise ValueError("not an eligible holiday-after update")
    summary = collected["summary"]
    if summary.get("publishable") is not False:
        raise ValueError("crawler's unverified evidence cannot authorize publication")
    if summary.get("base_data_production_sha") != plan.get("base_data_production_sha"):
        raise ValueError("baseline SHA mismatch")
    published = read_json(published_dir / "manifest.json")
    old_weeks = {w["sat"]: w for w in published["weekends"]}
    originals = {sat: existing_week(published_dir, w) for sat, w in old_weeks.items()}
    discovered = collected["candidate_pool"]
    weekly = []
    for week_index, target in enumerate(plan["weekends"]):
        sat, sun = target["sat"], target["sun"]
        already_listed = sat in originals
        if already_listed:
            prior = originals[sat]
        else:
            carried = {}
            for old_sat, rows in sorted(originals.items()):
                for ev in rows:
                    if is_overlapping(ev, sat, sun):
                        carried[event_identity(ev)] = {
                            "previous_week": old_sat, "event": ev}
            prior = [x["event"] for x in carried.values()]
        identified = {event_identity(ev) for ev in prior}
        next_sat = (plan["weekends"][week_index + 1]["sat"]
                    if week_index + 1 < len(plan["weekends"]) else None)
        attached_days = attached_weekday_holidays(
            target, plan.get("holiday_targets"), next_sat)
        target_dates = [sat, sun, *attached_days]
        links = []
        for c in discovered:
            via = c.get("discovered_via") or {}
            if any(discovery_mentions_date(c, day) for day in target_dates):
                links.append(c)
        # A missing candidate cannot be obscured by another week's review.
        holiday_leads = {day: [c for c in links if discovery_mentions_date(c, day)]
                         for day in attached_days}
        weekly.append({
            "sat": sat, "sun": sun, "tier": target["publication_tier"],
            "existing_week": already_listed,
            "prior_published_count": len(prior) if already_listed else 0,
            "carryover_review_count": 0 if already_listed else len(prior),
            "carryover_needs_daily_confirmation": not already_listed,
            "protected_prior_event_ids": sorted({ev.get("id") for ev in prior if ev.get("id")}),
            "suggested_discoveries_count": len(links),
            "attached_weekday_holidays": attached_days,
            "holiday_leads_by_date": {
                day: {"candidate_count": len(rows),
                      "candidate_ids": sorted({c["candidate_id"] for c in rows})}
                for day, rows in holiday_leads.items()
            },
            "undated_supplemental_candidates": [
                c for c in discovered if c.get("date_unverified") and
                (c.get("discovered_via") or {}).get("ward") == "中野区"
            ] if sat == plan["weekends"][0]["sat"] else [],
            "suggested_discoveries": links,
            "review_state": "needs_individual_official_event_checks_and_decisions"
        })
    holiday_reviews = []
    for holiday in plan.get("holiday_targets", []):
        day = holiday["date"]
        candidates = [c for c in discovered if discovery_mentions_date(c, day)]
        assigned_week = next((w for w in weekly
                              if day in w["attached_weekday_holidays"]), None)
        holiday_reviews.append({
            "date": day, "name": holiday.get("name"),
            "assigned_week_sat": assigned_week["sat"] if assigned_week else None,
            "candidate_count": len(candidates), "candidates": candidates,
            "review_week_candidate_ids": (assigned_week.get("holiday_leads_by_date", {})
                                          .get(day, {}).get("candidate_ids", [])
                                          if assigned_week else []),
            "candidate_handoff_complete": (
                assigned_week is not None and
                set(c["candidate_id"] for c in candidates) ==
                set(assigned_week.get("holiday_leads_by_date", {})
                    .get(day, {}).get("candidate_ids", []))),
            "publication_state": "unreviewed_candidates_not_published",
            "independent_official_date_and_opening_check": "pending"
        })
    return {
        "schema_version": 1, "kind": "holiday_after_reviewer_packet",
        "read_only": True, "publication_permitted": False,
        "as_of_jst": plan["as_of_jst"], "base_data_production_sha": plan["base_data_production_sha"],
        "published_history_preserved": True, "published_week_file_changes": 0,
        "family_fit_review_requirements": {
            "default_grade_allowed": False,
            "method": "individual_evidence_review",
            "required": ["all_eight_axes", "activity_specific_overall_reason", "strengths", "limitations", "grade_comparison", "audience_basis", "primary_excerpt_date_hash"],
            "rules": [
                "Do not average axes or set every event to B; select the overall grade for the actual activity.",
                "All-ages admission, a minimum age, accompanying children and child performers are different from a child-targeted program.",
                "Adult participation is not a child activity. Unknown conditions remain unknown and do not automatically cap the overall grade.",
                "A specific family concert may be A despite being viewing-only; booking does not automatically make a class B.",
                "Keep event and decision assessments consistent; C/D publication needs a reasoned override."
            ],
            "release_check": "python3 tools/validate_family_fit_quality.py --base-ref <immutable-data-production-sha>"
        },
        "required_source_failures": summary.get("required_source_failures") or [],
        "annual_schedule": summary.get("annual_schedule") or [],
        "wards": summary["wards"],
        "weeks": weekly,
        "independent_holiday_reviews": holiday_reviews,
        "approval_requirements": [
            "Reconcile every official schedule row with a published/excluded/duplicate decision",
            "Verify each new event's date, venue and official evidence for its participation unit",
            "Independently check both weekday holidays (November 3 and 23)",
            "Preserve each prior current-week event ID or obtain explicit removal approval",
            "Produce actual per-week 23-ward and required-source query logs",
            "Run all released strict validators, protected-event gate and npm test",
            "Append exact update history and use the unchanged data-only CI path"
        ],
        "note": "An old event spanning a target week is a review candidate, NOT proof it runs every holiday."
    }


def main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument("--plan", type=Path, required=True)
    p.add_argument("--evidence-dir", type=Path, required=True)
    p.add_argument("--published-data", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    args = p.parse_args(argv)
    evidence = {name: read_json(args.evidence_dir / (name + ".json"))
                for name in ("summary", "candidate_pool")}
    packet = build_packet(read_json(args.plan), args.published_data, evidence)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(packet, ensure_ascii=False, indent=2) + "\n",
                           encoding="utf-8")
    print("REVIEW PACKET generated; publication still blocked; weeks=%d" % len(packet["weeks"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
