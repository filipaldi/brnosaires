"""
i18n_fallback — synthesize English (`/en/...`) variants for content that has no
explicit translation yet, reusing the Czech body.

Pelican links translations purely by `slug` (ARTICLE_TRANSLATION_ID /
PAGE_TRANSLATION_ID, both default to "slug"): same slug + different `Lang:`
== one set of translations. `process_translations` (run inside
`generate_context`) partitions content into "originals" (default-lang or
singletons) and "translations" (the rest), and populates every object's
`.translations` list. Translation objects ARE written to disk — the writer
loops `chain(self.translations, self.pages, ...)` — and a non-default-lang
object automatically reads `PAGE_LANG_SAVE_AS` / `ARTICLE_LANG_SAVE_AS`
instead of the plain `*_SAVE_AS` (via `Content.get_url_setting`, which prefixes
the key with `lang_` when `not self.in_default_lang`).

So: in `*_generator_finalized` (fires after `generate_context`, before
`generate_output`), for every original whose `.translations` has no English
entry, build a clone with `Lang: en`, the same slug, and the same body, then
register it on the original's `.translations` AND on the generator's
`self.translations` so the writer picks it up.

Marathon pages are skipped — that sub-site is English-first with no Czech
mirror, so it must NOT get a `/en/marathon-...` duplicate.

ORDER MATTERS: this plugin must run *after* `widget_processor` so the clone
copies an already-widget-rendered `_content` (widget_processor only iterates
`generator.pages` / `generator.articles`, not `generator.translations`, so a
clone added only to `translations` would otherwise keep raw `<widget-*>` tags).
Achieved by listing `i18n_fallback` after `widget_processor` in PLUGINS.
"""
import logging

from pelican import signals

logger = logging.getLogger(__name__)

EN_LANG = "en"


def _is_marathon(content):
    """True if this content object belongs to the English-only marathon site."""
    url = getattr(content, "url", "") or ""
    if "marathon" in url:
        return True
    src = getattr(content, "source_path", "") or ""
    # source paths look like .../content/pages/marathon/venue.md
    return "/pages/marathon/" in src.replace("\\", "/") or src.replace("\\", "/").endswith("/pages/marathon")


def _has_en_translation(content):
    for t in getattr(content, "translations", []) or []:
        if (getattr(t, "lang", "") or "").lower() == EN_LANG:
            return True
    return (getattr(content, "lang", "") or "").lower() == EN_LANG


def _clone_as_en(content):
    """Build an English clone of `content`, sharing its (rendered) body."""
    klass = type(content)
    metadata = dict(getattr(content, "metadata", {}) or {})
    # Force the language; keep the same slug so process_translations would have
    # grouped them (we're doing that grouping manually here).
    metadata["lang"] = EN_LANG
    # `_content` is the body after earlier plugins (e.g. widget_processor) have
    # rewritten it — see module docstring re: plugin order.
    body = getattr(content, "_content", "") or ""
    clone = klass(
        content=body,
        metadata=metadata,
        settings=content.settings,
        source_path=getattr(content, "source_path", None),
        context=getattr(content, "_context", None),
    )
    # The original may have overridden save_as/url in its metadata.
    #   - the homepage (`url:` empty + `save_as: index.html`) -> the English
    #     clone should be the /en/ homepage, i.e. en/index.html at /en/.
    #   - any other override (a page pinned to a custom path) -> just drop it
    #     so the clone falls back to PAGE_LANG_SAVE_AS / PAGE_LANG_URL and
    #     doesn't collide with the cs page at the same custom path.
    orig_save_as = (getattr(content, "save_as", "") or "")
    is_homepage = orig_save_as in ("index.html", "/index.html") or (
        getattr(content, "url", "") in ("", "/")
    )
    for attr in ("override_save_as", "override_url"):
        if hasattr(clone, attr):
            delattr(clone, attr)
    if is_homepage:
        clone.override_save_as = "en/index.html"
        clone.override_url = "en/"
    # Make doubly sure the URL machinery treats it as a translation.
    clone.in_default_lang = False
    return clone


def _process(generator, originals, label):
    new_translations = []
    for content in originals:
        if _is_marathon(content):
            continue
        if _has_en_translation(content):
            continue
        try:
            clone = _clone_as_en(content)
        except Exception as exc:  # noqa: BLE001 — never break the build over one page
            logger.warning("i18n_fallback: could not clone %s (%s): %s",
                           getattr(content, "source_path", "?"), label, exc)
            continue
        # Wire the translation links both ways.
        content.translations = list(getattr(content, "translations", []) or []) + [clone]
        clone.translations = [content] + [t for t in content.translations if t is not clone]
        new_translations.append(clone)
        logger.debug("i18n_fallback: synthesized %s -> %s", content.url, clone.url)
    if new_translations:
        generator.translations = list(getattr(generator, "translations", []) or []) + new_translations
        logger.info("i18n_fallback: %d English fallback %s page(s) synthesized",
                    len(new_translations), label)


def _on_pages(page_generator):
    _process(page_generator, list(page_generator.pages), "page")


def _on_articles(article_generator):
    _process(article_generator, list(article_generator.articles), "article")


def register():
    signals.page_generator_finalized.connect(_on_pages)
    signals.article_generator_finalized.connect(_on_articles)
