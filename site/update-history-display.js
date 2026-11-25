// User-facing update history. Internal run rows are preserved in JSON, but
// the homepage groups multiple updates into one concise Japanese weekly record.
const jstDate = value => {
  if (!value) return null;
  const date = new Date(value);
  return Number.isNaN(date.valueOf()) ? null : date;
};
const jstDay = date => {
  const parts = new Intl.DateTimeFormat('en-US', {
    timeZone:'Asia/Tokyo',year:'numeric',month:'2-digit',day:'2-digit'
  }).formatToParts(date);
  const get=type=>parts.find(x=>x.type===type)?.value||'';
  return [get('year'),get('month'),get('day')].join('-');
};

function startOfWeek(day) {
  const parts = String(day||'').split('-').map(Number);
  if (parts.length!==3 || parts.some(n=>!Number.isInteger(n))) return '';
  const date=new Date(Date.UTC(parts[0],parts[1]-1,parts[2]));
  if (date.toISOString().slice(0,10)!==day) return '';
  date.setUTCDate(date.getUTCDate()-(date.getUTCDay()+6)%7);
  return date.toISOString().slice(0,10);
}
function userWeekKey(row) {
  const date = /^\d{4}-\d{2}-\d{2}$/.test(row?.as_of_jst||'')
    ? row.as_of_jst
    : jstDay(jstDate(row?.executed_at) || new Date(0));
  return startOfWeek(date);
}
export function formatJapaneseUpdateDate(value) {
  const date=jstDate(value);
  return date
    ? new Intl.DateTimeFormat('ja-JP',{
        timeZone:'Asia/Tokyo',year:'numeric',month:'2-digit',day:'2-digit',
        hour:'2-digit',minute:'2-digit',hour12:false
      }).format(date).replace(/\//g,'/')
    : '-';
}
const isFiniteCount = n=>typeof n==='number'&&Number.isFinite(n)&&n>=0;
function addedEventCount(row) {
  // A rolling update has carryovers; count ONLY genuinely new independent
  // participation units, never preserved carryover rows or entire week totals.
  // Current-horizon rollover carries old records into the newly visible week.
  // These are not newly found events; only independently verified additions count.
  if(row.run_type==='verified_current_horizon_subset'){
    return isFiniteCount(row.newly_verified_or_announced_records)
      ? row.newly_verified_or_announced_records : 0;
  }
  if(isFiniteCount(row.new_official_independent_records))return row.new_official_independent_records;
  if(isFiniteCount(row.added_weekly_records))return row.added_weekly_records;
  if(row.run_type==='holiday_after_update'&&isFiniteCount(row.added_unique))return row.added_unique;
  return 0;
}
function latestTime(row) {
  return jstDate(row.executed_at)?.getTime() || 0;
}
export function summarizeUpdateHistory(history) {
  if(!Array.isArray(history))return [];
  const groups=new Map();
  for(const row of history){
    if(!row||typeof row!=='object')continue;
    const key=userWeekKey(row);
    if(!key)continue;
    if(!groups.has(key))groups.set(key,{week:key,added:0,changed:0,removed:0,rollover:false,correction:false,
      pendingSources:0,entries:0,latestTime:0,published:0});
    const item=groups.get(key);
    item.entries++;
    item.added+=addedEventCount(row);
    if(isFiniteCount(row.changed_unique))item.changed+=row.changed_unique;
    if(isFiniteCount(row.removed_unique))item.removed+=row.removed_unique;
    if(isFiniteCount(row.unverified_required_source_failures))
      item.pendingSources=Math.max(item.pendingSources,row.unverified_required_source_failures);
    if(isFiniteCount(row.failed_required_source_urls))
      item.pendingSources=Math.max(item.pendingSources,row.failed_required_source_urls);
    item.rollover ||=row.run_type==='verified_horizon_subset'||row.run_type==='verified_current_horizon_subset'||row.run_type==='holiday_after_update';
    item.correction ||=row.run_type==='published_data_correction';
    if(latestTime(row)>=item.latestTime){
      item.latestTime=latestTime(row);
      if(isFiniteCount(row.published_unique_after))item.published=row.published_unique_after;
    }
  }
  return [...groups.values()].sort((a,b)=>b.week.localeCompare(a.week)).map(group=>{
    const short=group.week.slice(5).replace('-','/');
    const parts=[];
    if(group.rollover)parts.push('6週間更新');
    if(group.added>0)parts.push('追加'+group.added+'件');
    if(group.changed>0)parts.push('情報修正'+group.changed+'件');
    if(group.removed>0)parts.push('掲載終了'+group.removed+'件');
    if(group.correction&&!group.rollover)parts.push('掲載情報を再点検');
    if(group.pendingSources>0)parts.push('参照元未取得'+group.pendingSources+'件');
    return {week:group.week,label:short+'週',summary:parts.join('・')||'掲載情報を更新',
      entries:group.entries,latestTime:group.latestTime,added:group.added};
  });
}
