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
        self.title = getattr(article, "title", None)
        self.preview_image = getattr(article, "preview_image", None)
        self.metadata = copy(article.metadata) if getattr(article, "metadata", None) else {}
        self.metadata["event-start"] = start_dt
        self.metadata["event-end"] = end_dt
        self._start = start_dt

    @property
    def date(self):
        return self._start


def _recurrence_to_rrule(meta):
    raw = (meta.get("recurrence") or meta.get("Recurrence") or "").strip()
    if not raw:
        return None
    parts = raw.lower().split()
    if len(parts) == 2 and parts[0] == "weekly":
        day = WEEKDAY_TO_BYDAY.get(parts[1])
        if day:
            return f"FREQ=WEEKLY;BYDAY={day}"
    if len(parts) == 3 and parts[0] == "monthly":
        try:
            ord_val = int(parts[1])
        except (ValueError, TypeError):
            return None
        if ord_val < -1 or ord_val == 0 or ord_val > 4:
            return None
        day = WEEKDAY_TO_BYDAY.get(parts[2])
        if day:
            return f"FREQ=MONTHLY;BYDAY={ord_val}{day}"
    return None


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
    rrule_str = _recurrence_to_rrule(meta)
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
