"""
feed_one_language — keep the Atom/RSS feed to one entry per article.

Pelican's ALL feed is built from `self.articles` plus every article's
`.translations`, unconditionally — `TRANSLATION_FEED_ATOM = None` only
suppresses the separate per-language feed, it does not stop translations being
folded into the main one. This site synthesizes an English clone for *every*
article (plugins/i18n_fallback.py), so the shipped feed was ~50% duplicates:
half the entries were `/en/` mirrors carrying the same Czech title and the same
body as the entry right next to them.

That halves the useful length of the feed, and it is worse than cosmetic
downstream: scripts/publish_social.py treats each entry as one announcement, so
every article would go out twice — once linking `/x/` and once `/en/x/`.
Different ids and different URLs, so neither the Mastodon idempotency key nor
the Nostr event id catches it.

The default language wins because a feed carries one title and one language,
and this site's is Czech; the English page is linked from the very entry that
was duplicating it.

The language is read off the first path segment rather than matched against
`SITEURL + "/en/"`. Under publishconf.py the links are absolute
(`https://brnosaires.com/en/x/`), but pelicanconf.py sets `RELATIVE_URLS`, and
then the same entry is `en/x/` — a prefix built from an empty SITEURL matches
neither, so the local preview quietly kept every duplicate while CI looked
fine. A filter that only works under one URL style is a filter you cannot test
before you ship it.
"""
import logging
from urllib.parse import urlsplit

from pelican import signals

logger = logging.getLogger(__name__)


def _other_language_codes(context, default_language):
    """Language codes other than the default, e.g. {"en"}.

    Read off the content rather than a setting: the languages that exist are
    whichever ones i18n_fallback ended up synthesizing.
    """
    codes = set()
    for article in (context.get("articles") or []):
        for translation in (getattr(article, "translations", None) or []):
            code = (getattr(translation, "lang", "") or "").lower()
            if code and code != default_language:
                codes.add(code)
    return codes


def _first_path_segment(link, siteurl):
    """The first non-empty path segment of an entry link, whatever its style."""
    link = str(link or "")
    if siteurl and link.startswith(siteurl):
        link = link[len(siteurl):]
    for segment in urlsplit(link).path.split("/"):
        if segment:
            return segment.lower()
    return ""


def _filter(context, feed):
    items = getattr(feed, "items", None)
    if items is None:
        return
    default_language = (context.get("DEFAULT_LANG") or "cs").lower()
    codes = _other_language_codes(context, default_language)
    if not codes:
        return

    siteurl = (context.get("SITEURL") or "").rstrip("/")
    before = len(items)
    feed.items = [item for item in items
                  if _first_path_segment(item.get("link"), siteurl) not in codes]
    dropped = before - len(feed.items)
    if dropped:
        logger.info("feed_one_language: dropped %d translated entr%s from the feed",
                    dropped, "y" if dropped == 1 else "ies")


def register():
    signals.feed_generated.connect(_filter)
