"""
Reads nav documents from content/navigation/ and sets context['nav_items'].

- main.md      -> Czech main nav     -> nav_items['main']['cs']
- main.en.md   -> English main nav   -> nav_items['main']['en']  (optional;
                  if absent, the cs list is reused for both langs)
- footer.md    -> Czech footer links -> nav_items['footer']['cs']
- footer.en.md -> English footer     -> nav_items['footer']['en']  (optional;
                  if absent, the cs list is reused for both langs)
- marathon.md  -> Marathon nav (English-only sub-site, no per-lang variants)
                  -> nav_items['marathon']  (a flat list, not a {lang: ...} dict)

Each line is `Label, link` where `link` is either an absolute URL or a page
slug. Slugs are resolved against generator.pages; for the English main nav,
if the page has an `en` translation (the /en/ fallback synthesized by
i18n_fallback), the link points at the translation's URL so the nav stays
within /en/.

Plugin order: must run AFTER i18n_fallback (which populates page.translations
with the /en/ clones). pelicanconf.py lists nav_from_docs after i18n_fallback.
"""
import os
from pelican import signals

DEFAULT_LANG = "cs"
EN_LANG = "en"


def _parse_nav_file(path):
    if not os.path.isfile(path):
        return []
    items = []
    with open(path, "r", encoding="utf-8") as f:
        for raw in f:
            line = raw.strip()
            if not line or line.lstrip().startswith("#"):
                continue
            idx = line.find(",")
            if idx < 0:
                continue
            label = line[:idx].strip()
            link = line[idx + 1:].strip()
            if not label or not link:
                continue
            items.append({"label": label, "link": link})
    return items


def _en_url(page):
    """The /en/ URL of `page`: its en translation's url if one exists, else
    the page's own url prefixed with en/ as a last-resort fallback."""
    for tr in getattr(page, "translations", []) or []:
        if (getattr(tr, "lang", "") or "").lower() == EN_LANG:
            return tr.url
    return "en/" + page.url


def _resolve_items(items, pages_by_slug, lang=DEFAULT_LANG):
    result = []
    for item in items:
        label = item["label"]
        link = item["link"]
        if link.startswith("http://") or link.startswith("https://"):
            result.append({"label": label, "url": link, "slug": None, "external": True})
            continue
        page = pages_by_slug.get(link)
        if page is None:
            # slug we couldn't resolve to a page object — best-effort URL
            url = ("en/" if lang == EN_LANG else "") + link + "/"
        elif lang == EN_LANG:
            url = _en_url(page)
        else:
            url = page.url
        result.append({"label": label, "url": url, "slug": link, "external": False})
    return result


def build_nav_items(generator):
    settings = generator.settings
    path = settings.get("NAVIGATION_PATH")
    if path is None:
        path = os.path.join(settings["PATH"], "navigation")
    if not os.path.isdir(path):
        generator.context["nav_items"] = {"marathon": [], "main": {"cs": [], "en": []}, "footer": {"cs": [], "en": []}}
        return

    pages_by_slug = {p.slug: p for p in generator.pages}

    def _per_lang(basename):
        """Parse <basename>.md (+ optional <basename>.en.md) into a {cs, en} dict
        of resolved nav items; en falls back to the cs labels if no .en.md."""
        cs_raw = _parse_nav_file(os.path.join(path, basename + ".md"))
        en_path = os.path.join(path, basename + ".en.md")
        en_raw = _parse_nav_file(en_path) if os.path.isfile(en_path) else cs_raw
        return {
            "cs": _resolve_items(cs_raw, pages_by_slug, lang=DEFAULT_LANG),
            "en": _resolve_items(en_raw, pages_by_slug, lang=EN_LANG),
        }

    # Marathon nav: English-only sub-site, single flat list (no per-lang dict).
    marathon_raw = _parse_nav_file(os.path.join(path, "marathon.md"))
    marathon_nav = _resolve_items(marathon_raw, pages_by_slug, lang=DEFAULT_LANG)

    generator.context["nav_items"] = {
        "main": _per_lang("main"),
        "footer": _per_lang("footer"),
        "marathon": marathon_nav,
    }


def register():
    signals.page_generator_finalized.connect(build_nav_items)
