"""Per-language UI string tables for the theme.

`cs.py` / `en.py` each export a flat `STRINGS` dict keyed by a stable
identifier. `pelicanconf.py` builds `STRINGS = {"cs": cs.STRINGS, "en":
en.STRINGS}`, registers it as a Jinja global, and registers a `t(key, lang)`
filter that does `STRINGS.get(lang, STRINGS["cs"]).get(key, key)` — so an
unknown key or lang degrades to the key string / Czech rather than blowing up.

Templates call `{{ 'no_upcoming_dates' | t(page_lang) }}` where `page_lang`
is the current page's language (`"cs"` or `"en"`), defined once in base.html.

Keep both files key-for-key in sync. Add a key here, add it in both.
"""
from . import cs, en  # noqa: F401  (re-exported for convenience)

LANGS = ("cs", "en")
