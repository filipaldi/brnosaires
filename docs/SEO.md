# SEO + Social Cards

This document explains how the site exposes metadata to search engines and social-card consumers, and pins down decisions that aren't obvious from the templates alone.

> **Pro editory:** Tento dokument je technický (anglicky). Editorský průvodce metadaty s vysvětlením, jaká pole nastavovat ve frontmatteru a co každé dělá v náhledech na sociálních sítích, je v [EDITING.md](EDITING.md) (česky). This document is the architecture-level explanation underneath.

## Link strategy: relative URLs + `<base href>`

Every template emits **relative** URLs:

- `href="{{ x.slug }}/"` for navigation
- `src="{{ x.preview_image.lstrip('/') }}"` for images
- `href="{{ nav_page.url }}"` for the side menu

A single `<base href="{{ SITEURL }}/">` in [theme/templates/base.html](../theme/templates/base.html) resolves them all. **Do not remove or work around `<base href>`** — the side menu and every listing card depend on it. If you find yourself writing `{{ SITEURL }}/{{ x.url }}` in a template, you're fighting the existing strategy. Stop and reuse the relative form.

Trade-off: `<base href>` also rewrites `<a href="#section">` to `https://brnosaires.com/#section` instead of staying on the current page. We have no on-page fragment links today; if that ever changes, prefer JavaScript-driven scrolling or absolute `href="{current_url}#section"` rather than dropping `<base>`.

## Canonical URL

Every page emits `<link rel="canonical" href="{{ SITEURL }}/{{ url }}">`. This tells search engines the one true URL of the page and prevents duplicate-content penalties from `RELATIVE_URLS` artefacts (`/x/`, `/x/index.html`, etc.).

For **recurring events** (Milonga u Draka, Tango & Pizza, recurring lessons), the canonical URL of each instance points at the **hub page** in `pages/` rather than the instance itself. See "Recurring events: hub pages" below.

## Recurring events: hub pages

Some events recur but each occurrence is authored as its own dated file (e.g., `2026-04-18-milonga-u-draka.md`, `2026-05-16-milonga-u-draka.md`). Without intervention, search engines see N near-identical URLs competing for the same query and split the link equity. The `series:` convention solves this.

### How it works

1. **Author a hub page** in `content/pages/` with a stable slug, e.g. [content/pages/milonga-u-draka.md](../content/pages/milonga-u-draka.md). Set `series: <slug>` in the frontmatter to mark it as a hub. The body describes the recurring event in general (location, vibe, music style, organisers).

2. **Tag each instance** with the same `series: <slug>` field in its frontmatter. No body changes required.

3. **Templates do the rest:**
   - [theme/templates/base.html](../theme/templates/base.html) detects `series:` on the article and overrides `<link rel="canonical">` and `<meta property="og:url">` to point at the hub URL (`/<series>/`) instead of self. Same for the hub page itself, which trivially canonicals to itself.
   - [theme/templates/article.html](../theme/templates/article.html) renders a small "Součást pravidelné série: [Hub Title]" link below the event header so readers and crawlers can navigate instance → hub.
   - [theme/templates/page.html](../theme/templates/page.html) detects `series:` on a page and renders a "Nejbližší termíny" section listing all upcoming instances of the series (filtered by `event-start >= today`, sorted chronologically). Uses the existing `calendarium` Jinja filter to ensure event metadata is parsed consistently with the rest of the site.

### Adding a new series

1. Create `content/pages/<series-slug>.md` with `series: <series-slug>` in frontmatter and a descriptive body.
2. Add `series: <series-slug>` to each existing instance file in `content/events/`.
3. Future instances just need the same `series:` line and they auto-appear on the hub.

### What does NOT need a hub

- One-off events (a single milonga that won't repeat) — self-canonical is correct.
- Recurring classes/praktikas authored via the `recurrence:` field in [plugins/recurring_events.py](../plugins/recurring_events.py) — those are a single source file expanded into N occurrences sharing one URL, so they already have a single canonical surface.

## Open Graph + Twitter Card

`<head>` includes:

- Open Graph — `og:site_name / locale / title / description / type / url / image`. Used by Facebook, LinkedIn, Slack, Discord, WhatsApp, iMessage, Google for rendering link previews.
- Twitter Card — `twitter:card=summary_large_image` plus title/description/image. Twitter/X ignores OG alone and reads its own namespace. `summary_large_image` shows the preview image edge-to-edge above the headline.

### One image powers everything: `preview_image`

Articles and pages already declare `preview_image:` in frontmatter for in-page card rendering ([components/event_card.html](../theme/templates/components/event_card.html), [components/widget_articles.html](../theme/templates/components/widget_articles.html), [article.html](../theme/templates/article.html), [page.html](../theme/templates/page.html)). The same field powers `og:image` and `twitter:image` — there are deliberately **no separate `og_image` / `twitter_image` frontmatter fields**.

Reasons:

- One image to maintain per content item, not three.
- Guaranteed parity between in-site cards and external link previews.
- Zero authoring burden — every author already fills `preview_image`.

If a page lacks `preview_image`, no `og:image` / `twitter:image` is emitted (graceful degradation). Social previews still render with title + description, just without an image.

### Description fallback chain

`<meta description>`, `og:description`, `twitter:description` resolve in this order:

1. `article.description` / `page.description` (explicit frontmatter, when set)
2. `article.summary` (auto-generated by Pelican from the first ~50 words)
3. `SITEDESCRIPTION` (global fallback)

Truncated to 200 characters and stripped of HTML.

## llms.txt discoverability

`<head>` also includes:

```html
<link rel="alternate" type="text/plain" title="llms.txt" href=".../llms.txt">
<link rel="alternate" type="text/plain" title="llms-full.txt" href=".../llms-full.txt">
```

These point at the LLM-readable endpoints generated by `plugins/llms_index.py` (when that plugin lands). LLM crawlers and chatbots that follow the [llms.txt convention](https://llmstxt.org) discover the endpoints via these hints.

## What's NOT here yet

- JSON-LD structured data (Event schema for milongas) — planned.
- `sitemap.xml` — planned.
- Per-page Markdown mirrors + auto-generated `llms.txt` — planned.

See [ROADMAP.md](ROADMAP.md) for status.
