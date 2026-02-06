"""
Pelican plugin: calendarium filter (type, days, start, end, sort, limit) and group_events for calendar widget.
Input: articles + options. Output: filtered/sorted event list. group_events(events, group_by, lang) for grouping.
"""
import re
from datetime import datetime, timedelta

from recurring_events import expand_recurring

EXCLUDED_CATEGORIES = ["announcement", "curiosity"]

CALENDAR_DEFAULTS = {
    'type': None,
    'days': None,
    'start': None,
    'end': None,
    'limit': None,
    'sort': None,
    'group_by': None,
    'headers': None,
    'hide_empty_days': False,
    'card_size': 's',
}

ATTR_PATTERN = re.compile(r'(\w+)="([^"]*)"')


def parse_widget_attrs(tag_content, defaults=None):
    if defaults is None:
        defaults = CALENDAR_DEFAULTS
    result = dict(defaults)
    if not tag_content:
        return result
    for match in ATTR_PATTERN.finditer(tag_content):
        key = match.group(1).lower().replace('-', '_')
        value = match.group(2)
        if key not in result:
            continue
        if key == 'hide_empty_days':
            result[key] = value.lower() in ('true', 'yes', '1')
        elif key == 'days':
            try:
                result[key] = int(value)
            except (ValueError, TypeError):
                pass
        else:
            result[key] = value if value else None
    return result

MONTH_NAMES_CS = [
    "leden", "únor", "březen", "duben", "květen", "červen",
    "červenec", "srpen", "září", "říjen", "listopad", "prosinec"
]
MONTH_NAMES_EN = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December"
]


def _parse_date_str(s):
    if not s or len(str(s).strip()) < 10:
        return None
    s = str(s).strip()[:10]
    try:
        return datetime.strptime(s, "%Y-%m-%d")
    except (ValueError, TypeError):
        return None


def _date_from_now(now, token):
    if not token:
        return None
    t = str(token).strip().lower()
    if hasattr(now, "date"):
        d = now.date()
    else:
        d = now
    if t == "today":
        return d
    if t == "this-week":
        weekday = d.weekday()
        return d - timedelta(days=weekday)
    if t == "this-month":
        return d.replace(day=1)
    if t == "this-year":
        return d.replace(month=1, day=1)
    parsed = _parse_date_str(token)
    return parsed.date() if parsed and hasattr(parsed, "date") else parsed


def _resolve_start_end(now, days, start, end):
    if now is None:
        return (None, None)
    if hasattr(now, "date"):
        today = now.date()
    else:
        today = now
    start_val = start if start is None else (str(start).strip() or None)
    end_val = end if end is None else (str(end).strip() or None)
    if start_val or end_val:
        start_dt = _date_from_now(now, start_val) if start_val else None
        end_dt = _date_from_now(now, end_val) if end_val else None
        if start_val and start_dt is None:
            start_dt = _parse_date_str(start_val)
            if start_dt:
                start_dt = start_dt.date()
        if end_val and end_dt is None:
            end_dt = _parse_date_str(end_val)
            if end_dt:
                end_dt = end_dt.date()
        if start_dt is None and end_dt is None:
            return (None, None)
        if start_dt is None:
            start_dt = end_dt
        if end_dt is None:
            if days is not None:
                try:
                    d = int(days)
                    end_dt = start_dt + timedelta(days=abs(d))
                except (TypeError, ValueError):
                    end_dt = start_dt + timedelta(days=365)
            else:
                end_dt = start_dt + timedelta(days=365)
        if start_dt > end_dt:
            start_dt, end_dt = end_dt, start_dt
        return (start_dt.strftime("%Y-%m-%d"), end_dt.strftime("%Y-%m-%d"))
    if days is not None:
        try:
            d = int(days)
        except (TypeError, ValueError):
            return (None, None)
        if d >= 365:
            start_str = today.strftime("%Y-%m-%d")
            end_d = today + timedelta(days=365)
            end_str = end_d.strftime("%Y-%m-%d")
            return (start_str, end_str)
        if d <= -365:
            start_d = today - timedelta(days=365)
            start_str = start_d.strftime("%Y-%m-%d")
            end_str = today.strftime("%Y-%m-%d")
            return (start_str, end_str)
        if d > 0:
            start_str = today.strftime("%Y-%m-%d")
            end_d = today + timedelta(days=d)
            end_str = end_d.strftime("%Y-%m-%d")
            return (start_str, end_str)
        start_d = today + timedelta(days=d)
        start_str = start_d.strftime("%Y-%m-%d")
        end_str = today.strftime("%Y-%m-%d")
        return (start_str, end_str)
    return (None, None)


def _filter_by_type(articles, event_type):
    if not event_type:
        return list(articles) if articles else []
    allowed = set(s.strip().lower() for s in str(event_type).split() if s.strip())
    if not allowed:
        return list(articles) if articles else []
    out = []
    for a in articles or []:
        meta = getattr(a, "metadata", None) or {}
        pt = meta.get("event-type")
        if pt and (str(pt).strip().lower() in allowed):
            out.append(a)
    return out


def _apply_limit(events, limit):
    if limit is None or not events:
        return list(events) if events else []
    if str(limit).strip().lower() == "all":
        return list(events)
    s = str(limit).strip().lower()
    if "last" in s:
        try:
            n = int(s.replace("last", "").replace(" ", ""))
            return list(events)[-n:] if n > 0 else list(events)
        except (ValueError, TypeError):
            return list(events)
    try:
        n = int(limit)
        return list(events)[: max(0, n)]
    except (ValueError, TypeError):
        return list(events)


def calendar_filter(articles, now, type=None, days=None, start=None, end=None, sort=None, limit=None):
    event_pages = []
    for a in articles or []:
        if not getattr(a, "category", None):
            event_pages.append(a)
        elif getattr(a.category, "name", None) not in EXCLUDED_CATEGORIES:
            event_pages.append(a)
    type_filtered = _filter_by_type(event_pages, type)
    start_str, end_str = _resolve_start_end(now, days, start, end)
    calendar_events = expand_recurring(type_filtered, start_str, end_str)
    reverse = str(sort).strip().lower() == "newest"
    calendar_events.sort(key=lambda e: getattr(e, "date", None) or datetime.min, reverse=reverse)
    display_events = _apply_limit(calendar_events, limit)
    return display_events


def make_calendar_filter(now):
    def _filter(articles, type=None, days=None, start=None, end=None, sort=None, limit=None):
        return calendar_filter(articles, now, type=type, days=days, start=start, end=end, sort=sort, limit=limit)
    return _filter


def _parse_event_start(metadata):
    if not metadata:
        return None
    raw = metadata.get("event-start")
    if not raw:
        return None
    if isinstance(raw, datetime):
        return raw
    if isinstance(raw, str):
        try:
            return datetime.strptime(raw[:19], "%Y-%m-%d %H:%M:%S")
        except (ValueError, TypeError):
            try:
                return datetime.strptime(raw[:10], "%Y-%m-%d")
            except (ValueError, TypeError):
                return None
    return None


def _week_start(dt):
    return dt.date() - timedelta(days=dt.weekday())


def _week_end(dt):
    return dt.date() + timedelta(days=6 - dt.weekday())


def _format_date_day(dt, lang):
    if lang == "cs":
        return f"{dt.day}. {dt.month}. {dt.year}"
    return f"{dt.day} {dt.strftime('%b')} {dt.year}"


def _headline_day(key_ymd, lang):
    parts = key_ymd.split("-")
    if len(parts) != 3:
        return key_ymd
    y, m, d = int(parts[0]), int(parts[1]), int(parts[2])
    dt = datetime(y, m, d)
    return _format_date_day(dt, lang)


def _headline_day_short(key_ymd, lang):
    parts = key_ymd.split("-")
    if len(parts) != 3:
        return key_ymd
    y, m, d = int(parts[0]), int(parts[1]), int(parts[2])
    dt = datetime(y, m, d)
    weekday_cs = ["Po", "Út", "St", "Čt", "Pá", "So", "Ne"]
    weekday_en = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    if lang == "cs":
        return f"{weekday_cs[dt.weekday()]} {dt.day}.{dt.month}."
    return f"{weekday_en[dt.weekday()]} {dt.day} {dt.strftime('%b')}"


def _headline_week_range(key_monday_ymd, lang):
    parts = key_monday_ymd.split("-")
    if len(parts) != 3:
        return key_monday_ymd
    y, m, d = int(parts[0]), int(parts[1]), int(parts[2])
    monday = datetime(y, m, d)
    sunday = monday + timedelta(days=6)
    if lang == "cs":
        return f"Týden od {monday.day}.{monday.month}. do {sunday.day}.{sunday.month}. {sunday.year}"
    return f"Week from {monday.day} {monday.strftime('%b')} to {sunday.day} {sunday.strftime('%b')} {sunday.year}"


def _headline_week(key_monday_ymd, lang):
    return _headline_week_range(key_monday_ymd, lang)


def _headline_month(key_ym, lang):
    parts = key_ym.split("-")
    if len(parts) != 2:
        return key_ym
    y, m = int(parts[0]), int(parts[1])
    if lang == "cs":
        name = MONTH_NAMES_CS[m - 1] if 1 <= m <= 12 else key_ym
    else:
        name = MONTH_NAMES_EN[m - 1] if 1 <= m <= 12 else key_ym
    return f"{name} {y}"


def group_events_nested(events, group_by_tokens, lang, hide_empty=False):
    if not events or len(group_by_tokens) != 2:
        return []
    lang = (lang or "cs").lower()[:2]
    if lang not in ("cs", "en"):
        lang = "cs"
    outer_by, inner_by = group_by_tokens[0], group_by_tokens[1]
    if outer_by not in ("day", "week", "month") or inner_by not in ("day", "week", "month"):
        return []
    outer_buckets = {}
    for event in events:
        start = _parse_event_start(event.metadata if hasattr(event, "metadata") else None)
        if start is None:
            continue
        if outer_by == "day":
            outer_key = start.strftime("%Y-%m-%d")
        elif outer_by == "week":
            outer_key = _week_start(start).strftime("%Y-%m-%d")
        else:
            outer_key = start.strftime("%Y-%m")
        if outer_key not in outer_buckets:
            outer_buckets[outer_key] = []
        outer_buckets[outer_key].append(event)
    if not outer_buckets:
        return []
    result = []
    for outer_key in sorted(outer_buckets.keys()):
        outer_events = outer_buckets[outer_key]
        if outer_by == "day":
            outer_headline = _headline_day(outer_key, lang)
        elif outer_by == "week":
            outer_headline = _headline_week(outer_key, lang)
        else:
            outer_headline = _headline_month(outer_key, lang)
        inner_buckets = {}
        if outer_by == "week" and inner_by == "day":
            week_start_dt = datetime.strptime(outer_key, "%Y-%m-%d")
            for i in range(7):
                day_dt = week_start_dt + timedelta(days=i)
                day_key = day_dt.strftime("%Y-%m-%d")
                inner_buckets[day_key] = []
        for event in outer_events:
            start = _parse_event_start(event.metadata if hasattr(event, "metadata") else None)
            if start is None:
                continue
            if inner_by == "day":
                inner_key = start.strftime("%Y-%m-%d")
            elif inner_by == "week":
                inner_key = _week_start(start).strftime("%Y-%m-%d")
            else:
                inner_key = start.strftime("%Y-%m")
            if inner_key not in inner_buckets:
                inner_buckets[inner_key] = []
            inner_buckets[inner_key].append(event)
        for inner_key in inner_buckets:
            inner_buckets[inner_key].sort(key=lambda e: _parse_event_start(e.metadata) or datetime.min)
        sorted_inner_keys = sorted(inner_buckets.keys())
        inner_groups = []
        for inner_key in sorted_inner_keys:
            events_list = inner_buckets[inner_key]
            if hide_empty and len(events_list) == 0:
                continue
            if inner_by == "day":
                inner_headline = _headline_day_short(inner_key, lang)
            elif inner_by == "week":
                inner_headline = _headline_week(inner_key, lang)
            else:
                inner_headline = _headline_month(inner_key, lang)
            inner_groups.append((inner_headline, events_list))
        result.append((outer_headline, inner_groups))
    return result


def group_events(events, group_by, lang, hide_empty=False):
    if not events:
        return []
    tokens = str(group_by).lower().split()
    if len(tokens) == 2:
        return group_events_nested(events, tokens, lang, hide_empty)
    if group_by not in ("day", "week", "month"):
        return []
    lang = (lang or "cs").lower()[:2]
    if lang not in ("cs", "en"):
        lang = "cs"
    buckets = {}
    for event in events:
        start = _parse_event_start(event.metadata if hasattr(event, "metadata") else None)
        if start is None:
            continue
        if group_by == "day":
            key = start.strftime("%Y-%m-%d")
        elif group_by == "week":
            key = _week_start(start).strftime("%Y-%m-%d")
        else:
            key = start.strftime("%Y-%m")
        if key not in buckets:
            buckets[key] = []
        buckets[key].append(event)
    if not buckets:
        return []
    for key in buckets:
        buckets[key].sort(key=lambda e: _parse_event_start(e.metadata) or datetime.min)
    sorted_keys = sorted(buckets.keys())
    if group_by == "day":
        headline_fn = _headline_day
    elif group_by == "week":
        headline_fn = _headline_week
    else:
        headline_fn = _headline_month
    return [(headline_fn(k, lang), buckets[k]) for k in sorted_keys]


def register():
    pass
