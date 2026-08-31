"""
Event grouping utilities.
"""
from datetime import datetime, timedelta
from recurring_events import recurrence_parts
from . import config
from . import dates


def _group_events_three_level(events, group_by_tokens, lang, hide_empty=False):
    """Handle 3-level grouping like 'month week day'."""
    if len(group_by_tokens) != 3:
        return []
    
    level1_by, level2_by, level3_by = group_by_tokens[0], group_by_tokens[1], group_by_tokens[2]
    
    level1_buckets = {}
    for event in events:
        start = dates._parse_event_start(event.metadata if hasattr(event, "metadata") else None)
        if start is None:
            continue
        if level1_by == "day":
            level1_key = start.strftime("%Y-%m-%d")
        elif level1_by == "week":
            level1_key = dates._week_start(start).strftime("%Y-%m-%d")
        else:
            level1_key = start.strftime("%Y-%m")
        if level1_key not in level1_buckets:
            level1_buckets[level1_key] = []
        level1_buckets[level1_key].append(event)
    
    if not level1_buckets:
        return []
    
    result = []
    for level1_key in sorted(level1_buckets.keys()):
        level1_events = level1_buckets[level1_key]
        if level1_by == "day":
            level1_headline = dates._headline_day(level1_key, lang)
        elif level1_by == "week":
            level1_headline = dates._headline_week(level1_key, lang)
        else:
            level1_headline = dates._headline_month(level1_key, lang)
        
        level2_buckets = {}
        for event in level1_events:
            start = dates._parse_event_start(event.metadata if hasattr(event, "metadata") else None)
            if start is None:
                continue
            if level2_by == "day":
                level2_key = start.strftime("%Y-%m-%d")
            elif level2_by == "week":
                level2_key = dates._week_start(start).strftime("%Y-%m-%d")
            else:
                level2_key = start.strftime("%Y-%m")
            if level2_key not in level2_buckets:
                level2_buckets[level2_key] = []
            level2_buckets[level2_key].append(event)
        
        level2_groups = []
        for level2_key in sorted(level2_buckets.keys()):
            level2_events = level2_buckets[level2_key]
            if level2_by == "day":
                level2_headline = dates._headline_day_short(level2_key, lang)
            elif level2_by == "week":
                level2_headline = dates._headline_week(level2_key, lang)
            else:
                level2_headline = dates._headline_month(level2_key, lang)
            
            level3_buckets = {}
            if level2_by == "week" and level3_by == "day":
                week_start_dt = datetime.strptime(level2_key, "%Y-%m-%d")
                for i in range(7):
                    day_dt = week_start_dt + timedelta(days=i)
                    day_key = day_dt.strftime("%Y-%m-%d")
                    level3_buckets[day_key] = []
            
            for event in level2_events:
                start = dates._parse_event_start(event.metadata if hasattr(event, "metadata") else None)
                if start is None:
                    continue
                if level3_by == "day":
                    level3_key = start.strftime("%Y-%m-%d")
                elif level3_by == "week":
                    level3_key = dates._week_start(start).strftime("%Y-%m-%d")
                else:
                    level3_key = start.strftime("%Y-%m")
                if level3_key not in level3_buckets:
                    level3_buckets[level3_key] = []
                level3_buckets[level3_key].append(event)
            
            for level3_key in level3_buckets:
                level3_buckets[level3_key].sort(key=lambda e: dates._parse_event_start(e.metadata) or datetime.min)
            
            level3_groups = []
            for level3_key in sorted(level3_buckets.keys()):
                events_list = level3_buckets[level3_key]
                if hide_empty and len(events_list) == 0:
                    continue
                if level3_by == "day":
                    level3_headline = dates._headline_day_short(level3_key, lang)
                elif level3_by == "week":
                    level3_headline = dates._headline_week(level3_key, lang)
                else:
                    level3_headline = dates._headline_month(level3_key, lang)
                level3_groups.append((level3_headline, events_list))
            
            if level3_groups or not hide_empty:
                level2_groups.append((level2_headline, level3_groups))
        
        metadata = {"is_nested": True, "group_levels": [level1_by, level2_by, level3_by]}
        result.append((level1_headline, level2_groups, metadata))
    
    return result


def group_events_nested(events, group_by_tokens, lang, hide_empty=False):
    if not events or len(group_by_tokens) < 2 or len(group_by_tokens) > 3:
        return []
    lang = (lang or "cs").lower()[:2]
    if lang not in ("cs", "en"):
        lang = "cs"
    
    for token in group_by_tokens:
        if token not in ("day", "week", "month"):
            return []
    
    if len(group_by_tokens) == 3:
        return _group_events_three_level(events, group_by_tokens, lang, hide_empty)
    
    outer_by, inner_by = group_by_tokens[0], group_by_tokens[1]
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
        if outer_by == "week" and inner_by == "day":
            is_full_week = (len(inner_buckets) == 7) and not hide_empty
            metadata = {"is_nested": True, "is_full_week": is_full_week, "group_levels": [outer_by, inner_by]}
        else:
            metadata = {"is_nested": True, "group_levels": [outer_by, inner_by]}
        result.append((outer_headline, inner_groups, metadata))
    return result


def group_events_by_weekday(events, lang):
    """A schedule: every repeating event once, under the day it runs on.

    Not a window over the calendar. `group_by="week day"` answers "what is on
    in these seven days", which is the wrong question for a page listing the
    regular classes in town — a course starting in a fortnight is still a
    regular class, and it was simply absent. Widening the window does not help
    either: it repeats the same grid once per week in the span.

    So the occurrences arrive as usual and collapse back into the events they
    came from, keeping the earliest of each. Only repeating events take part.
    A one-off lesson filed under "Úterý" would read as a weekly commitment
    that does not exist, and the rule has to be one the build itself
    recognises — a schedule may not promise dates the calendar will not
    produce.
    """
    lang = (lang or "cs").lower()[:2]
    if lang not in ("cs", "en"):
        lang = "cs"
    earliest = {}
    for event in events or []:
        metadata = getattr(event, "metadata", None)
        start = dates._parse_event_start(metadata)
        if start is None or recurrence_parts(metadata) is None:
            continue
        key = getattr(event, "slug", None) or id(event)
        if key not in earliest or start < earliest[key][0]:
            earliest[key] = (start, event)
    buckets = {}
    for start, event in earliest.values():
        buckets.setdefault(start.weekday(), []).append((start, event))
    result = []
    for index in sorted(buckets):
        # By the clock, not by the date: a course running since March and one
        # starting in September share a Wednesday, and a reader of a schedule
        # reads down the evening, not down the calendar.
        rows = sorted(buckets[index],
                      key=lambda pair: (pair[0].hour, pair[0].minute,
                                        getattr(pair[1], "title", "") or ""))
        result.append((dates._headline_weekday(index, lang),
                       [event for _start, event in rows],
                       {"is_nested": False, "group_levels": ["weekday"]}))
    return result


def group_events(events, group_by, lang, hide_empty=False):
    if not events:
        return []
    tokens = str(group_by).lower().split()
    if tokens == ["weekday"]:
        return group_events_by_weekday(events, lang)
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
    return [(headline_fn(k, lang), buckets[k], {"is_nested": False, "group_levels": [group_by]}) for k in sorted_keys]
