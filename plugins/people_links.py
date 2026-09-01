"""
people_links — connect an event to the profiles of the people teaching it.

An event names its teachers exactly once, as a list of `content/people/` slugs:

    instructor_slugs: filip-paldia, lenka-platenikova

That field is where the event header gets the names it prints.

WHY A SLUG AND NOT A NAME
-------------------------
Events used to carry a second field, `instructor:`, free text, and it was what
the header printed. Nothing kept the two in step. The nineteen values in the
repo included "Filip a Lenka", "Filip and Lenka" and "Ondra a Pavla" — two
people in one string, in two languages, by first name — and five files
disagreed with their own slugs, so a real teacher was missing from three of his
own workshops. A slug cannot be wrong by accident: it either names a profile or
it stops the build.

WHAT IT DOES
------------
For every event it sets `article.instructors`: one `Instructor(name, url)` per
slug, taken from the profile in the reader's language. article.html joins those
names with the conjunction from theme/i18n/ and lists them as `Person` entries
in the event's structured data.

DELIBERATELY NOT HERE
---------------------
The other direction, event → profile. A profile used to grow a section of
"upcoming classes and workshops" on its own, assembled from every event naming
that person. It is gone on purpose: what a profile shows is the author's call,
written in the body like any other content, not something the build decides.

Schools. `school:` / `schools:` is the other half of the ticket and it needs an
answer this repo does not contain — which lecturer belongs to which school, and
whether one can belong to several. Inventing that would be inventing facts
about real people.
"""
import logging
import re
from collections import namedtuple

from pelican import signals

logger = logging.getLogger(__name__)

# The `- ` of a YAML list item, which Pelican's metadata reader leaves in place.
_SEQUENCE_MARKER = re.compile(r"^-(\s+|$)")

# One teacher as the templates want them: the name the profile prints, and the
# address of that profile in the same language as the page asking.
Instructor = namedtuple("Instructor", ("name", "url"))


class UnknownInstructor(Exception):
    """An `instructor_slugs:` entry that matches no file in content/people/."""


# `content/people/` is an ARTICLE_PATH, so a person is an Article. This is how
# one is recognised without hard-coding a path.
PEOPLE_PATH_MARKER = "/people/"


def _is_person(content):
    source = (getattr(content, "source_path", "") or "").replace("\\", "/")
    return PEOPLE_PATH_MARKER in source


def _instructor_slugs(content):
    """The `instructor_slugs:` value as a list of slugs, however it was written.

    Pelican hands multi-line metadata back as a list and a single line as a
    string; a YAML-style `[a, b]` arrives as one string with brackets; and the
    CMS writes a real YAML sequence, whose `- ` markers survive into the list
    because Pelican's reader is not a YAML parser. All four spellings appear in
    real front matter, so all four are accepted.
    """
    raw = (getattr(content, "metadata", None) or {}).get("instructor_slugs")
    if not raw:
        return []
    if isinstance(raw, str):
        raw = raw.strip().strip("[]")
        parts = raw.replace(";", ",").split(",")
    else:
        parts = list(raw)
    cleaned = (_SEQUENCE_MARKER.sub("", str(part).strip()).strip("'\"") for part in parts)
    slugs = (slug.strip() for part in cleaned for slug in part.replace(";", ",").split(","))
    return [slug for slug in slugs if slug]


def instructor_names(instructors, lang):
    """The teachers as one line of plain prose: "Filip Paldia a Lenka Plateníková".

    article.html builds the same sentence in Jinja, because there it wraps each
    name in a link and so cannot use a finished string. The conjunction is the
    one thing both take from theme/i18n; the comma rule is written twice, here
    and at that template's instructor row, so a change to either wants the same
    change in the other.

    Plain prose, so the conjunction's hard space is normalised to an ordinary
    one: that space is typography for a rendered line, and this string goes
    into a YAML scalar where it would be an invisible character with no job.

    Three or more names take commas before the conjunction - "X, Y a Z". No
    event in the repo has three teachers, so nothing exercises it.
    """
    names = [person.name for person in instructors]
    if len(names) < 2:
        return names[0] if names else ""
    # Imported here rather than at module scope because nothing else under
    # plugins/ depends on theme/: keeping the one place that does inside the
    # one function that needs it is the smaller coupling.
    from theme import i18n
    key = "event_instructor_and"
    table = getattr(i18n, lang if lang in i18n.LANGS else "cs").STRINGS
    # Falls back the way the `t` filter in pelicanconf.py does. A key renamed
    # in one table should read oddly in both places, not render the page and
    # kill the mirror.
    conjunction = table.get(key) or i18n.cs.STRINGS.get(key, key)
    return ", ".join(names[:-1]) + conjunction.replace("\u00a0", " ") + names[-1]


def _all_articles(generator):
    """Originals and translations.

    The /en/ twins live on `generator.translations`, and the ones i18n_fallback
    synthesizes are built from `metadata` — so an attribute set on the Czech
    original never reaches them. Both lists have to be walked, and the result
    written onto every object sharing a slug.
    """
    for bucket in ("articles", "translations"):
        for article in getattr(generator, bucket, None) or []:
            yield article


def _profiles_by_slug(generator):
    people = {}
    for article in _all_articles(generator):
        if _is_person(article):
            people.setdefault(article.slug, []).append(article)
    return people


def _in_language(profiles, lang):
    """The profile written in `lang`, or the original when it has no twin.

    A profile flagged `translate: false` exists in one language only, and one
    address is still the right answer for it — better a Czech URL than none.
    """
    for profile in profiles:
        if (getattr(profile, "lang", "") or "") == lang:
            return profile
    return profiles[0]


def _attach_instructors(generator, people):
    """Hang the resolved teachers on every event — and refuse the unknown ones.

    An unknown slug used to be a warning. A warning scrolls past, and now that
    the header is rendered from these profiles the cost of missing one has gone
    up: the event would quietly lose a teacher rather than merely lose a link.
    So it stops the build, and it says every slug it could not place, not just
    the first — one build tells the author about all of them.
    """
    # Keyed by file as well as slug: an event and the /en/ clone synthesized
    # for it are two objects over one source file, so the typo is reported
    # once — but a hand-written .en.md twin is its own file with its own copy
    # of the mistake, and the author has to fix both.
    missing = set()
    for article in _all_articles(generator):
        if _is_person(article):
            continue
        resolved = []
        for slug in _instructor_slugs(article):
            profiles = people.get(slug)
            if not profiles:
                missing.add((getattr(article, "source_path", "?"), slug))
                continue
            profile = _in_language(profiles, getattr(article, "lang", "") or "")
            resolved.append(Instructor(name=profile.title, url=profile.url))
        if resolved:
            article.instructors = resolved

    if not missing:
        return
    for source_path, slug in sorted(missing):
        logger.error("people_links: %s lists lector '%s', which is not a file "
                     "in content/people/", source_path, slug)
    raise UnknownInstructor(
        "instructor_slugs names {} lector(s) with no profile in "
        "content/people/: {}. Create the profile first, or fix the slug."
        .format(len({slug for _source_path, slug in missing}),
                ", ".join(f"'{slug}' in {source_path}"
                          for source_path, slug in sorted(missing))))


def _on_articles(generator):
    people = _profiles_by_slug(generator)
    _attach_instructors(generator, people)


def register():
    signals.article_generator_finalized.connect(_on_articles)
