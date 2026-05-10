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
JINJA_FILTERS = {"group_events": group_events, "calendarium": make_calendar_filter(NOW), "expand_recurring": expand_recurring, "date_add": date_add, "parse_widget_attrs": parse_widget_attrs, "parse_article_attrs": parse_article_attrs, "article_filter": article_filter, "gallery_images": get_gallery_images, "format_event_datetime": format_event_datetime, "event_iso8601": event_iso8601, "t": t}

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
    "pages/marathon": {"section": "marathon"},
    "extra/marathon/llms.txt": {"path": "marathon/llms.txt"},
    "extra/robots.txt": {"path": "robots.txt"},
    "extra/humans.txt": {"path": "humans.txt"},
    "extra/ads.txt": {"path": "ads.txt"},
    "extra/ai.txt": {"path": "ai.txt"},
}

CALENDAR_ICS_OUTPUT_DIR = "calendars"
CALENDAR_ICS_EXCLUDED_CATEGORIES = ["announcement", "curiosity"]