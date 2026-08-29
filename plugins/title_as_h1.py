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

AND IT DOES NOT STOP THE BUILD
------------------------------
Refusing to build was the obvious alternative and the wrong one. The person who
would have to fix it writes in the CMS and never opens an Actions run, so a red
build does not reach them — it only stops everything else from being published.
Instead the page is made correct and the build prints a report naming the texts
that still want a heading of their own, addressed to the person who has to
write it. When there is somewhere to send it, that report becomes the mail.

Articles only. Pages are not editable from the CMS (issue #74) and every one of
them already opens with its own heading.
"""
import logging
import os
import re
from html import escape

from pelican import signals

logger = logging.getLogger(__name__)

# Any h1, with or without attributes. Deliberately not a parser: this runs over
# the rendered body of every article on every build.
_H1 = re.compile(r"<h1[\s>]", re.IGNORECASE)


def _ensure(article):
    """Give the body an h1 from the title. True when it needed one."""
    body = getattr(article, "_content", "") or ""
    if not body.strip() or _H1.search(body):
        return False
    article._content = f"<h1>{escape(article.title, quote=False)}</h1>\n{body}"
    return True


def _report(paths):
    """What the author is told. Czech, because the author is who reads it.

    One line per file rather than a count: the fix is per file, and the person
    doing it should not have to go looking for which ones.
    """
    return "\n".join([
        "",
        f"Tyhle texty nemají vlastní nadpis, tak jim ho web zatím doplnil z pole "
        f"„Název\" ({len(paths)}):",
        *(f"  - {path}" for path in paths),
        "Stránka je v pořádku a je venku. Ale nadpis, který čtenář uvidí, je jen "
        "název akce — pokud má znít jinak, napište ho jako první řádek textu: "
        "# Váš nadpis",
    ])


def _in_repo(path, generator):
    """`content/events/…/x.md`, not the build machine's absolute path.

    The report is read by someone looking for the file in the repository, and
    on a runner the absolute path is four lines of noise before the useful part.
    """
    content_dir = (getattr(generator, "settings", None) or {}).get("PATH")
    if not content_dir:
        return path
    try:
        return os.path.relpath(path, os.path.dirname(os.path.abspath(content_dir)))
    except ValueError:  # different drive on Windows
        return path


def _on_articles(generator):
    fixed = []
    for article in generator.articles:
        for content in (article, *(getattr(article, "translations", None) or [])):
            if _ensure(content):
                fixed.append(_in_repo(getattr(content, "source_path", "?"), generator))
    if fixed:
        # Warning, not error: nothing is broken, something is unfinished.
        logger.warning("%s", _report(sorted(set(fixed))))


def register():
    signals.article_generator_finalized.connect(_on_articles)
