# calendarium

Pelican plugin for calendar widgets and iCal feed generation.

Provides two widgets (`<widget-calendar>` and `<widget-calendar-link>`), event filtering and grouping, and automatic `.ics` file generation for calendar subscriptions.

---

## Widgets

### `<widget-calendar>` — Display events

Renders a filtered, sorted list of event cards on a page.

```html
<widget-calendar
    filter_by_type="milonga"
    days="14"
    group_by="week day"
    headers="day"
    card_size="s">
</widget-calendar>
```

| Attribute | Type | Description |
|---|---|---|
| `filter_by_type` | string | Filter by `event-type` metadata. Space-separated = OR logic (e.g. `"milonga workshop"`). |
| `days` | integer | Relative date window from today. Positive = future, negative = past. |
| `start` | date/token | Start of date window. Values: `YYYY-MM-DD`, `today`, `this-week`, `this-month`, `this-year`. |
| `end` | date/token | End of date window. Same format as `start`. |
| `limit` | string | Limit results: `"3"`, `"all"`, `"last 3"`. |
| `sort` | string | `"oldest"` (default, chronological) or `"newest"` (reverse). |
| `group_by` | string | Group events: `"day"`, `"week"`, `"month"`, `"week day"` (nested grid). |
| `headers` | string | Show group headers: `"week"`, `"day"`, `"week day"`. Default: hidden. |
| `hide_empty_days` | boolean | Hide empty day columns in week-day grid. Default: `false`. |
| `card_size` | string | Card size: `"xs"`, `"s"` (default), `"m"`, `"l"`. |

`days` and `start`/`end` are mutually exclusive. `sort` is ignored when `group_by` is set (always chronological within groups).

Events with categories `announcement` and `curiosity` are always excluded.

---

### `<widget-calendar-link>` — Calendar subscription links

Renders three subscription links for an iCal feed: webcal (Apple/default), Google Calendar, and HTTPS (Outlook/manual).

```html
<widget-calendar-link
    cal_file_name="milongas"
    filter_by_path="events"
    filter_by_type="milonga practica neolonga"
    label="📆 Odebírej milongy do svého kalendáře"
    label_webcal="Apple"
    label_google="Google"
    label_outlook="Ostatní">
</widget-calendar-link>
```

| Attribute | Type | Description |
|---|---|---|
| `cal_file_name` | string | Output filename: `output/calendars/{cal_file_name}.ics`. Produces readable URLs. If omitted, an MD5 hash of the filter config is used. |
| `filter_by_type` | string | Filter by `event-type` metadata. Same logic as `<widget-calendar>`. |
| `filter_by_path` | string | Filter by article source path substring (e.g. `"events"` keeps only `content/events/...`). |
| `days` | integer | Relative date window. |
| `start` | date/token | Start of date window. |
| `end` | date/token | End of date window. |
| `category` | string | Filter by Pelican category name. |
| `tags` | string | Filter by tags (space-separated, OR logic). |
| `label` | string | Heading text above links. Default: `"Subscribe to calendar"`. |
| `label_webcal` | string | Link text for webcal link. Default: `"Apple / default calendar"`. |
| `label_google` | string | Link text for Google Calendar link. Default: `"Google Calendar"`. |
| `label_outlook` | string | Link text for HTTPS/copy link. Default: `"Copy link"`. |

Renders as:

```html
<div>
  <p>📆 Odebírej milongy do svého kalendáře</p>
  <a href="webcal://example.com/calendars/milongas.ics">Apple</a>
  <a href="https://www.google.com/calendar/render?cid=https%3A%2F%2F...">Google</a>
  <a href="https://example.com/calendars/milongas.ics">Ostatní</a>
</div>
```

---

## ICS Feed Generation

### How it works

1. **Feed discovery** — at `page_generator_finalized`, `feed_links.discover_calendar_link_feeds` scans all page content for `<widget-calendar-link>` tags. Each unique filter config becomes a registered feed.

2. **Deduplication** — feeds are deduplicated by fingerprint (sorted filter keys → string). Two tags with identical filters produce one `.ics` file. The `cal_file_name` of the first-scanned tag wins on collision.

3. **ICS generation** — at `finalized`, `ics.write_ics_feeds` filters all articles for each feed and writes `output/calendars/{cal_file_name}.ics`.

### Filter pipeline (per feed)

```
All articles
  → exclude categories (announcement, curiosity)
  → filter_by_type
  → filter_by_path
  → category
  → tags
  → date range (start/end or days=)
→ written to .ics
```

Note: ICS does **not** expand recurring events. It writes one `VEVENT` with `RRULE` per recurring event and lets the calendar app handle recurrence per RFC 5545. The display widget (`<widget-calendar>`) does expand recurring events for rendering.

### ICS file format

```
BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//Calendarium//EN
X-WR-TIMEZONE:Europe/Prague

BEGIN:VEVENT
UID:{slug}@{domain}
DTSTART;TZID=Europe/Prague:20260413T200000
DTEND;TZID=Europe/Prague:20260413T235900
SUMMARY:Milonga Fuera del Nido
DESCRIPTION:Short description
LOCATION:Taneční studio Stolárna, Olomoucká 14
URL:https://example.com/milonga-fuera-del-nido/
RRULE:FREQ=WEEKLY;BYDAY=SU    ← only for recurring events
END:VEVENT

END:VCALENDAR
```

### URL types

| Type | Format | Use |
|---|---|---|
| webcal | `webcal://domain/calendars/{id}.ics` | Apple Calendar, default OS calendar |
| Google | `https://www.google.com/calendar/render?cid={encoded_url}` | Google Calendar "Add by URL" |
| HTTPS | `https://domain/calendars/{id}.ics` | Outlook "Subscribe from web", manual copy |

### Pelicanconf.py settings

```python
CALENDAR_ICS_OUTPUT_DIR = "calendars"                          # default
CALENDAR_ICS_EXCLUDED_CATEGORIES = ["announcement", "curiosity"]  # default
```

---

## Module Overview

| Module | Responsibility |
|---|---|
| `__init__.py` | Registers Pelican signals: `page_generator_finalized` → feed discovery, `finalized` → ICS writing |
| `config.py` | Default attribute dicts (`CALENDAR_DEFAULTS`, `CALENDAR_LINK_DEFAULTS`), regex patterns, shared cache |
| `attrs.py` | Parses widget attribute strings into dicts keyed by defaults |
| `dates.py` | Date parsing (`event-start`/`event-end` metadata), date window resolution, group headlines |
| `filter.py` | `calendar_filter` — filters by type, date window, sort, limit; used by display widget via Jinja filter |
| `grouping.py` | `group_events` — groups events by day/week/month for the display widget |
| `feed_links.py` | Feed discovery, fingerprinting, deduplication, URL generation (webcal/Google/HTTPS) |
| `ics.py` | ICS filter pipeline and `build_ics` / `write_ics_feeds` |

### Signal registration (`__init__.py`)

```python
signals.page_generator_finalized.connect(feed_links.discover_calendar_link_feeds)
signals.finalized.connect(ics.write_ics_feeds)
```

The generator reference is stashed in `config._GENERATOR_CACHE` so `write_ics_feeds` (called with a different signal argument) can access it.

### Jinja filters registered in `pelicanconf.py`

```python
JINJA_FILTERS = {
    "calendarium": make_calendar_filter(NOW),  # used by widget_calendar.html
    "group_events": group_events,              # used by widget_calendar.html
    "expand_recurring": expand_recurring,      # used by widget_calendar.html
}
```
