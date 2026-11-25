"""Read a bounded subset of public ICS recurrences for manual evidence review.

This does not change the production collector. Unsupported rules fail closed.
"""
import calendar
import datetime as dt
import re


def entries(text):
    text = re.sub(r'\r?\n[ \t]', '', text)
    result = []
    for block in text.split('BEGIN:VEVENT')[1:]:
        row = {}
        for line in block.split('END:VEVENT', 1)[0].splitlines():
            if ':' not in line:
                continue
            key, value = line.split(':', 1)
            row.setdefault(key.split(';', 1)[0], []).append(value)
        result.append(row)
    return result


def monthly_dates(text, uid, start, end):
    rows = [r for r in entries(text) if r.get('UID') == [uid]]
    masters = [r for r in rows if 'RECURRENCE-ID' not in r]
    if len(masters) != 1:
        raise ValueError('exactly one recurring master required')
    master = masters[0]
    rule = master.get('RRULE', [])
    if len(rule) != 1 or not re.fullmatch(r'FREQ=MONTHLY;BYDAY=[1-4](MO|TU|WE|TH|FR|SA|SU)', rule[0]):
        raise ValueError('unsupported recurrence; manual review required')
    parse = lambda s: dt.datetime.strptime(s, '%Y%m%d').date()
    first = parse(master['DTSTART'][0])
    start, end = dt.date.fromisoformat(start), dt.date.fromisoformat(end)
    if end < start or (end-start).days > 366:
        raise ValueError('bounded review window required')
    if master.get('STATUS') == ['CANCELLED']:
        return []
    ordinal = int(rule[0].split('BYDAY=')[1][0])
    weekday = ['MO','TU','WE','TH','FR','SA','SU'].index(rule[0][-2:])
    excluded = {parse(v) for values in master.get('EXDATE', []) for v in values.split(',')}
    overrides = {parse(r['RECURRENCE-ID'][0]): r for r in rows if 'RECURRENCE-ID' in r}
    dates = set()
    month = start.replace(day=1)
    while month <= end:
        day = month + dt.timedelta(days=(weekday-month.weekday()) % 7 + 7*(ordinal-1))
        if day >= first and day not in excluded and day not in overrides and start <= day <= end:
            dates.add(day)
        month += dt.timedelta(days=calendar.monthrange(month.year, month.month)[1])
    for original, override in overrides.items():
        if original >= first and override.get('STATUS') != ['CANCELLED']:
            moved = parse(override['DTSTART'][0])
            if start <= moved <= end:
                dates.add(moved)
    return sorted(d.isoformat() for d in dates)
