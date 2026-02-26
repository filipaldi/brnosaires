# Brnos Aires Web - Editor Guide

This guide is for content editors working with the Brnos Aires website. It covers how to create and edit events, use widgets, manage images, and organize content.

---

## Table of Contents

1. [Before You Start](#before-you-start)
2. [Key Terms Explained](#key-terms-explained)
3. [Working with Event Files](#working-with-event-files)
4. [Event Metadata - Dates and Times](#event-metadata---dates-and-times)
5. [Widget System](#widget-system)
6. [Working with Images](#working-with-images)
7. [Content Organization](#content-organization)
8. [Common Tasks](#common-tasks)
9. [Quick Reference](#quick-reference)
10. [Need Help?](#need-help)

---

## Before You Start

### How Editing Works

You edit the website by modifying text files stored in this repository. Each file represents a piece of content — an event, a page, or an announcement.

**When changes go live:** After you save (commit) your changes, the website rebuilds automatically at the next scheduled time — typically within 12 hours. If you need an update to appear sooner, ask a developer to trigger a manual rebuild.

**File format:** All content files are plain text files ending in `.md` (Markdown). You can open them in any text editor.

There are two ways to edit files:

---

#### Option A: Edit directly on GitHub (recommended for small changes)

No software installation required — you only need a web browser and a GitHub account.

1. Go to the repository on GitHub
2. Navigate to the file you want to edit (e.g., open `content/events/2026/02/` and click on a file)
3. Click the **pencil icon** (✏️ "Edit this file") in the top-right corner of the file view
4. Make your changes in the text editor that appears
5. Scroll down to the **"Commit changes"** section
6. In the first text box, write a short description of your change (e.g., `Add milonga January 2026`)
7. Click **"Commit changes"** — your change is saved; the website will update at the next scheduled rebuild

> **Tip:** GitHub editing is ideal for updating event details, fixing text, or adding a new event file. It does **not** allow uploading images — use GitHub Desktop for that.

---

#### Option B: Edit locally with GitHub Desktop (recommended for uploading images or making many changes at once)

GitHub Desktop is a free app that lets you work with files on your computer and sync changes to GitHub.

**One-time setup:**
1. Install [GitHub Desktop](https://desktop.github.com/) and sign in with your GitHub account
2. Clone the repository: **File → Clone Repository** → select the repo → click **Clone**
   - This downloads all the website files to a folder on your computer

**Editing files:**
1. Open the cloned folder on your computer and find the file you want to edit
2. Open it in any plain text editor (Notepad on Windows, TextEdit on Mac)
3. Make your changes and **save the file**

**Uploading images:**
1. Copy your image file into the `content/images/` subfolder within the cloned folder

**Saving and publishing your changes:**
1. Open GitHub Desktop — it shows all the files you have changed or added
2. In the **"Summary"** field (bottom-left), write a short description (e.g., `Add milonga February 2026 event`)
3. Click **"Commit to main"**
4. Click **"Push origin"** in the top bar — your changes are sent to GitHub and the website will update at the next scheduled rebuild

---

### What is Markdown?

Markdown is a simple way to format text using symbols. For example:
- `**bold**` becomes **bold**
- `# Heading` becomes a large heading
- `- item` becomes a bullet point

You don't need to know Markdown deeply — the boilerplate templates in this guide cover everything you need.

---

## Key Terms Explained

| Term | What it means |
|------|--------------|
| **Frontmatter** | The block at the top of every file, between the two `---` lines. It contains structured information like the event title, date, and location. |
| **Slug** | The URL-friendly version of the event name. It appears in the web address: `brnosaires.cz/events/milonga-fuera-del-nido`. Use only lowercase letters, numbers, and hyphens — no spaces or special characters. |
| **Markdown file (`.md`)** | A plain text file with simple formatting. The website turns it into a styled webpage. |
| **AVIF** | An image file format (like JPG or PNG, but more efficient). The website uses `.avif` images. |
| **Widget** | A special code snippet you paste into a page to automatically display a list of events or articles. |
| **SEO description** | A short summary (1–2 sentences) shown in search engine results and on social media previews. |

---

## Working with Event Files

### Where Event Files Are Located

All event files are stored in the `content/events/` folder. Each event has its own Markdown file (`.md` file).

### Creating a New Event File

1. Create a new file in the appropriate subfolder:
   - For a dated event: `content/events/YYYY/MM/` — e.g., `content/events/2026/03/` for March 2026
   - For a recurring class: `content/events/classes/`
2. Name the file using lowercase letters, hyphens, and numbers only — no spaces, no accented letters (e.g., `milonga-fuera-del-nido.md`)
3. The file name becomes part of the event's web address, so make it descriptive

**File naming examples:**

| Content type | Format | Example |
|---|---|---|
| One-off event | `short-description.md` | `milonga-fuera-del-nido.md` |
| Recurring class | `studio-level.md` | `stolarna-tango-i.md` |
| Announcement | `YYYY-MM-DD-description.md` | `2026-03-15-spring-announcement.md` |

**General rules:**
- Lowercase letters only
- Hyphens instead of spaces (`milonga-brno`, not `milonga brno`)
- No underscores, no accented characters (`á`, `č`, `š`, etc.)

### Basic Event File Structure

Every event file has two parts:

1. **Frontmatter** (at the top, between `---` lines) — Contains metadata about the event
2. **Content** (below the frontmatter) — The event description and details

### Ideal Event Metadata (Boilerplate for Editors)

Events are displayed with metadata on the site (type, date range, location, organiser, instructors). Fill these in the frontmatter so the event page and widgets show consistent information.

| Field | Required | Use |
|-------|----------|-----|
| `title` | Yes | Event name. |
| `slug` | Yes | URL slug (lowercase, hyphens). Often same as filename without `.md`. |
| `date` | Yes | Article date. Use the same value as `event-start` unless you're publishing the article on a different day. Format: `YYYY-MM-DD HH:MM:SS`. |
| `event-type` | Recommended | One of: `milonga`, `workshop`, `class`, `praktika`. Used for filtering in widgets. |
| `event-start` | Yes | Start date and time. Format: `YYYY-MM-DD HH:MM:SS`. |
| `event-end` | Recommended | End date and time. Same format as `event-start`. |
| `event-location` | Recommended | Venue name and address (e.g. `Taneční studio Stolárna, Olomoucká 14` or `Café Adrinela`). |
| `event-organiser` | Recommended | Who organises the event (e.g. `Taneční studio Stolárna`, `Lenka a Filip`). |
| `instructor` | For classes/workshops | Instructors. For one instructor: just write the name. For multiple: `"['Name One', 'Name Two']"` (see note below). |
| `recurrence` | For recurring events | e.g. `weekly sunday`, `weekly tuesday`. See recurrence section below. |
| `description` | Recommended | Short summary for cards and search results (1–2 sentences). |
| `preview_image` | Optional | Path to image, e.g. `/images/event.avif`. |
| `author` | Optional | Content author. |

> **Multiple instructors:** The unusual format `"['Name One', 'Name Two']"` (with quotes and square brackets) is required by the website system. Copy it exactly and just replace the names. For a single instructor, you can write the name directly: `instructor: Filip Paldia`.

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

---

## Event Metadata - Dates and Times

Event files use four types of date/time information:

### 1. `date` - Article Date (Required)

The website system requires this field for every article. For events, set it to the same value as `event-start`. Only use a different date if you're writing and publishing the article on a separate day from when the event happens.

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
- Always include both the date and the time
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

3. **Using `date` instead of `event-start`:** only `date: 2026-01-17 18:00:00` ❌
   - **Correct:** Include both `date` and `event-start` with the same value ✅

4. **Using `end_date` instead of `event-end`:** `end_date: 2026-01-17 22:30:00` ❌
   - **Correct:** `event-end: 2026-01-17 22:30:00` ✅

5. **Missing `date` field:** Events must have both `date` and `event-start` ❌
   - **Correct:** Include both `date` and `event-start` with the same value ✅

---

## Widget System

Widgets are special components that automatically display lists of events on your pages. You can add them anywhere in your Markdown content.

For full widget documentation — all attributes, examples, and technical details — see **[docs/WIDGETS.md](docs/WIDGETS.md)**.

### How Widgets Work

Widgets are embedded using custom HTML tags that you paste into your Markdown file. The website automatically replaces these tags with the actual event list.

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

### Using Widgets in Pages

You can add widgets anywhere in your page content. Here's a complete example:

```markdown
---
title: Tango milongy Brno
slug: tango-milongy-brno
---

Tangové tančírny neboli **milongy v Brně** - pravidelné i nepravidelné.

<widget-calendar filter_by_type="milonga" days="365"></widget-calendar>

## Upcoming Events

<widget-calendar filter_by_type="milonga" days="7"></widget-calendar>

## Announcements

<widget-articles category="announcement" limit="3"></widget-articles>
```

### Widget Best Practices

1. **Add headings before widgets** — Help readers understand what they're looking at
2. **Place widgets where they make sense** — Put event lists near relevant content
3. **Test after adding** — Make sure events are showing up correctly
4. **Widgets only show if content exists** — If no matching content is found, the widget won't appear
5. **Use sorting for better organisation** — Sort by oldest for historical content, newest for recent updates

### Troubleshooting Widgets

**Widget not showing:**
- Check that events exist with the matching `event-type` field (e.g., `event-type: milonga`)
- Verify the syntax is correct (copy from [docs/WIDGETS.md](docs/WIDGETS.md))
- Make sure you're editing a page file, not an event file

**Events not appearing:**
- Verify events are in the `content/events/` folder
- Check that each event file has the correct `event-type` field set (e.g., `event-type: milonga`)
- Ensure events have valid `event-start` dates in the frontmatter

**Articles not appearing:**
- Verify content is in the correct folder (`content/announcements/`, `content/curiosities/`, `content/people/`, etc.)
- Check that the `category` attribute matches the folder name
- Ensure content files have valid dates

---

## Working with Images

### Where Images Are Stored

All images are in the `content/images/` folder. The website uses `.avif` image files (a modern, efficient format). If you have a JPG or PNG, ask a developer to convert it before uploading.

### Adding Images to Events

To add an image to an event, use this format in your event content:

```markdown
![Description of the image]({static}/images/your-image-name.avif)
```

> **Note:** `{static}` is a special keyword used by the website system to find the images folder. Write it exactly as shown — do not change it. Replace only `your-image-name.avif` with your actual filename.

> **Tip:** Always add a short description inside the `[ ]` brackets (e.g., `![Poster for Milonga Fuera del Nido]`). This helps visually impaired visitors using screen readers, and improves search engine visibility.

**Example:**
```markdown
---
title: Milonga Fuera del Nido
event-start: 2026-01-17 18:00:00
slug: milonga-fuera-del-nido
---

![Poster for Milonga Fuera del Nido]({static}/images/milonga-fuera-del-nido.avif)

Your event description here...
```

### Image Best Practices

1. **Use descriptive filenames** — Makes it easier to find images later (e.g., `milonga-january-2026.avif` instead of `IMG_4821.avif`)
2. **Use `.avif` format** — Ask a developer to convert images if needed
3. **Keep filenames simple** — Use lowercase letters, numbers, and hyphens only; no spaces or special characters
4. **Always add a description** — Fill in the `[ ]` brackets with a short description of the image

### Finding Images

To see what images are available, look in the `content/images/` folder. The filename you see there is what you use in your Markdown (without the folder path).

---

## Content Organization

### Directory Structure

The website content is organized into folders:

- **`content/events/`** — All event files, organized by year and month (e.g., `content/events/2026/03/`)
- **`content/events/classes/`** — Recurring class files
- **`content/pages/`** — Regular pages (about us, calendar pages, etc.)
- **`content/announcements/`** — Announcement posts
- **`content/images/`** — All images used on the website

### Content Types

**Events** (`content/events/YYYY/MM/`)
- Individual events with dates and times
- Must have `event-start` field
- Appear in calendars and event lists
- File naming: `short-description.md` (e.g., `milonga-fuera-del-nido.md`)

**Pages** (`content/pages/`)
- Regular website pages
- Can include widgets
- Examples: calendar pages, information pages

**Boilerplate – page:**

```markdown
---
title: Page title
slug: page-slug
date: 2026-01-17 18:00:00
description: Short description shown in search results.
author: Your name
preview_image: /images/your-image.avif
---

Body text here. Add widgets below to automatically display content.
```

**Announcements** (`content/announcements/`)
- News and updates
- Don't need event dates
- File naming: `YYYY-MM-DD-description.md` (e.g., `2026-03-15-spring-announcement.md`)

**Boilerplate – announcement:**

```markdown
---
title: Your announcement title
date: 2026-03-15 09:00:00
category: announcement
description: Short summary for cards and search results.
preview_image: /images/announcements/your-image.avif
author: Your name
---

Body text here.
```

**Classes** (`content/events/classes/`)
- Recurring class files with `recurrence` field
- File naming: `studio-level.md` (e.g., `stolarna-tango-i.md`)

---

## Common Tasks

### Adding a New Event

1. Create a new file in the correct subfolder (e.g., `content/events/2026/03/` for a March 2026 event)
2. Name it descriptively using lowercase and hyphens (e.g., `milonga-fuera-del-nido.md`)
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

**Example — changing start time from 18:00 to 19:00:**
```markdown
event-start: 2026-01-17 19:00:00
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

1. Place your `.avif` image file in `content/images/` folder
2. In your content, add: `![Short description]({static}/images/your-filename.avif)`
3. Replace `your-filename.avif` with your actual filename and add a description in the `[ ]` brackets

---

## Quick Reference

### Required Event Fields

- `title` — Event name
- `date` — Article date (format: `YYYY-MM-DD HH:MM:SS`, same value as `event-start`)
- `event-start` — When event starts (format: `YYYY-MM-DD HH:MM:SS`)
- `slug` — URL-friendly identifier (lowercase letters, hyphens, no spaces)

### Recommended / Optional Event Fields

- `event-type` — `milonga`, `workshop`, `class`, or `praktika`
- `event-end` — When event ends (same format as `event-start`)
- `event-location` — Venue and address
- `event-organiser` — Organiser name or studio
- `instructor` — For classes/workshops: `"['Name', 'Name']"` for multiple, or just the name for one
- `recurrence` — For recurring events, e.g. `weekly sunday`
- `description` — Short summary for cards and search results
- `preview_image` — e.g. `/images/event.avif`

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
![Short description of the image]({static}/images/filename.avif)
```

---

## Need Help?

If you're unsure about:
- **Date formats** — Use the examples in this guide
- **Widget syntax** — Copy the examples exactly
- **File locations** — Check the directory structure section
- **Image usage** — See the images section

Remember: When in doubt, look at existing files for examples of how things are done.
