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

ARTICLE_URL = "{slug}.html"
ARTICLE_SAVE_AS = "{slug}.html"
PAGE_URL = "{slug}.html"
PAGE_SAVE_AS = "{slug}.html"

DEFAULT_DATE_FORMAT = "%d. %m. %Y"
TIMEZONE = "Europe/Prague"

FEED_ALL_ATOM = None
FEED_ALL_RSS = None

DEFAULT_PAGINATION = 10

from datetime import datetime
import pytz

NOW = datetime.now(pytz.timezone(TIMEZONE))

JINJA_ENVIRONMENT = {"extensions": ["jinja2.ext.do"]}
JINJA_GLOBALS = {"NOW": NOW}

PLUGIN_PATHS = ["plugins"]
PLUGINS = ["inject_articles"]