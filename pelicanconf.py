SITENAME = "Brnos Aires"
SITEDESCRIPTION = "Přehledně a aktuálně o argentinském tangu v Brně"
# English meta-description fallback (base.html picks per page_lang).
SITEDESCRIPTION_EN = "Argentine tango in Brno, kept current and clear"
SITEURL = ""
RELATIVE_URLS = True
DEFAULT_LANG = "cs"

PATH = "content"
PAGE_PATHS = ["pages"]
ARTICLE_PATHS = ["announcements", "events", "classes", "curiosities", "people"]
STATIC_PATHS = [
    "images",
    "extra/marathon/llms.txt",
    "extra/robots.txt",
    "extra/humans.txt",
    "extra/ads.txt",
    "extra/ai.txt",
]
THEME_STATIC_PATHS = ["static"]

THEME = "theme"

OUTPUT_PATH = "output"
DELETE_OUTPUT_DIRECTORY = True

ARTICLE_URL = "{slug}/"
ARTICLE_SAVE_AS = "{slug}/index.html"
PAGE_URL = "{slug}/"
PAGE_SAVE_AS = "{slug}/index.html"
CATEGORY_URL = "category/{slug}/"
CATEGORY_SAVE_AS = "category/{slug}/index.html"

# Non-default-language content (Lang: en) lives under /en/. Default lang (cs)
# keeps the root-level URLs above untouched. A Content object with lang != cs
# automatically reads these via Content.get_url_setting (lang_ prefix).
ARTICLE_LANG_URL = "en/{slug}/"
ARTICLE_LANG_SAVE_AS = "en/{slug}/index.html"
PAGE_LANG_URL = "en/{slug}/"
PAGE_LANG_SAVE_AS = "en/{slug}/index.html"
CATEGORY_LANG_URL = "en/category/{slug}/"
CATEGORY_LANG_SAVE_AS = "en/category/{slug}/index.html"
PAGINATION_PATTERNS = (
    (1, '{url}', '{save_as}'),
    (2, '{base_name}/{number}/', '{base_name}/{number}/index.html'),
)

SLUGIFY_SOURCE = "basename"

DEFAULT_DATE_FORMAT = "%d. %m. %Y"
# Pelican keys date formatting by language. English: "8 January 2026" — full
# month name, day-first, no comma (the schema.org-/Google-friendly format).
DATE_FORMATS = {"cs": "%d. %m. %Y", "en": "%-d %B %Y"}
TIMEZONE = "Europe/Prague"

FEED_ALL_ATOM = None
FEED_ALL_RSS = None

DEFAULT_PAGINATION = False
PAGINATED_TEMPLATES = {"index": None, "tag": None, "author": None, "category": 12}
INDEX_SAVE_AS = ''
ARTICLE_ORDER_BY = 'reversed-date'

from datetime import datetime
import pytz
import sys
import os

NOW = datetime.now(pytz.timezone(TIMEZONE))


# Date-only format strings, keyed by language; the time ("HH:MM") is appended
# language-agnostically when the value carries a non-midnight time.
_DATE_ONLY_FMT = {"cs": "%d. %m. %Y", "en": "%-d %B %Y"}


def _fmt_dt(dt, lang):
    date_fmt = _DATE_ONLY_FMT.get(lang or "cs", _DATE_ONLY_FMT["cs"])
    # `dt` may be a datetime or a plain date (no .hour/.minute). A date, or a
    # datetime at midnight, renders date-only; otherwise append "HH:MM".
    hour = getattr(dt, "hour", 0)
    minute = getattr(dt, "minute", 0)
    if hour == 0 and minute == 0:
        return dt.strftime(date_fmt)
    return dt.strftime(date_fmt) + " " + dt.strftime("%H:%M")


def format_event_datetime(value, lang="cs"):
    """Render a date / datetime / ISO-ish string in the given language.

    Used by article.html and event_card.html — pass the page's `page_lang`.
    Defaults to Czech so existing call sites without the arg keep working.
    """
    if value is None:
        return ""
    if hasattr(value, "strftime"):
        return _fmt_dt(value, lang)
    s = str(value).strip()
    if not s or len(s) < 10:
        return ""
    try:
        dt = datetime.strptime(s[:19], "%Y-%m-%d %H:%M:%S")
    except (ValueError, TypeError):
        try:
            dt = datetime.strptime(s[:10], "%Y-%m-%d")
        except (ValueError, TypeError):
            return s
    return _fmt_dt(dt, lang)


_MONTH_NAME_TO_NUM = {
    # Czech — base + the genitive/locative variants that show up in titles ("v lednu", "ledna")
    "leden": 1, "ledna": 1, "lednu": 1,
    "unor": 2, "únor": 2, "unora": 2, "února": 2, "unoru": 2, "únoru": 2,
    "brezen": 3, "březen": 3, "brezna": 3, "března": 3, "breznu": 3, "březnu": 3,
    "duben": 4, "dubna": 4, "dubnu": 4,
    "kveten": 5, "květen": 5, "kvetna": 5, "května": 5, "kvetnu": 5, "květnu": 5,
    "cerven": 6, "červen": 6, "cervna": 6, "června": 6, "cervnu": 6, "červnu": 6,
    "cervenec": 7, "červenec": 7, "cervence": 7, "července": 7, "cervenci": 7, "červenci": 7,
    "srpen": 8, "srpna": 8, "srpnu": 8,
    "zari": 9, "září": 9,
    "rijen": 10, "říjen": 10, "rijna": 10, "října": 10, "rijnu": 10, "říjnu": 10,
    "listopad": 11, "listopadu": 11,
    "prosinec": 12, "prosince": 12, "prosinci": 12,
    # English
    "january": 1, "february": 2, "march": 3, "april": 4, "may": 5, "june": 6,
    "july": 7, "august": 8, "september": 9, "october": 10, "november": 11, "december": 12,
}


def _month_number(value):
    """Coerce a month given as int, numeric string, or CS/EN name → 1..12, or None."""
    if value is None:
        return None
    if isinstance(value, int):
        return value if 1 <= value <= 12 else None
    s = str(value).strip().lower()
    if s.isdigit():
        n = int(s)
        return n if 1 <= n <= 12 else None
    return _MONTH_NAME_TO_NUM.get(s)


def tango_year_for_month(value, now=None):
    """Return the year that month "belongs to" for an *upcoming* framing.

    Used by the 12 evergreen month pages (`/milongy-brno-<měsíc>/`) so their
    titles/H1s carry a year without anyone editing 12 files each January:
    if the month is this month or later → current year; if it's already passed
    this year → next year. So `tango_year_for_month('leden')` rendered in
    November → next year. `value` may be an int, a numeric string, or a CS/EN
    month name. Falls back to the current year if `value` can't be parsed
    (harmless — the page still builds, the year is just "this year").
    """
    ref = now if now is not None else NOW
    m = _month_number(value)
    if m is None:
        return ref.year
    return ref.year if m >= ref.month else ref.year + 1


# Nominative month names, indexed [0]=January … [11]=December. Mirrors
# calendarium.config.MONTH_NAMES_{CS,EN} — duplicated here so pelicanconf has
# no import-time dependency on a plugin module being importable yet.
_MONTH_NAMES = {
    "cs": ["leden", "únor", "březen", "duben", "květen", "červen",
           "červenec", "srpen", "září", "říjen", "listopad", "prosinec"],
    "en": ["January", "February", "March", "April", "May", "June",
           "July", "August", "September", "October", "November", "December"],
}
# Locative ("v ...") forms for Czech page titles/H1s: "Milongy v Brně v lednu".
_MONTH_NAMES_CS_LOCATIVE = ["lednu", "únoru", "březnu", "dubnu", "květnu", "červnu",
                            "červenci", "srpnu", "září", "říjnu", "listopadu", "prosinci"]
# ASCII (no-diacritics) month stems for the /milongy-brno-<month>/ URLs. The
# slug is the SAME in both languages (the EN month page is a `.en.md` twin with
# the same `Slug:`, routed to /en/<slug>/ by the i18n machinery — like every
# other .en.md). Only the `/en/` prefix differs, and the template adds that.
_MONTH_SLUG_STEMS = ["leden", "unor", "brezen", "duben", "kveten", "cerven",
                     "cervenec", "srpen", "zari", "rijen", "listopad", "prosinec"]


def month_name(value, lang="cs", form="nominative"):
    """Display name for a month (int / numeric string / CS|EN name) in `lang`.
    `form="locative"` gives the Czech "v lednu" form (English ignores it)."""
    m = _month_number(value)
    if m is None:
        return ""
    idx = m - 1
    if lang == "cs" and form == "locative":
        return _MONTH_NAMES_CS_LOCATIVE[idx]
    return _MONTH_NAMES.get(lang, _MONTH_NAMES["cs"])[idx]


def month_page_slug(value):
    """The slug of the evergreen month page for month `value`:
    `milongy-brno-<cs-month-stem>` (same slug in CS and EN — the EN page is a
    same-slug `.en.md` twin). Returns '' if `value` can't be parsed."""
    m = _month_number(value)
    if m is None:
        return ""
    return "milongy-brno-" + _MONTH_SLUG_STEMS[m - 1]


def month_page_url(value, lang="cs"):
    """The URL path of the evergreen month page for month `value` in `lang`:
    `/milongy-brno-<month>/` (cs) or `/en/milongy-brno-<month>/` (en)."""
    slug = month_page_slug(value)
    if not slug:
        return ""
    return ("/en/" + slug + "/") if lang == "en" else ("/" + slug + "/")


def month_wrap(value, delta):
    """Month arithmetic that wraps 12→1 / 1→12. `value` may be int/str/name;
    returns an int 1..12, or None if `value` can't be parsed."""
    m = _month_number(value)
    if m is None:
        return None
    return ((m - 1 + delta) % 12) + 1


def event_iso8601(value):
    if value is None:
        return ""
    tz = pytz.timezone(TIMEZONE)
    if hasattr(value, "isoformat") and hasattr(value, "tzinfo"):
        return (tz.localize(value) if value.tzinfo is None else value).isoformat()
    s = str(value).strip()
    if not s or len(s) < 10:
        return ""
    try:
        dt = datetime.strptime(s[:19], "%Y-%m-%d %H:%M:%S")
    except (ValueError, TypeError):
        try:
            dt = datetime.strptime(s[:10], "%Y-%m-%d")
        except (ValueError, TypeError):
            return s
    return tz.localize(dt).isoformat()


JINJA_ENVIRONMENT = {"extensions": ["jinja2.ext.do"]}

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'plugins'))
sys.path.insert(0, os.path.dirname(__file__))  # so `theme.i18n` is importable
from calendarium.filter import make_calendar_filter
from calendarium.grouping import group_events
from calendarium.attrs import parse_widget_attrs
from recurring_events import expand_recurring, date_add
from article_filter import parse_article_attrs, article_filter
from gallery_widget import get_gallery_images
from theme.i18n import cs as _i18n_cs, en as _i18n_en

# Per-language UI string tables. `t(key, lang)` is the template helper:
#   {{ 'no_upcoming_dates' | t(page_lang) }}
# Unknown lang -> Czech; unknown key -> the key itself (visible but harmless).
STRINGS = {"cs": _i18n_cs.STRINGS, "en": _i18n_en.STRINGS}


def t(key, lang="cs"):
    return STRINGS.get(lang, STRINGS["cs"]).get(key, STRINGS["cs"].get(key, key))


JINJA_GLOBALS = {"NOW": NOW, "STRINGS": STRINGS}
JINJA_FILTERS = {"group_events": group_events, "calendarium": make_calendar_filter(NOW), "expand_recurring": expand_recurring, "date_add": date_add, "parse_widget_attrs": parse_widget_attrs, "parse_article_attrs": parse_article_attrs, "article_filter": article_filter, "gallery_images": get_gallery_images, "format_event_datetime": format_event_datetime, "event_iso8601": event_iso8601, "tango_year_for_month": tango_year_for_month, "month_name": month_name, "month_page_slug": month_page_slug, "month_page_url": month_page_url, "month_wrap": month_wrap, "t": t}

PLUGIN_PATHS = ["plugins"]
# i18n_fallback must come AFTER widget_processor — it clones the post-widget body
# (widget_processor only iterates generator.pages/articles, not translations).
PLUGINS = ["calendarium", "recurring_events", "article_filter", "widget_processor", "i18n_fallback", "nav_from_docs", "pelican.plugins.sitemap", "llm_ally"]

SITEMAP = {
    "format": "xml",
    "priorities": {
        "articles": 0.7,
        "pages": 0.9,
        "indexes": 0.4,
    },
    "changefreqs": {
        "articles": "weekly",
        "pages": "monthly",
        "indexes": "daily",
    },
}

EXTRA_PATH_METADATA = {
    # `translate: False` -> this content is English-first with no Czech mirror
    # and never will have one: the i18n_fallback plugin synthesizes no
    # /en/<slug>/ clone for it, base.html renders no language switcher on it,
    # and page_lang is forced to 'en'. (`section: marathon` on the pages folder
    # is separate -> the marathon layout/nav.) The whole marathon sub-site lives
    # in three content folders, all flagged here. See docs/EDITING.md.
    "pages/marathon": {"section": "marathon", "translate": False},
    "events/2026-marathon": {"translate": False},
    "people/marathon-djs": {"translate": False},
    "extra/marathon/llms.txt": {"path": "marathon/llms.txt"},
    "extra/robots.txt": {"path": "robots.txt"},
    "extra/humans.txt": {"path": "humans.txt"},
    "extra/ads.txt": {"path": "ads.txt"},
    "extra/ai.txt": {"path": "ai.txt"},
}

CALENDAR_ICS_OUTPUT_DIR = "calendars"
CALENDAR_ICS_EXCLUDED_CATEGORIES = ["announcement", "curiosity"]