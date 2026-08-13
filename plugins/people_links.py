"""
people_links — connect an event to the profiles of the people teaching it.

`instructor:` is free text and stays that way: it is what the header prints,
and "Filip a Lenka" reads better than two links stapled together. Alongside it
an event may now carry

    instructor_slugs: [filip-paldia, lenka-platenikova]

a list of `content/people/` slugs. That is the machine-readable half, and it is
what lets a lecturer's own page answer the question the site could not answer
before: *when does this person next teach?*

WHY NOT PARSE `instructor:`
---------------------------
Because it cannot be parsed. The nineteen values in the repo include
"Filip a Lenka", "Filip and Lenka" and "Ondra a Pavla" — two people in one
string, in two languages, by first name, and one of those first names has no
profile at all. Guessing would put words in real people's mouths. An explicit
list of slugs cannot be wrong by accident, and a slug that matches no profile
is a build warning rather than a silent miss.

WHAT IT DOES
------------
For every person article it sets `article.instructor_events`: the upcoming events
that name them, soonest first, deduplicated across the /en/ mirror. Templates
render that; nothing else changes. Events keep whatever `instructor:` says.

DELIBERATELY NOT HERE
---------------------
Schools. `school:` / `schools:` is the other half of the ticket and it needs an
answer this repo does not contain — which lecturer belongs to which school, and
whether one can belong to several. Inventing that would be inventing facts
about real people.
"""
import logging

from pelican import signals

logger = logging.getLogger(__name__)

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


def _on_articles(generator):
    people = {}
    for article in _all_articles(generator):
        if _is_person(article):
            people.setdefault(article.slug, []).append(article)
    if not people:
        return

    by_person = {slug: [] for slug in people}
    unknown = set()
    now = generator.settings.get("NOW") or generator.context.get("NOW")
    today = str(now)[:10] if now else "0000-00-00"

    for article in _all_articles(generator):
        if _is_person(article):
            continue
        start = _event_start(article)
        if start is None:
            continue
        for slug in _instructor_slugs(article):
            if slug not in people:
                if slug not in unknown:
                    logger.warning(
                        "people_links: %s lists lector '%s', which is not a "
                        "file in content/people/",
                        getattr(article, "source_path", "?"), slug)
                    unknown.add(slug)
                continue
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


def register():
    signals.article_generator_finalized.connect(_on_articles)
