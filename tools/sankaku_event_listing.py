"""Venue cards link to external organizers with generic anchor labels.

Keep the heading, period and link in the same article. Output is discovery
only; a venue date hint is never a verified/publishable event.
"""
import datetime as dt
import hashlib
from html.parser import HTMLParser
import re
from urllib.parse import urljoin, urlsplit

SOURCE_ID = 'shinjuku_sankaku_hiroba'
SOURCE_URL = 'https://www.sumitomo-sankakuhiroba.jp/event/'

class Cards(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.cards = []
        self.current = None
        self.stack = []
        self.skip = 0

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag in ('script','style'):
            self.skip += 1
        if tag == 'article' and set(a.get('class','').split()) & {'event_now','event_list'}:
            self.current = {'name':[],'period':[],'links':[],'image':''}
            self.stack = []
        if self.current is None:
            return
        parent = self.stack[-1][1] if self.stack else ''
        mode = ('name' if tag == 'h4' else 'period' if 'event-period' in a.get('class','').split()
                else 'detail' if 'detail-link-btn' in a.get('class','').split() else parent)
        if tag == 'a' and mode == 'detail' and not self.skip:
            self.current['links'].append(a.get('href',''))
        if tag == 'img' and not self.current['image']:
            self.current['image'] = a.get('src','').strip()
        if tag not in ('img','br','hr','input','meta','link','source','wbr'):
            self.stack.append((tag,mode))

    def handle_data(self, data):
        if self.current is not None and self.stack and not self.skip:
            mode = self.stack[-1][1]
            if mode in ('name','period'):
                self.current[mode].append(data)

    def handle_endtag(self, tag):
        if tag in ('script','style'):
            self.skip = max(0,self.skip-1)
        if self.current is None:
            return
        if tag == 'article':
            self.cards.append(self.current)
            self.current = None
            self.stack = []
            return
        for i in range(len(self.stack)-1,-1,-1):
            if self.stack[i][0] == tag:
                del self.stack[i:]
                break


def period_dates(text):
    dates = re.findall(r'(?:(\d{4})/)?(\d{1,2})/(\d{1,2})',text)
    if len(dates) != 2 or not dates[0][0]:
        raise ValueError('missing explicit start year or date range')
    year, month, day = dates[0]
    start = dt.date(int(year),int(month),int(day))
    year2,month2,day2 = dates[1]
    year2 = int(year2) if year2 else start.year + (int(month2) < start.month)
    end = dt.date(year2,int(month2),int(day2))
    if end < start:
        raise ValueError('reversed event period')
    return start,end


def parse_listing(body, start, end, source_url=SOURCE_URL, holiday_dates=()):
    if urlsplit(source_url).hostname != urlsplit(SOURCE_URL).hostname:
        raise ValueError('unexpected venue host')
    p=Cards();p.feed(body)
    if not p.cards:
        raise ValueError('venue event cards missing; do not claim discovery complete')
    out={};invalid=[];seen=set();outside=0
    for c in p.cards:
        name=' '.join(''.join(c['name']).split())
        period=' '.join(''.join(c['period']).split())
        links=[urljoin(source_url,u.strip())for u in c['links']if u.strip()]
        links=[u for u in links if urlsplit(u).scheme == 'https' and urlsplit(u).hostname]
        try:
            a,b=period_dates(period)
            if not name or not links:
                raise ValueError('event heading or external detail link missing')
        except ValueError as e:
            invalid.append({'name':name,'period':period,'reason':str(e)})
            continue
        key=(name,a.isoformat(),b.isoformat(),links[0])
        if key in seen:
            continue
        seen.add(key)
        if b < start or a > end:
            outside+=1
            continue
        dates=[]
        for offset in range((min(b,end)-max(a,start)).days+1):
            day=max(a,start)+dt.timedelta(days=offset)
            if day.weekday()>=5 or day.isoformat() in holiday_dates:
                dates.append(day.isoformat())
        if not dates:
            outside+=1
            continue
        uid=hashlib.sha256('|'.join(key).encode()).hexdigest()[:16]
        out[uid]={'candidate_id':'sankaku-'+uid,'name':name,'ward':'新宿区',
                  'discovery_url':links[0],'official_url':links[0],
                  'source_id':SOURCE_ID,'listing_url':source_url,
                  'date_start_hint':a.isoformat(),'date_end_hint':b.isoformat(),
                  'matched_dates':dates,'date_unverified':True,
                  'source_kind':'official_venue_external_organizer_candidate_only',
                  'image_hint':urljoin(source_url,c['image']) if c['image'] else ''}
    # Partial extraction is not silently a successful complete source check.
    if invalid:
        raise ValueError('unparsed venue cards: '+str(invalid))
    return {'candidates':list(out.values()),'official_card_count':len(p.cards),
            'unique_event_count':len(seen),'outside_target_count':outside,
            'candidate_count':len(out),'decision_reconciliation':'pending'}

