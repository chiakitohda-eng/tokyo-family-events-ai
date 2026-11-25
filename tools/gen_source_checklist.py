#!/usr/bin/env python3
"""Generate docs/SOURCE_REGISTRY_CHECKLIST.md from site/data/discovery_sources.json.

The checklist is the per-run visit list: every site shown on the page (fixed sites and
AI exploration sites) must be visited or recorded as unreachable in each update.
Run:  python3 tools/gen_source_checklist.py [--check]
"""
import json, sys, pathlib
ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = ROOT / 'site/data/discovery_sources.json'
OUT = ROOT / 'docs/SOURCE_REGISTRY_CHECKLIST.md'

def build():
    d = json.loads(SRC.read_text(encoding='utf-8'))
    L = ['# 取得元チェックリスト（自動生成・手編集しない）', '',
         '`site/data/discovery_sources.json` の全サイトを一覧にしたもの。サイトに載っている取得元はすべて、毎回の更新で「訪問した／取得できなかった（理由）」を記録する。',
         '再生成: `python3 tools/gen_source_checklist.py`（`tests/source_checklist_sync.test.mjs` が一覧との一致を検査する）。', '']
    ex = d['explicit_sources']
    L += [f'## A. 固定サイト（{len(ex)}件・登録済みの検索URLから機械的に取得）', '',
          '| id | 名称 | 取得URL |', '|---|---|---|']
    for s in ex:
        urls = s.get('search_urls') or [s.get('base_url', '')]
        L.append(f"| `{s['id']}` | {s.get('label','')} | {' '.join(urls)} |")
    ai = d['ai_exploration_sites']
    L += ['', f"## B. AI探索先サイト（{len(ai['sites'])}件・AIが候補探しの入口にする）", '']
    for g in ai['group_order']:
        items = [s for s in ai['sites'] if s['group'] == g]
        L += [f'### {g}（{len(items)}件）', '', '| id | 名称 | URL |', '|---|---|---|']
        for s in items:
            L.append(f"| `{s['id']}` | {s['label']} | {s['url']} |")
        L.append('')
    return '\n'.join(L).rstrip() + '\n'

if __name__ == '__main__':
    text = build()
    if '--check' in sys.argv:
        sys.exit(0 if OUT.exists() and OUT.read_text(encoding='utf-8') == text else 1)
    OUT.write_text(text, encoding='utf-8')
    print('wrote', OUT)
