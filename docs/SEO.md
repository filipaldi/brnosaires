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

> **Known limitation (fallback `/en/` pages):** an `/en/<event-instance>/` fallback page (one with no real English translation) computes its canonical against the *Czech* hub (`/<hub-slug>/`), not the English hub. That's defensible — the fallback body *is* the Czech page — but if you ever translate the hub, also translate the instances, or accept the cross-language canonical.

## Multilingual: the `/en/` mirror

The site has an English version under the `/en/` prefix. Czech (the default language, `DEFAULT_LANG = "cs"`) keeps its original root-level URLs untouched — **zero risk to existing SEO** — and non-default-language content routes under `/en/` via `PAGE_LANG_URL` / `PAGE_LANG_SAVE_AS` / `ARTICLE_LANG_*` / `CATEGORY_LANG_*` in [pelicanconf.py](../pelicanconf.py).

**How a page gets an English version:** add a sibling file with `Lang: en` and the *same* `Slug` (Pelican links translations by slug, via `ARTICLE_TRANSLATION_ID` / `PAGE_TRANSLATION_ID`, both `"slug"`). E.g. `o-nas.md` (`Lang: cs`, `Slug: o-nas`) + `o-nas.en.md` (`Lang: en`, `Slug: o-nas`) → the latter renders at `/en/o-nas/`.

**The Czech fallback** is the one custom piece — core Pelican gives you `/en/<slug>/` only when a real `.en.md` exists. [plugins/i18n_fallback.py](../plugins/i18n_fallback.py) fills the gap: in `page_generator_finalized` / `article_generator_finalized` (after `process_translations`, before output is written) it synthesizes an `en` translation object for every Czech page lacking one — same slug, `Lang: en`, reusing the *already-rendered* `_content` (hence the plugin is registered **after** `widget_processor` in `PLUGINS`, so widgets in the body are already expanded). The clone is wired into `.translations` both ways and appended to `generator.translations` (the writer iterates that). Result: `/en/<slug>/` mirrors the whole site from launch, with English chrome (nav, dates, meta, hreflang, `<html lang="en">`) wrapping a Czech body until a real translation lands. Marathon pages are skipped — that sub-site is English-first with no Czech mirror, so it must not get a `/en/marathon-…` duplicate.

**`page_lang`** is computed once at the top of [base.html](../theme/templates/base.html) (before `<html>`): marathon section → `en`, otherwise the content object's `Lang:` (default `cs`). It drives `<html lang>`, `<meta og:locale>` (`cs_CZ` / `en_GB`), the meta description (`SITEDESCRIPTION` / `SITEDESCRIPTION_EN`), `hreflang`, the nav aria-labels, and the language-switcher guard. UI chrome strings come from per-language tables in [theme/i18n/](../theme/i18n/) via the `t(key, page_lang)` Jinja filter; dates from `DATE_FORMATS = {"cs": "%d. %m. %Y", "en": "%-d %B %Y"}`.

**`hreflang`:** every page (with `SITEURL` set) emits `<link rel="alternate" hreflang="…">` for itself plus each of its `.translations`, plus `hreflang="x-default"` pointing at the Czech (default-language) version. Marathon pages have no translation → no `hreflang` block, which is correct (single-language sub-site). The sitemap includes the `/en/` pages automatically.

**Language switcher** ([theme/templates/components/lang_switcher.html](../theme/templates/components/lang_switcher.html)): `CS · EN` in the header; the current language is inert, the other links to this page's translation counterpart (or `/` ↔ `/en/` for the homepage). It's omitted entirely on marathon pages. A small progressive-enhancement script in `base.html` remembers the chosen language in `localStorage` and, on the bare root path, redirects to `/en/` if `en` was previously chosen — the links work fine without JS.

**Footer note:** the footer is currently Czech on `/en/` pages too. Its English variant is folded into the separate "rework the footer" item in [ROADMAP.md](ROADMAP.md), not done here.

Editor-facing version of all this (the `.en.md` naming, what to write where): [EDITING.md → Jazykové verze](EDITING.md).

## Recurring events: hub pages

Some events recur but each occurrence is authored as its own dated file (e.g., `2026-04-18-milonga-u-draka.md`, `2026-05-16-milonga-u-draka.md`). Without intervention, search engines see N near-identical URLs competing for the same query and split the link equity. The `series:` convention solves this.

### How it works

1. **Author a hub page** in `content/pages/series/` with a stable slug, e.g. [content/pages/series/milonga-u-draka.md](../content/pages/series/milonga-u-draka.md). Set `series: <slug>` in the frontmatter to mark it as a hub. The body describes the recurring event in general (location, vibe, music style, organisers). (The `series/` subdir is organisational only — Pelican routes by `Slug:`, not path; one-off / multi-day event hubs like Tango Weekend live in `content/pages/events/`.)

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

## Evergreen month pages (`/milongy-brno-<měsíc>/`)

Twelve hand-authored pages, one per Czech month name (`/milongy-brno-leden/` … `/milongy-brno-prosinec/`), in [content/pages/events/](../content/pages/events/). They target the query pattern *"milonga Brno [měsíc]"* / *"milonga Brno [měsíc] [rok]"* — which nothing else on the site is titled or structured for. Each `.md` is a thin shell: an evergreen intro paragraph (year-free, with a sentence of per-month flavour), a `<widget-calendar month="<N>" filter_by_type="milonga praktika neolonga">`, the `.ics` subscribe widget — **and deliberately no `#` H1 and no year anywhere in the file**. They are **year-agnostic** — the URL is reused every year; only the displayed year changes, and it's the *template* that prints it (see below). Entry points: a `<widget-calendar>`-style "Milongy po měsících:" link strip on [milongy.md](../content/pages/milongy.md) and [kalendar.md](../content/pages/kalendar.md) (CS + `.en.md`), plus the inter-page prev/next ring + all-months strip the template emits.

### The moving parts

- **`month: <N>` frontmatter** on the page (a number 1–12) is the flag that switches on the month-page branch in [theme/templates/page.html](../theme/templates/page.html). It also tells the template which month's events to list in the JSON-LD.
- **`tango_year_for_month(month)`** — a Jinja filter ([pelicanconf.py](../pelicanconf.py)). `page.html` uses it (together with `month_name(N, lang, 'locative')`) to build the `<title>` *and* the `<h1>` for a month page — `Milongy v Brně v <6. pádu> <rok>` (CS) / `Milongas in Brno in <Month> <year>` (EN) — so the year is computed at build time: the current year, or next year if that month has already passed this year. So in November, `/milongy-brno-leden/`'s title reads "…leden 2027". **No annual edit chore, and nothing in the `.md` to update.** (The lang for that title is read from `page.lang`, not the usual `page_lang` — `page_lang` is set by `base.html` *after* the child template's top-level statements run, so it isn't visible up there yet.) Companion helpers, also in `pelicanconf.py` + registered in `JINJA_FILTERS`: `month_name(n, lang, form)` — display name, `form="locative"` gives the Czech "v lednu"; `month_page_slug(n)` / `month_page_url(n, lang)`; `month_wrap(n, ±1)` — month arithmetic that wraps 12↔1. The calendarium plugin keeps its own tiny `year_for_month` mirror in [dates.py](../plugins/calendarium/dates.py) — a plugin must not import the site config.
- **`<widget-calendar month="<N>">`** — the `month=` param (see [WIDGETS.md](WIDGETS.md)) restricts the widget to exactly that calendar month in the `tango_year_for_month`-resolved year, overriding `days`/`start`/`end`.
- **`page.html` month-page branch** (gated on `month:`):
  - emits a JSON-LD **`ItemList`** of that month's milongas/praktikas/neolongas (`itemListElement` → `ListItem` → `Event` with `startDate`/`endDate`/`location`/`url`) — built from the *same* `calendarium(month=…)` query the widget uses, so it can't drift from what's rendered;
  - if the month currently has **no events**, emits `<meta name="robots" content="noindex,follow">` (via the `head` block) plus an empty-state line — keeps the thin page crawlable but out of the index until an event lands; the `noindex` flips off automatically on the next build after a matching event is added;
  - renders **prev/next-month ring links** (`← květen` / `červenec →`) and an **all-months strip** — crawl paths between the 12, lang-aware (`/milongy-brno-<m>/` in CS, `/en/milongy-brno-<m>/` in EN).
- **English twins** are `.en.md` siblings with the *same* slug + `Lang: en` (like every other `.en.md`) → routed to `/en/milongy-brno-<m>/`. Only the copy and the displayed month/year wording differ; the `month=` param and the year filter are language-neutral.
- **Canonical/sitemap**: each month page is self-canonical and picked up by the sitemap plugin automatically; the `noindex` (empty months only) keeps the thin ones out of the index without removing them.

Editor-facing version (how to author/edit a month page, what to leave alone): [EDITING.md → Měsíční stránky milong](EDITING.md).

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

`<meta name="description">`, `og:description`, `twitter:description` all resolve in this order:

1. `article.description` / `page.description` (explicit frontmatter, when set)
2. `article.summary` (auto-generated by Pelican from the first ~50 words)
3. `_site_desc` — `SITEDESCRIPTION` (cs) / `SITEDESCRIPTION_EN` (en)

Truncated to 200 characters and stripped of HTML — that's the `_desc` variable in [base.html](../theme/templates/base.html). All three tags use it. (Until T1, `<meta name="description">` was hardcoded to the sitewide `{{ SITENAME }} - {{ SITEDESCRIPTION }}` and only `og:`/`twitter:` honoured `_desc` — so every page shipped the same search snippet. Fixed: the `<meta description>` tag now sits below the `_desc` assignment and uses it.)

## llms.txt discoverability

`<head>` also includes:

```html
<link rel="alternate" type="text/plain" title="llms.txt" href=".../llms.txt">
<link rel="alternate" type="text/plain" title="llms-full.txt" href=".../llms-full.txt">
```

These point at the LLM-readable endpoints generated by [plugins/llms_index.py](../plugins/llms_index.py). LLM crawlers and chatbots that follow the [llms.txt convention](https://llmstxt.org) discover the endpoints via these hints. See [LLMS.md](LLMS.md) for the plugin's structure and what each section contains.

## Structured data (JSON-LD)

Schema.org JSON-LD is emitted server-side (it's a static site — there's no JS to inject it). Where each block lives:

| `@type` | Where | Notes |
|---|---|---|
| `Event` | [article.html](../theme/templates/article.html), gated on `event-start` | `name`, `description`, `startDate`/`endDate` (ISO8601 via the `event_iso8601` filter), `eventStatus`, `eventAttendanceMode` (offline), `location` (see `event_address` below), `organizer`, `performer`, `image`, `url`, `@id` (`<canonical>#event`). For a `series:` instance: `superEvent` → `EventSeries` pointing at the hub, and `url`/`@id` resolve to the hub (same rule as the `<link rel=canonical>`). `offers` (`@type` Offer, `price`/`priceCurrency` CZK/`availability`) is **gated on a `entry:` frontmatter field** — no event has one yet (it's a ROADMAP item), so the block is dormant; `isAccessibleForFree: true` when `entry` is "zdarma"/"free"/"0"/"dobrovolné". |
| `EventSeries` | [page.html](../theme/templates/page.html), on a `series:` hub page | `name`, `description`, `url`, `image`, `location` (Brno), and `subEvent` — each upcoming instance as a minimal `Event`. Makes the hub a single structured surface for "all upcoming \<series\> dates". |
| `ItemList` | [page.html](../theme/templates/page.html), on `/tango-kalendar-brno/` (matched by `page.slug`) and on every month page (`month:` flag) | `itemListElement` → `ListItem` → `Event`. The kalendar list is the next ≤50 upcoming events; the month-page list is that month's milongas/praktikas/neolongas. Both built from the same `calendarium(...)` query the visible widget uses, so the data can't drift from what's rendered. |
| `FAQPage` | [page.html](../theme/templates/page.html), on `/tango-pro-zacatecniky-brno/` (the [E2 glossary page](EDITING.md)) | `mainEntity` → `Question`/`acceptedAnswer`, parsed from the page's `**Question?**` + answer-paragraph Markdown by the `faq_pairs` Jinja filter (only `<p><strong>…?</strong> …</p>` blocks whose bold text ends with `?` — ordinary bold body text is ignored). Add/edit FAQs by editing that page's "Časté otázky" section; nothing else needed. |
| `Organization` | [components/footer.html](../theme/templates/components/footer.html), once per page (the footer is on every page) | `@id` `<siteurl>/#organization`, `name`, `description` (per language), `areaServed` → `City` "Brno". The baseline entity signal; no `sameAs`/`email`/`logo` (none exist for the site — don't invent). |

The `event_address(loc)` filter ([pelicanconf.py](../pelicanconf.py)) turns a canonical `"Venue, Street, Brno-District"` event-location string into a `Place` (`name`) wrapping a `PostalAddress` (`streetAddress`/`addressLocality`/`addressCountry: "CZ"`), degrading safely: `"Venue, Brno"` → `Place` + `PostalAddress` with just `addressLocality`; bare `"Brno"` / `"Brno-District"` → `PostalAddress` locality only, no `name`; bare venue name (no comma) → `Place` `name` only, no address; empty → `{}` (template falls back to the raw string). It **never emits a half-built `PostalAddress`** — every level degrades to the next. This depends on `event-location` being in the canonical 3-/2-part form (the [E3 hygiene pass](EDITING.md) normalised it). `"Brno"` in `addressLocality` is the literal city signal for `milonga Brno`.

A small "Poprvé na milonze? [Mrkni, jak na to.](…)" line under the event header on `milonga`/`praktika`/`neolonga` event pages links the beginner page (strings `first_milonga_prompt` / `first_milonga_link` in [theme/i18n/](../theme/i18n/)) — site-wide internal links to the glossary page.

## Related shipped pieces

- **`sitemap.xml`** generated by the `pelican.plugins.sitemap` community plugin; configuration lives in `SITEMAP` in [pelicanconf.py](../pelicanconf.py). Advertised in [content/extra/robots.txt](../content/extra/robots.txt).
- **Per-page Markdown mirrors** generated by [plugins/md_mirror.py](../plugins/md_mirror.py). Documented in [LLMS.md](LLMS.md).
