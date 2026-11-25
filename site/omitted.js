/* Read-only candidate curation. This script does not alter published event data. */
(() => {
  'use strict';
  const path = 'curation/suginami_review_20261022.json';
  const statuses = ['対象外','掲載候補','ステージング既登録','要確認','前回のみ・再取得要'];
  const human = {
    '対象外':'今回見送り','掲載候補':'掲載審査中',
    'ステージング既登録':'既登録','要確認':'要確認',
    '前回のみ・再取得要':'再取得待ち'
  };
  const el = id => document.getElementById(id);
  const results = el('omittedResults');
  const status = el('omittedStatus');
  const more = el('showMore');
  const search = el('omittedSearch');
  const tabs = [...document.querySelectorAll('#omittedTabs button[data-filter]')];
  let items = [];
  let current = '対象外';
  let visibleLimit = 40;

  // Never use untrusted data in innerHTML or arbitrary external hrefs.
  function text(tag, value, className) {
    const node = document.createElement(tag);
    if (className) node.className = className;
    node.textContent = String(value == null ? '' : value);
    return node;
  }
  function safeSourceUrl(value) {
    if (typeof value !== 'string') return null;
    try {
      const url = new URL(value);
      return url.protocol === 'https:' &&
        url.hostname === 'www.city.suginami.tokyo.jp' &&
        /^\/s\d+\/event\/\d+\.html$/.test(url.pathname) && !url.username && !url.password
        ? url.href : null;
    } catch (_) { return null; }
  }
  function createRow(row) {
    const card = document.createElement('details');
    card.className = 'omit-result';
    const summary = text('summary', '', 'omit-result-summary');
    const head = text('div', '', 'omit-result-head');
    head.appendChild(text('h3', row.title || '名称未確認'));
    const tag = text('span', human[row.status] || '判定待ち', 'omit-status-mark');
    if (row.status === '要確認' || row.status === '前回のみ・再取得要') tag.classList.add('pending');
    head.appendChild(tag);
    summary.appendChild(head);
    const reason = String(row.reason || '確認中').replace(/\s+/g, ' ').trim();
    const preview = Array.from(reason);
    summary.appendChild(text('p', '理由：' + preview.slice(0, 64).join('') + (preview.length > 64 ? '…' : ''), 'omit-reason-preview'));
    card.appendChild(summary);
    const content = text('div', '', 'omit-result-content');
    const facts = [row.date ? '開催日：' + row.date : null,
                   row.venue ? '会場：' + row.venue : null,
                   row.target ? '対象：' + row.target : null].filter(Boolean);
    if (facts.length) content.appendChild(text('p', facts.join('\n'), 'omit-facts'));
    const explanation = document.createElement('div');
    explanation.className = 'omit-reason';
    explanation.appendChild(text('b', '判定理由：'));
    explanation.appendChild(document.createTextNode(row.reason || '確認中'));
    content.appendChild(explanation);
    const foot = text('div', '', 'omit-result-footer');
    const url = safeSourceUrl(row.official_url);
    if (url) {
      const a = text('a', '杉並区の公式ページを見る ↗');
      a.href = url;
      a.target = '_blank';
      a.rel = 'noopener noreferrer';
      foot.appendChild(a);
    } else {
      foot.appendChild(text('small', '公式ページのリンク未取得。再確認待ち。'));
    }
    content.appendChild(foot);
    card.appendChild(content);
    return card;
  }
  function filtered() {
    const query = search.value.trim().normalize('NFKC').toLocaleLowerCase('ja-JP');
    return items.filter(row => row.status === current &&
      (!query || [row.title,row.reason,row.venue,row.date,row.target,row.id]
        .some(s => String(s || '').normalize('NFKC').toLocaleLowerCase('ja-JP').includes(query))));
  }
  function render() {
    const list = filtered();
    const fragment = document.createDocumentFragment();
    for (const item of list.slice(0, visibleLimit)) fragment.appendChild(createRow(item));
    results.replaceChildren(fragment);
    status.textContent = human[current] + '：' + list.length.toLocaleString('ja-JP') +
      '件' + (list.length > visibleLimit ? '（うち' + visibleLimit + '件を表示）' : '');
    if (list.length === 0) results.appendChild(text('p', '該当する候補はありません。', 'omit-status'));
    more.hidden = list.length <= visibleLimit;
  }
  function setFilter(value) {
    if (!statuses.includes(value)) return;
    current = value;
    visibleLimit = 40;
    for (const tab of tabs) {
      const selected = tab.dataset.filter === value;
      tab.classList.toggle('selected', selected);
      tab.setAttribute('aria-pressed', selected ? 'true' : 'false');
    }
    render();
  }
  tabs.forEach(btn => btn.addEventListener('click', () => setFilter(btn.dataset.filter)));
  search.addEventListener('input', () => { visibleLimit = 40; render(); });
  more.addEventListener('click', () => { visibleLimit += 40; render(); });

  async function initialize() {
    try {
      const res = await fetch(path, {cache: 'no-store'});
      if (!res.ok) throw Error('HTTP ' + res.status);
      const data = await res.json();
      if (data.schema_version !== 1 || !Array.isArray(data.rows) || data.rows.length !== 310 ||
          !statuses.every(s => Number.isInteger(data.counts?.[s]) &&
            data.rows.filter(x => x.status === s).length === data.counts[s])) {
        throw Error('snapshot not reconciled');
      }
      const seen = new Set();
      for (const row of data.rows) {
        if (typeof row.id !== 'string' || seen.has(row.id) || !statuses.includes(row.status))
          throw Error('invalid or duplicate decision record');
        seen.add(row.id);
      }
      items = data.rows;
      el('rejectedCount').textContent = String(data.counts['対象外']);
      el('candidateCount').textContent = String(data.counts['掲載候補']);
      el('existingCount').textContent = String(data.counts['ステージング既登録']);
      el('pendingCount').textContent = String(data.counts['要確認'] + data.counts['前回のみ・再取得要']);
      tabs.forEach(tab => {
        const n = tab.querySelector('span');
        if (n) n.textContent = String(data.counts[tab.dataset.filter] || 0);
      });
      render();
    } catch (error) {
      console.error('Curation audit unavailable', error);
      status.textContent = '判定一覧を読み込めませんでした。元の掲載データには影響ありません。';
      more.hidden = true;
    }
  }
  initialize();
})();
