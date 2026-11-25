import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';

const root = new URL('../', import.meta.url);
const read = path => readFileSync(new URL(path, root), 'utf8');
const page = read('site/omitted.html');
const index = read('site/index.html');
const js = read('site/omitted.js');
const data = JSON.parse(read('site/curation/suginami_review_20261022.json'));

assert.match(index, /href="omitted\.html"/, 'homepage must link to exclusion audit');
assert.match(page, /id="omittedResults"/);
assert.match(page, /id="omittedSearch"/);
assert.match(page, /id="omittedTabs"/);
assert.match(page, /id="showMore"/);
assert.match(js, /noopener noreferrer/);
assert.match(js, /replaceChildren/);

assert.equal(data.schema_version, 1);
assert.equal(data.as_of_jst, '2026-10-22');
assert.equal(data.rows.length, 310);
assert.equal(new Set(data.rows.map(r => r.id)).size, 310);
const expected = {
  '対象外': 200, '掲載候補': 95, 'ステージング既登録': 8,
  '要確認': 3, '前回のみ・再取得要': 4
};
assert.deepEqual(data.counts, expected);
for (const [status, n] of Object.entries(expected)) {
  assert.equal(data.rows.filter(x => x.status === status).length, n);
}
for (const row of data.rows) {
  assert.ok(row.id && row.title && row.reason && expected[row.status] !== undefined,
    'every row has an individual decision and explanation');
  if (row.official_url) {
    const u = new URL(row.official_url);
    assert.equal(u.protocol, 'https:');
    assert.equal(u.hostname, 'www.city.suginami.tokyo.jp');
    assert.match(u.pathname, /^\/s\d+\/event\/\d+\.html$/);
  } else {
    assert.equal(row.status, '前回のみ・再取得要', 'missing original URL must be flagged, not guessed');
  }
}
assert.equal(data.rows.filter(x => x.official_url).length, 306);
assert.equal(data.rows.find(x => x.id === 'suginami-official-27652').status, 'ステージング既登録');
assert.equal(data.rows.find(x => x.id === 'suginami-official-28531').status, 'ステージング既登録');
assert.equal(data.rows.find(x => x.id === 'suginami-official-28567').status, 'ステージング既登録');
console.log('PASS: 310 decision-page rows/links/statuses reconciled and homepage has access link.');

// Render the real script to check disclosures retain full evidence, filters and paging.
const {default:vm}=await import('node:vm');
class Node {
 constructor(tag='div'){this.tag=tag;this.textContent='';this.children=[];this.dataset={};this.listeners={};this.value='';this.hidden=false;this.open=false;this.classList={add(){},toggle(){}};}
 appendChild(n){this.children.push(n);return n;}
 replaceChildren(...xs){this.children=xs.flatMap(x=>x.tag==='#fragment'?x.children:[x]);}
 addEventListener(name,fn){this.listeners[name]=fn;}
 setAttribute(){}
 querySelector(){return this.count||(this.count=new Node('span'));}
}
const nodes=new Map(),tabs=Object.keys(expected).map(status=>{const n=new Node('button');n.dataset.filter=status;return n;});
const document={getElementById(id){if(!nodes.has(id))nodes.set(id,new Node());return nodes.get(id);},createElement:tag=>new Node(tag),createTextNode:s=>Object.assign(new Node('#text'),{textContent:s}),createDocumentFragment:()=>new Node('#fragment'),querySelectorAll:()=>tabs};
const context=vm.createContext({document,URL,fetch:async()=>({ok:true,json:async()=>data}),console});
vm.runInContext(js.replace('  initialize();','  globalThis.loadCuration=initialize;'),context);await context.loadCuration();
const flattened=n=>n.textContent+n.children.map(flattened).join('');
let rendered=nodes.get('omittedResults').children;
assert.equal(rendered.length,40);assert.ok(rendered.every(n=>n.tag==='details'&&!n.open));
for(const card of rendered){assert.equal(card.children[0].tag,'summary');assert.equal(card.children[1].className,'omit-result-content');assert.ok(flattened(card.children[0]).includes('理由：'));}
const original=data.rows.find(r=>r.status==='対象外');assert.ok(flattened(rendered[0].children[1]).includes(original.reason));
nodes.get('showMore').listeners.click();assert.equal(nodes.get('omittedResults').children.length,80);
tabs.find(n=>n.dataset.filter==='要確認').listeners.click();assert.equal(nodes.get('omittedResults').children.length,3);
assert.ok(nodes.get('showMore').hidden);
tabs.find(n=>n.dataset.filter==='対象外').listeners.click();nodes.get('omittedSearch').value=original.id;nodes.get('omittedSearch').listeners.input();assert.equal(nodes.get('omittedResults').children.length,1);
assert.ok(flattened(nodes.get('omittedResults').children[0]).includes(original.title));
console.log('PASS: collapsed curation rows preserve full reasons and sources; tabs, search and show-more retained');
