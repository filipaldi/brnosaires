"""Every article starts at h1, whether or not the body says so.

The heading is the first thing a screen reader lands on and the outline the
whole page hangs from, and until now it came from the body: a `# Nadpis` typed
as the first line of the Markdown. That works for the hundred-odd events
written by hand and not at all for the ones written in the CMS, where the title
is a form field and the body is only the text below it. Five entries in a row
shipped with no h1 at all, and the editor had no way of knowing.

So the body keeps its heading when it has one — on about a hundred events that
heading deliberately reads differently from `title:`, and rewriting them would
be inventing copy — and gets `title:` as an h1 when it has none.

Articles only. Pages are not editable from the CMS (issue #74) and every one of
them already opens with its own heading.
"""
import re
from html import escape

from pelican import signals

# Any h1, with or without attributes. Deliberately not a parser: this runs over
# the rendered body of every article on every build.
_H1 = re.compile(r"<h1[\s>]", re.IGNORECASE)


def _ensure(article):
    body = getattr(article, "_content", "") or ""
    if not body.strip() or _H1.search(body):
        return
    article._content = f"<h1>{escape(article.title, quote=False)}</h1>\n{body}"


def _on_articles(generator):
    for article in generator.articles:
        _ensure(article)
        for translation in getattr(article, "translations", []):
            _ensure(translation)


def register():
    signals.article_generator_finalized.connect(_on_articles)
