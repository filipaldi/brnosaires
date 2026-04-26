# LLM discoverability

Two custom plugins make Brnos Aires content easy for LLM-driven assistants
(ChatGPT, Claude, Perplexity, etc.) to consume without scraping HTML/CSS.

## `md_mirror.py` — per-page Markdown mirrors

Hooks `article_generator_finalized` and `page_generator_finalized`.

For every public article and page, writes an `index.md` next to the
generated `index.html`:

```
output/tango-pizza-sesamo-2026-04-29/index.html   ← rendered HTML
output/tango-pizza-sesamo-2026-04-29/index.md     ← clean Markdown mirror
```

Each `.md` file contains:

1. **Mintlify-style discovery marker** — `> For a complete page index, fetch
   {SITEURL}/llms.txt`. Tells an LLM that landed on a single page where to
   find the full corpus index.
2. **YAML frontmatter** — `title`, `date`, `url`, plus event-specific fields
   (`event-type`, `event-start`, `event-end`, `event-location`,
   `event-organiser`, `instructor`, `recurrence`, `series`) when present. YAML
   is universally parsed; structured event metadata lets an LLM answer date
   queries without parsing prose.
3. **Body** — the raw Markdown from `source_path`, with the original
   frontmatter stripped (re-emitted as YAML above) and `<widget-*>` tags
   removed (those are SSR-only markers meaningless outside the build pipeline).

### Scope

| Content type | Mirrored? | Why |
|---|---|---|
| Events (`content/events/`) | ✅ | Primary discovery target — what is on / when / where. |
| Pages (`content/pages/`) | ✅ | About / hubs / explainer pages. |
| Announcements (`content/announcements/`) | ✅ | Time-stamped editorial updates. |
| Curiosities (`content/curiosities/`) | ❌ | Editorial color, not what users search for. |
| People (`content/people/`) | ❌ | Profile bios, redundant with structured org data. |

Exclusion is by source path (`/content/curiosities/`, `/content/people/`)
plus a fallback on Pelican `category` value.

## `llms_index.py` — auto-generated index + dump *(PR 6, planned)*

Will hook the global `finalized` signal and walk the full corpus once at
build time to emit:

- `output/llms.txt` — curated Key Pages + dynamic Upcoming Events / Regular
  Series Hubs / Recent Updates
- `output/llms-full.txt` — full bodies + recurring lessons expanded ~12 weeks
  ahead
- `output/.well-known/llms.txt` and `output/.well-known/llms-full.txt` —
  byte-identical copies (IETF well-known convention)

Will replace the existing hand-maintained `content/extra/llms.txt` whose
hardcoded dates go stale between deploys.
