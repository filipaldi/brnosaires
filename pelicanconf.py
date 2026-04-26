SITENAME = "Brnos Aires"
SITEDESCRIPTION = "Přehledně a aktuálně o argentinském tangu v Brně"
SITEURL = ""
RELATIVE_URLS = True
DEFAULT_LANG = "cs"

PATH = "content"
PAGE_PATHS = ["pages"]
ARTICLE_PATHS = ["announcements", "events", "classes", "curiosities", "people"]
STATIC_PATHS = [
    "images",
    "extra/llms.txt",
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
PAGINATION_PATTERNS = (
    (1, '{url}', '{save_as}'),
    (2, '{base_name}/{number}/', '{base_name}/{number}/index.html'),
)

SLUGIFY_SOURCE = "basename"

DEFAULT_DATE_FORMAT = "%d. %m. %Y"
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


def format_event_datetime(value):
    if value is None:
        return ""
    if hasattr(value, "strftime"):
        if getattr(value, "hour", 0) == 0 and getattr(value, "minute", 0) == 0:
            return value.strftime("%d. %m. %Y")
        return value.strftime("%d. %m. %Y %H:%M")
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
    if dt.hour == 0 and dt.minute == 0:
        return dt.strftime("%d. %m. %Y")
    return dt.strftime("%d. %m. %Y %H:%M")


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
JINJA_GLOBALS = {"NOW": NOW}

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'plugins'))
from calendarium.filter import make_calendar_filter
from calendarium.grouping import group_events
from calendarium.attrs import parse_widget_attrs
from recurring_events import expand_recurring, date_add
from article_filter import parse_article_attrs, article_filter
from gallery_widget import get_gallery_images
JINJA_FILTERS = {"group_events": group_events, "calendarium": make_calendar_filter(NOW), "expand_recurring": expand_recurring, "date_add": date_add, "parse_widget_attrs": parse_widget_attrs, "parse_article_attrs": parse_article_attrs, "article_filter": article_filter, "gallery_images": get_gallery_images, "format_event_datetime": format_event_datetime, "event_iso8601": event_iso8601}

PLUGIN_PATHS = ["plugins"]
PLUGINS = ["calendarium", "recurring_events", "article_filter", "widget_processor", "nav_from_docs", "pelican.plugins.sitemap"]

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
    "extra/llms.txt": {"path": "llms.txt"},
    "extra/marathon/llms.txt": {"path": "marathon/llms.txt"},
    "extra/robots.txt": {"path": "robots.txt"},
    "extra/humans.txt": {"path": "humans.txt"},
    "extra/ads.txt": {"path": "ads.txt"},
    "extra/ai.txt": {"path": "ai.txt"},
}

CALENDAR_ICS_OUTPUT_DIR = "calendars"
CALENDAR_ICS_EXCLUDED_CATEGORIES = ["announcement", "curiosity"]