SITENAME = "Brnos Aires"
SITEDESCRIPTION = "Přehledně a aktuálně o argentinském tangu v Brně"
SITEURL = ""
RELATIVE_URLS = True
DEFAULT_LANG = "cs"

PATH = "content"
PAGE_PATHS = ["pages"]
ARTICLE_PATHS = ["announcements", "events", "classes", "curiosities", "people"]
STATIC_PATHS = ["images"]
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

JINJA_ENVIRONMENT = {"extensions": ["jinja2.ext.do"]}
JINJA_GLOBALS = {"NOW": NOW}

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'plugins'))
from calendarium import group_events, make_calendar_filter, parse_widget_attrs
from recurring_events import expand_recurring, date_add
JINJA_FILTERS = {"group_events": group_events, "calendarium": make_calendar_filter(NOW), "expand_recurring": expand_recurring, "date_add": date_add, "parse_widget_attrs": parse_widget_attrs}

PLUGIN_PATHS = ["plugins"]
PLUGINS = ["inject_articles", "calendarium", "recurring_events"]

EXTRA_PATH_METADATA = {
    "pages/marathon": {"section": "marathon"},
}