"""
feed_one_language — keep the Atom/RSS feed to one entry per article.

Pelican's ALL feed is built from `self.articles` plus every article's
`.translations`, unconditionally — `TRANSLATION_FEED_ATOM = None` only
suppresses the separate per-language feed, it does not stop translations being
folded into the main one. This site synthesizes an English clone for *every*
article (plugins/i18n_fallback.py), so the shipped feed was ~50% duplicates:
13 of 30 entries were `/en/` mirrors carrying the same Czech title and the same
body as the entry right next to them.

That halves the useful length of the feed, and it is worse than cosmetic
downstream: scripts/publish_social.py treats each entry as one announcement, so
every article would go out twice — once linking `/x/` and once `/en/x/`.
Different ids and different URLs, so neither the Mastodon idempotency key nor
the Nostr event id catches it.

The default language wins because a feed carries one title and one language,
and this site's is Czech; the English page is linked from the very entry that
was duplicating it.
"""
import logging

from pelican import signals

logger = logging.getLogger(__name__)


def _other_language_prefixes(context, default_language):
    """URL prefixes used by the non-default languages, e.g. ("/en/",).

    Read off the content rather than a setting: the languages that exist are
    whichever ones i18n_fallback ended up synthesizing.
    """
    codes = set()
    for article in (context.get("articles") or []):
        for translation in (getattr(article, "translations", None) or []):
            code = (getattr(translation, "lang", "") or "").lower()
            if code and code != default_language:
                codes.add(code)
    siteurl = (context.get("SITEURL") or "").rstrip("/")
    return tuple(f"{siteurl}/{code}/" for code in sorted(codes))


def _filter(context, feed):
    items = getattr(feed, "items", None)
    if items is None:
        return
    default_language = (context.get("DEFAULT_LANG") or "cs").lower()
    prefixes = _other_language_prefixes(context, default_language)
    if not prefixes:
        return

    before = len(items)
    feed.items = [item for item in items
                  if not str(item.get("link") or "").startswith(prefixes)]
    dropped = before - len(feed.items)
    if dropped:
        logger.info("feed_one_language: dropped %d translated entr%s from the feed",
                    dropped, "y" if dropped == 1 else "ies")


def register():
    signals.feed_generated.connect(_filter)
