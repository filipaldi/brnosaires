"""A one-letter Czech word never ends a line (issue #70).

The one-letter prepositions and the conjunction — a, i, k, o, s, u, v, z —
only mean anything attached to the word after them. A line that ends in
" v" hangs the reader's eye on a letter that says nothing alone, and the
display font this site sets its headings in makes the orphan loud. Until
now nothing inserted the glue: templates printed titles raw
(`{{ event.title }}`) and bodies came out of Markdown untouched, so
"Milonga u Brněnského draka" broke wherever the box happened to end.

One function, two ways in:

  the filter   `nbsp_prepositions` in JINJA_FILTERS, applied where a title
               is rendered as visible text: cards, lists, the month pages'
               h1. Head attributes stay raw on purpose — <title>, og: and
               twitter: meta, alt/aria, JSON-LD are read by machines that
               want the plain string.

  the plugin   article_generator_finalized / page_generator_finalized
               rewrite the rendered body HTML: what Markdown produced, what
               widgets expanded into, and the h1 title_as_h1 injects from
               `title:` (the two-signal pattern of colocated_images).

The join is the entity (&nbsp;), not the character, so the HTML source stays
greppable where the text around it is. Idempotent: a pair already joined has
no space left to match, so a second pass — the filter over a body the plugin
already did, or a rebuild — changes nothing.

Text nodes only. Tags, comments and attribute values are stepped over, and
the contents of <script>, <style>, <pre> and <code> are left alone: pre and
code carry their spacing verbatim, and rewriting inside script strings is
how a build breaks quietly. An apostrophe does not start a word ("it's",
"Brno's" — the marathon pages are full of them), so the s in "it's" is not
a preposition however it looks.

ORDER: after title_as_h1 in PLUGINS, because the h1 it injects is body HTML
too. Before llm_ally, whose .md mirrors read the source files and keep
plain spaces — a mirror for machines is not typography.
"""
import re

from markupsafe import Markup, escape
from pelican import signals

# Both cases: a sentence starts with "V únoru" as surely as it continues
# with "v únoru". Matched as a whole word — not preceded by a word character
# or an apostrophe, and followed by whitespace with a word beyond it, i.e.
# there is something on the far side to glue to.
_PREPOSITION = re.compile(r"(?<![\w'’])([aikousvzAIKOUSVZ])(\s+)(?=\S)")

# What the walker steps over without reading: comments, doctypes, and tags.
# The tag branch is quote-aware, so a ">" inside a quoted attribute value
# does not end the tag and leak attribute text into a text node.
_MARKUP = re.compile(
    r"<!--.*?-->"
    r"|<![A-Za-z].*?>"
    r"|</?[A-Za-z][A-Za-z0-9:-]*(?:\"[^\"]*\"|'[^']*'|[^>\"'])*>",
    re.DOTALL,
)
_TAG_NAME = re.compile(r"</?([A-Za-z][A-Za-z0-9:-]*)")

# Contents of these are never reflowed. script and style are not prose at
# all; pre and code are exactly the spacing their author typed.
_VERBATIM = frozenset({"script", "style", "pre", "code"})


def _join(text, inside_verbatim):
    if inside_verbatim or not text:
        return text
    return _PREPOSITION.sub(r"\1&nbsp;", text)


def _join_html(html):
    """`html` with every lone one-letter preposition glued to the next word.

    Walks text nodes only — tags, comments and attribute values pass through
    untouched, and so does anything inside <script>, <style>, <pre> or
    <code>. A preposition with no following word in its own text node is
    left alone: joining across an element boundary ("v <em>Brně</em>") is
    not something a text-level pass can do honestly.

    Takes and returns a plain string of HTML; the input is trusted to be
    HTML already, so whoever has plain text escapes first (the filter does).
    """
    html = str(html)  # a Markup slice would escape what is spliced in
    parts = []
    at = 0
    verbatim = []  # open _VERBATIM elements, innermost last
    for token in _MARKUP.finditer(html):
        parts.append(_join(html[at:token.start()], verbatim))
        parts.append(token.group(0))
        name = _TAG_NAME.match(token.group(0))
        if name and name.group(1).lower() in _VERBATIM:
            element = name.group(1).lower()
            if token.group(0)[1] == "/":  # a closing tag
                if verbatim and verbatim[-1] == element:
                    verbatim.pop()
            elif not token.group(0).endswith("/>"):
                verbatim.append(element)
        at = token.end()
    parts.append(_join(html[at:], verbatim))
    return "".join(parts)


def nbsp_prepositions(value):
    """`value` with every lone one-letter preposition glued to the next word.

    A template value (event.title, an organiser, a description) is plain
    text, so it is escaped before the walk and the & of "Tango & Pizza"
    arrives as the entity it is meant to be. A Markup value is already
    HTML and is walked as it stands. Anything else (None from a field the
    content never set) passes through untouched.

    Returns Markup, so Jinja's own escaping cannot re-escape the entity —
    and cannot paper over a value this filter failed to escape.
    """
    if not isinstance(value, str):
        return value
    if isinstance(value, Markup):
        return Markup(_join_html(value))
    return Markup(_join_html(escape(value)))


def _reflow(generator, bucket):
    for content in getattr(generator, bucket, None) or []:
        # Originals plus their translations: authored .en.md siblings and
        # the clones i18n_fallback synthesizes from them all.
        for obj in (content, *(getattr(content, "translations", None) or [])):
            body = getattr(obj, "_content", None)
            if body:
                # _content is already rendered HTML, so it is walked as it
                # stands and stored back as a plain string — wrapping it in
                # Markup would tell Jinja not to touch it and defeat nothing
                # that needs defeating.
                obj._content = _join_html(body)


def _on_articles(generator):
    _reflow(generator, "articles")


def _on_pages(generator):
    _reflow(generator, "pages")


def register():
    signals.article_generator_finalized.connect(_on_articles)
    signals.page_generator_finalized.connect(_on_pages)
