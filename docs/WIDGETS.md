# Widget System - Technical Documentation

## Overview

The widget system allows embedding dynamic calendar components in markdown content using HTML `div` elements with `data-widget` attributes. Widgets are processed server-side during Pelican's template rendering phase.

## Architecture

### Processing Flow

1. **Content Input**: Markdown files contain HTML `div` elements with `data-widget` attributes
2. **Markdown Processing**: Pelican's markdown processor preserves HTML elements
3. **Template Processing**: `page.html` template calls `process_widgets()` macro
4. **Widget Parsing**: Macro extracts widget type and attributes from HTML
5. **Component Rendering**: Appropriate widget component template is included
6. **Output**: Rendered HTML replaces the original widget `div`

### File Structure

```
theme/templates/
├── page.html                          # Uses widget processor
└── components/
    ├── widget_processor.html          # Main processing macro
    ├── filtered_events_widget.html    # Filtered events component
    └── calendar_month_widget.html     # Calendar month component
```

## Widget Processor

### Location

`theme/templates/components/widget_processor.html`

### Macro: `process_widgets(content)`

Recursively processes page content to find and replace widget `div` elements.

**Parameters:**
- `content` (string): The page content HTML/markdown

**Returns:**
- Rendered HTML with widgets replaced by components

**Algorithm:**
1. Split content by widget pattern `<div data-widget="`
2. For each widget found:
   - Extract attributes from HTML
   - Parse `data-widget`, `data-filter`, `data-span-type`, `data-span-days`, `data-span-start`, `data-span-end`, `data-year`, `data-month`
   - Include appropriate component template
   - Recursively process remaining content

### Supported Widget Types

#### 1. `filtered_events`

Displays filtered lists of events from `content/events/`.

**Attributes:**
- `data-widget="filtered_events"` (required)
- `data-filter="milonga|workshop|class"` (optional)
- `data-span-type="next"` (optional) - Show events in the future, requires `data-span-days`
- `data-span-type="last"` (optional) - Show events from the past, requires `data-span-days`
- `data-span-type="range"` (optional) - Show events in a date range, requires `data-span-start` and `data-span-end`
- `data-span-days="7"` (optional) - Number of days, used with `data-span-type="next"` or `data-span-type="last"`
- `data-span-start="2026-06-01"` (optional) - Start date for range, used with `data-span-type="range"`
- `data-span-end="2026-08-31"` (optional) - End date for range, used with `data-span-type="range"`

**Implementation:**
- Component: `theme/templates/components/filtered_events_widget.html`
- Filters articles from `articles` context where `source_path` contains `'events/'`
- Filtering logic:
  - `milonga`: Title contains "milonga"
  - `workshop`: Title contains "workshop", "lekce", or "lekci"
  - `class`: Title contains "class" or "lekce"
  - Date filtering: Filters events by date span (next/last N days or date range)
  - Filter type and date span can be combined

**Event Access Pattern:**
```jinja2
{% set event_start = event.start | default(event.metadata.get('event-start')) %}
{% set event_end = event.end | default(event.metadata.get('event-end')) %}
```

#### 2. `calendar_month`

Displays a calendar grid for a specific month with events marked.

**Attributes:**
- `data-widget="calendar_month"` (required)
- `data-year="2025"` (optional, default: 2025)
- `data-month="1"` (optional, default: 1, range: 1-12)

**Implementation:**
- Component: `theme/templates/components/calendar_month_widget.html`
- Filters events by year and month using `event-start` metadata
- Generates calendar grid with day numbers
- Displays events on their respective days

**Event Filtering:**
```jinja2
{% set page_start = page.start | default(page.metadata.get('event-start')) %}
{% if page_start and page_start.year == current_year and page_start.month == current_month %}
```

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

Templates use hybrid access pattern for compatibility:

```jinja2
{% set event_start = event.start | default(event.metadata.get('event-start')) %}
{% set event_end = event.end | default(event.metadata.get('event-end')) %}
```

**Priority:**
1. `event.start` / `event.end` (from pelican-events plugin if active)
2. `event.metadata.get('event-start')` / `event.metadata.get('event-end')` (from frontmatter)

**No backward compatibility:** Templates do not use `event.date` or `event.metadata.get('end_date')`.

## Adding New Widgets

### Step 1: Create Component Template

Create `theme/templates/components/your_widget.html`:

```jinja2
{% set your_data = data_param | default('default_value') %}

<div class="your-widget">
  <!-- Your widget HTML -->
</div>
```

### Step 2: Update Widget Processor

Add widget type handling in `widget_processor.html`:

```jinja2
{% elif widget_type == 'your_widget' %}
  {% set data_param = widget_attrs.get('data-param') %}
  {% include 'components/your_widget.html' with context %}
```

### Step 3: Parse Attributes

Extract attributes in the processor loop:

```jinja2
{% elif 'data-param="' in attr %}
  {% set data_param = attr.split('data-param="')[1] %}
```

### Step 4: Document Usage

Update README.md with widget syntax and examples.

## Technical Details

### HTML Parsing

The processor uses string splitting to parse HTML attributes:

```jinja2
{% set attrs = widget_attrs.split('" ') %}
{% for attr in attrs %}
  {% if 'data-widget="' in attr %}
    {% set widget_type = attr.split('data-widget="')[1] %}
  {% elif 'data-span-type="' in attr %}
    {% set span_type = attr.split('data-span-type="')[1] | lower %}
  {% elif 'data-span-days="' in attr %}
    {% set span_days = attr.split('data-span-days="')[1] | int %}
  {% elif 'data-span-start="' in attr %}
    {% set span_start_date = attr.split('data-span-start="')[1] %}
  {% elif 'data-span-end="' in attr %}
    {% set span_end_date = attr.split('data-span-end="')[1] %}
  {% endif %}
{% endfor %}
```

**Limitations:**
- Attributes must be separated by `" ` (quote + space)
- Attribute values must not contain spaces (use separate attributes instead)
- Self-closing tags not supported
- Nested widgets supported via recursion

### Context Variables

Widgets have access to full Pelican template context:

- `articles`: All articles (events are filtered from this)
- `pages`: All pages
- `SITEURL`: Site base URL
- `SITENAME`: Site name
- All other Pelican context variables

### Event Filtering

Events are identified by checking `article.source_path`:

```jinja2
{% for article in articles %}
  {% if article.source_path and 'events/' in article.source_path %}
    {% set _ = event_pages.append(article) %}
  {% endif %}
{% endfor %}
```

This matches Pelican's `ARTICLE_PATHS = ["announcements", "events", "classes"]` configuration.

### Date Handling

Widgets use standardized date access pattern:

```jinja2
{% set event_start = event.start | default(event.metadata.get('event-start')) %}
```

**Important:**
- `event.start` is a datetime object (from pelican-events plugin)
- `event.metadata.get('event-start')` may be a string (needs parsing if used for calculations)
- For display: `event_start.strftime('%d. %m. %Y')`
- For filtering: Use datetime attributes (`.year`, `.month`, `.day`)

## Troubleshooting

### Widget Not Rendering

**Check:**
1. Widget syntax matches exactly (copy from README.md)
2. Page uses `page.html` template (not custom template)
3. `process_widgets()` macro is called in template
4. No syntax errors in widget HTML

**Debug:**
- Check Pelican build output for template errors
- Verify widget `div` is in page content (not stripped by markdown)
- Test with simple widget first

### Events Not Appearing

**Check:**
1. Events exist in `content/events/` directory
2. Events have valid `event-start` metadata
3. Filter criteria match event titles (case-insensitive)
4. Events are within date range (if `data-span-type` is specified)

**Debug:**
- Check `article.source_path` contains `'events/'`
- Verify event metadata format matches standard
- Test event access: `{{ event.metadata.get('event-start') }}`

### Date Display Issues

**Check:**
1. Event has `event-start` in frontmatter
2. Format is `YYYY-MM-DD HH:MM:SS`
3. pelican-events plugin active (if using `event.start`)

**Debug:**
- Check metadata: `{{ event.metadata }}`
- Verify datetime object: `{{ event_start }}`
- Test strftime: `{{ event_start.strftime('%d. %m. %Y') }}`

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

## Future Enhancements

### Potential Improvements

1. **Widget Caching**: Cache filtered event lists
2. **More Filters**: Add date range, location, organizer filters
3. **Widget Configuration**: YAML frontmatter for widget settings
4. **Client-side Rendering**: Optional JavaScript for dynamic updates
5. **Widget Validation**: Pre-build validation of widget syntax

### pelican-events Integration

When pelican-events plugin is fully configured:
- `event.start` and `event.end` will be datetime objects
- Recurrence via `event-rrule` will be processed
- ICS calendar generation will use widget events
- Template access pattern already supports this

## Related Documentation

- **README.md**: User-facing widget documentation
- **setup.md**: Development environment setup
- **local-testing.md**: Testing widgets locally
- **publishing.md**: Deployment process
