import assert from 'node:assert/strict';
import {summarizeUpdateHistory, formatJapaneseUpdateDate} from '../site/update-history-display.js';
const rows=[
 {run_type:'manual_independent_holiday_addition',as_of_jst:'2026-10-26',executed_at:'2026-10-26T07:02:00+09:00',added_weekly_records:9},
 {run_type:'manual_verified_subset_addition',as_of_jst:'2026-10-26',executed_at:'2026-10-26T23:16:00+09:00',added_weekly_records:4,failed_required_source_urls:5},
 {run_type:'manual_verified_weekend_subset_addition',as_of_jst:'2026-10-27',executed_at:'2026-10-27T00:22:00+09:00',added_weekly_records:5},
 {run_type:'verified_horizon_subset',as_of_jst:'2026-10-26',executed_at:'2026-10-27T01:11:37+09:00',added_weekly_records:28,new_official_independent_records:14,preserved_carryover_records:14,unverified_required_source_failures:5,note:'Six-week partial verified-subset rollover'},
 {run_type:'holiday_after_update',as_of_jst:'2026-10-19',executed_at:'2026-10-19T21:00:00+09:00',added_unique:21,changed_unique:9},
 {run_type:'published_data_correction',as_of_jst:'2026-10-13',executed_at:'2026-10-13T10:11:36+09:00',note:'Japanese note'}
];
const groups=summarizeUpdateHistory(rows);
assert.equal(groups.length,3,'one visible record per JST week');
assert.equal(groups[0].label,'10/26週');
assert.equal(groups[0].entries,4,'four internal runs collapse into one');
assert.equal(groups[0].added,32,'carryover 14 must not count as addition');
assert.match(groups[0].summary,/6週間更新/);
assert.match(groups[0].summary,/追加32件/);
assert.match(groups[0].summary,/参照元未取得5件/);
assert.doesNotMatch(groups[0].summary,/partial|verified-subset|[A-Za-z]{5}/);
assert.equal(groups[1].label,'10/19週');
assert.match(groups[1].summary,/追加21件/);
assert.equal(groups[2].label,'10/12週');
assert.match(groups[2].summary,/再点検/);
assert.equal(formatJapaneseUpdateDate('2026-10-26T16:11:37Z'),'2026/10/27 01:11');
assert.equal(summarizeUpdateHistory([]).length,0);
assert.equal(summarizeUpdateHistory(null).length,0);
console.log('PASS: Japanese weekly update history, 32 new not 46, UTC→JST, 3 groups');


const novRollover=[
 {run_type:'verified_current_horizon_subset',as_of_jst:'2026-11-08',executed_at:'2026-11-08T16:10:00+09:00',
  added_weekly_records:18,protected_carryover_records:13,newly_verified_or_announced_records:5},
 {run_type:'manual_official_add_only',as_of_jst:'2026-11-08',executed_at:'2026-11-08T17:44:28+09:00',
  added_weekly_records:11}
];
const novGroup=summarizeUpdateHistory(novRollover);
assert.equal(novGroup.length,1);
assert.equal(novGroup[0].added,16,'18 rollover records include 13 carryovers, plus 11 added later');
assert.match(novGroup[0].summary,/6週間更新/);
assert.match(novGroup[0].summary,/追加16件/);
