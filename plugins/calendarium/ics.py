"""
ICS file generation and filtering.
"""
import os
import re
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
from recurring_events import _recurrence_to_rrule as recurrence_to_rrule
# The same reading of the three place fields the templates get through the
# `event_place` filter — LOCATION here has to say what the page says.
from event_place import place
from . import config
from . import dates
from . import filter as filter_module


def _filter_by_path(articles, path):
    if not path or not str(path).strip():
        return list(articles) if articles else []
    needle = str(path).strip().replace("\\", "/")
    out = []
    for a in articles or []:
        src = getattr(a, "source_path", None) or ""
        src = src.replace("\\", "/")
        if needle in src:
            out.append(a)
    return out


def _filter_by_category_name(articles, category_name):
    if not category_name or not str(category_name).strip():
        return list(articles) if articles else []
    want = str(category_name).strip().lower()
    out = []
    for a in articles or []:
        cat = getattr(a, "category", None)
        if cat and getattr(cat, "name", "").lower() == want:
            out.append(a)
    return out


def _filter_by_tags(articles, tags_str):
    if not tags_str or not str(tags_str).strip():
        return list(articles) if articles else []
    want = set(s.strip().lower() for s in str(tags_str).split() if s.strip())
    if not want:
        return list(articles) if articles else []
    out = []
    for a in articles or []:
        tag_list = getattr(a, "tags", []) or []
        for t in tag_list:
            name = getattr(t, "name", None) or str(t)
            if name and name.lower() in want:
                out.append(a)
                break
    return out


def _event_start_in_range(metadata, start_str, end_str):
    start_dt = dates._parse_event_start(metadata)
    if start_dt is None:
        return False
    d = start_dt.date() if hasattr(start_dt, "date") else start_dt
    if start_str:
        try:
            low = datetime.strptime(start_str[:10], "%Y-%m-%d").date()
            if d < low:
                return False
        except (ValueError, TypeError):
            pass
    if end_str:
        try:
            high = datetime.strptime(end_str[:10], "%Y-%m-%d").date()
            if d > high:
                return False
        except (ValueError, TypeError):
            pass
    return True


def filter_events_for_ics(articles, filter_attrs, now, excluded_categories=None):
    if excluded_categories is None:
        excluded_categories = config.EXCLUDED_CATEGORIES
    out = []
    for a in articles or []:
        if not getattr(a, "category", None):
            out.append(a)
        elif getattr(a.category, "name", None) not in excluded_categories:
            out.append(a)
    f = filter_attrs or {}
    out = filter_module._filter_by_type(out, f.get("filter_by_type"))
    out = _filter_by_path(out, f.get("filter_by_path"))
    out = _filter_by_category_name(out, f.get("category"))
    out = _filter_by_tags(out, f.get("tags"))
    start_str, end_str = dates._resolve_start_end(now, f.get("days"), f.get("start"), f.get("end"))
    if start_str is not None or end_str is not None:
        out = [a for a in out if _event_start_in_range(getattr(a, "metadata", None) or {}, start_str, end_str)]
    return out


def _ics_escape(s):
    if s is None:
        return ""
    s = str(s).replace("\\", "\\\\").replace(";", "\\;").replace(",", "\\,").replace("\n", "\\n")
    return s


def _format_ics_datetime(dt, timezone_name=None):
    if dt is None:
        return ""
    if hasattr(dt, "strftime"):
        if timezone_name:
            return (dt.strftime("%Y%m%dT%H%M%S"), timezone_name)
        return (dt.strftime("%Y%m%dT%H%M%S"), None)
    return ("", None)


_UNTIL_RE = re.compile(r"(UNTIL=)(\d{8}T\d{6})(?!Z)")


def _until_to_utc(rule, timezone_name):
    """Rewrite a floating UNTIL to UTC.

    RFC 5545 3.3.10: when DTSTART carries a TZID, UNTIL must be UTC. This
    writer emits `DTSTART;TZID=Europe/Prague:`, so a floating UNTIL makes the
    VEVENT invalid — dateutil raises outright and strict clients drop the
    event, which is the whole series gone from someone's calendar.
    """
    if not rule or not timezone_name or "UNTIL=" not in rule:
        return rule

    def to_utc(match):
        local = datetime.strptime(match.group(2), "%Y%m%dT%H%M%S")
        try:
            aware = local.replace(tzinfo=ZoneInfo(timezone_name))
        except Exception:  # noqa: BLE001 — unknown tz: leave it floating
            return match.group(0)
        return match.group(1) + aware.astimezone(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

    return _UNTIL_RE.sub(to_utc, rule)


def _event_rrule(metadata):
    """(RRULE string or None, series start date or None).

    `recurrence:` may carry a `from` date that moves the first occurrence
    without touching `event-start`; the caller shifts DTSTART/DTEND by the same
    amount so the feed and the site agree on when the series begins.
    """
    if not metadata:
        return None, None
    rule, from_date = recurrence_to_rrule(metadata)
    if rule:
        return rule, from_date
    return (metadata.get("event-rrule") or "").strip() or None, None


def build_ics(events, siteurl, timezone_name=None):
    lines = ["BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//Calendarium//EN"]
    
    if timezone_name:
        lines.append(f"X-WR-TIMEZONE:{timezone_name}")
        lines.append("BEGIN:VTIMEZONE")
        lines.append(f"TZID:{timezone_name}")
        lines.append("END:VTIMEZONE")
    
    for event in events or []:
        meta = getattr(event, "metadata", None) or {}
        start_dt = dates._parse_event_start(meta)
        if start_dt is None:
            continue
        end_raw = meta.get("event-end")
        if isinstance(end_raw, datetime):
            end_dt = end_raw
        elif end_raw:
            try:
                end_dt = datetime.strptime(str(end_raw)[:19], "%Y-%m-%d %H:%M:%S")
            except (ValueError, TypeError):
                try:
                    end_dt = datetime.strptime(str(end_raw)[:10], "%Y-%m-%d")
                except (ValueError, TypeError):
                    end_dt = start_dt
        else:
            end_dt = start_dt
        uid = getattr(event, "slug", None) or "event"
        if siteurl:
            from urllib.parse import urlparse
            try:
                netloc = urlparse(siteurl).netloc or "site"
            except Exception:
                netloc = "site"
            uid = f"{uid}@{netloc}"
        summary = _ics_escape(getattr(event, "title", "") or "Event")
        desc = _ics_escape(meta.get("description") or getattr(event, "summary", "") or "")
        location = _ics_escape(place(meta).get("line", ""))
        url = (siteurl or "").rstrip("/") + "/" + (getattr(event, "slug", "") or "").strip("/") + "/"
        if url and url != "/":
            url = _ics_escape(url)
        
        rrule, rrule_from = _event_rrule(meta)
        if rrule_from is not None:
            # Keep the duration, move both ends onto the series start date.
            duration = end_dt - start_dt
            start_dt = start_dt.replace(year=rrule_from.year, month=rrule_from.month,
                                        day=rrule_from.day)
            end_dt = start_dt + duration

        start_str, start_tz = _format_ics_datetime(start_dt, timezone_name)
        end_str, end_tz = _format_ics_datetime(end_dt, timezone_name)
        
        lines.append("BEGIN:VEVENT")
        lines.append(f"UID:{uid}")
        if start_tz:
            lines.append(f"DTSTART;TZID={start_tz}:{start_str}")
        else:
            lines.append(f"DTSTART:{start_str}")
        if end_tz:
            lines.append(f"DTEND;TZID={end_tz}:{end_str}")
        else:
            lines.append(f"DTEND:{end_str}")
        lines.append(f"SUMMARY:{summary}")
        if desc:
            lines.append(f"DESCRIPTION:{desc}")
        if location:
            lines.append(f"LOCATION:{location}")
        if url:
            lines.append(f"URL:{url}")
        if rrule:
            lines.append(f"RRULE:{_until_to_utc(rrule, timezone_name)}")
        lines.append("END:VEVENT")
    lines.append("END:VCALENDAR")
    return "\r\n".join(lines)


def write_ics_feeds(pelican, **kwargs):
    generator = config._GENERATOR_CACHE.get("generator")
    if generator is None:
        return
    
    feeds = config._GENERATOR_CACHE.get("feeds") or []
    if not feeds:
        return
    
    articles = generator.context.get("articles", []) or []
    settings = pelican.settings
    output_path = settings.get("OUTPUT_PATH", "output")
    ics_dir = settings.get("CALENDAR_ICS_OUTPUT_DIR", "calendars")
    excluded = settings.get("CALENDAR_ICS_EXCLUDED_CATEGORIES", config.EXCLUDED_CATEGORIES)
    timezone_name = settings.get("TIMEZONE", "Europe/Prague")
    now = settings.get("NOW")
    if now is None:
        now = datetime.now()
    siteurl = settings.get("SITEURL", "") or ""
    out_dir = os.path.join(output_path, ics_dir)
    try:
        os.makedirs(out_dir, exist_ok=True)
    except OSError:
        return
    for feed in feeds:
        feed_id = feed.get("cal_file_name", "all")
        filter_spec = feed.get("filter", {})
        events = filter_events_for_ics(articles, filter_spec, now, excluded)
        ics_content = build_ics(events, siteurl, timezone_name)
        path = os.path.join(out_dir, f"{feed_id}.ics")
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(ics_content)
        except OSError:
            pass
