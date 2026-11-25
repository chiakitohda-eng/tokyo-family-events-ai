import assert from 'node:assert/strict';
import fs from 'node:fs';

const html=fs.readFileSync('site/index.html','utf8');
const css=fs.readFileSync('site/styles.css','utf8');
const sourceConfig=JSON.parse(fs.readFileSync('site/data/discovery_sources.json','utf8'));
const sources=sourceConfig.explicit_sources.filter(x=>x.enabled===true);

assert.ok(sources.length>=24,'existing fixed discovery sources must not vanish');
assert.ok(sources.every(x=>typeof x.label==='string' && x.label.trim()),'all displayed source labels need names');
assert.match(html,/id="logic"[^>]*aria-labelledby="logicTitle"/,'directory must be inside the extraction explanation');
assert.match(html,/id="fixedSourceDetails"/);
assert.match(html,/固定サイト（登録済み参照元）一覧/);
assert.match(html,/id="fixedSourceCount"/);
assert.match(html,/id="fixedSourceList"/);
assert.match(html,/loadDiscoverySources\(/,'render from live registry; no manually maintained list');
assert.match(html,/all\.filter\(source=>source && source\.enabled===true\)/);
assert.match(html,/source\.origin==='official'/);
assert.match(html,/source\.origin==='official_added'/);
assert.match(html,/従来からの固定サイト/);
assert.match(html,/追加登録した地域情報サイト/,'newly registered community sources must have their own section');
assert.match(html,/source\.origin==='manual'/,'manually added community sources must not be counted as legacy');
assert.match(html,/source\.origin==='legacy'/,'legacy section must include only legacy origins');
assert.doesNotMatch(html,/source\.origin!=='official'&&source\.origin!=='official_added'/,'non-official must not be mislabeled legacy');
assert.match(html,/その他の固定サイト（要分類）/,'new origins must remain visible instead of being mislabeled');
const originCounts = Object.groupBy(sources, source=>source.origin);
assert.equal((originCounts.official||[]).length+(originCounts.official_added||[]).length,11,'keep previous official sources and add Shinjuku Sankaku venue, GREEN SPRINGS (Tachikawa), Futako-Tamagawa Rise and Chuo-sen RR (Suginami) and Hachilabo (Shibuya)' );
assert.equal((originCounts.legacy||[]).length,18,'only 18 previous fixed sources');
assert.equal((originCounts.manual||[]).length,2,'two newly added community sites');
assert.ok((originCounts.manual||[]).some(source=>source.id==='tamemap_nakano'));
assert.ok((originCounts.manual||[]).some(source=>source.id==='itabashi_times_event'));
assert.deepEqual([...new Set(sources.map(source=>source.id))].length,sources.length,'no source IDs duplicated');
assert.ok(sources.every(source=>['official','official_added','manual','legacy'].includes(source.origin)),'unclassified source needs a new explicit group');
assert.match(html,/safeHttpUrl\(source\.annual_listing_url\|\|source\.base_url\|\|source\.search_urls\?\.\[0\]\)/);
assert.match(html,/escapeHtml\(source\.annual_listing_label\|\|source\.label/);
assert.match(html,/target="_blank" rel="noopener noreferrer"/);
assert.match(html,/catch\(error\)[\s\S]*固定サイト一覧を取得できませんでした/);
assert.match(css,/\.logic-fixed-sources-group ul/);
assert.match(css,/@media\(max-width:520px\)[^{]*\{\.logic-fixed-sources/);
for(const id of ['nakano_official_tourism','itabashi_official_festival','itabashi_tourism_festival','tamemap_nakano','itabashi_times_event','shinjuku_sankaku_hiroba','greensprings_tachikawa','futako_tamagawa_rise','chuosen_rr_suginami','hachilabo_shibuya']){
  assert.ok(sources.some(x=>x.id===id),'new official source included: '+id);
}
assert.ok(sources.some(x=>x.id==='nakano'),'legacy Nakano source retained');
assert.ok(sources.some(x=>x.id==='nerima_district_festivals_2026'),'official Nerima table retained');
console.log('Fixed-source directory visibility / dynamic source / mobile safeguards: OK ('+sources.length+' sources)');

// AI exploration entry sites are listed separately from fixed sources (explicit_sources stays untouched).
const aiSites=sourceConfig.ai_exploration_sites?.sites||[];
assert.ok(aiSites.length>=90,'AI exploration sites must include wards, Tama cities, parks and facilities');
const aiGroups=new Set(aiSites.map(x=>x.group));
assert.equal(aiGroups.size,6,'AI sites use exactly six clean groups');
assert.deepEqual(sourceConfig.ai_exploration_sites.group_order.slice().sort(),[...aiGroups].sort(),'group_order matches groups');
assert.equal(new Set(aiSites.map(x=>x.id)).size,aiSites.length,'AI exploration site ids unique');
assert.ok(aiSites.every(x=>x.label&&x.group&&/^https:\/\//.test(x.url)),'AI exploration sites need label, group and https url');
assert.ok(aiSites.some(x=>x.id==='ai_yomiuriland')&&aiSites.some(x=>x.id==='ai_puroland'));
assert.match(html,/ai_exploration_sites/);
assert.match(html,/id="aiSourceDetails"/);
assert.match(html,/id="aiSourceList"/);
assert.match(html,/AI探索先サイト（候補探しの入口）一覧/);
assert.match(html,/renderAiSources\(registry\)/);
assert.ok(!sourceConfig.explicit_sources.some(x=>String(x.id).startsWith('ai_')),'AI sites must not be mixed into fixed sources');

// Visit status (2026-11-22): every listed site shows how its last fetch went.
{
  assert.match(html,/function visitBadge\(/);
  assert.match(html,/visit_status/);
  const vs=sourceConfig.visit_status;
  assert.ok(vs&&vs.checked_on&&vs.sites&&typeof vs.sites==='object','visit_status.sites must exist');
  const ids=[...sourceConfig.explicit_sources.map(s=>s.id),...sourceConfig.ai_exploration_sites.sites.map(s=>s.id)];
  const missing=ids.filter(id=>!vs.sites[id]);
  assert.deepEqual(missing,[],'every listed site needs a visit state (use read/no_body/failed)');
  assert.ok(Object.values(vs.sites).every(v=>['read','no_body','failed'].includes(v.state)));
}
