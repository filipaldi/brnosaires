# Brnos Aires — Agent Instructions

> Shared instructions for any AI coding agent (Claude Code, Codex, Cursor, Gemini, etc.).
> Claude Code reads its own copy at `.claude/CLAUDE.md`; Cursor reads `.claude/rules/*.md`.
> This file is the merged, tool-agnostic source. Keep the three in sync when editing.

## Environment

- Virtualenv at `venv/` — activate before running anything
- Keep `requirements.txt` up to date
- Pelican is installed in the `venv/` environment
- Deployment: GitHub Pages via GitHub Actions, see `.github/workflows/deploy.yml`

## Commands

Rules: no `--autoreload`, port 41234 only, rebuild manually after each edit.

Each step below is one shell command. Run the rebuild in shell A, leave the server in shell B running, re-run rebuild in A after every edit.

### Run dev server (main checkout)

Shell A - activate venv, then rebuild after each edit:

```bash
source venv/bin/activate
```
```bash
pelican content -s pelicanconf.py
```

Shell B - serve `output/` (start once, leave running):

```bash
source venv/bin/activate
```
```bash
pelican --listen --port 41234
```

### Run dev server (git worktree)

Shell A - rebuild after each edit:

```bash
../brnos-aires-web/venv/bin/pelican content -s pelicanconf.py
```

Shell B - serve `output/` (start once, leave running):

```bash
../brnos-aires-web/venv/bin/pelican --listen --port 41234
```

### Phone preview (same Wi-Fi)

Replace last line with: `pelican --listen --bind 0.0.0.0 --port 41234`. Get the Mac's LAN IP via `ipconfig getifaddr en0`, open `http://<that-ip>:41234/` on the phone.

### Other

```bash
pelican content -s publishconf.py                                # prod build (SITEURL set)
pelican content -s pelicanconf.py --delete-output-directory      # wipe output/ first (hook-blocked for agents — a human runs this)
```

See [docs/local-testing.md](docs/local-testing.md) for port-41234 rationale, firewall/`cloudflared`/`ngrok` fallbacks, and Safari Web Inspector notes.

### Tests

```bash
python -m unittest discover -s tests -t .       # what CI runs
```

The build has one source of "now", `NOW` in `pelicanconf.py`, and it decides
which events count as upcoming. `BRNOSAIRES_NOW=YYYY-MM-DD` pins it:

```bash
BRNOSAIRES_NOW="2026-08-01" pelican content -s pelicanconf.py
```

The suite always pins it (`BUILD_CLOCK` in `tests/__init__.py`) so a build-based
test depends on the repo, not on today's date. **A test that asserts something
is "upcoming" must run on the pinned clock** — on the real one it goes red the
day its fixture's last date passes, with nothing actually broken. Details in
[docs/local-testing.md](docs/local-testing.md#hodiny-buildu--brnosaires_now).

- `pelicanconf.py` — dev (`RELATIVE_URLS = True`)
- `publishconf.py` — prod (`SITEURL = "https://brnosaires.com"`)
- Deployment: GitHub Actions `.github/workflows/deploy.yml` → GitHub Pages

## Working on two branches in parallel (git worktrees)

Two agents (or two human sessions) can work on two branches at the same time using `git worktree` — one repo, multiple checked-out branches in separate folders, sharing the same `.git`.

```bash
git worktree add ../brnos-aires-web-<branch> <branch>   # create
git worktree list                                       # see what's checked out where
git worktree remove ../brnos-aires-web-<branch>         # clean up when done
```

Conventions for this project:

- **Share one `venv/` via the symlink shown in Commands.** Caveat: if one branch bumps `requirements.txt`, both worktrees see the new versions — re-run `pip install -r requirements.txt` in the main checkout deliberately, never automatically.
- **One dev server at a time on port 41234.** Run `pelican --listen --port 41234` in whichever worktree you're previewing. The other worktree can still rebuild with `pelican content` freely — only the live server binds the port. Switch the browser tab to match whichever build you want to see. Never spin up a second server on a different port to dodge this.
- **No autoreload, ever — in any worktree.** Same rule as the single-checkout workflow: rebuild manually with `pelican content` on demand, hard-reload the browser. Auto-rebuild causes surprise breakages; on-demand only.
- Git refuses to check out the same branch in two worktrees — that's a built-in safety, not a bug.
- When testing always open new tab and keep it open for user review.

## Project Structure

```
content/events/YYYY/MM/   announcements/   curiosities/   people/   images/
content/pages/            landing pages + o-nas, skoly-a-lektorstvi, the curiosity/announcement hubs
content/pages/series/     hub pages for recurring series (series: <slug>) — milonga-u-draka, tango-pizza
content/pages/events/     hub pages for one-off / multi-day events — tango-vikend, tango-leto
content/pages/marathon/   the marathon sub-site (section: marathon, translate: false)
plugins/   theme/   docs/
```

The `pages/` subdirs are organisational only — Pelican routes pages by `Slug:` (or filename, `SLUGIFY_SOURCE = "basename"`), **not by path**, so moving a page between subdirs never changes its URL.

## Plugins

All in `plugins/`, registered in `pelicanconf.py`:
- `calendarium/` — event filtering, grouping, `.ics` feed generation
- `recurring_events.py` — expands `recurrence: weekly sunday` metadata into multiple instances
- `article_filter.py` — powers `<widget-articles>`
- `widget_processor.py` — renders `<widget-*>` tags in Markdown via Jinja (processes both `generator.pages`/`articles` and `generator.translations`)
- `gallery_widget.py` — scans image folders for alt text
- `nav_from_docs.py` — builds nav from `content/navigation/`
- `i18n_fallback.py` — see "Internationalization" below

## Internationalization (`/en/`)

The site has an English mirror under `/en/`. Lightweight engine — no `i18n_subsites`, no `gettext`:
- A page/article gets a Czech file plus an optional English sibling `foo.en.md` with **the same `Slug`** and `Lang: en`; Pelican links them as translations and the `*_LANG_URL`/`*_LANG_SAVE_AS` settings route the English one to `en/{slug}/`. Czech (default lang) URLs are unchanged. (`index.en.md` is special: `Slug: index` because `SLUGIFY_SOURCE = "basename"`, plus `save_as: en/index.html` / `url: en/`.)
- `plugins/i18n_fallback.py` synthesizes an English clone (Czech body, English chrome) for every default-lang page/article that has no `.en.md` yet — so `/en/` is a full navigable mirror from day one.
- Per-language UI strings live in `theme/i18n/{cs,en}.py`, exposed as the `STRINGS` Jinja global + a `t(key, lang)` filter; `base.html` computes `page_lang` once and drives `<html lang>`, `og:locale`, meta-desc, `hreflang`, the bottom-of-rail language switcher (`components/lang_switcher.html`), and lang-aware dates (`DATE_FORMATS`).
- **Monolingual content declares `translate: false`** in front-matter (the marathon folders get it in bulk via `EXTRA_PATH_METADATA`): no `/en/` clone, no switcher, `page_lang` forced to `en`. Marathon is English-first with no Czech mirror.
- Editor workflow: [docs/ANGLICKA-VERZIA.md](docs/ANGLICKA-VERZIA.md). Architecture / SEO: [docs/SEO.md](docs/SEO.md) → "Multilingual: the /en/ mirror".

## Content Format

Markdown with Pelican metadata headers (no `---` fencing). Key event fields:
`Title`, `Slug`, `Date`, `Event-type` (milonga|workshop|class|praktika), `Event-start`, `Event-end`, `Event-location`, `Recurrence`, `Series` (optional, groups instances under a hub page), `Preview-image`, `Description`. For an English version of a page, see "Internationalization" above.

Editor-facing field reference: [docs/EDITING.md](docs/EDITING.md). Architecture / SEO mechanics: [docs/SEO.md](docs/SEO.md).

## Widget System

See `docs/WIDGETS.md`. Widgets are `<widget-*>` tags in Markdown processed by `widget_processor.py`: `<widget-calendar>`, `<widget-calendar-link>`, `<widget-articles>`.

## CSS / Styles

NEVER CREATE NEW CSS STYLES BEFORE TRYING THE EXISTING STYLES.
- CSS styles are stored in the `theme/static/css/` folder.
- ALWAYS start by checking `variables.css` for all the properties, then look for existing styles in `layout.css`, `spacing.css`, `aesthetic.css`, `typography.css`.
- No raw pixels: sizes come from `--size`/`--const` tokens, never raw `px`.

### When a new utility is needed
- ALWAYS discuss what kind of utility is needed and how it fits into the current utility system.
- ALWAYS let the user confirm that a new utility is going to be defined.

### When a new component is needed
Component styles are an abstraction and a shorthand for the underlying utility classes. See `components.css` for existing components.
DO NOT define component styles when fewer than 3 utility classes are used in the style.

## Voice & Tone

Write like a Buenos Aires local with attitude—cheeky, concise, and to the point.

**Key Elements:**
- **Tango Flirtation**: A raised eyebrow, a knowing glance. Playful but never pushy.
- **Sardonic Edge**: Dry humor, slight irreverence. Eye-roll at pretension, but affectionate.
- **Warm Welcome**: Despite the sass, genuinely inviting. Like a friend who teases because they care.

**In Practice:**
- Cut the fluff. No one has time for that.
- A wink in the words, not a wink emoji.
- Confident, not cocky. Charming, not sleazy.
- Make them smile while getting straight to business.

**Language & Grammar:**
- Use British English (organise, colour, favour, programme, etc.)
- **Avoid em-dashes (—).** Maximum 1 per page. Use commas, full stops, or split into sentences instead.
