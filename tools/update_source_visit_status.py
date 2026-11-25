#!/usr/bin/env python3
"""Write visit_status into site/data/discovery_sources.json from a read-only fetch round.

Usage: python3 tools/update_source_visit_status.py ROUND_DIR IDS_FILE DATE
ROUND_DIR holds STATUS.txt and pageN.html (N = line number in the round's urlsNN.txt);
IDS_FILE lists one source id per line in the same order (ids ending in __extra are skipped).
State: read (HTTP 2xx and the body has enough text and date-like strings),
       no_body (HTTP 2xx but nav-only/JS-rendered: little text or no dates),
       failed (non-2xx, timeout, or no response). A fetch failure is never success.
"""
import html, json, pathlib, re, sys
root = pathlib.Path(sys.argv[1]); ids = pathlib.Path(sys.argv[2]).read_text().split(); day = sys.argv[3]
reg_path = pathlib.Path(__file__).resolve().parent.parent / 'site/data/discovery_sources.json'
status = {}
for line in (root / 'STATUS.txt').read_text(errors='ignore').splitlines():
    m = re.match(r'page(\d+) (\S+) (\d{3}|FAIL)(?: (\d+))?$', line)
    if m:
        n = int(m.group(1)); code = m.group(3)
        if code != 'FAIL' and (n not in status or status[n][0] == 'FAIL'):
            status[n] = (code, m.group(2))
        elif n not in status:
            status[n] = (code, m.group(2))
DATE = re.compile(r'\d{1,2}月\d{1,2}日|\d{1,2}/\d{1,2}|20\d\d[./年-]\d{1,2}')
def classify(n):
    code, _ = status.get(n, ('FAIL', ''))
    if code == 'FAIL' or code == '000':
        return 'failed', '接続できず（タイムアウトまたは拒否）'
    if not code.startswith('2'):
        return 'failed', f'HTTP {code}'
    p = root / f'page{n}.html'
    raw = p.read_text(errors='ignore') if p.exists() else ''
    raw = re.sub(r'<(script|style)[^>]*>.*?</\1>', '', raw, flags=re.S)
    t = re.sub(r'\s+', '', html.unescape(re.sub(r'<[^>]+>', ' ', raw)))
    d = len(DATE.findall(t))
    if re.fullmatch(r'https://www\.tokyo-park\.or\.jp/park/[a-z_]+/', status.get(n, ('', ''))[1]):
        return 'no_body', f'HTTP {code}・公園の紹介ページ（イベントは「お知らせ」「イベント」の別ページにあり、個別取得が必要）'
    if len(t) >= 1000 and d >= 3:
        return 'read', f'HTTP {code}・本文約{len(t)}文字・日付表記{d}件'
    return 'no_body', f'HTTP {code}・本文約{len(t)}文字・日付表記{d}件（画面表示で本文なしの可能性）'
reg = json.loads(reg_path.read_text(encoding='utf-8'))
sites = {}
for i, sid in enumerate(ids, 1):
    if sid.endswith('__extra'):
        continue
    st, note = classify(i)
    sites[sid] = {'state': st, 'note': note}
listed = [s['id'] for s in reg['explicit_sources']] + [s['id'] for s in reg['ai_exploration_sites']['sites']]
reg['visit_status'] = {'checked_on': day, 'method': 'GitHub Actionsからの読み取り専用取得（第65回）。1ページ目のみ。',
                       'sites': {k: sites[k] for k in listed if k in sites}}
reg_path.write_text(json.dumps(reg, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
from collections import Counter
print(Counter(v['state'] for v in reg['visit_status']['sites'].values()), 'missing:', [k for k in listed if k not in sites])
