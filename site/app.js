export const WARDS = [
  '千代田区','中央区','港区','新宿区','文京区','台東区','墨田区','江東区','品川区','目黒区','大田区',
  '世田谷区','渋谷区','中野区','杉並区','豊島区','北区','荒川区','板橋区','練馬区','足立区','葛飾区','江戸川区'
];

// Tama (non-23-ward) municipalities. The event field stays `ward` and holds a
// ward or city name. Keep this list in sync with tools/validate_data.py.
export const TAMA_CITIES = [
  '武蔵野市','三鷹市','調布市','府中市','小金井市','小平市','国分寺市','国立市','立川市','昭島市',
  '日野市','西東京市','東久留米市','清瀬市','東村山市','狛江市','多摩市','稲城市','町田市','八王子市','浦安市'
];
export const AREAS = [...WARDS, ...TAMA_CITIES];
export const AREA_GROUPS = {
  ward:{label:'23区',unit:'区',areas:WARDS},
  tama:{label:'市部',unit:'市',areas:TAMA_CITIES}
};
// Display names for areas outside Tokyo (button text only; the stored `ward` stays '浦安市').
export const AREA_DISPLAY_NAMES = {'浦安市':'千葉県浦安市'};
export function areaDisplayName(name){ return AREA_DISPLAY_NAMES[name] || name; }
export function areaGroupOf(name){ return TAMA_CITIES.includes(name) ? 'tama' : 'ward'; }

export const PUBLICATION_TIERS = {
  full:{label:'本番',description:'今週〜2週間先。全掲載イベントを公式確認済み'},
  preview:{label:'先取り',description:'3〜4週間先。公式発表済み、詳細待ちを含む'},
  announcement:{label:'予告',description:'5〜6週間先。日付・会場を公式確認済み'},
  planned:{label:'取得前',description:'ローリング探索の対象。次回更新で取得'}
};

export const VERIFICATION_STATES = {
  verified:{label:'✓ 公式確認済み',className:'verify-ok'},
  announced:{label:'○ 開催発表済み・詳細待ち',className:'verify-announced'},
  unverified:{label:'要確認',className:'verify-pending'}
};

export const OFFICIAL_VERIFICATION_SOURCE_KINDS = new Set([
  'official','organizer_official','official_tourism','public_official','venue_official'
]);

export function isOfficialVerificationSource(sourceKind){
  return OFFICIAL_VERIFICATION_SOURCE_KINDS.has(String(sourceKind||''));
}

export const HERO_SEASONS = {
  spring:{label:'春・桜',source:'https://unsplash.com/photos/cherry-blossoms-in-full-bloom-in-a-park-AaxFt3GY7VQ'},
  summer:{label:'夏・祭り',source:'https://unsplash.com/photos/japanese-festival-with-lanterns-and-signage-mF9gUmfnJYQ'},
  autumn:{label:'秋・紅葉',source:'https://unsplash.com/photos/autumn-trees-with-yellow-and-orange-leaves-in-a-park-aUFgdqvFi2A'},
  winter:{label:'冬・クリスマス',source:'https://unsplash.com/photos/a-group-of-people-standing-in-front-of-a-christmas-tree-bxPS1gNKJso'}
};

export function heroSeasonForDate(dateStr){
  const month=Number(String(dateStr||'').slice(5,7));
  if(month>=3&&month<=5) return 'spring';
  if(month>=6&&month<=8) return 'summer';
  if(month>=9&&month<=11) return 'autumn';
  return 'winter';
}
export function heroSeasonMeta(season){ return HERO_SEASONS[season] || HERO_SEASONS.winter; }

export const FAMILY_FIT_AXES = {
  child_target:'子ども対象度',
  interactivity:'体験性',
  age_fit:'年齢適合',
  stay_flexibility:'滞在自由度',
  burden:'安全・負担',
  cost:'費用負担',
  reservation:'予約難易度',
  family_value:'家族価値'
};

export function isoLocal(d){
  const y=d.getFullYear(), m=String(d.getMonth()+1).padStart(2,'0'), day=String(d.getDate()).padStart(2,'0');
  return `${y}-${m}-${day}`;
}

export function addDays(dateStr,days){
  const [y,m,d]=dateStr.split('-').map(Number);
  return isoLocal(new Date(y,m-1,d+days));
}

export function defaultDate(){
  const t = new Date();
  const wd = t.getDay();
  if(wd === 6 || wd === 0) return isoLocal(t);
  return isoLocal(new Date(t.getFullYear(), t.getMonth(), t.getDate() + (6-wd)));
}

export function saturdayOf(dateStr){
  const [y,m,d] = dateStr.split('-').map(Number);
  const base = new Date(y,m-1,d);
  const wd = base.getDay();
  const diff = wd === 6 ? 0 : wd === 0 ? -1 : 6-wd;
  return isoLocal(new Date(y,m-1,d+diff));
}

export function fmtRange(sat,sun){
  const s=new Date(sat+'T00:00:00'), e=new Date(sun+'T00:00:00');
  const w=['日','月','火','水','木','金','土'];
  return `${s.getFullYear()}/${s.getMonth()+1}/${s.getDate()}(${w[s.getDay()]}) 〜 ${e.getMonth()+1}/${e.getDate()}(${w[e.getDay()]})`;
}

export function shortWeekendLabel(sat){
  const d=new Date(sat+'T00:00:00');
  return `${d.getMonth()+1}/${d.getDate()}`;
}

export function weekdayJa(dateStr){
  const d=new Date(dateStr+'T00:00:00');
  return ['日','月','火','水','木','金','土'][d.getDay()];
}

export function holidayPeriodSlots(manifest,anchorSat=''){
  const slots=rollingWeekSlots(manifest,anchorSat);
  const holidayRows=Array.isArray(manifest?.holidays)?manifest.holidays:[];
  const holidayByDate=new Map(holidayRows.map(x=>[x.date,x]));
  const used=new Set();
  const periods=slots.map(slot=>{
    let start=slot.sat,end=slot.sun;
    for(;;){
      const prev=addDays(start,-1);
      if(!holidayByDate.has(prev)) break;
      start=prev;used.add(prev);
    }
    for(;;){
      const next=addDays(end,1);
      if(!holidayByDate.has(next)) break;
      end=next;used.add(next);
    }
    const holidayDates=holidayRows.filter(x=>x.date>=start&&x.date<=end).map(x=>x.date);
    holidayDates.forEach(x=>used.add(x));
    return {...slot,start,end,sourceSat:slot.sat,kind:'weekend',holiday_dates:holidayDates};
  });
  if(!periods.length) return [];
  const horizonStart=periods[0].start;
  const horizonEnd=periods[periods.length-1].end;
  for(const holiday of holidayRows){
    if(!holiday?.date || holiday.date<horizonStart || holiday.date>horizonEnd || used.has(holiday.date)) continue;
    const source=[...slots].reverse().find(s=>s.sun<holiday.date)||slots[0];
    periods.push({
      start:holiday.date,end:holiday.date,sourceSat:source.sat,kind:'holiday',
      holiday_dates:[holiday.date],holiday_name:holiday.name||'祝日',
      entry:source.entry,available:source.available,publication_tier:source.publication_tier
    });
  }
  return periods.sort((a,b)=>a.start.localeCompare(b.start));
}

export function holidayTabMeta(period,manifest){
  const holidays=new Set((manifest?.holidays||[]).map(x=>x.date));
  const md=dateStr=>{const d=new Date(dateStr+'T00:00:00');return `${d.getMonth()+1}/${d.getDate()}`;};
  const endDay=dateStr=>String(Number(dateStr.slice(8,10)));
  const dayLabel=dateStr=>`${weekdayJa(dateStr)}${holidays.has(dateStr)?'・祝':''}`;
  if(period.start===period.end) return {primary:md(period.start),secondary:dayLabel(period.start)};
  const sameMonth=period.start.slice(0,7)===period.end.slice(0,7);
  return {
    primary:sameMonth?`${md(period.start)}–${endDay(period.end)}`:`${md(period.start)}–${md(period.end)}`,
    secondary:`${dayLabel(period.start)}〜${dayLabel(period.end)}`
  };
}

export function holidayRangeLabel(start,end,manifest){
  const holidays=new Set((manifest?.holidays||[]).map(x=>x.date));
  const fmt=(dateStr,withYear)=>{
    const d=new Date(dateStr+'T00:00:00');
    const prefix=withYear?`${d.getFullYear()}/`:'';
    return `${prefix}${d.getMonth()+1}/${d.getDate()}(${weekdayJa(dateStr)}${holidays.has(dateStr)?'・祝':''})`;
  };
  return start===end?fmt(start,true):`${fmt(start,true)} 〜 ${fmt(end,false)}`;
}

export function eventsOverlappingPeriod(events,start,end){
  return (events||[]).filter(ev=>{
    const s=ev?.date_start||ev?.date_end||'';
    const e=ev?.date_end||ev?.date_start||'';
    if(!s||!e) return false;
    return s<=end && e>=start;
  });
}

export function publicationTierMeta(tier){ return PUBLICATION_TIERS[tier] || PUBLICATION_TIERS.planned; }
export function verificationStateMeta(status,sourceKind='official'){
  if(status==='verified' && !isOfficialVerificationSource(sourceKind)) return {label:'✓ 確認済み',className:'verify-ok'};
  return VERIFICATION_STATES[status] || VERIFICATION_STATES.unverified;
}
export function verificationSourceHeading(verification){
  if(verification?.status==='announced') return '開催発表';
  return isOfficialVerificationSource(verification?.source_kind)?'公式確認':'確認';
}

export function rollingWeekSlots(manifest,anchorSat=''){
  const weeks=Array.isArray(manifest?.weekends)?manifest.weekends:[];
  const bySat=new Map(weeks.map(w=>[w.sat,w]));
  const horizon=Math.max(1,Number(manifest?.rolling_horizon_weeks)||6);
  const anchor=anchorSat || manifest?.default || weeks[0]?.sat || saturdayOf(defaultDate());
  const slots=[];
  for(let i=0;i<horizon;i++){
    const sat=addDays(anchor,i*7);
    const entry=bySat.get(sat)||null;
    const inferredTier=i<2?'full':i<4?'preview':'announcement';
    slots.push({sat,sun:addDays(sat,1),horizon_index:i+1,publication_tier:entry?.publication_tier||inferredTier,entry,available:!!entry});
  }
  return slots;
}

export function normalizeText(value){
  return String(value ?? '').normalize('NFKC').toLocaleLowerCase('ja-JP').replace(/\s+/g,' ').trim();
}

export function familyFitAxisRows(familyFit){
  const axes=familyFit?.axes;
  if(!axes || typeof axes!=='object') return [];
  return Object.entries(FAMILY_FIT_AXES).map(([key,label])=>{
    const item=axes[key];
    return item&&typeof item==='object'?{key,label,grade:item.grade||'unknown',reason:item.reason||''}:null;
  }).filter(Boolean);
}

export function recommendationStarCount(ev){
  const grade=typeof ev==='string'?ev:(ev?.family_fit?.overall||ev?.family_fit?.grade||'');
  return grade==='A'?3:grade==='B'?2:grade==='C'?1:0;
}

export function eventPriceCategory(ev){
  const raw=normalizeText(ev?.price||'');
  if(!raw || raw==='-' || raw==='未定' || raw==='不明' || raw.includes('要確認')) return 'unknown';
  const admissionFree=/入場無料|来場無料|全会場入場無料|入園料無料|観覧無料/.test(raw);
  const plainFree=raw==='無料' || /^無料(?:[、，。\s（(]|$)/.test(raw);
  const mixedPhrase=/無料および有料|無料・有料|無料プログラム|無料および有料プログラム/.test(raw);
  if((admissionFree || plainFree) && !mixedPhrase) return 'free';
  if(/無料/.test(raw)) return 'mixed';
  return 'paid';
}

export function eventPriceLabel(ev){
  const c=eventPriceCategory(ev);
  return c==='free'?'無料':c==='mixed'?'無料あり':c==='paid'?'有料':'料金要確認';
}

export function indoorOutdoorCategory(ev){
  const raw=normalizeText(typeof ev==='string'?ev:(ev?.indoor_outdoor||''));
  if(!raw) return 'unknown';
  if(['indoor','inside','屋内','室内'].includes(raw)) return 'indoor';
  if(['outdoor','outside','屋外','野外'].includes(raw)) return 'outdoor';
  if(['mixed','both','indoor/outdoor','indoor・outdoor','屋内外','屋内・屋外','屋内/屋外','屋内屋外'].includes(raw)) return 'mixed';
  if(raw.includes('屋内')&&raw.includes('屋外')) return 'mixed';
  if(raw.includes('indoor')&&raw.includes('outdoor')) return 'mixed';
  return 'unknown';
}

export function indoorOutdoorLabel(ev){
  const c=indoorOutdoorCategory(ev);
  return c==='indoor'?'屋内':c==='outdoor'?'屋外':c==='mixed'?'屋内・屋外':'';
}

export function reservationCategory(ev){
  const r=ev?.reservation;
  if(!r || typeof r!=='object') return 'unknown';
  if(r.required===true) return 'required';
  if(r.required===false) return 'none';
  const note=normalizeText(r.note||'');
  if(!note) return 'unknown';
  if(/企画.*(申込|予約)|プログラム.*(申込|予約)|一部.*(申込|予約)|(申込|予約).*(企画|プログラム|一部)/.test(note)) return 'partial';
  if(/要申込|要予約|事前申込|事前予約|予約制|申込制|申込必須|予約必須|チケット購入が必要/.test(note)) return 'required';
  if(/申込不要|予約不要|事前申込不要|事前予約不要|自由参加|当日参加可|一般来場|入場自由|直接会場/.test(note)) return 'none';
  return 'unknown';
}

export function reservationLabel(ev){
  const c=reservationCategory(ev);
  return c==='required'?'要事前申込':c==='none'?'申込不要':c==='partial'?'一部要申込':'申込要確認';
}

function canonicalEventUrl(ev){
  for(const value of [ev?.official_url,ev?.url]){
    if(!value) continue;
    try{
      const u=new URL(value);
      return (u.hostname.replace(/^www\./,'')+u.pathname.replace(/\/$/,'')).toLowerCase();
    }catch{}
  }
  return '';
}

export function eventIdentityKey(ev){
  const name=normalizeText(ev?.name||'');
  const start=ev?.date_start||'';
  const end=ev?.date_end||'';
  const dateToken=(start||end)?`${start}|${end}`:normalizeText(ev?.period||'');
  const venue=normalizeText(ev?.venue||'');
  const identity=venue?`v:${venue}`:`u:${canonicalEventUrl(ev)}`;
  return `${name}|${dateToken}|${identity}`;
}

// Guard against one event published by different sources with different venue
// descriptions. Require same ward, normalized name, exact dates and a concrete
// common venue anchor; otherwise preserve separate performances/branches.
function sameEventAcrossWeeks(a,b){
  if((a?.ward||'') !== (b?.ward||'')) return false;
  const title=v=>normalizeText(v||'').replace(/[\s　・･「」『』【】()（）ー－‐―:：!?！？]/g,'');
  if(!title(a?.name) || title(a?.name)!==title(b?.name)) return false;
  const date=v=>[v?.date_start||'',v?.date_end||'',normalizeText(v?.period||'')].join('|');
  if(date(a)!==date(b)) return false;
  const anchors=v=>normalizeText(v||'').split(/[、,，・／\/（）()\s　]+/)
    .map(x=>x.replace(/(?:ほか|など|周辺|付近|会場)$/g,''))
    .filter(x=>x.length>=5 && !/^(?:東京都|練馬区|杉並区|区内|複数会場)$/.test(x));
  const av=anchors(a?.venue), bv=anchors(b?.venue);
  return av.length>0 && bv.length>0 && av.some(x=>bv.some(y=>x===y));
}

export function mergeEventsAcrossWeeks(weekData){
  const map=new Map();
  for(const data of (weekData||[])){
    for(const ev of (data?.events||[])){
      const key=eventIdentityKey(ev);
      // Different descriptions of a shared multi-venue event have different
      // exact keys. Keep the first public ID and merge only confirmed anchors.
      const actualKey=map.has(key)?key:([...map.entries()].find(([,row])=>
        // Match against every already-verified venue alias in the cluster.
        // With A↔B and B↔C matches, the third row must not reappear as C.
        (row._identity_venues||[row.venue]).some(venue=>sameEventAcrossWeeks({...row,venue},ev))
      )?.[0]||key);
      if(!map.has(actualKey)){
        map.set(actualKey,{...ev,_identity_venues:ev.venue?[ev.venue]:[],_decision_rows:[],_week_sats:[]});
      }else{
        const cur=map.get(actualKey);
        // Preserve the venue descriptions from all verified sources for future
        // matches; never overwrite source records or erase distinct venues.
        cur._identity_venues ||= cur.venue?[cur.venue]:[];
        if(ev.venue && !cur._identity_venues.includes(ev.venue)) cur._identity_venues.push(ev.venue);
        const prefer=(v,a)=>a||v;
        cur.image=prefer(cur.image,ev.image);
        // Prefer an event detail over a genre/list URL when both are official.
        const detailUrl=url=>/\/event\/detail_[a-z]+\.cgi\?/i.test(url||'');
        cur.official_url=detailUrl(ev.official_url)&&!detailUrl(cur.official_url)?ev.official_url:prefer(cur.official_url,ev.official_url);
        cur.url=prefer(cur.url,ev.url);
        cur.description=(ev.description||'').length>(cur.description||'').length?ev.description:cur.description;
        if(ev.verification?.status==='verified' && cur.verification?.status!=='verified') cur.verification=ev.verification;
      }
      const merged=map.get(actualKey);
      const d=findDecisionForEvent(ev,data?.decision_audit);
      if(d && !merged._decision_rows.includes(d)) merged._decision_rows.push(d);
      if(data?.sat && !merged._week_sats.includes(data.sat)) merged._week_sats.push(data.sat);
    }
  }
  return [...map.values()];
}

export function eventSearchText(ev){
  return normalizeText([
    ev.name, ev.ward, ev.venue, ev.description, ev.price, ev.period, ev.time,
    ...(Array.isArray(ev.categories) ? ev.categories : []),
    ev.family_fit?.reason, ev.family_fit?.age, ev.family_fit?.overall,
    ...familyFitAxisRows(ev.family_fit).flatMap(x=>[x.label,x.grade,x.reason]),
    ev.reservation?.note, ev.verification?.note,
    verificationStateMeta(ev.verification?.status,ev.verification?.source_kind).label,
    indoorOutdoorLabel(ev), reservationLabel(ev)
  ].filter(Boolean).join(' '));
}

export function filterEvents(events, filters={}){
  const ward = filters.ward || '__all__';
  const q = normalizeText(filters.q || '');
  const recMin = Number(filters.recMin || 0);
  const price = filters.price || 'all';
  const environment = filters.environment || 'all';
  const reservation = filters.reservation || 'all';
  const sourceMode = ['ai_cross','explicit'].includes(filters.sourceMode) ? filters.sourceMode : 'all';
  const selected=(field)=>Array.isArray(filters[field])?filters[field]:[];
  const areaGroup = ['ward','tama'].includes(filters.areaGroup) ? filters.areaGroup : '';
  const wards=selected('wards'),ratings=selected('ratings'),prices=selected('prices'),environments=selected('environments'),
    reservations=selected('reservations'),sourceModes=selected('sourceModes'),periods=selected('periods');
  return (events || []).filter(ev => {
    if(areaGroup && areaGroupOf(ev.ward)!==areaGroup) return false;
    if(wards.length ? !wards.includes(ev.ward) : (ward!=='__all__' && ev.ward!==ward)) return false;
    if(q && !eventSearchText(ev).includes(q)) return false;
    const rating=recommendationStarCount(ev);
    if(ratings.length ? !ratings.map(Number).includes(rating) : (recMin && rating < recMin)) return false;
    if(prices.length ? !prices.includes(eventPriceCategory(ev)) : (price!=='all' && eventPriceCategory(ev)!==price)) return false;
    if(environments.length ? !environments.includes(indoorOutdoorCategory(ev)) : (environment!=='all' && indoorOutdoorCategory(ev)!==environment)) return false;
    if(reservations.length ? !reservations.includes(reservationCategory(ev)) : (reservation!=='all' && reservationCategory(ev)!==reservation)) return false;
    if(periods.length && !periods.some(period=>eventsOverlappingPeriod([ev],period.start,period.end).length)) return false;
    if(sourceModes.length===1 || (!sourceModes.length && sourceMode!=='all')){
      const mode=sourceModes.length ? sourceModes[0] : sourceMode;
      const provenance=eventDiscoveryProvenance(ev,filters.decisionAudit,filters.registry);
      if(mode==='ai_cross' && !provenance.ai) return false;
      if(mode==='explicit' && !provenance.explicit) return false;
    }
    return true;
  });
}

export function countsByWard(events){
  const counts = Object.fromEntries(AREAS.map(w => [w,0]));
  (events || []).forEach(ev => { if(ev.ward in counts) counts[ev.ward] += 1; });
  return counts;
}

export function readFiltersFromUrl(){
  const p = new URLSearchParams(location.search);
  const ward = AREAS.includes(p.get('ward')) ? p.get('ward') : '__all__';
  const areaGroup = p.get('g')==='tama' ? 'tama' : (areaGroupOf(ward)==='tama' && ward!=='__all__' ? 'tama' : 'ward');
  return {areaGroup,date:p.get('date')||'',ward,q:p.get('q')||'',recMin:p.get('rec')||'0',price:p.get('price')||'all',environment:p.get('env')||'all',reservation:p.get('reserve')||'all',sourceMode:['ai_cross','explicit'].includes(p.get('src'))?p.get('src'):'all'};
}

export function serializeEventFilters(filters){
  const p=new URLSearchParams();
  if(filters.q) p.set('q',filters.q);
  // Custom start/end has precedence over legacy single-period bookmarks.
  if(filters.range?.start && filters.range?.end){
    p.set('from',filters.range.start);
    p.set('to',filters.range.end);
  }else if(Array.isArray(filters.dates) && filters.dates.length){
    p.set('d',String(filters.dates[0]));
  }
  // 23区 is the default group and is not serialized, so existing bookmarks stay unchanged.
  if(filters.areaGroup==='tama') p.set('g','tama');
  const mappings=[['wards','w'],['ratings','star'],['prices','p'],['environments','e'],['reservations','r'],['sourceModes','s']];
  for(const [field,key] of mappings){
    if(Array.isArray(filters[field])) filters[field].forEach(value=>p.append(key,String(value)));
  }
  // Continue accepting previous single-choice bookmarks.
  if(!Array.isArray(filters.dates)&&filters.date) p.set('date',filters.date);
  if(!Array.isArray(filters.wards)&&filters.ward && filters.ward!=='__all__') p.set('ward',filters.ward);
  if(!Array.isArray(filters.ratings)&&Number(filters.recMin)) p.set('rec',String(filters.recMin));
  if(!Array.isArray(filters.prices)&&filters.price && filters.price!=='all') p.set('price',filters.price);
  if(!Array.isArray(filters.environments)&&filters.environment && filters.environment!=='all') p.set('env',filters.environment);
  if(!Array.isArray(filters.reservations)&&filters.reservation && filters.reservation!=='all') p.set('reserve',filters.reservation);
  if(!Array.isArray(filters.sourceModes) && ['ai_cross','explicit'].includes(filters.sourceMode)) p.set('src',filters.sourceMode);
  return p.toString();
}

export function buildCopyUrl(filters){
  const qs=serializeEventFilters(filters);
  return 'copy.html'+(qs?'?'+qs:'');
}

export function applyVerification(events, audit){
  const rows = Array.isArray(audit?.events) ? audit.events : [];
  const byId = new Map(rows.map(row => [row.id,row]));
  return (events || []).map(ev => {
    const row = byId.get(ev.id);
    if(!row) return {...ev,verification:{status:'unverified'}};
    const c = row.corrections && typeof row.corrections === 'object' ? row.corrections : {};
    const merged = {...ev,...c};
    if(c.family_fit) merged.family_fit={...(ev.family_fit||{}),...c.family_fit};
    if(c.reservation) merged.reservation={...(ev.reservation||{}),...c.reservation};
    merged.verification={status:row.status||'unverified',source:row.source||'',source_kind:row.source_kind||'',fields:row.fields||{},note:row.note||'',verified_on:row.verified_on||audit?.verified_on||''};
    return merged;
  });
}

export async function loadManifest(){
  const res = await fetch('data/manifest.json',{cache:'no-store'});
  if(!res.ok) throw new Error(`manifest load failed: ${res.status}`);
  return res.json();
}

export async function loadUpdateHistory(){
  const res = await fetch('data/update_history.json',{cache:'no-store'});
  if(!res.ok) throw new Error(`update history load failed: ${res.status}`);
  const data = await res.json();
  if(!Array.isArray(data.history)) data.history=[];
  return data;
}

export async function loadDiscoverySources(){
  const res=await fetch('data/discovery_sources.json',{cache:'no-store'});
  if(!res.ok) throw new Error(`discovery source load failed: ${res.status}`);
  return res.json();
}

export function findDecisionForEvent(event,audit){
  const rows=Array.isArray(audit?.decisions)?audit.decisions:[];
  if(!event) return null;
  const direct=rows.find(row=>row.candidate_id===event.id);
  if(direct) return direct;
  const name=normalizeText(event.name),ward=event.ward||'';
  const same=rows.filter(row=>normalizeText(row.name)===name && (row.ward||'')===ward);
  if(same.length===1) return same[0];
  const urls=[event.url,event.official_url,event.source].filter(Boolean).map(v=>{
    try{const u=new URL(v);return (u.hostname.replace(/^www\./,'')+u.pathname.replace(/\/$/,'')).toLowerCase();}
    catch{return '';}
  }).filter(Boolean);
  if(urls.length){
    const byUrl=rows.find(row=>{
      const candidates=[...(row.discovery_sources||[]).map(x=>x?.url),...(row.evidence||[]).map(x=>x?.url)].filter(Boolean);
      return candidates.some(v=>{
        try{const u=new URL(v);const c=(u.hostname.replace(/^www\./,'')+u.pathname.replace(/\/$/,'')).toLowerCase();return urls.includes(c);}
        catch{return false;}
      });
    });
    if(byUrl) return byUrl;
  }
  return same[0]||null;
}

export function eventDiscoveryProvenance(event,audit,registry){
  const rows=Array.isArray(event?._decision_rows)&&event._decision_rows.length
    ? event._decision_rows
    : [findDecisionForEvent(event,audit)].filter(Boolean);
  const combined={discovery_sources:rows.flatMap(row=>row?.discovery_sources||[])};
  return classifyDiscoveryProvenance(event,combined,registry);
}

export function classifyDiscoveryProvenance(event,decision,registry){
  const entries=Array.isArray(decision?.discovery_sources)?decision.discovery_sources:[];
  const explicitRegistry=Array.isArray(registry?.explicit_sources)?registry.explicit_sources:[];
  const byId=new Map(explicitRegistry.map(x=>[x.id,x]));
  const explicitKinds=new Set(['legacy_media','legacy_detail','explicit_source','manual_source','registered_source']);
  const aiKinds=new Set(['official_ai_search','v15_web_search','ai_cross_search','web_search','ai_search']);
  let explicit=false,ai=false;
  const explicitSources=[],urls=[],signals=[];
  const addExplicit=(sourceId,url,kind)=>{
    explicit=true;
    const meta=sourceId?byId.get(sourceId):explicitRegistry.find(src=>{
      if(!url) return false;
      try{
        const uh=new URL(url).hostname.replace(/^www\./,'');
        const bh=new URL(src.base_url).hostname.replace(/^www\./,'');
        return uh===bh;
      }catch{return false;}
    });
    const key=meta?.id||sourceId||url||kind||'explicit';
    if(!explicitSources.some(x=>x.key===key)) explicitSources.push({key,id:sourceId||'',label:meta?.label||sourceId||'明示参照元',url:url||meta?.base_url||''});
  };
  for(const src of entries){
    if(!src) continue;
    const channel=src.channel||'',kind=src.kind||'',url=src.url||'',sourceId=src.source_id||'';
    if(url && !urls.includes(url)) urls.push(url);
    if(channel==='explicit' || explicitKinds.has(kind) || (sourceId && byId.has(sourceId))) addExplicit(sourceId,url,kind);
    if(channel==='ai_cross' || aiKinds.has(kind)) ai=true;
    if(kind) signals.push(kind);
  }
  if(!explicit && !ai){
    const sourceUrl=event?.source||'';
    const hit=explicitRegistry.find(src=>src.enabled!==false && sourceUrl && (
      sourceUrl===src.base_url ||
      (src.search_urls||[]).some(u=>!u.includes('{') && sourceUrl===u)
    ));
    if(hit) addExplicit(hit.id,sourceUrl,'source_url_match');
  }
  const channel=explicit&&ai?'both':explicit?'explicit':ai?'ai_cross':'unknown';
  return {channel,explicit,ai,explicitSources,urls,signals};
}

export async function loadWeekend(manifest,satIso){
  const entry=(manifest.weekends||[]).find(w=>w.sat===satIso);
  if(!entry) return {entry:null,data:null};
  const res=await fetch('data/'+entry.file,{cache:'no-store'});
  if(!res.ok) throw new Error(`weekend load failed: ${res.status}`);
  const data=await res.json();
  data.horizon_index=data.horizon_index || entry.horizon_index || null;
  data.publication_tier=data.publication_tier || entry.publication_tier || 'full';
  const baseEvents=Array.isArray(data.events) ? data.events : [];
  const shardFiles=Array.isArray(data.event_files) ? data.event_files : [];
  if(shardFiles.length){
    const shards=await Promise.all(shardFiles.map(async file=>{
      const r=await fetch('data/'+file,{cache:'no-store'});
      if(!r.ok) throw new Error(`event shard load failed: ${file} ${r.status}`);
      const rows=await r.json();
      if(!Array.isArray(rows)) throw new Error(`event shard is not array: ${file}`);
      return rows;
    }));
    data.events=[...baseEvents,...shards.flat()];
  }else data.events=baseEvents;

  if(data.verification_file){
    const vr=await fetch('data/'+data.verification_file,{cache:'no-store'});
    if(!vr.ok) throw new Error(`verification load failed: ${vr.status}`);
    const audit=await vr.json();
    data.verification=audit;
    data.events=applyVerification(data.events,audit).map(ev=>({...ev,indoor_outdoor:indoorOutdoorLabel(ev)}));
  }else{
    data.verification=null;
    data.events=applyVerification(data.events,null).map(ev=>({...ev,indoor_outdoor:indoorOutdoorLabel(ev)}));
  }

  if(data.run_file){
    const rr=await fetch('data/'+data.run_file,{cache:'no-store'});
    if(!rr.ok) throw new Error(`run manifest load failed: ${rr.status}`);
    data.run=await rr.json();
  }else data.run=null;

  const decisionFile=data.run?.source_data?.decision_file;
  if(decisionFile){
    const dr=await fetch('data/'+decisionFile,{cache:'no-store'});
    if(!dr.ok) throw new Error(`decision audit load failed: ${dr.status}`);
    data.decision_audit=await dr.json();
  }else data.decision_audit=null;
  return {entry,data};
}

export function escapeHtml(value){
  return String(value ?? '').replace(/[&<>"']/g, ch => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[ch]));
}

export function safeHttpUrl(value){
  try { const u = new URL(String(value || '')); return (u.protocol === 'http:' || u.protocol === 'https:') ? u.href : ''; }
  catch { return ''; }
}
