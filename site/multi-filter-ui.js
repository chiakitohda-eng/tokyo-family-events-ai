import {groupFestivalDisplayEvents} from './festival-display-grouping.js?v=20261027-fest-parent';
import {WARDS,AREAS,AREA_GROUPS,areaGroupOf,areaDisplayName,saturdayOf,holidayPeriodSlots,holidayTabMeta,filterEvents,countsByWard,escapeHtml,serializeEventFilters} from './app.js';

// Shared multi-select UI for event search and copy list.
// Empty selections mean "all". Within a group use OR; across groups use AND.
const GROUPS=[
  {key:'sourceModes',param:'s',title:'取得元',items:[['ai_cross','AI探索'],['explicit','固定サイト']]},
  {key:'ratings',param:'star',title:'子連れオススメ度',items:[['3','★★★'],['2','★★'],['1','★'],['0','評価なし']]},
  {key:'prices',param:'p',title:'料金',items:[['free','無料'],['mixed','無料あり'],['paid','有料'],['unknown','料金要確認']]},
  {key:'environments',param:'e',title:'屋内・屋外',items:[['indoor','屋内'],['outdoor','屋外'],['mixed','屋内・屋外'],['unknown','場所要確認']]},
  {key:'reservations',param:'r',title:'予約・申込',items:[['none','申込不要'],['required','要事前申込'],['partial','一部要申込'],['unknown','申込要確認']]}
];
function validValues(values,allow){return new Set(values.filter(v=>allow.includes(v)));}
// Quick shortcuts show ongoing/upcoming periods only. Historical data and
// query-string/date-picker searches retain the complete six-week period set.
export function todayJst(now=new Date()){
  const jst=new Date(now.getTime()+9*60*60*1000);
  return jst.toISOString().slice(0,10);
}
export function visibleQuickPeriods(periods,today=todayJst()){
  return (periods||[]).filter(period=>period?.end>=today);
}
// A blank date selection means "from this weekend through the last published
// weekend", not the entire historical dataset. An explicit past-date selection
// still uses the original period and never deletes old event records.
export function currentAndFutureWindow(periods,today=todayJst()){
  const first=saturdayOf(today);
  const last=(periods||[]).filter(p=>p?.kind==='weekend').at(-1)?.end;
  // Preserve a nonempty impossible window if the manifest is stale: without
  // this guard filterEvents would interpret an empty periods array as ALL.
  if(!last || first>last) return {start:'9999-12-31',end:'9999-12-31'};
  return {start:first,end:last};
}

export function validatedDateRange(from,to,periods){
  if(!from && !to)return {error:'開始日または終了日を指定してください。'};
  const start=from||to,end=to||from;
  if(!/^\d{4}-\d{2}-\d{2}$/.test(start)||!/^\d{4}-\d{2}-\d{2}$/.test(end))
    return {error:'正しい日付を指定してください。'};
  if(start>end)return {error:'開始日は終了日以前にしてください。'};
  const first=periods?.[0]?.start,last=periods?.at(-1)?.end;
  if(!first||!last||start<first||end>last)
    return {error:'掲載対象の期間内で開始日と終了日を指定してください。'};
  return {start,end};
}
function initialState(params,periods){
  const validDate=params.getAll('d').find(date=>periods.some(period=>period.start===date));
  const dates=new Set(validDate?[validDate]:[]);
  const legacyDate=params.get('date');
  if(!dates.size && legacyDate && legacyDate!=='all'){
    const p=periods.find(x=>legacyDate>=x.start&&legacyDate<=x.end);
    if(p)dates.add(p.start);
  }
  const wards=validValues(params.getAll('w'),AREAS);
  if(!wards.size && AREAS.includes(params.get('ward')))wards.add(params.get('ward'));
  const state={dates,wards};
  for(const group of GROUPS){
    const allowed=group.items.map(x=>x[0]);
    const values=validValues(params.getAll(group.param),allowed);
    if(!values.size){
      if(group.key==='sourceModes' && allowed.includes(params.get('src'))) values.add(params.get('src'));
      if(group.key==='prices' && allowed.includes(params.get('price'))) values.add(params.get('price'));
      if(group.key==='environments' && allowed.includes(params.get('env'))) values.add(params.get('env'));
      if(group.key==='reservations' && allowed.includes(params.get('reserve'))) values.add(params.get('reserve'));
      if(group.key==='ratings'){
        const old=Number(params.get('rec')||0);
        if(old>=1&&old<=3) for(let i=old;i<=3;i++)values.add(String(i));
      }
    }
    state[group.key]=values;
  }
  return state;
}
export function createMultiFilterUI({manifest,registry,onChange,getData}){
  const $=id=>document.getElementById(id);
  const periods=holidayPeriodSlots(manifest,manifest.default);
  const params=new URLSearchParams(location.search);
  const state=initialState(params,periods);
  // Area group: 23区 is the default; the group is kept out of `state` (a map of Sets).
  let areaGroup=params.get('g')==='tama'||[...state.wards].some(w=>areaGroupOf(w)==='tama')?'tama':'ward';
  for(const w of [...state.wards])if(areaGroupOf(w)!==areaGroup)state.wards.delete(w);
  const initialCustom=(params.has('from')||params.has('to'))
    ?validatedDateRange(params.get('from')||'',params.get('to')||'',periods):null;
  let customRange=initialCustom&&!initialCustom.error?initialCustom:null;
  if(customRange)state.dates.clear();
  const filters=()=>({
    dates:[...state.dates],range:customRange,wards:[...state.wards],areaGroup,
    ratings:[...state.ratings],prices:[...state.prices],
    environments:[...state.environments],reservations:[...state.reservations],
    sourceModes:[...state.sourceModes],
    periods:customRange?[customRange]:state.dates.size
      ?periods.filter(x=>state.dates.has(x.start)).map(x=>({start:x.start,end:x.end}))
      :[currentAndFutureWindow(periods)]
  });
  function notify(){updateSummary();onChange();}
  function renderWeekTabs(){
    const all=!state.dates.size&&!customRange;
    $('weekTabs').innerHTML=`<button type="button" class="week-tab all-week-tab ${all?'active':''}" data-date="all" aria-pressed="${all}"><b>全期間</b><span>今週末から</span></button>`+
      visibleQuickPeriods(periods).map(period=>{
        const meta=holidayTabMeta(period,manifest),checked=state.dates.has(period.start);
        return `<button type="button" class="week-tab ${checked?'active':''} ${period.available?'':'pending'}" data-date="${period.start}" aria-pressed="${checked}"><b>${escapeHtml(meta.primary)}</b><span>${escapeHtml(meta.secondary)}</span></button>`;
      }).join('');
  }
  function renderWardChips(data){
    if(!data)return;
    const group=AREA_GROUPS[areaGroup];
    const base=filterEvents(data.events,{...filters(),wards:[],registry,decisionAudit:data.decision_audit});
    // Count in display units (festival programmes folded into one card) so the chips match the result count.
    const shown=groupFestivalDisplayEvents(base);
    const counts=countsByWard(shown),all=!state.wards.size;
    const tabs=`<span class="area-group-tabs" role="group" aria-label="地域">`+Object.entries(AREA_GROUPS).map(([key,g])=>
      `<button type="button" class="chip area-group-chip ${key===areaGroup?'active':''}" data-area-group="${key}" aria-pressed="${key===areaGroup}">${escapeHtml(g.label)}</button>`).join('')+`</span>`;
    $('chips').innerHTML=tabs+`<button type="button" class="chip ${all?'active':''}" data-ward="__all__" aria-pressed="${all}">すべて <span>${shown.length}</span></button>`+
      group.areas.map(ward=>{
        const checked=state.wards.has(ward);
        return `<label class="chip ${checked?'active':''} ${counts[ward]===0?'zero':''}"><input type="checkbox" data-ward="${escapeHtml(ward)}" ${checked?'checked':''}><span>${escapeHtml(areaDisplayName(ward))} ${counts[ward]}</span></label>`;
      }).join('');
  }
  function renderGroups(){
    $('filterGroups').innerHTML=GROUPS.map(group=>`<fieldset class="multi-fieldset">
      <legend>${group.title}</legend><div class="multi-option-grid">${group.items.map(([value,label])=>`
        <label class="multi-option"><input type="checkbox" data-group="${group.key}" value="${value}" ${state[group.key].has(value)?'checked':''}><span>${label}</span></label>`).join('')}</div>
    </fieldset>`).join('')+
    '<p class="multi-help">同じ項目で複数選択した場合は「いずれか」、異なる項目間は「すべて満たす」で検索します。未選択は条件なしです。「AI探索」と「固定サイト」の両方を選ぶと全件対象です。</p>';
  }
  function updateSummary(){
    const parts=[];
    if(customRange)parts.push(customRange.start+'〜'+customRange.end);
    else if(state.dates.size)parts.push('期間指定');
    if(areaGroup==='tama')parts.push('市部');
    if(state.wards.size)parts.push(AREA_GROUPS[areaGroup].unit+state.wards.size);
    for(const group of GROUPS){if(state[group.key].size)parts.push(group.title+state[group.key].size);}
    $('filterSummary').textContent=parts.length?`（${parts.join('・')}）`:'（条件なし）';
    // Reset is available even if only the keyword search is active.
    const selectedPeriod=periods.find(p=>state.dates.has(p.start));
    const pastSelection=selectedPeriod && selectedPeriod.end<todayJst();
    $('selectedHint').textContent=customRange
      ?'指定期間：'+customRange.start+' 〜 '+customRange.end+'（両端の日付を含む）。週末ボタンまたは「全期間」で解除できます。'
      :pastSelection
      ?'過去の期間を検索中です。ほかの過去の日程は「日付指定」から検索できます。「全期間」で解除できます。'
      :'日付を1日または開始日〜終了日で指定できます。区や詳細条件は複数選択できます。';
  }
  function toggleSet(bucket,value,checked){
    if(checked) bucket.add(value);else bucket.delete(value);
    notify();
  }
  function choosePeriod(value){
    state.dates.clear();
    customRange=null;
    if(value!=='all')state.dates.add(value);
    $('dateInput').value='';
    $('dateEndInput').value='';
    notify();
  }
  function handleWeek(e){
    const button=e.target.closest('button[data-date]');if(!button)return;
    choosePeriod(button.dataset.date);
  }
  function handleWard(e){
    const input=e.target.closest('input[data-ward]');if(!input)return;
    toggleSet(state.wards,input.dataset.ward,input.checked);
  }
  function handleDate(){
    const start=$('dateInput').value,end=$('dateEndInput').value;
    if(!start&&!end){choosePeriod('all');$('dateRefine').open=false;return;}
    const range=validatedDateRange(start,end,periods);
    const el=$('msgBox');
    if(range.error){el.textContent=range.error;el.style.display='block';return;}
    el.textContent='';el.style.display='none';
    state.dates.clear();
    customRange=range;
    $('dateInput').value=range.start;
    $('dateEndInput').value=range.end;
    $('dateRefine').open=false;
    notify();
  }
  function reset(){
    for(const value of Object.values(state))value.clear();
    areaGroup='ward';
    customRange=null;
    $('dateInput').value='';
    $('dateEndInput').value='';
    $('searchInput').value='';
    renderGroups();notify();
  }
  if(customRange){
    $('dateInput').value=customRange.start;
    $('dateEndInput').value=customRange.end;
  }
  // Restore past selections shared by URL even when the shortcut is hidden.
  const selectedPeriod=periods.find(p=>state.dates.has(p.start));
  if(selectedPeriod && selectedPeriod.end<todayJst()){
    $('dateInput').value=selectedPeriod.start;
  }
  $('weekTabs').addEventListener('click',handleWeek);
  $('chips').addEventListener('change',handleWard);
  $('chips').addEventListener('click',e=>{
    const tab=e.target.closest('button[data-area-group]');
    if(tab){
      const next=tab.dataset.areaGroup;
      if(AREA_GROUPS[next]&&next!==areaGroup){areaGroup=next;state.wards.clear();notify();}
      return;
    }
    if(!e.target.closest('button[data-ward="__all__"]'))return;
    state.wards.clear();notify();
  });
  $('filterGroups').addEventListener('change',e=>{
    const input=e.target.closest('input[data-group]');
    if(!input)return;
    const bucket=state[input.dataset.group];
    if(!bucket)return;
    if(input.checked)bucket.add(input.value);else bucket.delete(input.value);
    notify();
  });
  $('updateBtn').addEventListener('click',handleDate);
  $('clearFiltersBtn').addEventListener('click',reset);
  const panel=$('filterPanel');
  const closePanel=(focusTrigger=false)=>{
    if(!panel.open)return;
    panel.open=false;
    if(focusTrigger)panel.querySelector('summary')?.focus();
  };
  // On mobile the floating panel covers its own <summary>, so keep an
  // always-visible way to dismiss it without resetting any filter state.
  $('filterCloseBtn').addEventListener('click',()=>closePanel(true));
  $('filterApplyBtn').addEventListener('click',()=>closePanel(true));
  panel.querySelector('.multi-filter-backdrop').addEventListener('click',()=>closePanel());
  document.addEventListener('pointerdown',e=>{
    if(panel.open && !panel.contains(e.target))closePanel();
  });
  document.addEventListener('keydown',e=>{
    if(e.key==='Escape'&&panel.open){e.preventDefault();closePanel(true);}
  });
  panel.addEventListener('toggle',()=>{
    if(panel.open)$('dateRefine').open=false;
  });
  $('dateRefine').addEventListener('toggle',()=>{
    if($('dateRefine').open)closePanel();
  });
  renderGroups();
  updateSummary();
  return {filters,renderWeekTabs,renderWardChips,reset,serialize:(q)=>serializeEventFilters({...filters(),q:q||''}),summary:()=>$('filterSummary').textContent};
}
