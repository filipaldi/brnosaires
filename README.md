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

### Ideal Event Metadata (Boilerplate for Editors)

Events are displayed with metadata on the site (type, date range, location, organiser, instructors). Fill these in the frontmatter so the event page and widgets show consistent information.

| Field | Required | Use |
|-------|----------|-----|
| `title` | Yes | Event name. |
| `slug` | Yes | URL slug (lowercase, hyphens). Often same as filename without `.md`. |
| `date` | Yes | Article date. Use same as `event-start` unless published on another day. Format: `YYYY-MM-DD HH:MM:SS`. |
| `event-type` | Recommended | One of: `milonga`, `workshop`, `class`, `praktika`. Used for filtering in widgets. |
| `event-start` | Yes | Start date and time. Format: `YYYY-MM-DD HH:MM:SS`. |
| `event-end` | Recommended | End date and time. Same format as `event-start`. |
| `event-location` | Recommended | Venue name and address (e.g. `Taneční studio Stolárna, Olomoucká 14` or `Café Adrinela`). |
| `event-organiser` | Recommended | Who organises the event (e.g. `Taneční studio Stolárna`, `Lenka a Filip`). |
| `instructor` | For classes/workshops | Instructors. Use list format: `"['Name One', 'Name Two']"` or a single name. |
| `recurrence` | For recurring events | e.g. `weekly sunday`, `weekly tuesday`. See recurrence section below. |
| `description` | Recommended | Short summary for cards and SEO. |
| `preview_image` | Optional | Path to image, e.g. `/images/event.avif`. |
| `author` | Optional | Content author. |

**Boilerplate – one-off event (milonga or workshop):**

```markdown
---
title: Event name
slug: event-name
date: 2026-01-17 18:00:00
event-type: milonga
event-start: 2026-01-17 18:00:00
event-end: 2026-01-17 22:30:00
event-location: Venue name, address
event-organiser: Organiser name
description: Short summary for cards and search.
preview_image: /images/your-image.avif
author: Your name
---

Body text here.
```

**Boilerplate – recurring class:**

```markdown
---
title: Class name
slug: class-name
date: 2026-01-16 01:00:00
event-type: class
event-start: 2026-01-08 18:00:00
event-end: 2026-01-08 20:00:00
recurrence: weekly tuesday
event-organiser: Studio name
event-location: Address, Brno
instructor: "['Instructor One', 'Instructor Two']"
description: Short summary.
preview_image: /images/class.avif
author: Your name
---

Body text here.
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

### 4. `recurrence` - Recurring Events (Optional)

This field is for events that repeat regularly (like weekly classes). Most events don't need this. If you're not sure, skip it.

**When to use:**
- Weekly classes that happen every Monday
- Monthly events that repeat
- Other regular recurring events

**Format:** Simple phrase. `event-start` is the first occurrence; the rule repeats from that date.

**Examples:**
- Every Sunday: `recurrence: weekly sunday`
- First Saturday of month: `recurrence: monthly 1 saturday`
- Every Monday: `recurrence: weekly monday`

For advanced use, raw iCalendar RRULE is still supported via `event-rrule` (e.g. `event-rrule: "FREQ=WEEKLY;BYDAY=SU"`).

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

Widgets are special components that automatically display lists of events on your pages. You can add them anywhere in your markdown content.

For full widget documentation — all attributes, examples, and technical details — see **[docs/WIDGETS.md](docs/WIDGETS.md)**.

### Available Widgets

**`<widget-calendar>`** — displays filtered event cards:
```html
<widget-calendar filter_by_type="milonga" days="14"></widget-calendar>
```

**`<widget-calendar-link>`** — renders calendar subscription links (Apple, Google, Outlook):
```html
<widget-calendar-link
    cal_file_name="milongas"
    filter_by_path="events"
    filter_by_type="milonga"
    label="📆 Odebírej milongy do svého kalendáře"
    label_webcal="Apple"
    label_google="Google"
    label_outlook="Ostatní">
</widget-calendar-link>
```

**`<widget-articles>`** — displays article cards filtered by category:
```html
<widget-articles category="announcement" limit="3"></widget-articles>
```

### Troubleshooting Widgets

**Widget not showing:**
- Verify the syntax is correct (copy from [docs/WIDGETS.md](docs/WIDGETS.md))
- Make sure you're editing a page file, not an event file

**Events not appearing:**
- Verify events are in the `content/events/` folder
- Ensure events have valid `event-start` dates in the frontmatter

**Articles not appearing:**
- Verify content is in the correct folder (`content/announcements/`, `content/curiosities/`, `content/people/`, etc.)
- Check that the `category` attribute matches the folder name

## Working with Images

### Where Images Are Stored

All images are in the `content/images/` folder. You can use JPG, JPEG, or PNG files.

### Adding Images to Events

To add an image to an event, use this format in your event content:

```markdown
![]({static}/images/your-image-name.avif)
```

**Example:**
```markdown
---
title: Milonga Fuera del Nido
event-start: 2026-01-17 18:00:00
slug: milonga-fuera-del-nido
---

![]({static}/images/605635436_10241120531540882_4611790588703681234_n.avif)

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

<widget-calendar filter_by_type="milonga" days="365"></widget-calendar>
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
2. In your content, add: `![]({static}/images/your-filename.avif)`
3. Replace `your-filename.avif` with your actual filename

## Quick Reference

### Required Event Fields

- `title` - Event name
- `date` - Article date for Pelican (format: `YYYY-MM-DD HH:MM:SS`)
- `event-start` - When event starts (format: `YYYY-MM-DD HH:MM:SS`)
- `slug` - URL-friendly identifier (usually lowercase, hyphens)

### Recommended / Optional Event Fields

- `event-type` - `milonga`, `workshop`, `class`, or `praktika`
- `event-end` - When event ends (same format as `event-start`)
- `event-location` - Venue and address
- `event-organiser` - Organiser name or studio
- `instructor` - For classes/workshops: `"['Name', 'Name']"` or single name
- `recurrence` - For recurring events, e.g. `weekly sunday`
- `description` - Short summary for cards and SEO
- `preview_image` - e.g. `/images/event.avif`
- `event-rrule` - Recurrence rule (advanced)

### Widget Quick Syntax

**Events:**
```html
<widget-calendar filter_by_type="milonga" days="365"></widget-calendar>
<widget-calendar filter_by_type="milonga" days="7"></widget-calendar>
<widget-calendar filter_by_type="milonga" days="-30"></widget-calendar>
<widget-calendar filter_by_type="milonga" start="2026-06-01" end="2026-08-31"></widget-calendar>
```

**Articles (announcements, curiosities, people):**
```html
<widget-articles category="announcement" limit="3"></widget-articles>
<widget-articles category="curiosity" limit="all"></widget-articles>
<widget-articles category="people" metadata="description"></widget-articles>
<widget-articles category="people" slugs="filip-paldia lenka-platenikova" metadata="description"></widget-articles>
```


### Image Syntax

```markdown
![]({static}/images/filename.avif)
```

## Need Help?

If you're unsure about:
- Date formats - Use the examples in this guide
- Widget syntax - Copy the examples exactly
- File locations - Check the directory structure section
- Image usage - See the images section

Remember: When in doubt, look at existing files for examples of how things are done.
