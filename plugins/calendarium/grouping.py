"""
Event grouping utilities.
"""
from datetime import datetime, timedelta
from . import config
from . import dates


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
        start = dates._parse_event_start(event.metadata if hasattr(event, "metadata") else None)
        if start is None:
            continue
        if outer_by == "day":
            outer_key = start.strftime("%Y-%m-%d")
        elif outer_by == "week":
            outer_key = dates._week_start(start).strftime("%Y-%m-%d")
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
            outer_headline = dates._headline_day(outer_key, lang)
        elif outer_by == "week":
            outer_headline = dates._headline_week(outer_key, lang)
        else:
            outer_headline = dates._headline_month(outer_key, lang)
        inner_buckets = {}
        if outer_by == "week" and inner_by == "day":
            week_start_dt = datetime.strptime(outer_key, "%Y-%m-%d")
            for i in range(7):
                day_dt = week_start_dt + timedelta(days=i)
                day_key = day_dt.strftime("%Y-%m-%d")
                inner_buckets[day_key] = []
        for event in outer_events:
            start = dates._parse_event_start(event.metadata if hasattr(event, "metadata") else None)
            if start is None:
                continue
            if inner_by == "day":
                inner_key = start.strftime("%Y-%m-%d")
            elif inner_by == "week":
                inner_key = dates._week_start(start).strftime("%Y-%m-%d")
            else:
                inner_key = start.strftime("%Y-%m")
            if inner_key not in inner_buckets:
                inner_buckets[inner_key] = []
            inner_buckets[inner_key].append(event)
        for inner_key in inner_buckets:
            inner_buckets[inner_key].sort(key=lambda e: dates._parse_event_start(e.metadata) or datetime.min)
        sorted_inner_keys = sorted(inner_buckets.keys())
        inner_groups = []
        for inner_key in sorted_inner_keys:
            events_list = inner_buckets[inner_key]
            if hide_empty and len(events_list) == 0:
                continue
            if inner_by == "day":
                inner_headline = dates._headline_day_short(inner_key, lang)
            elif inner_by == "week":
                inner_headline = dates._headline_week(inner_key, lang)
            else:
                inner_headline = dates._headline_month(inner_key, lang)
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
        start = dates._parse_event_start(event.metadata if hasattr(event, "metadata") else None)
        if start is None:
            continue
        if group_by == "day":
            key = start.strftime("%Y-%m-%d")
        elif group_by == "week":
            key = dates._week_start(start).strftime("%Y-%m-%d")
        else:
            key = start.strftime("%Y-%m")
        if key not in buckets:
            buckets[key] = []
        buckets[key].append(event)
    if not buckets:
        return []
    for key in buckets:
        buckets[key].sort(key=lambda e: dates._parse_event_start(e.metadata) or datetime.min)
    sorted_keys = sorted(buckets.keys())
    if group_by == "day":
        headline_fn = dates._headline_day
    elif group_by == "week":
        headline_fn = dates._headline_week
    else:
        headline_fn = dates._headline_month
    return [(headline_fn(k, lang), buckets[k]) for k in sorted_keys]
