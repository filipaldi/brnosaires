# LLM discoverability

A single custom plugin — `llm_ally.py` — produces LLM-friendly output
for Brnos Aires. It is a **dumb renderer**: it holds no site-specific
knowledge. All editorial decisions (what to surface, what to omit, how
to frame each audience) live in editor-edited files.

## Two responsibilities

### 1. Editor-curated `*.txt` files

For every `*.md` file in `content/llm/`, the plugin writes a matching
`.txt` to the site root **and** to `/.well-known/`. Filename mapping is
one-to-one:

| Source | Output (canonical) | Output (well-known alias) |
|---|---|---|
| `content/llm/llms.md` | `output/llms.txt` | `output/.well-known/llms.txt` |
| `content/llm/llms-full.md` | `output/llms-full.txt` | `output/.well-known/llms-full.txt` |
| `content/llm/<anything>.md` | `output/<anything>.txt` | `output/.well-known/<anything>.txt` |

Authoring a new audience is a `cp` plus an edit:

```bash
cp content/llm/llms.md content/llm/androids.md
# edit headings, widget filters, prose for the android audience
pelican content -s pelicanconf.py
# /androids.txt and /.well-known/androids.txt now exist
```

No code change. No registration step. The plugin walks the directory at
build time and emits whatever it finds.

`content/llm/` is **not registered with Pelican** — files there don't
become standalone HTML pages. The plugin reads them directly during the
`finalized` signal, strips the YAML frontmatter, expands every
`<widget-*>` tag via `widget_processor.render_widgets_in_text()`, and
writes the result.

### 2. Per-page Markdown mirrors

For every public article and page, `llm_ally` writes an `index.md` next
to the generated `index.html`:

```
output/tango-pizza-sesamo-2026-04-29/index.html   ← rendered HTML
output/tango-pizza-sesamo-2026-04-29/index.md     ← clean Markdown mirror
```

Each `.md` contains:

1. **Mintlify-style discovery marker** — `> For a complete page index,
   fetch {SITEURL}/llms.txt`. Tells an LLM that landed on a single page
   where to find the full corpus index.
2. **YAML frontmatter** — `title`, `date`, `url`, plus event-specific
   fields (`event-type`, `event-start`, `event-end`, `event-location`,
   `event-organiser`, `instructor`, `recurrence`, `series`) when present.
3. **Body** — the raw Markdown from `source_path`, with `<widget-*>`
   tags rendered as plain-text bullets via the same Jinja templates that
   power the HTML site (text-mode siblings: `widget_calendar.txt.j2`,
   `widget_articles.txt.j2`, etc.).

### Opting individual content out

Any article or page can opt out of mirror generation by adding one line
to its frontmatter:

```yaml
---
title: Smutné období drogových dealerů
slug: smutne-obdobi-drogovych-dealeru
date: 2026-04-12 18:00:00
llm_mirror: false
---
```

For Brnos Aires, every file under `content/curiosities/` and
`content/people/` carries `llm_mirror: false` (curiosities are
editorial color, people files are profile bios — neither is what users
search for). Other sites set the flag where it makes sense for them.

The flag has no central counterpart in code or config. Editors mark
opt-outs at the source.

## Widget text-mode templates

`theme/templates/components/widget_*.txt.j2` are the text-rendering
counterparts to the HTML templates. The widget processor exposes
`render_widgets_in_text(text, env, context)` which the plugin calls;
the helper resolves `widget_calendar.html` → `widget_calendar.txt.j2`
at render time.

A missing `.txt.j2` template renders the widget as the empty string —
deliberately, to avoid injecting `<div>` markup into Markdown.

### Recurring-class deduplication

In text mode, `<widget-calendar>` defaults to `dedupe-recurring="true"`.
Each recurring source appears once as
`- weekly Sunday 18:00 — Title — Location (URL)`, not N concrete-date
rows. Opt out per-tag with `dedupe-recurring="false"`. The dedup is
implemented in the text template, not in the plugin — the plugin is
unaware of "recurring" as a concept.

## Why a dumb renderer

Earlier versions of this work hardcoded the curated section list, the
recurring window in weeks, the announcement category name, the event
source path, and the curiosity/people exclusions in Python. Every
editorial decision required a code edit, and the plugin was bound to
Brnos Aires.

The dumb-renderer model puts every editorial decision into editor-owned
files: `content/llm/*.md` defines what `*.txt` outputs the site ships
and what's in each one; per-content `llm_mirror: false` defines what
gets mirrored. The plugin is now portable to any Pelican site that has
`widget_processor`.

## File reference

- `plugins/llm_ally.py` — the plugin (~165 LoC, no site-specific strings).
- `plugins/widget_processor.py` — exposes `render_widgets_in_text`.
- `theme/templates/components/widget_*.txt.j2` — text-mode widget templates.
- `content/llm/*.md` — editor-authored audience files.

The `marathon/llms.txt` static file under `content/extra/marathon/` is
kept as-is; it's a separate marathon sub-site fixture, not part of this
plugin's scope.
