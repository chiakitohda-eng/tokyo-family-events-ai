#!/usr/bin/env python3
"""Actual 2026-11-17 HTTP evidence for 14 previously announced old-week events.

Do not upgrade on HTTP errors, missing 2026/year/event/date/venue tokens,
or generic page availability alone. Only changes status and a dated, source-backed note.
Never changes a previous event fact or any historic source-failure record.
"""
import collections,datetime,hashlib,html,json,re,sys,unicodedata
from html.parser import HTMLParser
from pathlib import Path
from urllib.request import Request,urlopen

JST=datetime.timezone(datetime.timedelta(hours=9))
NOW=datetime.datetime.now(JST).isoformat(timespec="seconds")
DATA=Path("candidate/site/data")
WEEKS=["2026-11-21","2026-11-28"]
REQUIRE={
 "official-2026-nijin-expo":["NIJIN教育万博2026","2026.11.21","11.22","DMM六本木"],
 "official-2026-urban-agriculture-pre":["全国都市農業フェスティバル2027","11月21日","光が丘公園"],
 "official-2026-edogawa-parasports":["えどがわパラスポーツ体験会","11月22日","スポーツセンター"],
 "official-2026-nihonbashi-komichi":["みちみちこみち2026","10月1日","11月30日","日本橋案内所"],
 "official-2026-haneda-museum":["Haneda Aviation Museum","November 29, 2026","Haneda Innovation City"],
 "official-2026-nerima-cultural-craft":["手工芸作家展","11月19日","11月23日","石神井公園ふるさと文化館"],
 "official-2026-nerima-cultural-dance":["日本舞踊の会","11月22日","練馬文化センター"],
 "official-2026-sumida-light-garden":["SUMIDA光のナイトガーデン","11月19日","12月27日","旧安田庭園"],
 "nerima-district-0275426b6920":["地区祭開催日程","11月29日","豊玉南小学校"],
 "official-2026-lumina-nogata":["LUMINA STUDIO","2026年11月28日","野方区民ホール"],
 "official-2026-sumida-moa-art":["MOA美術館墨田児童作品展","11月28日","11月29日","すみだ生涯学習センター"],
}
class Visible(HTMLParser):
 def __init__(self):super().__init__(convert_charrefs=True);self.text=[];self.skip=0
 def handle_starttag(self,tag,attrs):
  if tag in ("script","style","noscript"):self.skip+=1
 def handle_endtag(self,tag):
  if tag in ("script","style","noscript"):self.skip=max(0,self.skip-1)
 def handle_data(self,data):
  if not self.skip:self.text.append(data)
def norm(s):return re.sub(r"\s+","",unicodedata.normalize("NFKC",html.unescape(s))).casefold()
def load(path):return json.loads(path.read_text())
def save(path,value):path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+"\n")
def get(url):
 row={"url":url,"checked_at":NOW,"status":"error","http_status":None}
 try:
  request=Request(url,headers={"User-Agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/129 Safari/537.36",
                               "Accept-Language":"ja-JP,ja;q=0.9,en;q=0.5"})
  with urlopen(request,timeout=16) as resp:
   raw=resp.read(1500000)
   row.update(http_status=resp.status,final_url=resp.geturl(),sha256_full_response=hashlib.sha256(raw).hexdigest())
   encoding=resp.headers.get_content_charset() or "utf-8"
  text=raw.decode(encoding,errors="replace")
  parser=Visible();parser.feed(text)
  normalized=norm(" ".join(parser.text))
  row["page_text_length"]=len(normalized)
  row["2026_or_reiwa8_present"]=("2026" in normalized or "令和8" in normalized)
  row["status"]="checked" if row["http_status"]==200 and row["2026_or_reiwa8_present"] else "page_year_unverified"
  return row,normalized
 except Exception as e:
  row["error"]=str(e)[:250]
  return row,""
def main():
 loaded={week:load(DATA/(week+"-verification.json")) for week in WEEKS}
 all_rows=[(w,row) for w,v in loaded.items() for row in v["events"] if row["status"]=="announced"]
 assert len(all_rows)==14,("expected existing 14 announced",len(all_rows))
 assert set(row["id"] for week,row in all_rows)==set(REQUIRE),("unexpected carried IDs",set(REQUIRE)^set(row["id"] for _,row in all_rows))
 cache={}
 result=[]
 for week,row in all_rows:
  src=row["source"]
  if src not in cache:cache[src]=get(src)
  source,t=cache[src]
  tokens=REQUIRE[row["id"]]
  hits=[x for x in tokens if norm(x) in t]
  missing=[x for x in tokens if x not in hits]
  passed=source["status"]=="checked" and not missing
  record={"week":week,"id":row["id"],"url":src,
          "http_status":source.get("http_status"),"checked_at":NOW,
          "verified":passed,"required_exact_event_date_venue_markers":tokens,
          "matched":hits,"missing":missing,
          "raw_response_sha256":source.get("sha256_full_response"),
          "retrieval_error":source.get("error"),
          "source_status":source["status"]}
  if passed:
   row["status"]="verified"
   row["note"]=(row.get("note") or "")+" 2026-11-17現在の公式ページ本文を再取得して企画名・開催日/期間・会場の文字列一致を確認。"
   row["independent_recheck"]={"checked_at":NOW,"source_url":src,"http_status":200,
     "raw_response_sha256":source["sha256_full_response"],
     "exact_marker_hits":hits,"note":"HTMLの可視文字列をUnicode正規化して照合。差分がなければ事前登録内容を保持。"}
  result.append(record)
 for week,doc in loaded.items():
  c=collections.Counter(x["status"] for x in doc["events"])
  doc["verified_on"]="2026-11-17"
  doc["summary"]["total"]=len(doc["events"])
  doc["summary"]["verified"]=c["verified"]
  doc["summary"]["announced"]=c["announced"]
  save(DATA/(week+"-verification.json"),doc)
  run=load(DATA/(week+"-run.json"))
  run["summary"]["verified"]=c["verified"]
  run["summary"]["announced"]=c["announced"]
  run.setdefault("scoped_rollover_20261117",{})["full_tier_verification_not_yet_complete"]=c["announced"]>0
  run["scoped_rollover_20261117"]["official_rechecks_status"]="partial" if c["announced"] else "complete_individual_14_only"
  save(DATA/(week+"-run.json"),run)
 summary={"status":"complete" if all(x["verified"] for x in result) else "partial_unverified_held",
  "as_of_jst":"2026-11-17","source_rechecks_did_not_waive_23_ward_or_25_source_audit":True,
  "verified":sum(x["verified"] for x in result),"still_announced":sum(not x["verified"] for x in result),
  "source_urls_retrieved":len(cache),"checked_urls":sum(x[0]["status"]=="checked" for x in cache.values()),
  "per_event":result}
 save(DATA/"2026-11-17-carried-announcement-rechecks.json",summary)
 print("OFFICIAL_CARRIED_RECHECK",json.dumps({"verified":summary["verified"],"pending":summary["still_announced"],
                                        "urls_checked":summary["checked_urls"],"urls_total":summary["source_urls_retrieved"]},ensure_ascii=False))
 for x in result:print("RECHECK_EVENT",json.dumps(x,ensure_ascii=False))
 return 0
if __name__=="__main__":sys.exit(main())
