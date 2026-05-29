---
name: ux-visual-once-over
description: Click-through UX visual once-over of the Brnos Aires site. First prints the full UX scenario it will run (every page it will visit + the action on each), then walks the homepage → calendar → event → lectures → curiosities → announcements path, hops into the English (/en/) version via the language-switcher chip and back, then enters the Marathon sub-site via the footer link and walks its separate nav, by clicking real links (never goto). Takes a screenshot of every page for visual review, and checks console + network on each. Use before reporting frontend or content work as complete. Accepts an environment argument — `local` (default) or `live`.
---

# UX visual once-over — Brnos Aires

A tester-agent walkthrough. The agent walks the site like a real human user: clicks links, looks at the page, then clicks the next link. The point is to catch broken links, missing widgets, and visual regressions that DOM-only assertions miss.

## Hard constraints (project-specific)

The generic constraints — print the scenario before walking, one `browser_navigate` per run, click-don't-goto, screenshot every page, backtrack via `browser_navigate_back`, i18n/a11y micro-checks, the screenshot path rule, browser cleanup, the two-part report — live in the agent file at `~/.claude/agents/ux-visual-once-over.md`. This SKILL.md only carries Brnos-Aires facts.

**Project-specific gate:** never run against `live` before the deploy containing the change has succeeded. Run `gh run list --workflow=deploy.yml --limit 1 --json status,conclusion,headSha` and confirm `conclusion=success` and `headSha` matches the commit being verified. If it doesn't match, refuse and tell the user to either push first or run `local` instead.

## Environments

| Argument | Base URL | When to use |
|---|---|---|
| `local` *(default)* | `http://localhost:41234` | In-flight dev work, before commit. If `:41234` isn't already serving: build once with `pelican content -s pelicanconf.py`, then start the plain server `pelican --listen --port 41234` in the background. **Never `--autoreload`, never any other port** (project rule). |
| `live` | `https://brnosaires.com` | After a successful GitHub Pages deploy for the commit being verified. |

No staging environment exists for this project — GitHub Pages serves prod off `gh-pages`. Don't invent one.

## Step 0 — Resolve `BASE_URL`

- **`local`**: check `curl -sf http://localhost:41234/ -o /dev/null` (or equivalent). If it fails: activate `venv/`, build once with `pelican content -s pelicanconf.py`, then start `pelican --listen --port 41234` with `run_in_background: true` (the plain static server — **no `--autoreload`**, **no other port** — rebuilds are manual). Wait until the server responds, then proceed. If the change under review was just committed, build the *current* working tree first so the server reflects it.
- **`live`**: run `gh run list --workflow=deploy.yml --limit 1 --json status,conclusion,headSha`, confirm `conclusion=success` and `headSha == git rev-parse HEAD`. If not, stop and report.

## Default scenario skeleton

The agent file already mandates printing the scenario before walking; this skeleton is the starting point — adapt per environment + change under review, and append any pages the parent's `context` flagged.

```
1.  /                              — navigate (only navigate of the run)         — screenshot; console; nav links present
2.  /tango-kalendar-brno/          — click nav → Kalendář                          — <widget-calendar> rendered to cards; no raw <widget-*>; ≥1 card
3.  /{event-slug}/                 — click first event card                        — title/date/location visible; console clean
4.  /tango-lekce-brno/             — back; click nav → Lekce                        — lecture listing/widget rendered
5.  /{lecture-slug}/               — click first lecture link                       — body + recurrence visible
6.  /tango-pikosky/                — back; click nav → Pikošky                      — <widget-articles category=curiosity> rendered
7.  /{curiosity-slug}/             — click first curiosity                          — article body rendered
8.  /lenka-pise-oznamy/            — back; click nav → Oznámení                     — <widget-articles category=announcement> rendered
9.  /{announcement-slug}/          — click first announcement                       — article body rendered
9a. /en/...                        — back to a main page; click the English chip   — <html lang=en>; English nav labels; chip now says Čeština
9b. /en/tango-kalendar-brno/       — English nav → Calendar                         — calendar + subscribe block rendered; no raw <widget-*>
9c. /en/o-nas/                     — English nav → About us                         — English body; people cards; no raw <widget-*>
9d. /o-nas/                        — click the Čeština chip                         — <html lang=cs>; Czech nav; chip says English
9e. /en/                           — back to /; click English                       — English homepage body + all widget blocks rendered
10. /marathon/                     — back; scroll to footer; click Tango Marathon   — separate Marathon nav; data-section=marathon; main nav absent
11. /marathon-djs-team/            — Marathon nav → DJs                             — DJ profiles/photos; image alt text
12. /marathon-venue/               — Marathon nav → Venue                           — venue info / map renders
13. /marathon-gallery/             — Marathon nav → Gallery                         — gallery widget → images; thumbnails load
14. /marathon-schedule/            — Marathon nav → Schedule                        — schedule table/list legible
15. /marathon-getting-to-brno/     — Marathon nav → Travel                          — travel info renders
16. /marathon-stay-in-brno/        — Marathon nav → City                            — accommodation/city info renders
17. /marathon/                     — Marathon nav → Home                            — in-section back-nav works
18. <new feature / changed pages>  — click through end-to-end                       — exercise whatever this PR added/changed
+   screenshot + console + network checked on EVERY page above.
```

(`{...-slug}` items resolve at runtime from whatever the listing shows first — fine to write them as placeholders in the printed scenario. Re-read `content/navigation/marathon.md` if the marathon walk looks stale, and adjust the printed scenario to match.)

## Step 1 — Open the homepage *(only `browser_navigate` call in the run)*

`browser_navigate` → `${BASE_URL}/`

Checks: take screenshot; `browser_console_messages` clean; nav links visible in the snapshot.

## Steps 2–9 — Click through the site

Use `browser_snapshot` to find the next link by accessible name (Czech labels — match by text content), then `browser_click` it.

| # | Click target | Lands on | What to verify |
|---|---|---|---|
| 2 | Nav link → *Kalendář* | `/kalendar/` | screenshot; `<widget-calendar>` rendered to event cards; **no raw `<widget-*>` text in the DOM**; ≥ 1 card visible |
| 3 | First event card's title link | `/{event-slug}/` | screenshot; event title, date, location visible; console clean |
| 4 | `browser_navigate_back` → nav → *Lekce* | `/lekce/` | screenshot; lecture listing/widget rendered |
| 5 | First specific lecture link | `/{lecture-slug}/` | screenshot; lecture body + recurrence info visible |
| 6 | `browser_navigate_back` → nav → *Píkošky* | `/pikosky/` | screenshot; `<widget-articles category="curiosity">` rendered |
| 7 | First curiosity link | `/{curiosity-slug}/` | screenshot; article body rendered |
| 8 | `browser_navigate_back` → nav → *Lenka píše oznamy* (or whatever the announcements link is named) | `/lenka-pise-oznamy/` | screenshot; `<widget-articles category="announcement">` rendered |
| 9 | First announcement link | `/{announcement-slug}/` | screenshot; article body rendered |

If the expected nav link or first listing item isn't present, **stop and report**. That's the bug — don't try to recover by typing a URL.

## Steps 9a–9e — English version (`/en/`), via the language-switcher chip

The site has an English version under `/en/`. It's reached by the **language-switcher chip at the *bottom* of the menu rail** — labelled `English` on Czech pages, `Čeština` on English pages (it's an `<a class="aesthetic-chip chip-m">` inside a `<nav aria-label="Switch to English" / "Přepnout na češtinu">`, rendered by [lang_switcher.html](../../../theme/templates/components/lang_switcher.html)). It is **not in the main nav** and **not on marathon pages** (marathon is English-only — no Czech counterpart, no switcher).

Generic i18n checks (`<html lang>`, `og:locale`, `hreflang`, switcher absence on single-language sub-sites) live in the agent file. Project-specific facts the agent needs to apply them correctly:

- Czech sections use `cs` / `cs_CZ`; English sections (`/en/...`) and the marathon sub-site use `en` / `en_GB`.
- `hreflang` alternates (cs + en + x-default) are present on non-marathon pages, absent on marathon pages.
- The switcher chip is **byte-identical in styling to the other menu chips** (`aesthetic-chip chip-m`) and sits **last in the rail**. Bespoke styling, a `·` separator, or an inert "current language" element is a regression.

| # | Click target | Lands on | What to verify |
|---|---|---|---|
| 9a | `browser_navigate_back` to a main page (e.g. the homepage or the announcements list), then scroll the rail to the bottom and click the **`English`** chip | `/en/...` (the counterpart of the page you were on, or `/en/` from `/`) | screenshot; `<html lang="en">` in the snapshot/DOM; main nav labels are **English** (`Calendar`, `Classes`, `Milongas`, `Curiosities`, `Announcements`, `About us`, `Tango weekend`); the switcher chip now says **`Čeština`**; console clean |
| 9b | English nav → *Calendar* | `/en/tango-kalendar-brno/` | screenshot; large month/week-grouped calendar with event cards rendered; subscribe block (Apple / Google / Copy for others) rendered; **no raw `<widget-*>` text** |
| 9c | English nav → *About us* | `/en/o-nas/` | screenshot; English body ("The Brnos Aires Initiative"); "The people behind Brnos Aires" section with people cards rendered; subscribe block rendered; **no raw `<widget-*>` text** |
| 9d | Click the **`Čeština`** chip at the bottom of the rail | back on the Czech counterpart (`/o-nas/`) | screenshot; `<html lang="cs">`; nav labels Czech again; switcher says `English` |
| 9e | `browser_navigate_back` to `/`, click `English` | `/en/` | screenshot; English body ("Brnos Aires is a bunch of people from Brno…"); "Where to dance tango this week" event cards, "Next classes" and "Next workshops" calendars, "Curiosities from the world of Argentine tango" article cards, announcement cards near top (from two `<widget-articles category="announcement">` blocks), and subscribe block all rendered; **no raw `<widget-*>` text** |

If the switcher chip isn't at the bottom of the rail, or clicking it doesn't land on the counterpart page, **stop and report**.

## Known dev-mode false-positives

Under `local`, the following are **pre-existing characteristics, not regressions** — don't flag them:

- **CSS/asset 404s and unstyled rendering on any *sub*-page** (anything not at `/` — incl. `/o-nas/`, `/en/o-nas/`, `/marathon-venue/`). Cause: `RELATIVE_URLS = True` + the theme's literal `theme/...` asset paths, which only resolve via the prod `<base href>`. The homepage (`/`) and `/en/` both render styled because they're at directory roots.
- Verify styling properly against `live` after a deploy, or against a prod build. Only flag a sub-page styling issue if it's *new* relative to the same sub-page on the pre-change site.

## Steps 10–17 — Marathon sub-site (separate nav, reachable only from the footer)

The Marathon area is a sub-site with its **own navigation** (rendered by [navigation.html](../../../theme/templates/components/navigation.html) when `nav_slot == 'Marathon'`, switched via URL/section detection in `theme/templates/base.html` lines 72–74). It is **not linked from the main menu**. The only way in is the **`Tango Marathon` link in the footer** (`theme/templates/components/footer.html` line 11) — which is present on every page, including the announcement detail you're already on after Step 9.

Nav slots come from [content/navigation/marathon.md](../../../content/navigation/marathon.md): `Home, DJs, Venue, Gallery, Schedule, Travel, City`. URLs are flat at the site root (Pelican slug-based) — `/marathon/`, `/marathon-djs-team/`, `/marathon-venue/`, `/marathon-gallery/`, `/marathon-schedule/`, `/marathon-getting-to-brno/`, `/marathon-stay-in-brno/`.

| # | Click target | Lands on | What to verify |
|---|---|---|---|
| 10 | Footer link → *Tango Marathon* (from current page — **scroll to footer first**, do not `browser_navigate`) | `/marathon/` | screenshot; **separate Marathon nav visible** (not the main site nav); hero/intro renders; console clean |
| 11 | Marathon nav → *DJs* | `/marathon-djs-team/` | screenshot; DJ profiles/photos render; alt text present on images |
| 12 | Marathon nav → *Venue* | `/marathon-venue/` | screenshot; venue info, map/embed (if any) renders |
| 13 | Marathon nav → *Gallery* | `/marathon-gallery/` | screenshot; gallery widget rendered to images (no raw `<widget-*>` text); thumbnails load (no broken images in network tab) |
| 14 | Marathon nav → *Schedule* | `/marathon-schedule/` | screenshot; schedule table/list renders; times and days legible |
| 15 | Marathon nav → *Travel* | `/marathon-getting-to-brno/` | screenshot; travel info renders |
| 16 | Marathon nav → *City* | `/marathon-stay-in-brno/` | screenshot; accommodation/city info renders |
| 17 | Marathon nav → *Home* | `/marathon/` | screenshot; confirms in-section back-navigation works via the sub-nav (no jump back to main site nav) |

Marathon-specific checks on **every** marathon page:
- The active nav item is highlighted (`nav__item--active` class — visible in `theme/templates/components/navigation.html` line 5).
- The page `<body>` carries `data-section="marathon"` (`theme/templates/base.html` line 63) — confirms the section detection fired and the right nav slot is being used.
- The **main site nav is not present** on marathon pages — if it is, the sub-site/section detection is broken and that's a regression to report.
- If the footer link isn't visible from your current page (Step 9's announcement detail), **stop and report** — `Tango Marathon` is supposed to be on every page. Don't recover by typing `/marathon/`.

If `content/navigation/marathon.md` has been edited since this skill was written, the slot list and slugs above may be stale — re-read that file at the start of the marathon walk and use it as source-of-truth for which links to click and what URLs to expect.

## Step 18 — Exercise any new feature

If the user just implemented a feature, walk through it end-to-end by clicking. Screenshot at each step. If the feature touches forms, fill them via `browser_fill_form`; if it adds new nav, click it; if it changes a widget's output, verify the new output appears on the relevant page.

## When the skill should be invoked

The global rule in `~/.claude/CLAUDE.md` triggers it before reporting frontend or content work as complete. The user can also invoke it explicitly as `/ux-visual-once-over` or `/ux-visual-once-over live`.

Per-page primitives (screenshots, console, network), reporting format, and "don't fix" live in the agent file — see `~/.claude/agents/ux-visual-once-over.md`.
