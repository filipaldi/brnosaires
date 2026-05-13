# Widget System - Technical Documentation

## Overview

The widget system allows embedding dynamic components in markdown content using custom HTML tags. Widgets are processed server-side during Pelican's template rendering phase.

## Architecture

### Processing Flow

1. **Content Input**: Markdown files contain custom HTML tags (`<widget-calendar>`, `<widget-articles>`)
2. **Markdown Processing**: Pelican's markdown processor preserves HTML elements
3. **Template Processing**: `page.html` template calls `process_widgets()` macro
4. **Widget Detection**: Macro detects widget tags and extracts tag name + raw attributes string
5. **Routing**: Macro routes to appropriate component template based on tag name
6. **Attribute Parsing**: Each component parses its own attributes from the raw tag content
7. **Component Rendering**: Component filters, sorts, limits, and renders content
8. **Output**: Rendered HTML replaces the original widget tag

### File Structure

```
theme/templates/
├── page.html                          # Uses widget processor
└── components/
    ├── widget_processor.html          # Simplified: detection + routing only
    ├── widget_calendar.html           # Events: parses filter_by_type, days, start, end, limit, sort, group_by
    └── widget_articles.html           # Articles: unified widget for announcements, curiosities, people

plugins/
├── calendarium/                        # Calendar filtering and grouping (package)
│   ├── __init__.py                    # Plugin registration
│   ├── config.py                      # Constants and defaults
│   ├── attrs.py                       # Widget attribute parsing
│   ├── dates.py                       # Date utilities
│   ├── filter.py                      # Event filtering
│   ├── grouping.py                    # Event grouping
│   ├── feed_links.py                  # Calendar link/feed discovery
│   └── ics.py                         # ICS file generation
└── article_filter.py                  # Article filtering by category, slugs, sort, limit
```

## Widget Processor

### Location

`theme/templates/components/widget_processor.html`

### Macro: `process_widgets(content)`

Recursively processes page content to find and replace widget tags.

**Parameters:**
- `content` (string): The page content HTML/markdown

**Returns:**
- Rendered HTML with widgets replaced by components

**Responsibilities:**
- Detects widget tags (`<widget-calendar />`, `<widget-articles />`, etc.)
- Extracts tag name and raw tag content (attributes string)
- Routes to appropriate component template
- Passes `tag_content` variable to component (contains raw attributes string)
- Handles recursive processing for nested widgets

**Algorithm:**
1. Split content by widget pattern `<widget-`
2. For each widget found:
   - Extract tag name from tag content
   - Extract raw tag content (includes all attributes as string)
   - Route to component based on tag name (`calendar`, `articles`)
   - Pass `tag_content` variable to component
   - Component handles its own attribute parsing
   - Recursively process remaining content

**Key Design:**
- Processor does NOT parse attributes (components handle their own parsing)
- Processor only detects and routes widgets
- Each component is self-contained and independent

## Standardization Rules

### Widget Type Naming

- All widget tags use **kebab-case** (lowercase with hyphens)
- Tag names: `widget-calendar`, `widget-articles`
- Internal widget types: `calendar` (widget_calendar.html), `articles` (widget_articles.html)

### Attribute Naming

- **All attributes use standard HTML format (no `data-` prefix)**
- **All attributes use kebab-case**
- Examples: `type="milonga"`, `days="365"`, `limit="3"`, `category="announcement"`

### Tag to Component Mapping

- `<widget-calendar>` → `widget_calendar.html`
- `<widget-articles>` → `widget_articles.html`

## Supported Widget Types

### 1. Events Widget (`<widget-calendar>`)

Displays filtered lists of events from `content/events/`.

**Attributes:**
- `filter_by_type="milonga|workshop|class|..."` (optional) - Event type filter. Single type or space-separated list for OR logic (e.g. `filter_by_type="milonga neolonga pocoloco"`).
- `days="7"` (optional) - Days from today (positive = future, negative = past)
- `start="2026-06-01"` (optional) - Start of date window. Can be used alone (forward from start) or with `end`. Values: `YYYY-MM-DD`, or tokens `today`, `this-week` (Monday of current week), `this-month` (1st of month), `this-year` (1st Jan).
- `end="2026-08-31"` (optional) - End of date window. Same format as `start`. If only `start` is set, end defaults to start + 365 days.
- `month="6"` (optional) - Restrict the widget to **one calendar month** — the whole of month 6 (June) in the *upcoming-framing* year (this year, or next year if June has already passed). Accepts a number `1`–`12` or a month name, Czech (incl. locative forms — `cerven`, `červnu`, `leden`, `prosinci`…) or English (`June`). **Overrides `days`/`start`/`end`** (if `month` is unparseable, the widget falls through to the normal `days`/`start`/`end` logic). This is what powers the 12 evergreen month pages (`/milongy-brno-<měsíc>/` — see [SEO.md → Evergreen month pages](SEO.md)); year resolution mirrors the `tango_year_for_month` Jinja filter.
- `limit="3"` (optional) - Limit number of items displayed (`"3"`, `"all"`, `"last 3"`)
- `sort="newest|oldest"` (optional) - Sort order (default: **oldest first**, i.e. chronological)
- `group_by="day|week|month|week day"` (optional) - Group events into rows with a headline per group. Single value (e.g. `"week"`) = flat grouping. Space-separated tokens (e.g. `"week day"`) = nested grouping with 7-column grid layout (first token = outer/rows, second token = inner/columns). When set, only non-empty groups are shown; sort is chronological (earliest first) between and within groups.
- `headers="week|day|week day"` (optional) - Show group headers. Default: headers hidden. Values: `"week"` (show week headers only), `"day"` (show day headers only), `"week day"` (show both). Only applies when `group_by` is set.
- `hide_empty_days="true"` (optional) - Hide empty day columns in week-day grid layout. Default: false (all 7 days rendered). Only applies when `group_by="week day"` is set.
- `card_size="xs|s|m|l"` (optional) - Card size for event cards. Default: `s` (small). Values: `xs` (extra small), `s` (small), `m` (medium), `l` (large).

**Date Filtering:**
- `days="7"` = next 7 days from today
- `days="-7"` = last 7 days from today
- `days="365"` or `days="-365"` = one-year window from today
- `start` (optional) = start of window; use with or without `end`. With `end` = date range; without `end` = from start to start+365 days. Mutually exclusive with `days`.
- `start` and `end` accept tokens `today`, `this-week`, `this-month`, `this-year` or `YYYY-MM-DD`
- `month="6"` / `month="cerven"` = exactly that calendar month in the upcoming-framing year; overrides `days`/`start`/`end`

**Examples:**
```html
<!-- Next 7 days of milongas -->
<widget-calendar filter_by_type="milonga" days="7"></widget-calendar>

<!-- All workshops in next year -->
<widget-calendar filter_by_type="workshop" days="365"></widget-calendar>

<!-- Milongas in date range -->
<widget-calendar filter_by_type="milonga" start="2026-06-01" end="2026-08-31"></widget-calendar>

<!-- Just June's milongas/praktikas (the evergreen-month-page widget) -->
<widget-calendar filter_by_type="milonga praktika neolonga" month="6"></widget-calendar>

<!-- Last 3 milongas -->
<widget-calendar filter_by_type="milonga" days="-7" limit="3"></widget-calendar>

<!-- Milongas from today (default sort is oldest first) -->
<widget-calendar filter_by_type="milonga" start="today"></widget-calendar>

<!-- Multiple event types (OR): milonga or neolonga or pocoloco -->
<widget-calendar filter_by_type="milonga neolonga pocoloco" days="7"></widget-calendar>

<!-- Events grouped by week (rows per week with headline) -->
<widget-calendar days="365" group_by="week"></widget-calendar>

<!-- Events in week-day grid (7 columns, no headers) -->
<widget-calendar start="this-week" group_by="week day" days="14"></widget-calendar>

<!-- Events in week-day grid with week headers only -->
<widget-calendar start="this-week" group_by="week day" days="14" headers="week"></widget-calendar>

<!-- Events in week-day grid with both headers -->
<widget-calendar start="this-week" group_by="week day" days="14" headers="week day"></widget-calendar>

<!-- Events in week-day grid, hiding empty days -->
<widget-calendar start="this-week" group_by="week day" days="14" headers="day" hide_empty_days="true"></widget-calendar>

<!-- Events with medium-sized cards -->
<widget-calendar filter_by_type="milonga" days="7" card_size="m"></widget-calendar>

<!-- Events with large-sized cards -->
<widget-calendar filter_by_type="workshop" days="30" card_size="l"></widget-calendar>
```

**Grouping (`group_by`):**
- **Flat grouping:** Single value (`day`, `week`, `month`). Events shown in rows by group; each row has a headline (day date, week date range, or month name + year).
- **Nested grouping:** Space-separated tokens (e.g. `"week day"`). First token = outer grouping (rows), second token = inner grouping (columns). Creates a 7-column grid layout when using `"week day"`.
- **Week:** Monday–Sunday; headline = date range "Týden od 3.2. do 9.2. 2026" in Czech, "Week from 3 Feb to 9 Feb 2026" in English.
- **Day (nested):** Short format with weekday abbreviation: "Po 3.2." (Czech), "Mon 3 Feb" (English).
- **Empty groups:** Rows with zero events are not rendered (flat grouping). In nested grouping with `"week day"`, all 7 day columns are rendered by default (even if empty) to maintain grid structure. Use `hide_empty_days="true"` to hide empty columns.
- **Sort:** Chronological (earliest first) between groups and within each group. The widget's `sort` attribute does not apply when `group_by` is set.
- **Headers:** By default, group headers are hidden. Use `headers` attribute to show them (e.g. `headers="week"`, `headers="day"`, `headers="week day"`).
- **Layout:** Nested grouping uses a responsive day-column grid (`.calendar-days-grid`) that keeps all visible days in a single row. Columns automatically expand to fill available width based on the number of visible days. When `hide_empty_days="true"`, only days with events are shown and each takes equal width. Events within each day stack vertically using `.el-stack`.
- **Locale:** Headlines and date formats depend on `DEFAULT_LANG` (e.g. `cs`, `en`). Czech is supported now; English can be added by setting `DEFAULT_LANG = "en"` and ensuring the theme uses it.

**Implementation:**
- Component: `theme/templates/components/widget_calendar.html` parses attributes from `tag_content` and calls the `calendarium` Jinja filter (from plugin `plugins/calendarium/filter.py`) for all filtering, date window, sort, and limit.
- Filtering (filter_by_type, date window, sort, limit) is implemented in the calendarium plugin; the template only parses attributes and renders the result. Event type uses metadata `event-type`; multiple types in `filter_by_type="a b c"` are OR. Categories `announcement` and `curiosity` are excluded.
- Grouping: When `group_by` is set, the calendarium plugin's `group_events` filter groups events by day/week/month and returns `(headline, events)` pairs; template renders a section per group with headline + card grid.
- Default sort: oldest first (chronological). Use `sort="newest"` for reverse.

### 2. Calendar Subscribe Link (`<widget-calendar-link>`)

Generates a headline and three platform subscribe links for an iCal (.ics) feed: webcal (Apple / default calendar apps), Google Calendar, and a plain HTTPS link (e.g. for Outlook “Subscribe from web”). The plugin discovers these widgets, creates one `.ics` file per unique feed configuration, and renders one headline plus one plain `<a>` per platform. No classes are applied.

**Attributes:**
- `cal_file_name="all|marathon|..."` (optional) - Output filename for the feed: `/calendars/{cal_file_name}.ics`. If omitted, a stable ID is derived from the filter (hash). Use explicit `cal_file_name` for readable URLs (e.g. `/calendars/marathon.ics`).
- `filter_by_type="milonga|workshop|..."` (optional) - Event type filter (same as `widget-calendar`)
- `days="7"` (optional) - Days from today (positive = future, negative = past)
- `start="2026-06-01"` (optional) - Start of date window (same as `widget-calendar`)
- `end="2026-08-31"` (optional) - End of date window
- `filter_by_path="events/2026-marathon"` (optional) - Filter by article source path containing this substring
- `category="events"` (optional) - Filter by Pelican category name (e.g. `events`, `classes`)
- `tags="tango workshop"` (optional) - Space-separated tags (OR logic)
- `label="Subscribe"` (optional) - Headline text above the links (default: "Subscribe to calendar")
- `label_webcal="Apple"` (optional) - Link text for the webcal link (default: "Apple / default calendar")
- `label_google="Google"` (optional) - Link text for the Google Calendar link (default: "Google Calendar")
- `label_outlook="Ostatní"` (optional) - Link text for the HTTPS/copy link (default: "Copy link")

**Feed Generation:**
- The plugin scans all pages and articles for `<widget-calendar-link>` tags at build time
- For each unique feed configuration (same `feed_id` or same filter), one `.ics` file is generated in `output/calendars/`
- Events with recurrence metadata emit RRULE in the iCal feed
- The widget renders as: one `<div>` with a `<p>` (headline from `label`) and one plain `<a>` per platform (webcal, Google, https).

**Renders as (example):**
```html
<div>
  <p>📆 Odebírej akce do svého kalendáře</p>
  <a href="webcal://example.com/calendars/events.ics">Apple</a>
  <a href="https://www.google.com/calendar/render?cid=https%3A%2F%2Fexample.com%2Fcalendars%2Fevents.ics">Google</a>
  <a href="https://example.com/calendars/events.ics">Ostatní</a>
</div>
```

**Examples:**
```html
<!-- All events (no filter) -->
<widget-calendar-link cal_file_name="all" label="Přidat do kalendáře"></widget-calendar-link>

<!-- Headline and custom link labels -->
<widget-calendar-link
  cal_file_name="events"
  filter_by_path="events"
  label="📆 Odebírej akce do svého kalendáře"
  label_webcal="Apple"
  label_google="Google"
  label_outlook="Ostatní"
></widget-calendar-link>

<!-- Marathon events only -->
<widget-calendar-link cal_file_name="marathon" filter_by_path="events/2026-marathon" label="Marathon 2026"></widget-calendar-link>

<!-- Milongas in next 30 days -->
<widget-calendar-link cal_file_name="milongas" filter_by_type="milonga" days="30" label="Upcoming milongas"></widget-calendar-link>
```

**Configuration (optional):**
In `pelicanconf.py`:
```python
CALENDAR_ICS_OUTPUT_DIR = "calendars"  # Default: "calendars"
CALENDAR_ICS_EXCLUDED_CATEGORIES = ["announcement", "curiosity"]  # Default: same as EXCLUDED_CATEGORIES
```

**Implementation:**
- See `plugins/calendarium/README.md` for full plugin documentation: feed discovery, ICS generation, filter pipeline, URL types, and module overview.
- Component: `theme/templates/components/widget_calendar_link.html` renders one headline and three links (no classes)

### 3. Articles Widget (`<widget-articles>`)

Unified widget for displaying articles filtered by category. Replaces the old `widget-announcements`, `widget-curiosities`, `widget-classes`, and `widget-people` widgets.

**Attributes:**
- `category="announcement|curiosity|people"` (required) - Category to filter by
- `slugs="slug1 slug2"` (optional) - Space-separated list of article slugs to display in order. Overrides `sort` and `limit`.
- `sort="newest|oldest|title"` (optional) - Sort order (default: oldest first)
- `limit="3"` (optional) - Limit number of items (`"3"`, `"all"`, `"last 3"`)
- `columns="3"` (optional) - Grid columns for layout (uses `.el-grid-N`)
- `metadata="description location"` (optional) - Space-separated list of extra metadata fields to display

**Examples:**
```html
<!-- Last 3 announcements -->
<widget-articles category="announcement" limit="3"></widget-articles>

<!-- All curiosities -->
<widget-articles category="curiosity" limit="all"></widget-articles>

<!-- People with descriptions -->
<widget-articles category="people" metadata="description"></widget-articles>

<!-- Specific people in specific order -->
<widget-articles category="people" slugs="filip-paldia lenka-platenikova" metadata="description"></widget-articles>

<!-- Announcements sorted newest first -->
<widget-articles category="announcement" limit="12" sort="newest"></widget-articles>
```

**Implementation:**
- Component: `theme/templates/components/widget_articles.html`
- Plugin: `plugins/article_filter.py` provides `parse_article_attrs` and `article_filter` Jinja filters
- Filters articles by `article.category.name`
- Returns list of `{article, extra_metadata}` dicts
- Template renders cards with title, description (if present), preview image, and any extra metadata fields

**Paginated archive (two-tier pattern):** For a preview page with limited items plus a link to full archive, use `limit="12"` and add a link to the category page: `[Všechny oznamy →](/category/announcement/)`. The full paginated list is at `/category/announcement/` via Pelican's category template with 12 items per page.

## Attribute Reference

### widget-calendar Attributes

| Attribute | Type | Required | Values | Description |
|-----------|------|----------|--------|-------------|
| `filter_by_type` | string | No | `milonga`, `workshop`, `class`, or space-separated for OR | Event type filter |
| `days` | integer | No | `7`, `365`, `-7` | Days from today (positive = future, negative = past) |
| `start` | date/token | No | `YYYY-MM-DD`, `today`, `this-week`, `this-month`, `this-year` | Start of date window |
| `end` | date/token | No | Same as `start` | End of date window (optional if `start` set) |
| `limit` | string/integer | No | `"3"`, `"all"`, `"last 3"` | Limit number of items |
| `sort` | string | No | `newest`, `oldest` | Sort order (default: oldest) |
| `group_by` | string | No | `day`, `week`, `month`, `week day` | Group events into rows |
| `headers` | string | No | `week`, `day`, `week day` | Show group headers (default: hidden) |
| `hide_empty_days` | boolean | No | `true`, `false` | Hide empty day columns in week-day grid |
| `card_size` | string | No | `xs`, `s`, `m`, `l` | Card size (default: `s`) |

### widget-articles Attributes

| Attribute | Type | Required | Values | Description |
|-----------|------|----------|--------|-------------|
| `category` | string | Yes | `announcement`, `curiosity`, `people`, etc. | Category to filter by |
| `slugs` | string | No | `"slug1 slug2 slug3"` | Space-separated slugs to show in order (overrides sort/limit) |
| `sort` | string | No | `newest`, `oldest`, `title` | Sort order (default: oldest) |
| `limit` | string/integer | No | `"3"`, `"all"`, `"last 3"` | Limit number of items |
| `columns` | string/integer | No | `"3"` | Grid columns for layout |
| `metadata` | string | No | `"title description image location"` | Space-separated fields to display (default: `title description`) |
| `card_size` | string | No | `s`, `m`, `l` | Card size: small, medium (default), or large |
| `link` | string | No | `true`, `false`, `yes`, `no`, `0` | Whether each card links to the article; default is link. `false`/`no`/`0` render non-clickable cards. |

**Rules:**
- `days` and `start`/`end` are mutually exclusive for `widget-calendar`
- `group_by` only applies to `widget-calendar`; when set, sort is always chronological
- `slugs` overrides `sort` and `limit` for `widget-articles`
- Default sort: `oldest` (chronological)

## Event Metadata Standard

Widgets expect events to use standardized metadata format:

### Required Fields

- `date`: Article date (Pelican requirement, format: `YYYY-MM-DD HH:MM:SS`)
- `event-start`: Event start date/time (format: `YYYY-MM-DD HH:MM:SS`)
- `slug`: URL-friendly identifier

### Optional Fields

- `event-end`: Event end date/time (format: `YYYY-MM-DD HH:MM:SS`)
- `recurrence`: Recurring events are expanded into multiple occurrences in the calendar widget. Use a simple phrase: `recurrence: weekly sunday` (every Sunday), `recurrence: monthly 1 saturday` (first Saturday of month). Raw RRULE is also supported via optional `event-rrule` for advanced use.

### Template Access Pattern

Templates use metadata only for event start/end:

```jinja2
{% set event_start = event.metadata.get('event-start') if event.metadata else none %}
{% set event_end = event.metadata.get('event-end') if event.metadata else none %}
```

Templates do not use `event.date` or `event.metadata.get('end_date')`.

## Adding New Widgets

### Step 1: Create Component Template

Create `theme/templates/components/your-widget.html`:

```jinja2
{% set your_param = none %}

{% if tag_content %}
  {% set tag_name_parts = tag_content.split(' ') %}
  {% set tag_name = tag_name_parts[0] %}
  {% if tag_name_parts | length > 1 %}
    {% set attrs_str = tag_content[tag_name | length:] | trim %}
    {% if attrs_str %}
      {% set attrs_list = attrs_str.split('" ') %}
      {% for attr in attrs_list %}
        {% if 'your-attr="' in attr %}
          {% set your_param = attr.split('your-attr="')[1] %}
        {% endif %}
      {% endfor %}
    {% endif %}
  {% endif %}
{% endif %}

<div class="your-widget">
  <!-- Your widget HTML -->
</div>
```

**Key points:**
- Component receives `tag_content` variable from processor
- Component parses its own attributes from `tag_content`
- Use standard attribute parsing pattern (split by `" `)

### Step 2: Update Widget Processor

Add routing in `widget_processor.html`:

```jinja2
{% elif tag_name == 'your-widget' %}
  {% include 'components/your_widget.html' with context %}
```

**Key points:**
- Processor only routes based on `tag_name`
- Passes `tag_content` variable automatically
- No attribute parsing in processor

### Step 3: Document Usage

Update this documentation with widget syntax and examples.

## Technical Details

### Widget Tag Detection

The processor uses string splitting to detect widget tags:

```jinja2
{% set parts = content.split('<widget-') %}
{% for part in parts[1:] %}
  {% set tag_parts = part.split('>', 1) %}
  {% set tag_content = tag_parts[0] %}
  {% set tag_name_parts = tag_content.split(' ') %}
  {% set tag_name = tag_name_parts[0] %}
  <!-- Route to component, pass tag_content -->
{% endfor %}
```

### Attribute Parsing (in Components)

Each component parses its own attributes from `tag_content`:

```jinja2
{% set tag_name_parts = tag_content.split(' ') %}
{% set tag_name = tag_name_parts[0] %}
{% if tag_name_parts | length > 1 %}
  {% set attrs_str = tag_content[tag_name | length:] | trim %}
  {% if attrs_str %}
    {% set attrs_list = attrs_str.split('" ') %}
    {% for attr in attrs_list %}
      {% if 'your-attr="' in attr %}
        {% set your_param = attr.split('your-attr="')[1] %}
      {% endif %}
    {% endfor %}
  {% endif %}
{% endif %}
```

**Features:**
- Supports both self-closing (`<widget-calendar />`) and paired tags (`<widget-calendar></widget-calendar>`)
- Handles whitespace and newlines in tags
- Attributes must be separated by `" ` (quote + space)
- Attribute values must not contain spaces (use separate attributes instead)
- Nested widgets supported via recursion
- Each component is self-contained and handles its own parsing

### Context Variables

Widgets have access to full Pelican template context:

- `articles`: All articles (events are filtered from this)
- `pages`: All pages
- `SITEURL`: Site base URL
- `SITENAME`: Site name
- `NOW`: Current datetime object (automatically exposed from `pelicanconf.py`)
- All other Pelican context variables

### Content Filtering

**widget-calendar:** Uses the `calendarium` plugin which filters by event metadata and excludes categories `announcement` and `curiosity`.

**widget-articles:** Uses the `article_filter` plugin which filters by `article.category.name`:

```python
def _filter_by_category(articles, category):
    category_lower = category.strip().lower()
    out = []
    for a in articles or []:
        cat = getattr(a, "category", None)
        if cat and getattr(cat, "name", "").lower() == category_lower:
            out.append(a)
    return out
```

This matches Pelican's `ARTICLE_PATHS = ["announcements", "events", "classes", "curiosities", "people"]` configuration where each subdirectory becomes a category.

### Date Handling

Widgets use metadata for event dates:

```jinja2
{% set event_start = event.metadata.get('event-start') if event.metadata else none %}
```

**Important:**
- The value may be a string (needs parsing if used for calculations)
- For display: branch on `event_start is string` and slice or use `strftime` accordingly
- For filtering: normalise to date/datetime before comparing

## Troubleshooting

### Widget Not Rendering

**Check:**
1. Widget syntax matches exactly (copy from examples above)
2. Widget tag name uses correct format (`widget-calendar`, not `widget_calendar`)
3. All attributes use standard HTML format (no `data-` prefix)
4. Page uses `page.html` template (not custom template)
5. `process_widgets()` macro is called in template
6. No syntax errors in widget HTML

**Debug:**
- Check Pelican build output for template errors
- Verify widget tag is in page content (not stripped by markdown)
- Test with simple widget first

### Events Not Appearing

**Check:**
1. Events exist in correct directory (`content/events/`, `content/announcements/`, etc.)
2. Events have valid `event-start` metadata
3. Filter criteria match event titles (case-insensitive)
4. Events are within date range (if `days` or `start`/`end` specified)

**Debug:**
- Check `article.source_path` contains expected path
- Verify event metadata format matches standard
- Test event access: `{{ event.metadata.get('event-start') }}`

### Date Display Issues

**Check:**
1. Event has `event-start` in frontmatter
2. Format is `YYYY-MM-DD HH:MM:SS`

**Debug:**
- Check metadata: `{{ event.metadata }}`
- Verify datetime object: `{{ event_start }}`
- Test strftime: `{{ event_start.strftime('%d. %m. %Y') }}`

## Migration Guide

### From Legacy Widgets to widget-articles

The following widgets have been replaced by the unified `widget-articles`:

| Old Widget | New Widget |
|------------|------------|
| `<widget-announcements limit="3">` | `<widget-articles category="announcement" limit="3">` |
| `<widget-curiosities limit="3">` | `<widget-articles category="curiosity" limit="3">` |
| `<widget-classes limit="3">` | `<widget-articles category="class" limit="3">` |
| `<widget-people>` | `<widget-articles category="people" metadata="description">` |
| `<widget-people slugs="...">` | `<widget-articles category="people" slugs="..." metadata="description">` |

**Key changes:**
- All article-based widgets now use `<widget-articles>` with a `category` attribute
- The `metadata` attribute allows specifying which extra fields to display (e.g., `description`)
- The `slugs` attribute works the same way for selecting specific articles in order
- `pagination` attribute was never implemented and is removed

## Performance Considerations

### Widget Processing

- Widgets are processed during template rendering (server-side)
- No client-side JavaScript required
- Processing is recursive (supports nested widgets)
- Each widget processes all articles (consider caching for large sites)

### Event Filtering

- Filtering happens in Jinja2 templates (no database queries)
- All articles loaded into memory
- Filtering is O(n) where n = number of articles
- Consider pagination for large event lists

## Related Documentation

- **README.md**: User-facing widget documentation
- **setup.md**: Development environment setup
- **local-testing.md**: Testing widgets locally
- **publishing.md**: Deployment process
