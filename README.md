# Brnos Aires Web - Editor Guide

This guide is for content editors working with the Brnos Aires website. It covers how to create and edit events, use widgets, manage images, and organize content.

## Working with Event Files

### Where Event Files Are Located

All event files are stored in the `content/events/` folder. Each event has its own markdown file (`.md` file).

### Creating a New Event File

1. Create a new file in the `content/events/` folder
2. Name the file using lowercase letters, hyphens, and numbers (e.g., `milonga-fuera-del-nido.md`)
3. The file name becomes part of the event's web address, so make it descriptive

### Basic Event File Structure

Every event file has two parts:

1. **Frontmatter** (at the top, between `---` lines) - Contains metadata about the event
2. **Content** (below the frontmatter) - The event description and details

Example:

```markdown
---
title: Milonga Fuera del Nido
event-start: 2026-01-17 18:00:00
event-end: 2026-01-17 22:30:00
slug: milonga-fuera-del-nido
---

Your event description goes here. You can use **bold**, *italic*, and [links](https://example.com).
```

## Event Metadata - Dates and Times

Event files use four types of date/time information:

### 1. `date` - Article Date (Required)

Pelican requires this field for all articles. For events, this should match `event-start` in most cases. Only set it differently if the article was published on a different date than when the event happens.

**Format:** `YYYY-MM-DD HH:MM:SS`

**Example:**
```markdown
date: 2026-01-17 18:00:00
```

### 2. `event-start` - Event Start Time (Required)

This is the most important field. It tells when your event begins.

**Format:** `YYYY-MM-DD HH:MM:SS`

**Examples:**
```markdown
event-start: 2026-01-17 18:00:00
event-start: 2026-03-15 20:30:00
event-start: 2026-12-25 19:00:00
```

**Important:**
- Always include the date and time
- Use 24-hour format (18:00 instead of 6:00 PM)
- Use the format exactly as shown above

### 3. `event-end` - Event End Time (Optional)

Use this when your event has a specific end time. If the event doesn't have a fixed end time, you can skip this field.

**Format:** `YYYY-MM-DD HH:MM:SS`

**Examples:**
```markdown
event-end: 2026-01-17 22:30:00
event-end: 2026-03-15 23:00:00
```

**Important:**
- Must be on the same day or later than `event-start`
- Use the same format as `event-start`

### 4. `event-rrule` - Recurring Events (Advanced, Optional)

This field is for events that repeat regularly (like weekly classes). Most events don't need this. If you're not sure, skip it.

**When to use:**
- Weekly classes that happen every Monday
- Monthly events that repeat
- Other regular recurring events

**Format:** Uses pelican-events format (advanced - contact technical support if needed)

### Complete Event Example

```markdown
---
title: Milonga Fuera del Nido
date: 2026-01-17 18:00:00
event-start: 2026-01-17 18:00:00
event-end: 2026-01-17 22:30:00
slug: milonga-fuera-del-nido
---

Další Milonga tentokrát v úchvatných prostorách v parkovacím domě Domini Park.

Openclass od 18:00 (není nutné přijít s partnerem)
19.00-22.30 Milonga, DJ Kenan
```

### Common Date/Time Mistakes to Avoid

1. **Wrong format:** `17.1.2026 18:00` ❌
   - **Correct:** `2026-01-17 18:00:00` ✅

2. **Missing time:** `2026-01-17` ❌
   - **Correct:** `2026-01-17 18:00:00` ✅

3. **Using `date` instead of `event-start`:** `date: 2026-01-17 18:00:00` ❌
   - **Correct:** Include both `date` and `event-start` with the same value ✅

4. **Using `end_date` instead of `event-end`:** `end_date: 2026-01-17 22:30:00` ❌
   - **Correct:** `event-end: 2026-01-17 22:30:00` ✅

5. **Missing `date` field:** Events must have both `date` and `event-start` ❌
   - **Correct:** Include both `date` and `event-start` with the same value ✅

## Widget System

Widgets are special components that automatically display lists of events or calendars on your pages. You can add them anywhere in your markdown content.

### How Widgets Work

Widgets are embedded using simple HTML code that you paste into your markdown file. The website automatically replaces this code with the actual event list or calendar.

### Available Widgets

#### 1. Filtered Events Widget

Shows a list of events filtered by type (milongas, workshops, etc.) or time period.

**Basic Syntax:**
```html
<div data-widget="filtered_events" data-filter="milonga"></div>
```

**Options:**

- **Show all milongas:**
  ```html
  <div data-widget="filtered_events" data-filter="milonga"></div>
  ```

- **Show all workshops/lessons:**
  ```html
  <div data-widget="filtered_events" data-filter="workshop"></div>
  ```

- **Show events in the next 7 days:**
  ```html
  <div data-widget="filtered_events" data-filter="milonga" data-span-type="next" data-span-days="7"></div>
  ```

- **Show events from the last 30 days:**
  ```html
  <div data-widget="filtered_events" data-filter="milonga" data-span-type="last" data-span-days="30"></div>
  ```

- **Show events in a date range:**
  ```html
  <div data-widget="filtered_events" data-filter="milonga" data-span-type="range" data-span-start="2026-06-01" data-span-end="2026-08-31"></div>
  ```

**Attributes:**
- `data-widget="filtered_events"` - Always required
- `data-filter="milonga"`, `data-filter="workshop"`, or `data-filter="class"` - What type of events to show (optional)
- `data-span-type="next"` - Show events in the future (requires `data-span-days`)
- `data-span-type="last"` - Show events from the past (requires `data-span-days`)
- `data-span-type="range"` - Show events in a date range (requires `data-span-start` and `data-span-end`)
- `data-span-days="7"` - Number of days (used with `data-span-type="next"` or `data-span-type="last"`)
- `data-span-start="2026-06-01"` - Start date for range (used with `data-span-type="range"`)
- `data-span-end="2026-08-31"` - End date for range (used with `data-span-type="range"`)

#### 2. Calendar Month Widget

Shows a calendar grid for a specific month with events marked on their dates.

**Basic Syntax:**
```html
<div data-widget="calendar_month" data-year="2025" data-month="1"></div>
```

**Examples:**

- **Show current month (defaults to 2025, January):**
  ```html
  <div data-widget="calendar_month"></div>
  ```

- **Show specific month:**
  ```html
  <div data-widget="calendar_month" data-year="2025" data-month="3"></div>
  ```

**Attributes:**
- `data-widget="calendar_month"` - Always required
- `data-year="2025"` - Which year to show (optional, defaults to 2025)
- `data-month="1"` - Which month to show, 1-12 (optional, defaults to 1)

### Using Widgets in Pages

You can add widgets anywhere in your page content. Here's a complete example:

```markdown
---
title: Tango milongy Brno
slug: tango-milongy-brno
---

Tangové tančírny neboli **milongy v Brně** - pravidelné i nepravidelné.

<div data-widget="filtered_events" data-filter="milonga"></div>

## Upcoming Events

<div data-widget="filtered_events" data-filter="milonga" data-span-type="next" data-span-days="7"></div>
```

### Widget Best Practices

1. **Add headings before widgets** - Help readers understand what they're looking at
2. **Place widgets where they make sense** - Put event lists near relevant content
3. **Test after adding** - Make sure events are showing up correctly
4. **Widgets only show if events exist** - If no matching events are found, the widget won't appear

### Troubleshooting Widgets

**Widget not showing:**
- Check that events exist matching your filter (e.g., events with "milonga" in the title)
- Verify the syntax is correct (copy the examples exactly)
- Make sure you're editing a page file, not an event file

**Events not appearing:**
- Verify events are in the `content/events/` folder
- Check that event titles contain the right keywords (milonga, workshop, etc.) for filtering
- Ensure events have valid `event-start` dates

## Working with Images

### Where Images Are Stored

All images are in the `content/images/` folder. You can use JPG, JPEG, or PNG files.

### Adding Images to Events

To add an image to an event, use this format in your event content:

```markdown
![]({static}/images/your-image-name.jpg)
```

**Example:**
```markdown
---
title: Milonga Fuera del Nido
event-start: 2026-01-17 18:00:00
slug: milonga-fuera-del-nido
---

![]({static}/images/605635436_10241120531540882_4611790588703681234_n.jpg)

Your event description here...
```

### Image Best Practices

1. **Use descriptive filenames** - Makes it easier to find images later
2. **Optimize images before uploading** - Large images slow down the website
3. **Use JPG for photos, PNG for graphics** - Better file sizes
4. **Keep filenames simple** - Use lowercase letters, numbers, and hyphens

### Finding Images

To see what images are available, look in the `content/images/` folder. The filename you see there is what you use in your markdown (without the path).

## Content Organization

### Directory Structure

The website content is organized into folders:

- **`content/events/`** - All event files (milongas, workshops, etc.)
- **`content/pages/`** - Regular pages (about us, calendar pages, etc.)
- **`content/announcements/`** - Announcement posts
- **`content/classes/`** - Information about regular classes
- **`content/images/`** - All images used on the website

### Content Types

**Events** (`content/events/`)
- Individual events with dates and times
- Must have `event-start` field
- Appear in calendars and event lists

**Pages** (`content/pages/`)
- Regular website pages
- Can include widgets
- Examples: calendar pages, information pages

**Announcements** (`content/announcements/`)
- News and updates
- Don't need event dates

**Classes** (`content/classes/`)
- Information about regular classes
- May have recurring schedules

## Common Tasks

### Adding a New Event

1. Create a new file in `content/events/` folder
2. Name it descriptively (e.g., `milonga-fuera-del-nido.md`)
3. Add the frontmatter with required fields:
   ```markdown
   ---
   title: Your Event Title
   date: 2026-01-17 18:00:00
   event-start: 2026-01-17 18:00:00
   event-end: 2026-01-17 22:30:00
   slug: your-event-slug
   ---
   ```
4. Add your event description below the frontmatter
5. Save the file

### Updating Event Dates

1. Open the event file in `content/events/`
2. Find the `event-start` or `event-end` line in the frontmatter
3. Update the date/time using the format: `YYYY-MM-DD HH:MM:SS`
4. Save the file

**Example - changing start time:**
```markdown
event-start: 2026-01-17 19:00:00  (was 18:00:00)
```

### Adding Widgets to a Page

1. Open the page file in `content/pages/`
2. Find where you want the widget to appear
3. Add the widget code (copy from examples above)
4. Save the file

**Example:**
```markdown
## Upcoming Milongas

<div data-widget="filtered_events" data-filter="milonga"></div>
```

### Finding and Editing Existing Content

**To find an event:**
- Look in `content/events/` folder
- Search by filename or open files to see titles

**To find a page:**
- Look in `content/pages/` folder
- Filenames usually match the page topic

**To edit:**
- Open the file
- Make your changes
- Save the file

### Adding Images to Content

1. Place your image file in `content/images/` folder
2. In your content, add: `![]({static}/images/your-filename.jpg)`
3. Replace `your-filename.jpg` with your actual filename

## Quick Reference

### Required Event Fields

- `title` - Event name
- `date` - Article date for Pelican (format: `YYYY-MM-DD HH:MM:SS`)
- `event-start` - When event starts (format: `YYYY-MM-DD HH:MM:SS`)
- `slug` - URL-friendly identifier (usually lowercase, hyphens)

### Optional Event Fields

- `event-end` - When event ends
- `event-rrule` - Recurrence rule (advanced)

### Widget Quick Syntax

**Filtered events:**
```html
<div data-widget="filtered_events" data-filter="milonga"></div>
<div data-widget="filtered_events" data-filter="milonga" data-span-type="next" data-span-days="7"></div>
<div data-widget="filtered_events" data-filter="milonga" data-span-type="last" data-span-days="30"></div>
<div data-widget="filtered_events" data-filter="milonga" data-span-type="range" data-span-start="2026-06-01" data-span-end="2026-08-31"></div>
```

**Calendar month:**
```html
<div data-widget="calendar_month" data-year="2025" data-month="1"></div>
```

### Image Syntax

```markdown
![]({static}/images/filename.jpg)
```

## Need Help?

If you're unsure about:
- Date formats - Use the examples in this guide
- Widget syntax - Copy the examples exactly
- File locations - Check the directory structure section
- Image usage - See the images section

Remember: When in doubt, look at existing files for examples of how things are done.
