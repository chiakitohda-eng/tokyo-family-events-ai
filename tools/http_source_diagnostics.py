"""Fail-closed bounded HTTP-error evidence and official INDEX fallback policy.

A successful official index does not make a missing article or an unavailable
required source 'checked'. No captcha, UA spoofing, or automatic publication.
"""
import hashlib
import html
import re
from urllib.parse import urlsplit

MAX_ERROR_BYTES = 4096
TITLE = re.compile(r"<title(?:\s[^>]*)?>(.*?)</title\s*>", re.I | re.S)
ALLOWED_OFFICIAL_INDEX = {
    "www.city.suginami.tokyo.jp": ("https://www.city.suginami.tokyo.jp/event/index.html",),
    "www.city.tokyo-nakano.lg.jp": ("https://www.city.tokyo-nakano.lg.jp/event/calendar/list_calendar.html",),
    "www.city.nerima.tokyo.jp": ("https://www.city.nerima.tokyo.jp/kankomoyoshi/event/calendar/list_calendar.html",),
}

def diagnostic_for_html_challenge(raw, final_url, http_status=200, content_type=""):
    """Recognize a known challenge interstitial even when it returns HTTP 200.

    Require both its characteristic document title and challenge script marker;
    ordinary pages mentioning Cloudflare or using its analytics remain usable.
    Only the bounded signature is retained, never the challenge page body.
    """
    bounded = raw[:MAX_ERROR_BYTES]
    body = bounded.decode("utf-8", errors="replace")
    found = TITLE.search(body)
    title = html.unescape(re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", found.group(1)))).strip()[:160] if found else ""
    if (not re.fullmatch(r"just a moment[.!…\s]*", title, re.I)
            or not any(marker in body.lower() for marker in ("cf-chl", "challenge-platform"))):
        return None
    return {
        "http_status": http_status,
        "final_url": str(final_url or "")[:1200],
        "response_content_type": str(content_type or "")[:180],
        "response_title": title,
        "error_body_sha256": hashlib.sha256(bounded).hexdigest(),
        "error_body_truncated": len(raw) > MAX_ERROR_BYTES,
        "cloudflare_challenge_detected": True,
        "challenge_detected": True,
        "error_kind": "security_challenge",
        "retryable_http_error": False,
    }

def diagnostic_for_http_error(error):
    """Record a bounded response signature without storing arbitrary page HTML."""
    headers = error.headers
    def header(key):
        return str(headers.get(key, "") or "")[:180] if headers else ""
    raw = error.read(MAX_ERROR_BYTES + 1)
    bounded = raw[:MAX_ERROR_BYTES]
    body = bounded.decode("utf-8", errors="replace")
    found = TITLE.search(body)
    title = html.unescape(re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", found.group(1)))).strip()[:160] if found else ""
    server = header("Server")
    lower = body.lower()
    cloudflare = "cloudflare" in server.lower() and (
        "just a moment" in lower or "cf-chl" in lower or "challenge-platform" in lower
    )
    if error.code == 403 and cloudflare:
        kind = "security_challenge"
    elif error.code == 404 and ("ページが見つかりません" in title or "お探しのページは見つかりません" in title):
        kind = "official_page_not_found"
    elif error.code == 404:
        kind = "ambiguous_http_404"
    elif error.code in (429, 500, 502, 503, 504):
        kind = "retryable_http_error"
    else:
        kind = "http_error"
    return {
        "http_status": error.code,
        "final_url": str(error.geturl() or "")[:1200],
        "response_server": server,
        "response_content_type": header("Content-Type"),
        "response_title": title,
        "error_body_sha256": hashlib.sha256(bounded).hexdigest(),
        "error_body_truncated": len(raw) > MAX_ERROR_BYTES,
        "cloudflare_challenge_detected": cloudflare,
        "challenge_detected": cloudflare,
        "response_cf_ray_present": bool(header("CF-Ray")),
        "error_kind": kind,
        "retryable_http_error": error.code in (429, 500, 502, 503, 504),
    }

def suggested_official_index(url, http_status):
    """Return only a known OFFICIAL INDEX, never an unverified event detail."""
    if http_status != 404:
        return None
    try:
        parsed = urlsplit(url)
        if parsed.scheme != "https" or parsed.username or parsed.password or parsed.port not in (None,443):
            return None
        host = (parsed.hostname or "").lower()
        path = parsed.path
    except (ValueError, TypeError):
        return None
    if host == "www.city.suginami.tokyo.jp" and not re.fullmatch(r"/s\d+/event/\d+\.html",path):
        return None
    if host == "www.city.tokyo-nakano.lg.jp" and not path.startswith("/"):
        return None
    if host == "www.city.nerima.tokyo.jp" and not path.startswith("/kankomoyoshi/"):
        return None
    values = ALLOWED_OFFICIAL_INDEX.get(host)
    return values[0] if values else None

def official_index_fallback_proof(source_url, http_status, fetch_index):
    """Fetch a known municipal index but retain original failed status.

    fetch_index returns {'status':..., 'http_status':...}. Never returns
    event-level approval and never changes original HTTP error.
    """
    alternative = suggested_official_index(source_url, http_status)
    if not alternative:
        return None
    observed = fetch_index(alternative)
    success = observed.get("status") in ("checked", "checked_body_not_individually_verified")
    return {
        "fallback_url": alternative,
        "fallback_status": observed.get("status", "error"),
        "fallback_http_status": observed.get("http_status"),
        "fallback_index_reachable": bool(success),
        "original_source_still_failed": True,
        "event_detail_verified": False,
        "decision_reconciliation": "pending",
        "note": "Official index reachability is NOT proof that this event's original detail, schedule, venue or selection was verified.",
    }
