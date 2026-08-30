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

Monolingual content is skipped — a page that declares `translate: false` in
its front-matter (the marathon sub-site does this in bulk via
EXTRA_PATH_METADATA in pelicanconf.py) has no translation and never will, so
it must NOT get an `/en/<slug>/` duplicate. (Before, this plugin sniffed for
"marathon" in the URL / source path; the explicit flag replaces that — see
docs/EDITING.md.)

ORDER MATTERS: this plugin must run *after* `widget_processor` so the clone
copies an already-widget-rendered `_content` (widget_processor only iterates
`generator.pages` / `generator.articles`, not `generator.translations`, so a
clone added only to `translations` would otherwise keep raw `<widget-*>` tags).
Achieved by listing `i18n_fallback` after `widget_processor` in PLUGINS.
"""
import logging
import os

from pelican import signals
from pelican.utils import slugify

logger = logging.getLogger(__name__)

EN_LANG = "en"
EN_SUFFIX = ".en.md"


def _slugify(value, settings):
    """Pelican's own slug, with Pelican's own settings.

    The three keyword arguments are the ones `Content.__init__` passes; this
    has to agree with that call exactly, because the whole point is to land on
    the slug the Czech file next door was given.
    """
    return slugify(
        value,
        regex_subs=settings.get("SLUG_REGEX_SUBSTITUTIONS", []),
        preserve_case=settings.get("SLUGIFY_PRESERVE_CASE", False),
        use_unicode=settings.get("SLUGIFY_USE_UNICODE", False),
    )


def pair_by_filename(content):
    """`x.en.md` takes the slug of `x.md`, so the two are one article.

    Translations are paired by slug (see above), and under
    `SLUGIFY_SOURCE = "basename"` a file that declares none is named after its
    filename — which for the English half still contains the `.en`. Pelican
    slugifies `kurz-tango-1.en` into `kurz-tango-1en` and the pair becomes two
    unrelated articles: the English text at an address nothing links to, and
    the Czech text served in its place under `/en/` by the fallback below.

    It stayed hidden because it breaks nothing loudly. Every page is written,
    the build is green, and the only complaint comes from `calendars/*.ics`
    pointing at a `/kurz-tango-1en/` that was never written — three days and
    eleven files later.

    A declared `slug:` still wins: 63 pairs in the repo name one, and taking
    that away from them would move 63 published addresses. This only fills in
    the silence, which since the CMS stopped writing the field (#97) is what
    every new entry arrives with.
    """
    source = getattr(content, "source_path", None) or ""
    if not source.endswith(EN_SUFFIX):
        return
    if "slug" in (getattr(content, "metadata", None) or {}):
        return
    stem = os.path.basename(source)[: -len(EN_SUFFIX)]
    content.slug = _slugify(stem, getattr(content, "settings", None) or {})


def _is_monolingual(content):
    """True if this content opts out of translation — no /en/ mirror is
    synthesized for it.

    Both spellings of the flag count, and that is the point. EXTRA_PATH_METADATA
    injects a real Python `False`, but a `translate: false` typed into a file's
    own front matter arrives as the *string* "false": Pelican only coerces
    metadata it knows about, and this field is ours. Testing `is False` alone
    therefore honoured the path rule and silently ignored the per-file flag —
    while docs/EDITING.md and docs/ANGLICKA-VERZIA.md both tell editors to write
    exactly that. The file-level form is what a folder move or the CMS produces,
    so it has to work.
    """
    meta = getattr(content, "metadata", None) or {}
    value = meta.get("translate")
    if isinstance(value, bool):
        return value is False
    return str(value).strip().lower() in ("false", "no", "0")


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
        if _is_monolingual(content):
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
    # Fires at the end of every Content.__init__, so the slug is corrected
    # long before `process_translations` groups anything by it.
    signals.content_object_init.connect(pair_by_filename)
    signals.page_generator_finalized.connect(_on_pages)
    signals.article_generator_finalized.connect(_on_articles)
