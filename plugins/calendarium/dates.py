"""
Date parsing, formatting, and headline generation utilities.
"""
import calendar as _calmod
from datetime import datetime, timedelta
from . import config


def _month_number(value):
    """Coerce a month given as int / numeric string / CS|EN name → 1..12, or None."""
    if value is None:
        return None
    if isinstance(value, int):
        return value if 1 <= value <= 12 else None
    s = str(value).strip().lower()
    if not s:
        return None
    if s.isdigit():
        n = int(s)
        return n if 1 <= n <= 12 else None
    return config.MONTH_NAME_TO_NUM.get(s)


def year_for_month(month_num, now):
    """The year that month "belongs to" for an *upcoming* framing: the current
    year, or next year if that month has already passed this year. Mirrors
    `tango_year_for_month` in pelicanconf.py — kept here to avoid a circular
    import (the plugin must not import the site config)."""
    return now.year if month_num >= now.month else now.year + 1


def _month_range(now, month_value):
    """Return (first-day, last-day) ISO strings for `month_value` in the
    upcoming-framing year, or None if `month_value` can't be parsed."""
    m = _month_number(month_value)
    if m is None:
        return None
    y = year_for_month(m, now)
    last_day = _calmod.monthrange(y, m)[1]
    return (f"{y:04d}-{m:02d}-01", f"{y:04d}-{m:02d}-{last_day:02d}")


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


def _resolve_start_end(now, days, start, end, month=None):
    if now is None:
        return (None, None)
    # `month=` (the evergreen-month-page param) overrides days/start/end: it
    # brackets exactly that calendar month in the upcoming-framing year.
    if month is not None and str(month).strip():
        rng = _month_range(now, month)
        if rng is not None:
            return rng
        # unparseable month → fall through to the normal days/start/end logic
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


WEEKDAY_NAME = {
    "cs": ("Pondělí", "Úterý", "Středa", "Čtvrtek", "Pátek", "Sobota", "Neděle"),
    "en": ("Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"),
}


def _headline_weekday(index, lang):
    """"Úterý" — the heading of a schedule row, not of a date.

    Full names, unlike the Po/Út/St above: those label a cell in a week grid
    where the date next to them says the rest, and here the day is the whole
    statement.
    """
    names = WEEKDAY_NAME.get(lang, WEEKDAY_NAME["cs"])
    return names[index % 7]


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
        name = config.MONTH_NAMES_CS[m - 1] if 1 <= m <= 12 else key_ym
    else:
        name = config.MONTH_NAMES_EN[m - 1] if 1 <= m <= 12 else key_ym
    return f"{name} {y}"
