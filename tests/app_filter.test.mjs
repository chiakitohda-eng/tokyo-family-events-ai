import assert from 'node:assert/strict';
import {filterEvents,normalizeText,countsByWard,applyVerification,rollingWeekSlots,publicationTierMeta,verificationStateMeta,verificationSourceHeading,familyFitAxisRows,heroSeasonForDate,heroSeasonMeta,recommendationStarCount,eventPriceCategory,eventPriceLabel,classifyDiscoveryProvenance,eventDiscoveryProvenance,findDecisionForEvent,buildCopyUrl,serializeEventFilters,indoorOutdoorCategory,indoorOutdoorLabel,reservationCategory,reservationLabel,holidayPeriodSlots,holidayTabMeta,holidayRangeLabel,eventsOverlappingPeriod,mergeEventsAcrossWeeks} from '../site/app.js';

const rangeBookmark=serializeEventFilters({range:{start:'2026-10-31',end:'2026-11-03'},dates:[],wards:['練馬区']});
assert.equal(new URLSearchParams(rangeBookmark).get('from'),'2026-10-31');
assert.equal(new URLSearchParams(rangeBookmark).get('to'),'2026-11-03');
assert.equal(new URLSearchParams(rangeBookmark).get('w'),'練馬区');
assert.equal(new URLSearchParams(rangeBookmark).has('d'),false);
const axes={
  child_target:{grade:'A',reason:'親子対象'},
  interactivity:{grade:'A',reason:'体験あり'},
  age_fit:{grade:'A',reason:'幼児小学生向け'},
  stay_flexibility:{grade:'B',reason:'時間枠あり'},
  burden:{grade:'A',reason:'負担小'},
  cost:{grade:'A',reason:'無料'},
  reservation:{grade:'B',reason:'事前予約'},
  family_value:{grade:'A',reason:'家族で行く価値が高い'}
};
const events=[
  {id:'suginami-plafes',ward:'杉並区',name:'高円寺プラフェス 2026秋',period:'10/10〜10/11',date_end:'2026-10-11',venue:'IMAGINUS',description:'巨大レイアウトでプラレールを走らせる親子イベント',categories:['電車','プラレール'],family_fit:{grade:'A',overall:'A',reason:'幼児・小学生を中心に親子で楽しめる',age:'子ども〜大人',axes},reservation:{required:true,note:'事前予約'}},
  {id:'edogawa-festival',ward:'江戸川区',name:'江戸川区民まつり',venue:'都立篠崎公園',description:'親子向け体験・動物・キッズステージ',categories:['祭り','動物']}
];

assert.equal(filterEvents(events,{ward:'杉並区',q:''}).length,1);
assert.equal(filterEvents(events,{ward:'__all__',q:'プラレール'}).length,1);
assert.equal(filterEvents(events,{ward:'杉並区',q:'IMAGINUS'}).length,1);
assert.equal(filterEvents(events,{ward:'杉並区',q:'いまじなす'}).length,0);
assert.equal(filterEvents(events,{ward:'江戸川区',q:'動物'}).length,1);
assert.equal(filterEvents(events,{ward:'杉並区',q:'家族価値'}).length,1);
assert.equal(filterEvents(events,{ward:'杉並区',q:'負担小'}).length,1);
assert.equal(normalizeText('  ＡＢＣ　１２３  '),'abc 123');
assert.equal(familyFitAxisRows(events[0].family_fit).length,8);
assert.equal(familyFitAxisRows(events[1].family_fit).length,0);
assert.equal(recommendationStarCount(events[0]),3);
assert.equal(filterEvents(events,{ward:'__all__',q:'',recMin:3}).length,1);
const priceCases=[
  {price:'無料'},
  {price:'入場無料（一部ワークショップ有料）'},
  {price:'小学生以下無料、大人2,000円'},
  {price:'一般500円'}
];
assert.equal(eventPriceCategory(priceCases[0]),'free');
assert.equal(eventPriceCategory(priceCases[1]),'free');
assert.equal(eventPriceCategory(priceCases[2]),'mixed');
assert.equal(eventPriceCategory(priceCases[3]),'paid');
assert.equal(filterEvents(priceCases,{price:'free'}).length,2);
assert.equal(filterEvents(priceCases,{price:'mixed'}).length,1);
assert.equal(filterEvents(priceCases,{price:'paid'}).length,1);
console.log('price + recommendation filters: OK');
assert.equal(eventPriceLabel(priceCases[0]),'無料');
assert.equal(eventPriceLabel(priceCases[1]),'無料');
assert.equal(eventPriceLabel(priceCases[2]),'無料あり');
assert.equal(eventPriceLabel(priceCases[3]),'有料');
assert.equal(eventPriceLabel({price:null}),'料金要確認');
console.log('price badge labels: OK');
assert.equal(indoorOutdoorLabel('indoor'),'屋内');
assert.equal(indoorOutdoorLabel('outdoor'),'屋外');
assert.equal(indoorOutdoorLabel('mixed'),'屋内・屋外');
assert.equal(indoorOutdoorCategory('屋内外'),'mixed');
const envCases=[{indoor_outdoor:'indoor'},{indoor_outdoor:'屋内'},{indoor_outdoor:'outdoor'},{indoor_outdoor:'屋外'},{indoor_outdoor:'mixed'}];
assert.equal(filterEvents(envCases,{environment:'indoor'}).length,2);
assert.equal(filterEvents(envCases,{environment:'outdoor'}).length,2);
assert.equal(filterEvents(envCases,{environment:'mixed'}).length,1);
const mergeWeekA={sat:'2026-10-10',events:[{id:'a1',name:'同名イベント',date_start:'2026-10-10',date_end:'2026-10-10',venue:'会場A',official_url:'https://example.jp/e',verification:{status:'verified'}}]};
const mergeWeekB={sat:'2026-10-17',events:[{id:'a2',name:'同名イベント',date_start:'2026-10-17',date_end:'2026-10-17',venue:'会場A',official_url:'https://example.jp/e',verification:{status:'verified'}}]};
const mergeSameA={sat:'2026-10-10',events:[{id:'b1',name:'長期イベント',date_start:'2026-10-01',date_end:'2026-11-30',venue:'会場B',official_url:'https://example.jp/long',verification:{status:'verified'}}]};
const mergeSameB={sat:'2026-10-17',events:[{id:'b2',name:'長期イベント',date_start:'2026-10-01',date_end:'2026-11-30',venue:'会場B',official_url:'https://example.jp/long',verification:{status:'announced'}}]};
assert.equal(mergeEventsAcrossWeeks([mergeWeekA,mergeWeekB]).length,2);
assert.equal(mergeEventsAcrossWeeks([mergeSameA,mergeSameB]).length,1);
console.log('stable indoor/outdoor + date-sensitive all-period merge: OK');
const reservationCases=[
  {reservation:{required:false,note:'事前申込不要、直接会場へ'}},
  {reservation:{required:true,note:'オンライン予約制'}},
  {reservation:{required:null,note:'企画により事前申込が必要。無料企画は当日参加可。'}},
  {reservation:{required:null,note:'参加方法・空き状況は公式ページで確認。'}}
];
assert.equal(reservationCategory(reservationCases[0]),'none');
assert.equal(reservationCategory(reservationCases[1]),'required');
assert.equal(reservationCategory(reservationCases[2]),'partial');
assert.equal(reservationCategory(reservationCases[3]),'unknown');
assert.equal(reservationLabel(reservationCases[0]),'申込不要');
assert.equal(reservationLabel(reservationCases[1]),'要事前申込');
assert.equal(reservationLabel(reservationCases[2]),'一部要申込');
assert.equal(reservationLabel(reservationCases[3]),'申込要確認');
assert.equal(filterEvents(reservationCases,{reservation:'none'}).length,1);
assert.equal(filterEvents(reservationCases,{reservation:'required'}).length,1);
assert.equal(filterEvents(reservationCases,{reservation:'partial'}).length,1);
assert.equal(filterEvents(reservationCases,{reservation:'unknown'}).length,1);
console.log('reservation filter + labels: OK');
const environmentCases=[
  {indoor_outdoor:'indoor'},
  {indoor_outdoor:'屋内'},
  {indoor_outdoor:'outdoor'},
  {indoor_outdoor:'屋外'},
  {indoor_outdoor:'mixed'},
  {indoor_outdoor:'屋内外'}
];
assert.equal(indoorOutdoorCategory(environmentCases[0]),'indoor');
assert.equal(indoorOutdoorCategory(environmentCases[1]),'indoor');
assert.equal(indoorOutdoorCategory(environmentCases[2]),'outdoor');
assert.equal(indoorOutdoorCategory(environmentCases[3]),'outdoor');
assert.equal(indoorOutdoorCategory(environmentCases[4]),'mixed');
assert.equal(indoorOutdoorCategory(environmentCases[5]),'mixed');
assert.equal(indoorOutdoorLabel(environmentCases[0]),'屋内');
assert.equal(indoorOutdoorLabel(environmentCases[2]),'屋外');
assert.equal(indoorOutdoorLabel(environmentCases[4]),'屋内・屋外');
assert.equal(filterEvents(environmentCases,{environment:'indoor'}).length,2);
assert.equal(filterEvents(environmentCases,{environment:'outdoor'}).length,2);
assert.equal(filterEvents(environmentCases,{environment:'mixed'}).length,2);
const mergedPeriods=mergeEventsAcrossWeeks([
  {sat:'2026-10-10',events:[{id:'a1',name:'長期イベント',venue:'会場A',official_url:'https://example.jp/e/1',description:'短い'}],decision_audit:{decisions:[{candidate_id:'a1',name:'長期イベント',ward:'',discovery_sources:[{channel:'ai_cross',url:'https://search.example/a'}]}]}},
  {sat:'2026-10-17',events:[{id:'a2',name:'長期イベント',venue:'会場A',official_url:'https://example.jp/e/1',description:'より詳しい説明'}],decision_audit:{decisions:[{candidate_id:'a2',name:'長期イベント',ward:'',discovery_sources:[{channel:'explicit',source_id:'manual-x',url:'https://events.example.jp/'}]}]}}
]);
assert.equal(mergedPeriods.length,1);
assert.equal(mergedPeriods[0]._decision_rows.length,2);
assert.equal(mergedPeriods[0].description,'より詳しい説明');
console.log('indoor/outdoor normalization + all-period merge: OK');

const counts=countsByWard(events);assert.equal(counts['杉並区'],1);assert.equal(counts['江戸川区'],1);assert.equal(counts['中野区'],0);

const audit={verified_on:'2026-10-06',events:[
  {id:'suginami-plafes',status:'verified',source:'https://example.com/official',source_kind:'organizer_official',fields:{name:'pass',date:'corrected',venue:'corrected'},note:'公式確認済み',corrections:{period:'10/10〜10/12',date_end:'2026-10-12',venue:'IMAGINUS 3階 企画展示室'}},
  {id:'edogawa-festival',status:'announced',source:'https://example.com/announcement',source_kind:'official',fields:{name:'pass',date:'pass',venue:'pass',time:'unknown',price:'unknown'},note:'開催日と会場は公式発表済み。時間と料金は後日発表。',corrections:{}}
]};
const corrected=applyVerification(events,audit);assert.equal(corrected[0].period,'10/10〜10/12');assert.equal(corrected[0].date_end,'2026-10-12');assert.equal(corrected[0].venue,'IMAGINUS 3階 企画展示室');assert.equal(corrected[0].verification.status,'verified');assert.equal(corrected[0].verification.verified_on,'2026-10-06');assert.equal(corrected[1].verification.status,'announced');assert.equal(filterEvents(corrected,{ward:'杉並区',q:'企画展示室'}).length,1);assert.equal(filterEvents(corrected,{ward:'江戸川区',q:'詳細待ち'}).length,1);

const manifest={default:'2026-10-10',rolling_horizon_weeks:6,weekends:[{sat:'2026-10-10',sun:'2026-10-11',publication_tier:'full',horizon_index:1,count:37},{sat:'2026-10-24',sun:'2026-10-25',publication_tier:'preview',horizon_index:3,count:12}]};
const slots=rollingWeekSlots(manifest);assert.equal(slots.length,6);assert.equal(slots[0].sat,'2026-10-10');assert.equal(slots[1].sat,'2026-10-17');assert.equal(slots[1].available,false);assert.equal(slots[2].publication_tier,'preview');assert.equal(slots[4].publication_tier,'announcement');assert.equal(publicationTierMeta('preview').label,'先取り');assert.equal(verificationStateMeta('verified').label,'✓ 公式確認済み');assert.equal(verificationStateMeta('verified','organizer_partner').label,'✓ 確認済み');assert.equal(verificationSourceHeading({status:'verified',source_kind:'official'}),'公式確認');assert.equal(verificationSourceHeading({status:'verified',source_kind:'organizer_partner'}),'確認');assert.equal(verificationStateMeta('announced').label,'○ 開催発表済み・詳細待ち');

assert.equal(heroSeasonForDate('2027-04-10'),'spring');assert.equal(heroSeasonForDate('2027-07-10'),'summer');assert.equal(heroSeasonForDate('2027-09-10'),'autumn');assert.equal(heroSeasonForDate('2026-10-10'),'autumn');assert.equal(heroSeasonForDate('2026-11-10'),'autumn');assert.equal(heroSeasonForDate('2026-12-10'),'winter');assert.match(heroSeasonMeta('winter').source,/unsplash\.com/);
const holidayManifest={
  default:'2026-10-10',
  rolling_horizon_weeks:6,
  holidays:[{date:'2026-10-12',name:'スポーツの日'},{date:'2026-11-03',name:'文化の日'}],
  weekends:[
    {sat:'2026-10-10',sun:'2026-10-11',publication_tier:'full',count:10},
    {sat:'2026-10-17',sun:'2026-10-18',publication_tier:'full',count:10},
    {sat:'2026-10-24',sun:'2026-10-25',publication_tier:'preview',count:10},
    {sat:'2026-10-31',sun:'2026-11-01',publication_tier:'preview',count:10},
    {sat:'2026-11-07',sun:'2026-11-08',publication_tier:'announcement',count:10},
    {sat:'2026-11-14',sun:'2026-11-15',publication_tier:'announcement',count:10}
  ]
};
const holidayPeriods=holidayPeriodSlots(holidayManifest);
assert.equal(holidayPeriods[0].start,'2026-10-10');
assert.equal(holidayPeriods[0].end,'2026-10-12');
assert.deepEqual(holidayTabMeta(holidayPeriods[0],holidayManifest),{primary:'10/10–12',secondary:'土〜月・祝'});
const culture=holidayPeriods.find(x=>x.start==='2026-11-03');
assert.ok(culture);
assert.equal(culture.kind,'holiday');
assert.deepEqual(holidayTabMeta(culture,holidayManifest),{primary:'11/3',secondary:'火・祝'});
assert.equal(holidayRangeLabel('2026-10-10','2026-10-12',holidayManifest),'2026/10/10(土) 〜 10/12(月・祝)');
const holidayEvents=[
  {date_start:'2026-11-01',date_end:'2026-11-03'},
  {date_start:'2026-11-03',date_end:'2026-11-03'},
  {date_start:'2026-11-04',date_end:'2026-11-05'}
];
assert.equal(eventsOverlappingPeriod(holidayEvents,'2026-11-03','2026-11-03').length,2);
console.log('holiday period tabs: OK');

console.log('hero seasonal background policy: OK');
const provenanceRegistry={explicit_sources:[
  {id:'nakano',label:'中野',enabled:true,base_url:'https://www.nakanoevent.com/',search_urls:['https://www.nakanoevent.com/']},
  {id:'manual-x',label:'追加媒体',enabled:true,base_url:'https://events.example.jp/',search_urls:['https://events.example.jp/']}
]};
const legacyDecision={candidate_id:'legacy-1',name:'旧媒体イベント',ward:'中野区',discovery_sources:[
  {kind:'legacy_media',url:'https://www.nakanoevent.com/'},
  {kind:'legacy_detail',url:'https://www.nakanoevent.com/sample/'}
]};
const aiDecision={candidate_id:'ai-1',name:'AIイベント',ward:'中野区',discovery_sources:[
  {channel:'ai_cross',kind:'web_search',url:'https://example.org/event'}
]};
const bothDecision={candidate_id:'both-1',name:'両方イベント',ward:'中野区',discovery_sources:[
  {channel:'explicit',source_id:'manual-x',kind:'explicit_source',url:'https://events.example.jp/'},
  {channel:'ai_cross',kind:'web_search',url:'https://search.example/event'}
]};
assert.equal(classifyDiscoveryProvenance(null,legacyDecision,provenanceRegistry).channel,'explicit');
assert.equal(classifyDiscoveryProvenance(null,legacyDecision,provenanceRegistry).explicitSources[0].label,'中野');
assert.equal(classifyDiscoveryProvenance(null,aiDecision,provenanceRegistry).channel,'ai_cross');
assert.equal(classifyDiscoveryProvenance(null,bothDecision,provenanceRegistry).channel,'both');
// Source-scope search: events found by both paths belong to both individual modes.
const bySource=[
  {id:'ai',name:'AI only',ward:'中野区',_decision_rows:[aiDecision]},
  {id:'fixed',name:'Fixed only',ward:'中野区',_decision_rows:[legacyDecision]},
  {id:'both',name:'Both',ward:'中野区',_decision_rows:[bothDecision]},
  {id:'unknown',name:'Unknown origin',ward:'中野区'}
];
assert.deepEqual(filterEvents(bySource,{sourceMode:'ai_cross',registry:provenanceRegistry}).map(x=>x.id),['ai','both']);
assert.deepEqual(filterEvents(bySource,{sourceMode:'explicit',registry:provenanceRegistry}).map(x=>x.id),['fixed','both']);
assert.deepEqual(filterEvents(bySource,{sourceMode:'all',registry:provenanceRegistry}).map(x=>x.id),['ai','fixed','both','unknown']);
assert.equal(filterEvents(bySource,{sourceMode:'invalid'}).length,4);
assert.equal(filterEvents(bySource,{sourceMode:'explicit',registry:provenanceRegistry,ward:'渋谷区'}).length,0);
assert.equal(eventDiscoveryProvenance(bySource[2],null,provenanceRegistry).channel,'both');
// Six-week dedup preserves decision rows for every week.
assert.equal(mergedPeriods.length,1);
assert.equal(eventDiscoveryProvenance(mergedPeriods[0],null,provenanceRegistry).channel,'both');
assert.equal(filterEvents(mergedPeriods,{sourceMode:'ai_cross',registry:provenanceRegistry}).length,1);
assert.equal(filterEvents(mergedPeriods,{sourceMode:'explicit',registry:provenanceRegistry}).length,1);
// Single-week data uses its audit if no combined decision rows exist.
assert.equal(filterEvents([{id:'ai-1',ward:'中野区'}],{sourceMode:'ai_cross',decisionAudit:{decisions:[aiDecision]},registry:provenanceRegistry}).length,1);
assert.equal(new URL(buildCopyUrl({date:'all',sourceMode:'explicit'}),'https://example.com/').searchParams.get('src'),'explicit');
assert.equal(new URL(buildCopyUrl({date:'all',sourceMode:'all'}),'https://example.com/').searchParams.has('src'),false);
// Multi-selection must preserve OR within a group and AND across groups.
const multiScope=[
  {id:'a',name:'Free indoor',ward:'中野区',price:'無料',indoor_outdoor:'indoor',date_start:'2026-10-10',date_end:'2026-10-10',family_fit:{overall:'A'},_decision_rows:[aiDecision]},
  {id:'b',name:'Paid outdoor',ward:'杉並区',price:'有料',indoor_outdoor:'outdoor',date_start:'2026-10-17',date_end:'2026-10-17',family_fit:{overall:'B'},_decision_rows:[legacyDecision]},
  {id:'c',name:'Mixed indoor',ward:'渋谷区',price:'無料／一部有料',indoor_outdoor:'indoor',date_start:'2026-10-10',date_end:'2026-10-18',family_fit:{overall:'C'},_decision_rows:[bothDecision]}
];
assert.deepEqual(filterEvents(multiScope,{wards:['中野区','杉並区']}).map(x=>x.id),['a','b']);
assert.deepEqual(filterEvents(multiScope,{prices:['free','paid']}).map(x=>x.id),['a','b']);
assert.deepEqual(filterEvents(multiScope,{wards:['中野区','杉並区'],prices:['free'],environments:['indoor']}).map(x=>x.id),['a']);
assert.deepEqual(filterEvents(multiScope,{ratings:['2','3']}).map(x=>x.id),['a','b']);
assert.deepEqual(filterEvents(multiScope,{sourceModes:['ai_cross'],registry:provenanceRegistry}).map(x=>x.id),['a','c']);
assert.deepEqual(filterEvents(multiScope,{sourceModes:['explicit'],registry:provenanceRegistry}).map(x=>x.id),['b','c']);
assert.deepEqual(filterEvents(multiScope,{sourceModes:['ai_cross','explicit'],registry:provenanceRegistry}).map(x=>x.id),['a','b','c']);
assert.deepEqual(filterEvents(multiScope,{periods:[{start:'2026-10-10',end:'2026-10-11'}]}).map(x=>x.id),['a','c']);
assert.deepEqual(filterEvents(multiScope,{periods:[{start:'2026-10-10',end:'2026-10-11'},{start:'2026-10-17',end:'2026-10-18'}]}).map(x=>x.id),['a','b','c']);
assert.deepEqual(filterEvents(multiScope,{periods:[{start:'2026-10-17',end:'2026-10-18'}],wards:['杉並区']}).map(x=>x.id),['b']);
const encoded=serializeEventFilters({q:'祭り',dates:['2026-10-10','2026-10-17'],wards:['中野区','杉並区'],prices:['free','paid'],ratings:['3','2'],sourceModes:['ai_cross']});
const params=new URLSearchParams(encoded);
assert.deepEqual(params.getAll('d'),['2026-10-10']);
assert.deepEqual(params.getAll('w'),['中野区','杉並区']);
assert.deepEqual(params.getAll('p'),['free','paid']);
assert.deepEqual(params.getAll('star'),['3','2']);
assert.deepEqual(params.getAll('s'),['ai_cross']);
assert.equal(params.get('q'),'祭り');
assert.equal(new URL(buildCopyUrl({dates:['2026-10-10','2026-10-17'],wards:['中野区','杉並区']}),'https://example.com/').searchParams.getAll('w').length,2);
assert.deepEqual(new URL(buildCopyUrl({dates:['2026-10-10','2026-10-17']}),'https://example.com/').searchParams.getAll('d'),['2026-10-10']);
const fsSourceUI=(await import('node:fs')).default;
const sharedUI=fsSourceUI.readFileSync(new URL('../site/multi-filter-ui.js',import.meta.url),'utf8');
assert.match(sharedUI,/type="checkbox"/);
assert.match(sharedUI,/initialState/);
assert.match(sharedUI,/state\.dates\.add/);
assert.match(sharedUI,/function choosePeriod\(value\)/);
assert.match(sharedUI,/state\.dates\.clear\(\);\s*customRange=null;\s*if\(value!=='all'\)state\.dates\.add\(value\)/);
assert.match(sharedUI,/const validDate=params\.getAll\('d'\)\.find/);
assert.match(sharedUI,/weekTabs'\)\.addEventListener\('click',handleWeek\)/);
assert.doesNotMatch(sharedUI,/input type="checkbox" data-date/);
assert.match(sharedUI,/button type="button" class="week-tab/);
assert.match(sharedUI,/input type="checkbox" data-ward/);
assert.match(sharedUI,/toggleSet\(state\.wards/);
for(const page of ['search.html','copy.html']){
  const markup=fsSourceUI.readFileSync(new URL('../site/'+page,import.meta.url),'utf8');
  assert.match(markup,/id="filterPanel"/);
  assert.match(markup,/id="filterGroups"/);
  assert.match(markup,/id="filterSummary"/);
  assert.match(markup,/createMultiFilterUI/);
  assert.match(markup,/filterUI\.serialize/);
  assert.doesNotMatch(markup,/id="sourceSelect"/);
  assert.match(markup,/aria-label="全期間または1つの週末・祝日を選択"/);
  assert.match(markup,/指定期間で検索/);
  assert.match(markup,/id="dateEndInput"/);
  assert.match(markup,/id="filterCloseBtn"/);
  assert.match(markup,/id="filterApplyBtn"/);
  assert.match(markup,/class="multi-filter-backdrop"/);
  assert.match(markup,/class="multi-filter-body"/);
}
assert.match(sharedUI,/\$\('filterCloseBtn'\)\.addEventListener\('click'/);
assert.match(sharedUI,/\$\('filterApplyBtn'\)\.addEventListener\('click'/);
assert.match(sharedUI,/\.multi-filter-backdrop'\)\.addEventListener\('click'/);
assert.match(sharedUI,/document\.addEventListener\('pointerdown'/);
assert.match(sharedUI,/document\.addEventListener\('keydown'/);
assert.match(sharedUI,/panel\.open=false/);
const filterCSS=fsSourceUI.readFileSync(new URL('../site/styles.css',import.meta.url),'utf8');
assert.match(filterCSS,/\.multi-filter-sheet-header/);
assert.match(filterCSS,/\.multi-filter-actions/);
assert.match(filterCSS,/\.multi-filter-body\s*\{/);
assert.match(filterCSS,/safe-area-inset-bottom/);
console.log('multi-selection OR/AND, URL state, cross-week date + search/copy UI: OK');
const matchAudit={decisions:[{candidate_id:'other-id',name:'江戸川区民まつり',ward:'江戸川区',discovery_sources:[]}]};
assert.equal(findDecisionForEvent(events[1],matchAudit)?.name,'江戸川区民まつり');
console.log('discovery provenance compatibility: OK');

console.log('shared filter + verification + rolling horizon + family-fit tests: OK');


/* LEGACY PARITY REGRESSION
   Every legacy event in overlapping weeks must be accounted for by published data
   or the decision audit. Tokyo-23-ward exclusions must retain a reason; outside-23
   entries must be explicitly excluded as outside_23wards. */
const fsParity=(await import('node:fs')).default;
const pathParity=(await import('node:path')).default;
const assertParity=(await import('node:assert/strict')).default;
const legacyBaseline=[
  {
    "sat": "2026-10-10",
    "name": "ちいかわ☆星ふるスカイツリー(R)とひみつの島",
    "area": "墨田",
    "official_url": "https://www.tokyo-skytree.jp/event/special/chiikawa/",
    "in_scope_23wards": true
  },
  {
    "sat": "2026-10-10",
    "name": "すみだ五彩の芸術祭",
    "area": "墨田",
    "official_url": "https://sumida-artfest.jp",
    "in_scope_23wards": true
  },
  {
    "sat": "2026-10-10",
    "name": "オクトーバーフェストin東京スカイツリータウン®︎2026",
    "area": "墨田",
    "official_url": "https://okfes.jp/202609-skytree/",
    "in_scope_23wards": true
  },
  {
    "sat": "2026-10-10",
    "name": "お祭りBBQビアガーデン 浅草エキミセ屋台村",
    "area": "浅草",
    "official_url": "https://bbq.urban-earth.jp/asakusa",
    "in_scope_23wards": true
  },
  {
    "sat": "2026-10-10",
    "name": "祝）いきもの超ワールド展 国立科学博物館×ダーウィンが来た！",
    "area": "上野公園",
    "official_url": "https://www.kahaku.go.jp",
    "in_scope_23wards": true
  },
  {
    "sat": "2026-10-10",
    "name": "特別展「発見された東京の化石」",
    "area": "日比谷公園",
    "official_url": "https://www.library.chiyoda.tokyo.jp/information/20260705-tokyonokaseki/",
    "in_scope_23wards": true
  },
  {
    "sat": "2026-10-10",
    "name": "HUMAN AND NATURE",
    "area": "日比谷公園",
    "official_url": "https://www.hibiya.tokyo-midtown.com/humanandnature.yuichihirako/",
    "in_scope_23wards": true
  },
  {
    "sat": "2026-10-10",
    "name": "祝）ざんねんないきもの展３",
    "area": "池袋",
    "official_url": "https://sunshinecity.jp/file/aquarium/zannen/",
    "in_scope_23wards": true
  },
  {
    "sat": "2026-10-10",
    "name": "ボボボーボ・ボーボボ展 DIVE INTO THE BO-BOBO WORLD",
    "area": "池袋",
    "official_url": "https://www.toei-anim.co.jp/lp/bo-bobo/world/",
    "in_scope_23wards": true
  },
  {
    "sat": "2026-10-10",
    "name": "祝）第17回 九州観光・物産フェアin代々木2026",
    "area": "代々木公園",
    "official_url": "https://kyushu-yoyogipark.com/",
    "in_scope_23wards": true
  },
  {
    "sat": "2026-10-10",
    "name": "祝）HERO GATE",
    "area": "代々木公園",
    "official_url": null,
    "in_scope_23wards": true
  },
  {
    "sat": "2026-10-10",
    "name": "TVアニメ『薬屋のひとりごと』 × 東京シティビュー 舞が織りなす幻想の世界 ―天空に響く、舞のしらべ―",
    "area": "六本木",
    "official_url": "https://kusuriya-event-roppongihills.com/",
    "in_scope_23wards": true
  },
  {
    "sat": "2026-10-10",
    "name": "祝）〜（月・祝）ピクサーの世界展",
    "area": "豊洲",
    "official_url": "https://mundopixar.com/ja/cities/tokyo",
    "in_scope_23wards": true
  },
  {
    "sat": "2026-10-10",
    "name": "祝）オクトーバーフェスト2026 in アーバンドック ららぽーと豊洲",
    "area": "豊洲",
    "official_url": "https://www.oktober-fest.jp/",
    "in_scope_23wards": true
  },
  {
    "sat": "2026-10-10",
    "name": "祝）BMSG FES'26",
    "area": "お台場",
    "official_url": "https://bmsgfes.tokyo/",
    "in_scope_23wards": true
  },
  {
    "sat": "2026-10-10",
    "name": "祝）UNI9UE PARK MARCHE’26",
    "area": "お台場",
    "official_url": "https://www.nikoand.jp/uni9ue_park_2026/",
    "in_scope_23wards": true
  },
  {
    "sat": "2026-10-10",
    "name": "特別展「エリック・カールといのちの色‐同じ世界で、ちがう色‐」",
    "area": "品川",
    "official_url": "https://www.aquarium.gr.jp/news/events/31639",
    "in_scope_23wards": true
  },
  {
    "sat": "2026-10-10",
    "name": "祝）妖怪盆踊り2026",
    "area": "立川",
    "official_url": "http://www.yokaibonodori.tokyo/",
    "in_scope_23wards": false
  },
  {
    "sat": "2026-10-17",
    "name": "ちいかわ☆星ふるスカイツリー(R)とひみつの島",
    "area": "墨田",
    "official_url": "https://www.tokyo-skytree.jp/event/special/chiikawa/",
    "in_scope_23wards": true
  },
  {
    "sat": "2026-10-17",
    "name": "すみだ五彩の芸術祭",
    "area": "墨田",
    "official_url": "https://sumida-artfest.jp",
    "in_scope_23wards": true
  },
  {
    "sat": "2026-10-17",
    "name": "オクトーバーフェストin東京スカイツリータウン®︎2026",
    "area": "墨田",
    "official_url": "https://okfes.jp/202609-skytree/",
    "in_scope_23wards": true
  },
  {
    "sat": "2026-10-17",
    "name": "お祭りBBQビアガーデン 浅草エキミセ屋台村",
    "area": "浅草",
    "official_url": "https://bbq.urban-earth.jp/asakusa",
    "in_scope_23wards": true
  },
  {
    "sat": "2026-10-17",
    "name": "特別展「発見された東京の化石」",
    "area": "日比谷公園",
    "official_url": "https://www.library.chiyoda.tokyo.jp/information/20260705-tokyonokaseki/",
    "in_scope_23wards": true
  },
  {
    "sat": "2026-10-17",
    "name": "HUMAN AND NATURE",
    "area": "日比谷公園",
    "official_url": "https://www.hibiya.tokyo-midtown.com/humanandnature.yuichihirako/",
    "in_scope_23wards": true
  },
  {
    "sat": "2026-10-17",
    "name": "祝）ざんねんないきもの展３",
    "area": "池袋",
    "official_url": "https://sunshinecity.jp/file/aquarium/zannen/",
    "in_scope_23wards": true
  },
  {
    "sat": "2026-10-17",
    "name": "ボボボーボ・ボーボボ展 DIVE INTO THE BO-BOBO WORLD",
    "area": "池袋",
    "official_url": "https://www.toei-anim.co.jp/lp/bo-bobo/world/",
    "in_scope_23wards": true
  },
  {
    "sat": "2026-10-17",
    "name": "カリブ・ラテンアメリカストリート代々木2026",
    "area": "代々木公園",
    "official_url": "https://wsavannast.com/events/the-caribbean-latin-america-street/",
    "in_scope_23wards": true
  },
  {
    "sat": "2026-10-17",
    "name": "TVアニメ『薬屋のひとりごと』 × 東京シティビュー 舞が織りなす幻想の世界 ―天空に響く、舞のしらべ―",
    "area": "六本木",
    "official_url": "https://kusuriya-event-roppongihills.com/",
    "in_scope_23wards": true
  },
  {
    "sat": "2026-10-17",
    "name": "特別展「エリック・カールといのちの色‐同じ世界で、ちがう色‐」",
    "area": "品川",
    "official_url": "https://www.aquarium.gr.jp/news/events/31639",
    "in_scope_23wards": true
  }
];
const dataRoot=pathParity.resolve(process.cwd(),'site/data');
const normLegacyName=value=>{
  let s=String(value??'').normalize('NFKC').toLowerCase()
    .replaceAll('令和8年','').replaceAll('2026','');
  if(s.startsWith('祝)'))s=s.slice(2);
  const dropChars=[" ","\t","\n","(",")","（","）","「","」","『","』","【","】","[","]",":","：","/","／","・","_","-","‐","‑","–","—","―","~","〜","～","'","\"","®","™","︎"];
  for(const ch of dropChars)s=s.split(ch).join('');
  return s;
};
const canonLegacyUrl=value=>{
  try{const u=new URL(String(value||''));const host=u.hostname.startsWith('www.')?u.hostname.slice(4):u.hostname;const pathname=u.pathname.endsWith('/')?u.pathname.slice(0,-1):u.pathname;return (host+pathname).toLowerCase();}
  catch{return '';}
};
const legacyNameMatch=(a,b)=>{
  const x=normLegacyName(a),y=normLegacyName(b);
  return x===y || (Math.min(x.length,y.length)>=6 && (x.includes(y)||y.includes(x)));
};
const legacyRowMatch=(legacy,row)=>{
  if(legacyNameMatch(legacy.name,row.name))return true;
  const lu=canonLegacyUrl(legacy.official_url);if(!lu)return false;
  const urls=[row.url,row.official_url,row.source,...((row.evidence||[]).map(x=>x?.url))].map(canonLegacyUrl);
  return urls.includes(lu);
};
const loadPublishedForParity=sat=>{
  const meta=JSON.parse(fsParity.readFileSync(pathParity.join(dataRoot,sat+'.json'),'utf8'));
  const rows=Array.isArray(meta.events)?[...meta.events]:[];
  for(const file of (meta.event_files||[]))rows.push(...JSON.parse(fsParity.readFileSync(pathParity.join(dataRoot,file),'utf8')));
  return rows;
};
for(const sat of [...new Set(legacyBaseline.map(x=>x.sat))]){
  const published=loadPublishedForParity(sat);
  const decisions=JSON.parse(fsParity.readFileSync(pathParity.join(dataRoot,sat+'-decisions.json'),'utf8')).decisions||[];
  for(const legacy of legacyBaseline.filter(x=>x.sat===sat)){
    const pub=published.find(row=>legacyRowMatch(legacy,row));
    const dec=decisions.find(row=>legacyRowMatch(legacy,row));
    if(legacy.in_scope_23wards){
      assertParity.ok(pub||dec,`${sat}: legacy event is unaccounted for: ${legacy.name}`);
      if(!pub){
        assertParity.ok(['excluded','duplicate'].includes(dec?.decision),`${sat}: non-published legacy event needs an audited disposition: ${legacy.name}`);
        assertParity.ok((dec?.reasons||[]).length>0,`${sat}: audited disposition needs reasons: ${legacy.name}`);
      }
    }else{
      assertParity.ok(dec,`${sat}: outside-scope legacy event needs an audit row: ${legacy.name}`);
      assertParity.equal(dec.decision,'excluded',`${sat}: outside-scope legacy event must be excluded: ${legacy.name}`);
      assertParity.equal(dec.primary_reason_code,'outside_23wards',`${sat}: outside-scope reason must be outside_23wards: ${legacy.name}`);
    }
  }
}
console.log(`legacy parity regression: ${legacyBaseline.length}/${legacyBaseline.length} rows accounted for`);


const artsName='アーツ中村橋 2026―わたしとまちの記憶';
const artsWeeks=mergeEventsAcrossWeeks([
  {sat:'2026-10-24',events:[{id:'arts-1',ward:'練馬区',name:artsName,date_start:'2026-09-12',date_end:'2026-11-08',venue:'中村橋周辺（練馬区立美術館ほか）',official_url:'https://www.neribun.or.jp/event/museum.cgi?genre=2026'}]},
  {sat:'2026-10-31',events:[{id:'arts-2',ward:'練馬区',name:artsName,date_start:'2026-09-12',date_end:'2026-11-08',venue:'練馬区立美術館・サンライフ練馬・サンツ中村橋商店街 ほか',official_url:'https://www.neribun.or.jp/event/detail_m.cgi?id=202606301782802063'}]},
  {sat:'2026-11-07',events:[{id:'arts-3',ward:'練馬区',name:artsName,date_start:'2026-09-12',date_end:'2026-11-08',venue:'中村橋周辺（練馬区立美術館ほか）'}]}
]);
assert.equal(artsWeeks.length,1,'Arts Nakamurabashi must appear once across the six-week search');
assert.equal(artsWeeks[0].id,'arts-1','preserve original event ID');
assert.equal(artsWeeks[0]._week_sats.length,3);
assert.match(artsWeeks[0].official_url,/detail_m.cgi/);
const separateVenues=mergeEventsAcrossWeeks([{events:[
  {name:'同名イベント',ward:'練馬区',date_start:'2026-10-24',date_end:'2026-10-24',venue:'練馬区立美術館'},
  {name:'同名イベント',ward:'練馬区',date_start:'2026-10-24',date_end:'2026-10-24',venue:'区立スポーツセンター'}
]}]);
assert.equal(separateVenues.length,2,'independent venues must remain separate');
console.log('Arts Nakamurabashi duplicate regression + distinct venue guard: OK');


const correctedArtsWeeks=mergeEventsAcrossWeeks([
  {sat:'2026-10-24',events:[{id:'arts-s24',ward:'練馬区',name:artsName,
    date_start:'2026-09-12',date_end:'2026-11-08',period:'9/12〜11/8',
    venue:'サンツ中村橋商店街・サンライフ練馬ほか（美術館内の展示は10月18日終了、10月19〜30日は展示替休館）'}]},
  {sat:'2026-10-31',events:[{id:'arts-s31',ward:'練馬区',name:artsName,
    date_start:'2026-09-12',date_end:'2026-11-08',period:'9/12〜11/8',
    venue:'練馬区立美術館・サンライフ練馬・サンツ中村橋商店街 ほか'}]},
  {sat:'2026-11-07',events:[{id:'arts-n07',ward:'練馬区',name:artsName,
    date_start:'2026-09-12',date_end:'2026-11-08',period:'9/12〜11/8',
    venue:'中村橋周辺（練馬区立美術館ほか）'}]}
]);
assert.equal(correctedArtsWeeks.length,1,'the corrected venue chain must collapse A-B-C to ONE event');
assert.deepEqual(correctedArtsWeeks[0]._week_sats,['2026-10-24','2026-10-31','2026-11-07']);
assert.equal(correctedArtsWeeks[0]._identity_venues.length,3,'all trusted venue aliases should remain');
assert.equal(correctedArtsWeeks[0].id,'arts-s24','original event ID preserved');
const nonMatchingDate=mergeEventsAcrossWeeks([{events:[
  {id:'separate-date1',ward:'練馬区',name:artsName,venue:'練馬区立美術館',date_start:'2026-10-24',date_end:'2026-10-24'},
  {id:'separate-date2',ward:'練馬区',name:artsName,venue:'練馬区立美術館',date_start:'2026-10-25',date_end:'2026-10-25'}
]}]);
assert.equal(nonMatchingDate.length,2,'independent events on different dates must not merge');
console.log('actual verification venue correction chain A-B-C: OK');

// --- 23区 / 多摩 area group (staging, 2026-11-21) ---
{
  const {AREAS,TAMA_CITIES,areaGroupOf,readFiltersFromUrl}=await import('../site/app.js');
  assert.equal(TAMA_CITIES.length,21);
  assert.equal(AREAS.length,44);
  assert.equal(areaGroupOf('立川市'),'tama');
  assert.equal(areaGroupOf('浦安市'),'tama');
  const {areaDisplayName}=await import('../site/app.js');
  assert.equal(areaDisplayName('浦安市'),'千葉県浦安市');
  assert.equal(areaDisplayName('立川市'),'立川市');
  assert.equal(areaGroupOf('杉並区'),'ward');
  const mixed=[
    {id:'w1',ward:'杉並区',name:'区のイベント',period:'11/21'},
    {id:'t1',ward:'立川市',name:'立川のイベント',period:'11/21'}
  ];
  assert.equal(filterEvents(mixed,{}).length,2,'no group means all events (existing behaviour)');
  assert.deepEqual(filterEvents(mixed,{areaGroup:'ward'}).map(e=>e.id),['w1']);
  assert.deepEqual(filterEvents(mixed,{areaGroup:'tama'}).map(e=>e.id),['t1']);
  assert.deepEqual(filterEvents(mixed,{areaGroup:'tama',wards:['立川市']}).map(e=>e.id),['t1']);
  assert.equal(filterEvents(mixed,{areaGroup:'tama',wards:['杉並区']}).length,0);
  const counts=countsByWard(mixed);
  assert.equal(counts['立川市'],1);
  assert.equal(counts['杉並区'],1);
  // default group is not serialized; tama is
  assert.equal(new URLSearchParams(serializeEventFilters({areaGroup:'ward',wards:['練馬区']})).has('g'),false);
  const tama=new URLSearchParams(serializeEventFilters({areaGroup:'tama',wards:['立川市']}));
  assert.equal(tama.get('g'),'tama');
  assert.equal(tama.get('w'),'立川市');
}
