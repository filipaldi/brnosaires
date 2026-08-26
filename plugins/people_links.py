"""
people_links — connect an event to the profiles of the people teaching it.

An event names its teachers exactly once, as a list of `content/people/` slugs:

    instructor_slugs: filip-paldia, lenka-platenikova

That single field is both halves of the job. It puts the event on each
lecturer's own page, and it is where the event header gets the names it prints.

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

For every person article it sets `article.instructor_events`: the upcoming
events that name them, soonest first, deduplicated across the /en/ mirror.

DELIBERATELY NOT HERE
---------------------
Schools. `school:` / `schools:` is the other half of the ticket and it needs an
answer this repo does not contain — which lecturer belongs to which school, and
whether one can belong to several. Inventing that would be inventing facts
about real people.
"""
import logging
from collections import namedtuple

from pelican import signals

logger = logging.getLogger(__name__)

# One teacher as the templates want them: the name the profile prints, and the
# address of that profile in the same language as the page asking.
Instructor = namedtuple("Instructor", ("name", "url"))


class UnknownInstructor(Exception):
    """An `instructor_slugs:` entry that matches no file in content/people/."""


# `content/people/` is an ARTICLE_PATH, so a person is an Article. This is how
# one is recognised without hard-coding a path.
PEOPLE_PATH_MARKER = "/people/"

# Events further out than this are not "upcoming", they are a wall of text.
MAX_EVENTS_PER_PERSON = 8


def _is_person(content):
    source = (getattr(content, "source_path", "") or "").replace("\\", "/")
    return PEOPLE_PATH_MARKER in source


def _instructor_slugs(content):
    """The `instructor_slugs:` value as a list of slugs, however it was written.

    Pelican hands multi-line metadata back as a list and a single line as a
    string; a YAML-style `[a, b]` arrives as one string with brackets. All
    three spellings appear in real front matter, so all three are accepted.
    """
    raw = (getattr(content, "metadata", None) or {}).get("instructor_slugs")
    if not raw:
        return []
    if isinstance(raw, str):
        raw = raw.strip().strip("[]")
        parts = raw.replace(";", ",").split(",")
    else:
        parts = list(raw)
    return [str(part).strip().strip("'\"") for part in parts if str(part).strip()]


def _event_start(content):
    return (getattr(content, "metadata", None) or {}).get("event-start")


def _next_occurrence(event, today):
    """The next date this event actually happens, as a card-ready Occurrence.

    A weekly class carries the date of its FIRST session in `event-start`, so
    filtering on that value alone hides every class that started before today —
    which is every class that is actually running. Expanding the recurrence
    gives the next real date, and shows it on the card instead of January.

    Returns None when the event is over.
    """
    from recurring_events import expand_recurring, _normalize_event

    metadata = getattr(event, "metadata", None) or {}
    if metadata.get("recurrence") or metadata.get("event-rrule"):
        horizon = f"{int(today[:4]) + 1}{today[4:]}"
        occurrences = expand_recurring([event], today, horizon)
        return occurrences[0] if occurrences else None
    if str(metadata.get("event-start"))[:10] < today:
        return None
    return _normalize_event(event)


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


def _collect_upcoming(generator, people):
    by_person = {slug: [] for slug in people}
    now = generator.settings.get("NOW") or generator.context.get("NOW")
    today = str(now)[:10] if now else "0000-00-00"

    for article in _all_articles(generator):
        if _is_person(article):
            continue
        start = _event_start(article)
        if start is None:
            continue
        for slug in _instructor_slugs(article):
            # Every slug resolves by now — _attach_instructors stopped the
            # build otherwise.
            by_person[slug].append(article)

    linked = 0
    for slug, events in by_person.items():
        seen, upcoming = set(), []
        for event in events:
            # One event and its /en/ twin are two Articles with one slug; the
            # person's page should list the date once.
            if event.slug in seen:
                continue
            seen.add(event.slug)
            occurrence = _next_occurrence(event, today)
            if occurrence is not None:
                upcoming.append(occurrence)
        upcoming.sort(key=lambda o: o.date)
        for profile in people[slug]:
            profile.instructor_events = upcoming[:MAX_EVENTS_PER_PERSON]
        linked += len(upcoming)

    if linked:
        logger.info("people_links: %d upcoming event(s) linked to %d profile(s)",
                    linked, sum(1 for e in by_person.values() if e))


def _on_articles(generator):
    people = _profiles_by_slug(generator)
    _attach_instructors(generator, people)
    _collect_upcoming(generator, people)


def register():
    signals.article_generator_finalized.connect(_on_articles)
