SITENAME = "Brnos Aires"
SITEDESCRIPTION = "Přehledně a aktuálně o argentinském tangu v Brně"
SITEURL = ""
RELATIVE_URLS = True
DEFAULT_LANG = "cs"

PATH = "content"
PAGE_PATHS = ["pages"]
ARTICLE_PATHS = ["announcements", "events", "classes", "curiosities"]
STATIC_PATHS = ["images"]
THEME_STATIC_PATHS = ["static"]

THEME = "theme"

OUTPUT_PATH = "output"
DELETE_OUTPUT_DIRECTORY = True

ARTICLE_URL = "{slug}/"
ARTICLE_SAVE_AS = "{slug}/index.html"
PAGE_URL = "{slug}/"
PAGE_SAVE_AS = "{slug}/index.html"

SLUGIFY_SOURCE = "basename"

DEFAULT_DATE_FORMAT = "%d. %m. %Y"
TIMEZONE = "Europe/Prague"

FEED_ALL_ATOM = None
FEED_ALL_RSS = None

DEFAULT_PAGINATION = 10

from datetime import datetime
import pytz
import sys
import os

NOW = datetime.now(pytz.timezone(TIMEZONE))

JINJA_ENVIRONMENT = {"extensions": ["jinja2.ext.do"]}
JINJA_GLOBALS = {"NOW": NOW}

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'plugins'))
from calendar_group import group_events
from recurring_events import expand_recurring, date_add
JINJA_FILTERS = {"group_events": group_events, "expand_recurring": expand_recurring, "date_add": date_add}

PLUGIN_PATHS = ["plugins"]
PLUGINS = ["inject_articles", "calendar_group", "recurring_events"]

EXTRA_PATH_METADATA = {
    "pages/marathon": {"section": "marathon"},
}