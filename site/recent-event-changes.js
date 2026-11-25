// Provenance for user-facing '今週追加' / '今週更新'. Never infer updates
// from reappearing carryovers or from a changed weekly count.
function jstDay(date){
  const value=new Intl.DateTimeFormat('en-US',{timeZone:'Asia/Tokyo',year:'numeric',month:'2-digit',day:'2-digit'}).formatToParts(date);
  const p=k=>value.find(v=>v.type===k)?.value||'';
  return [p('year'),p('month'),p('day')].join('-');
}
export function mondayOf(day){
  if(!/^\d{4}-\d{2}-\d{2}$/.test(String(day||'')))return '';
  const d=new Date(day+'T00:00:00Z');
  if(Number.isNaN(d.getTime())||d.toISOString().slice(0,10)!==day)return '';
  d.setUTCDate(d.getUTCDate()-(d.getUTCDay()+6)%7);
  return d.toISOString().slice(0,10);
}
const yes=x=>Array.isArray(x)&&x.every(id=>typeof id==='string'&&id.length>0);

export function recentEventChanges(history,{today=new Date(),lastWeekNewRows=[]}={}){
  const week=mondayOf(jstDay(today));
  const added=new Set(),updated=new Set();
  const rows=Array.isArray(history?.history)?history.history:[];
  for(const row of rows){
    if(!row||mondayOf(row.as_of_jst)!==week)continue;
    if(row.run_type==='verified_current_horizon_subset'){
      // A published snapshot may contain preserved carryovers. Accept only an
      // explicit, complete and unique ID list for this new rollover variant.
      const n=row.newly_verified_or_announced_records;
      const ids=row.new_event_ids;
      if(Number.isInteger(n)&&n>=0&&yes(ids)&&ids.length===n&&new Set(ids).size===n)
        ids.forEach(x=>added.add(x));
    }else if(yes(row.new_event_ids))row.new_event_ids.forEach(x=>added.add(x));
    // The new official programme shard belongs only to the verified 6-week
    // horizon rollover. A carryover is NOT a new programme.
    if(row.run_type==='verified_horizon_subset'&&
       Number(row.new_official_independent_records)===lastWeekNewRows.length&&
       Number(row.new_official_independent_records)>0){
      for(const ev of lastWeekNewRows)if(ev?.id)added.add(ev.id);
    }
    // "Changed" requires explicit immutable event identity; a summary count
    // is not sufficient to claim which event changed.
    if(yes(row.changed_event_ids))row.changed_event_ids.forEach(x=>updated.add(x));
  }
  for(const id of added)updated.delete(id);
  return {week,added,updated};
}
export function changeKind(ev,changes){
  if(changes?.added?.has(ev?.id))return 'added';
  if(changes?.updated?.has(ev?.id))return 'updated';
  return '';
}
export function changeBadge(ev,changes){
  const kind=changeKind(ev,changes);
  return kind==='added'
    ? '<span class="event-change-badge added" aria-label="今週追加したイベント">今週追加</span>'
    : kind==='updated'
      ? '<span class="event-change-badge updated" aria-label="今週情報を更新したイベント">今週更新</span>'
      : '';
}
export function currentChangeCounts(events,changes){
  const total={added:0,updated:0};
  for(const ev of events||[]){
    const kind=changeKind(ev,changes);
    if(kind)total[kind]++;
  }
  return total;
}
export async function loadChangeData({manifest,history,fetcher=fetch,today=new Date()}){
  let rows=[];
  const recentWeek=mondayOf(jstDay(today));
  const last=manifest?.weekends?.at(-1);
  const rollover=history?.history?.find(r=>r.run_type==='verified_horizon_subset'&&mondayOf(r.as_of_jst)===recentWeek);
  const expected=Number(rollover?.new_official_independent_records||0);
  if(rollover&&last&&expected>0){
    const weekResponse=await fetcher('data/'+last.file,{cache:'no-store'});
    if(weekResponse.ok){
      const week=await weekResponse.json();
      // Only the exact official verified new programme shard is eligible.
      const shard=(week.event_files||[]).find(p=>p===last.sat+'-events-official-verified.json');
      if(shard){
        const response=await fetcher('data/'+shard,{cache:'no-store'});
        if(response.ok){
          const a=await response.json();
          if(Array.isArray(a)&&a.length===expected&&new Set(a.map(x=>x.id)).size===a.length)rows=a;
        }
      }
    }
  }
  return recentEventChanges(history,{today,lastWeekNewRows:rows});
}
