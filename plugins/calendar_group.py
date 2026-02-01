"""
Pelican plugin: Jinja filter group_events for calendar widget grouping by day/week/month.
Input: events, group_by, lang. Output: list of (headline_str, list_of_events).
"""
from datetime import datetime, timedelta
from pelican import signals

MONTH_NAMES_CS = [
    "leden", "únor", "březen", "duben", "květen", "červen",
    "červenec", "srpen", "září", "říjen", "listopad", "prosinec"
]
MONTH_NAMES_EN = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December"
]


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


def _headline_week(key_monday_ymd, lang):
    parts = key_monday_ymd.split("-")
    if len(parts) != 3:
        return key_monday_ymd
    y, m, d = int(parts[0]), int(parts[1]), int(parts[2])
    dt = datetime(y, m, d)
    date_str = _format_date_day(dt, lang)
    if lang == "cs":
        return f"Týden {date_str}"
    return f"Week of {date_str}"


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


def group_events(events, group_by, lang):
    if not events or group_by not in ("day", "week", "month"):
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
    sorted_keys = sorted(buckets.keys(), reverse=True)
    if group_by == "day":
        headline_fn = _headline_day
    elif group_by == "week":
        headline_fn = _headline_week
    else:
        headline_fn = _headline_month
    return [(headline_fn(k, lang), buckets[k]) for k in sorted_keys]


def register():
    pass
