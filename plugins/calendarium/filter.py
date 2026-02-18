"""
Event filtering utilities.
"""
from datetime import datetime
from recurring_events import expand_recurring
from . import config
from . import dates


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
        elif getattr(a.category, "name", None) not in config.EXCLUDED_CATEGORIES:
            event_pages.append(a)
    type_filtered = _filter_by_type(event_pages, type)
    start_str, end_str = dates._resolve_start_end(now, days, start, end)
    calendar_events = expand_recurring(type_filtered, start_str, end_str)
    reverse = str(sort).strip().lower() == "newest"
    calendar_events.sort(key=lambda e: getattr(e, "date", None) or datetime.min, reverse=reverse)
    display_events = _apply_limit(calendar_events, limit)
    return display_events


def make_calendar_filter(now):
    def _filter(articles, type=None, days=None, start=None, end=None, sort=None, limit=None):
        return calendar_filter(articles, now, type=type, days=days, start=start, end=end, sort=sort, limit=limit)
    return _filter
