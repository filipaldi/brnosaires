"""
Pelican plugin: Jinja filters expand_recurring and date_add for recurring calendar events.
Expands events with recurrence (or event-rrule) into occurrence wrappers; date_add adds days to a datetime.
"""
import logging
from datetime import datetime, timedelta
from copy import copy

from dateutil.rrule import rrulestr

logger = logging.getLogger(__name__)

MAX_OCCURRENCES = 200

WEEKDAY_TO_BYDAY = {
    "monday": "MO", "tuesday": "TU", "wednesday": "WE", "thursday": "TH",
    "friday": "FR", "saturday": "SA", "sunday": "SU",
}


def _parse_event_datetime(metadata, key):
    if not metadata:
        return None
    raw = metadata.get(key)
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


def _parse_date_str(s):
    if not s or len(s) < 10:
        return None
    try:
        return datetime.strptime(s[:10], "%Y-%m-%d")
    except (ValueError, TypeError):
        return None


class Occurrence:
    def __init__(self, article, start_dt, end_dt):
        self.slug = getattr(article, "slug", None)
        # Carry the source article's URL (e.g. "en/<slug>/" for an English
        # event, "<slug>/" for a Czech one) so event_card.html can link to the
        # right page — "{slug}/" alone resolves against the site root and would
        # send an /en/ card to the Czech event.
        self.url = getattr(article, "url", None)
        self.lang = getattr(article, "lang", None)
        self.title = getattr(article, "title", None)
        self.preview_image = getattr(article, "preview_image", None)
        self.metadata = copy(article.metadata) if getattr(article, "metadata", None) else {}
        self.metadata["event-start"] = start_dt
        self.metadata["event-end"] = end_dt
        self._start = start_dt

    @property
    def date(self):
        return self._start


def _split_bounds(parts):
    """Peel `from` / `until` / `count` off the end of a recurrence value.

    Returns (base_parts, from_date, until_date, count). A malformed modifier is
    dropped with a warning rather than killing the whole series — a class that
    silently collapses to a single date is a worse outcome than one that runs
    past its intended end, and the warning is visible in the build log.
    """
    base = []
    from_date = until_date = count = None
    index = 0
    while index < len(parts):
        token = parts[index]
        argument = parts[index + 1] if index + 1 < len(parts) else None
        if token in ("from", "until", "count") and argument is None:
            # `weekly monday until` with nothing after it. Left in `base` this
            # made the pattern unrecognisable, so the whole rule was dropped and
            # a 52-week class silently became a single date — on a green build,
            # with no warning at all.
            logger.warning("recurring_events: '%s' has no value — ignoring it", token)
            index += 1
            continue
        if token in ("from", "until") and argument is not None:
            parsed = _parse_date_str(argument)
            if parsed is None:
                logger.warning("recurring_events: ignoring '%s %s' — not a YYYY-MM-DD date",
                               token, argument)
            elif token == "from":
                from_date = parsed
            else:
                until_date = parsed
            index += 2
            continue
        if token == "count" and argument is not None:
            try:
                parsed_count = int(argument)
            except (ValueError, TypeError):
                parsed_count = 0
            if parsed_count < 1:
                logger.warning("recurring_events: ignoring 'count %s' — not a positive integer",
                               argument)
            else:
                count = parsed_count
            index += 2
            continue
        base.append(token)
        index += 1
    return base, from_date, until_date, count


def _recurrence_to_rrule(meta):
    """Turn a `recurrence:` value into (RRULE string, series start date).

    Grammar:
        weekly <day>            [from D] [until D] [count N]
        monthly <ordinal> <day> [from D] [until D] [count N]

    `from` moves the first occurrence without touching `event-start`, whose
    time-of-day still applies to every occurrence. `until` is inclusive of the
    named day. RFC 5545 forbids UNTIL and COUNT together, so UNTIL wins.

    Returns (None, None) when nothing recognisable is there.
    """
    raw = (meta.get("recurrence") or meta.get("Recurrence") or "").strip()
    if not raw:
        return None, None
    parts, from_date, until_date, count = _split_bounds(raw.lower().split())

    rule = None
    if len(parts) == 2 and parts[0] == "weekly":
        day = WEEKDAY_TO_BYDAY.get(parts[1])
        if day:
            rule = f"FREQ=WEEKLY;BYDAY={day}"
    elif len(parts) == 3 and parts[0] == "monthly":
        try:
            ord_val = int(parts[1])
        except (ValueError, TypeError):
            ord_val = 0
        day = WEEKDAY_TO_BYDAY.get(parts[2])
        if day and ord_val != 0 and -1 <= ord_val <= 4:
            rule = f"FREQ=MONTHLY;BYDAY={ord_val}{day}"
    if rule is None:
        # Reached by a typo'd keyword ("untill 2027-06-28"), which leaves a
        # token in `base` that no pattern matches. Silence here is what turned
        # a weekly class into one occurrence with nothing in the log.
        logger.warning("recurring_events: recurrence %r is not a pattern I know — "
                       "expected 'weekly <day>' or 'monthly <n> <day>', with "
                       "optional 'from'/'until'/'count'. The event keeps its "
                       "single date.", raw)
        return None, None

    if until_date is not None:
        # Inclusive of the named day, so run to the last second of it.
        rule += ";UNTIL=" + until_date.replace(
            hour=23, minute=59, second=59).strftime("%Y%m%dT%H%M%S")
        if count is not None:
            logger.warning("recurring_events: 'until' and 'count' are mutually "
                           "exclusive in %r — using 'until'", raw)
    elif count is not None:
        rule += f";COUNT={count}"
    return rule, from_date


WEEKDAY_TO_INDEX = {
    "monday": 0, "tuesday": 1, "wednesday": 2, "thursday": 3,
    "friday": 4, "saturday": 5, "sunday": 6,
}


def recurrence_parts(metadata):
    """The rule as pieces, for whoever has to say it out loud.

    `_recurrence_to_rrule` answers the calendar's question — which dates does
    this event fall on. A page and a schema.org block ask a different one:
    what do I tell a reader, and in which language. Neither can be answered
    from an RRULE string without parsing it back, so the parsing happens once,
    here, and both callers get the same pieces.

    Returns None for an event that does not repeat, and for a rule the build
    itself does not recognise: the page must never promise a repetition the
    calendar will not deliver. That is the failure this whole area keeps
    producing — a file saying one thing and the site another.
    """
    raw = ((metadata or {}).get("recurrence")
           or (metadata or {}).get("Recurrence") or "")
    raw = str(raw).strip()
    if not raw:
        return None
    parts, from_date, until_date, count = _split_bounds(raw.lower().split())
    if len(parts) == 2 and parts[0] == "weekly" and parts[1] in WEEKDAY_TO_INDEX:
        result = {"freq": "weekly", "weekday": WEEKDAY_TO_INDEX[parts[1]]}
    elif len(parts) == 3 and parts[0] == "monthly" and parts[2] in WEEKDAY_TO_INDEX:
        try:
            ordinal = int(parts[1])
        except (ValueError, TypeError):
            return None
        if not (-1 <= ordinal <= 4) or ordinal == 0:
            return None
        result = {"freq": "monthly", "weekday": WEEKDAY_TO_INDEX[parts[2]],
                  "ordinal": ordinal}
    else:
        return None
    result.update(start=from_date, until=until_date, count=count)
    return result


def _naive(dt):
    if dt is None:
        return None
    if getattr(dt, "tzinfo", None) is not None:
        return dt.replace(tzinfo=None)
    return dt


def _expand_event(event, window_start_dt, window_end_dt):
    meta = getattr(event, "metadata", None) or {}
    slug = getattr(event, "slug", None)
    start_dt = _parse_event_datetime(meta, "event-start")
    if start_dt is None:
        return []
    start_dt = _naive(start_dt)
    end_dt = _parse_event_datetime(meta, "event-end")
    if end_dt is None:
        end_dt = start_dt
    end_dt = _naive(end_dt)
    duration = end_dt - start_dt
    rrule_str, from_date = _recurrence_to_rrule(meta)
    if from_date is not None:
        # `from` moves the first occurrence; the time of day still comes from
        # event-start, so a series can be re-anchored without editing two
        # fields that have to agree.
        start_dt = start_dt.replace(year=from_date.year, month=from_date.month,
                                    day=from_date.day)
    if rrule_str is None:
        rrule_str = (meta.get("event-rrule") or "").strip()
    if not rrule_str:
        if window_start_dt <= start_dt.replace(hour=0, minute=0, second=0, microsecond=0) <= window_end_dt:
            return [Occurrence(event, start_dt, end_dt)]
        return []
    try:
        rule = rrulestr(rrule_str, dtstart=start_dt)
        occurrence_dts = list(rule.between(window_start_dt, window_end_dt, inc=True))[:MAX_OCCURRENCES]
        logger.debug("recurring_events: slug=%s rrule=%s occurrences=%s window=%s..%s",
                     slug, rrule_str, len(occurrence_dts), window_start_dt, window_end_dt)
    except Exception as e:
        logger.debug("recurring_events: slug=%s rrule=%s exception=%r fallback=one",
                     slug, rrule_str, e)
        if window_start_dt <= start_dt.replace(hour=0, minute=0, second=0, microsecond=0) <= window_end_dt:
            return [Occurrence(event, start_dt, end_dt)]
        return []
    out = []
    for occ_start in occurrence_dts:
        occ_end = occ_start + duration
        out.append(Occurrence(event, _naive(occ_start), _naive(occ_end)))
    return out


def _normalize_event(event):
    meta = getattr(event, "metadata", None) or {}
    start_dt = _parse_event_datetime(meta, "event-start")
    if start_dt is None:
        return event
    end_dt = _parse_event_datetime(meta, "event-end")
    if end_dt is None:
        end_dt = start_dt
    return Occurrence(event, _naive(start_dt), _naive(end_dt))


def expand_recurring(events, start_date_str, end_date_str):
    window_start_dt = _parse_date_str(start_date_str)
    window_end_dt = _parse_date_str(end_date_str)
    if window_start_dt is None or window_end_dt is None:
        return [_normalize_event(e) for e in (events or [])]
    if window_start_dt > window_end_dt:
        window_start_dt, window_end_dt = window_end_dt, window_start_dt
    window_end_dt = window_end_dt.replace(hour=23, minute=59, second=59, microsecond=999999)
    result = []
    for event in events or []:
        result.extend(_expand_event(event, window_start_dt, window_end_dt))
    return result


def date_add(value, days):
    if value is None:
        return None
    try:
        d = int(days)
    except (TypeError, ValueError):
        return value
    if hasattr(value, "replace"):
        return value + timedelta(days=d)
    return value


def register():
    pass
