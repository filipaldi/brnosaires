# Widget System - Technical Documentation

## Overview

The widget system allows embedding dynamic components in markdown content using custom HTML tags. Widgets are processed server-side during Pelican's template rendering phase.

## Architecture

### Processing Flow

1. **Content Input**: Markdown files contain custom HTML tags (`<widget-calendar>`, `<widget-announcements>`, `<widget-curiosities>`, `<widget-classes>`)
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
    ├── widget_calendar.html           # Events: parses type, days, start, end, limit, sort
    ├── widget_announcements.html     # Announcements: parses limit, sort
    ├── widget_curiosities.html       # Curiosities: parses limit, sort
    └── widget_classes.html           # Classes: parses limit, sort
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
- Detects widget tags (`<widget-calendar />`, `<widget-announcements />`, etc.)
- Extracts tag name and raw tag content (attributes string)
- Routes to appropriate component template
- Passes `tag_content` variable to component (contains raw attributes string)
- Handles recursive processing for nested widgets

**Algorithm:**
1. Split content by widget pattern `<widget-`
2. For each widget found:
   - Extract tag name from tag content
   - Extract raw tag content (includes all attributes as string)
   - Route to component based on tag name (`calendar`, `announcements`, `curiosities`, `classes`)
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
- Tag names: `widget-calendar`, `widget-announcements`, `widget-curiosities`
- Internal widget types: `calendar` (widget_calendar.html), `announcements`, `curiosities`

### Attribute Naming

- **All attributes use standard HTML format (no `data-` prefix)**
- **All attributes use kebab-case**
- Examples: `type="milonga"`, `days="365"`, `limit="3"`

### Tag to Component Mapping

- `<widget-calendar>` → `widget_calendar.html`
- `<widget-announcements>` → `widget_announcements.html`
- `<widget-curiosities>` → `widget_curiosities.html`
- `<widget-classes>` → `widget_classes.html`

## Supported Widget Types

### 1. Events Widget (`<widget-calendar>`)

Displays filtered lists of events from `content/events/`.

**Attributes:**
- `type="milonga|workshop|class"` (optional) - Event type filter
- `days="7"` (optional) - Days from today (positive = future, negative = past)
- `start="2026-06-01"` (optional) - Start date for range (YYYY-MM-DD, requires `end`)
- `end="2026-08-31"` (optional) - End date for range (YYYY-MM-DD, requires `start`)
- `limit="3"` (optional) - Limit number of items displayed (`"3"`, `"all"`, `"last 3"`)
- `sort="newest|oldest"` (optional) - Sort order (default: newest first)

**Date Filtering:**
- `days="7"` = next 7 days from today
- `days="-7"` = last 7 days from today
- `days="365"` or `days="-365"` = all events (no date filtering)
- `start` + `end` = date range (both required, mutually exclusive with `days`)

**Examples:**
```html
<!-- Next 7 days of milongas -->
<widget-calendar type="milonga" days="7"></widget-calendar>

<!-- All workshops in next year -->
<widget-calendar type="workshop" days="365"></widget-calendar>

<!-- Milongas in date range -->
<widget-calendar type="milonga" start="2026-06-01" end="2026-08-31"></widget-calendar>

<!-- Last 3 milongas -->
<widget-calendar type="milonga" days="-7" limit="3"></widget-calendar>

<!-- Milongas sorted oldest first -->
<widget-calendar type="milonga" days="365" sort="oldest"></widget-calendar>
```

**Implementation:**
- Component: `theme/templates/components/widget_calendar.html`
- Parses attributes: `type`, `days`, `start`, `end`, `limit`, `sort` from `tag_content`
- Filters articles from `articles` context where `source_path` contains `'events/'`
- Filtering logic:
  - `milonga`: Title contains "milonga"
  - `workshop`: Title contains "workshop", "lekce", or "lekci"
  - `class`: Title contains "class" or "lekce"
  - Date filtering: Filters events by days from today or date range
  - Filter type and date filtering can be combined
- Sorting: By `date` attribute (newest/oldest)
- Limit: Applied after filtering and sorting

### 2. Announcements Widget (`<widget-announcements>`)

Displays announcements from `content/announcements/` as cards with images.

**Attributes:**
- `limit="3"` (optional) - Limit number of items (`"3"`, `"all"`, `"last 3"`)
- `sort="newest|oldest"` (optional) - Sort order (default: newest first)

**Examples:**
```html
<!-- Last 3 announcements -->
<widget-announcements limit="3"></widget-announcements>

<!-- All announcements sorted oldest first -->
<widget-announcements limit="all" sort="oldest"></widget-announcements>
```

**Implementation:**
- Component: `theme/templates/components/widget_announcements.html`
- Parses attributes: `limit`, `sort` from `tag_content`
- Filters articles from `articles` context where `source_path` contains `'announcements/'`
- Extracts first image from article content
- Renders cards with title and image
- Widget title: "Oznámení"

### 3. Curiosities Widget (`<widget-curiosities>`)

Displays curiosities from `content/curiosities/` as cards with images.

**Attributes:**
- `limit="3"` (optional) - Limit number of items (`"3"`, `"all"`, `"last 3"`)
- `sort="newest|oldest"` (optional) - Sort order (default: newest first)

**Examples:**
```html
<!-- Last 3 curiosities -->
<widget-curiosities limit="3"></widget-curiosities>

<!-- All curiosities sorted oldest first -->
<widget-curiosities limit="all" sort="oldest"></widget-curiosities>
```

**Implementation:**
- Component: `theme/templates/components/widget_curiosities.html`
- Parses attributes: `limit`, `sort` from `tag_content`
- Filters articles from `articles` context where `source_path` contains `'curiosities/'`
- Extracts first image from article content
- Renders cards with title and image
- Widget title: "Pikošky"

### 4. Classes Widget (`<widget-classes>`)

Displays classes from `content/classes/` as cards with images.

**Attributes:**
- `limit="3"` (optional) - Limit number of items (`"3"`, `"all"`, `"last 3"`)
- `sort="newest|oldest|title"` (optional) - Sort order (default: newest first)

**Examples:**
```html
<!-- Last 3 classes -->
<widget-classes limit="3"></widget-classes>

<!-- All classes sorted alphabetically by title -->
<widget-classes limit="all" sort="title"></widget-classes>
```

**Implementation:**
- Component: `theme/templates/components/widget_classes.html`
- Parses attributes: `limit`, `sort` from `tag_content`
- Filters articles from `articles` context where `source_path` contains `'classes/'`
- Extracts first image from article content
- Renders cards with title and image
- Widget title: "Lekce"
- Sorting: By `date` (newest/oldest) or `title` (alphabetical)

## Attribute Reference

| Attribute | Type | Required | Values | Description |
|-----------|------|----------|--------|-------------|
| `type` | string | No | `milonga`, `workshop`, `class` | Event type filter (for `widget-calendar` only) |
| `days` | integer | No | `7`, `365`, `-7` | Days from today (positive = future, negative = past) |
| `start` | date | No* | `YYYY-MM-DD` | Start date for range (*required if `end` present) |
| `end` | date | No* | `YYYY-MM-DD` | End date for range (*required if `start` present) |
| `limit` | string/integer | No | `"3"`, `"all"`, `"last 3"` | Limit number of items |
| `sort` | string | No | `newest`, `oldest`, `title` | Sort order (`title` only for `widget-classes`) |

**Rules:**
- If `start` is present, `end` is required (and vice versa)
- `days` and `start`/`end` are mutually exclusive
- `type` only applies to `widget-calendar` widget
- `sort="title"` only applies to `widget-classes` widget
- Default sort: `newest` (newest first)

## Event Metadata Standard

Widgets expect events to use standardized metadata format:

### Required Fields

- `date`: Article date (Pelican requirement, format: `YYYY-MM-DD HH:MM:SS`)
- `event-start`: Event start date/time (format: `YYYY-MM-DD HH:MM:SS`)
- `slug`: URL-friendly identifier

### Optional Fields

- `event-end`: Event end date/time (format: `YYYY-MM-DD HH:MM:SS`)
- `event-rrule`: Recurrence rule (pelican-events format)

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

Widgets identify content by checking `article.source_path`:

**Events:**
```jinja2
{% for article in articles %}
  {% if article.source_path and 'events/' in article.source_path %}
    {% set _ = event_pages.append(article) %}
  {% endif %}
{% endfor %}
```

**Announcements:**
```jinja2
{% for article in articles %}
  {% if article.source_path and 'announcements/' in article.source_path %}
    {% set _ = announcement_pages.append(article) %}
  {% endif %}
{% endfor %}
```

**Curiosities:**
```jinja2
{% for article in articles %}
  {% if article.source_path and 'curiosities/' in article.source_path %}
    {% set _ = curiosity_pages.append(article) %}
  {% endif %}
{% endfor %}
```

**Classes:**
```jinja2
{% for article in articles %}
  {% if article.source_path and 'classes/' in article.source_path %}
    {% set _ = class_pages.append(article) %}
  {% endif %}
{% endfor %}
```

This matches Pelican's `ARTICLE_PATHS = ["announcements", "events", "classes", "curiosities"]` configuration.

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

### Architecture Changes

**Old Architecture:**
- Widget processor parsed all attributes centrally
- Components received pre-parsed variables
- Widget type mapping required

**New Architecture:**
- Widget processor only detects and routes widgets
- Components parse their own attributes from `tag_content`
- Direct routing based on tag name
- Each component is self-contained

### From Old to New Syntax

**Widget Tags:**
- `<div data-widget="calendar">` → `<widget-calendar>` (widget_calendar.html)
- `<div data-widget="announcements">` → `<widget-announcements>`
- `<div data-widget="curiosities">` → `<widget-curiosities>`
- `<div data-widget="classes">` → `<widget-classes>`

**Attributes:**
- `data-type="milonga"` → `type="milonga"`
- `data-days="7"` → `days="7"`
- `data-start="2026-06-01"` → `start="2026-06-01"`
- `data-end="2026-08-31"` → `end="2026-08-31"`
- `data-limit="3"` → `limit="3"`
- `data-pagination="12"` → removed (not supported)
- New: `sort="newest|oldest|title"` (available for all widgets)

**Examples:**
```html
<!-- Old -->
<div data-widget="calendar" data-type="milonga" data-days="7"></div>

<!-- New -->
<widget-calendar type="milonga" days="7"></widget-calendar>

<!-- New with sorting -->
<widget-calendar type="milonga" days="365" sort="oldest"></widget-calendar>
```

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
