"""Invariants of the rendered HTML: structure, accessibility, structured
data, Czech line-breaking.

These are the things that only break in the output — no template diff shows
them, and nobody notices until a screen reader user cannot navigate or Google
silently drops a rich result.
"""
import os
import re
import unittest
from html import unescape
from urllib.parse import parse_qs, urlsplit

from tests import REPO_ROOT, build_site

HEADING = re.compile(r"<h([1-6])\b", re.IGNORECASE)
SCRIPT_OR_STYLE = re.compile(r"<(script|style)\b.*?</\1>", re.DOTALL | re.IGNORECASE)


# Every page the theme rendered carries this. Anything served as a static file
# and deliberately not themed has no <base>, and testing it against the
# theme's invariants would be testing the wrong thing.
THEMED = '<base href="https://brnosaires.com/">'


def pages(output):
    for root, _dirs, files in os.walk(output):
        for name in sorted(files):
            if name.endswith(".html"):
                full = os.path.join(root, name)
                with open(full, encoding="utf-8", errors="replace") as handle:
                    html = handle.read()
                if THEMED in html:
                    yield os.path.relpath(full, output), html


class _Built(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.output = build_site()
        cls.pages = list(pages(cls.output))
        assert len(cls.pages) > 100, "suspiciously small build"


class Headings(_Built):
    """One h1, first, and no skipped levels — the document outline a screen
    reader navigates by."""

    def outlines(self):
        for path, html in self.pages:
            levels = [int(m) for m in HEADING.findall(SCRIPT_OR_STYLE.sub("", html))]
            if levels:
                yield path, levels

    def test_the_first_heading_is_always_h1(self):
        bad = [p for p, levels in self.outlines() if levels[0] != 1]
        self.assertEqual(bad, [], f"pages not starting at h1: {bad[:5]}")

    def test_there_is_exactly_one_h1(self):
        bad = [p for p, levels in self.outlines() if levels.count(1) != 1]
        self.assertEqual(bad, [], f"pages with 0 or 2+ h1: {bad[:5]}")

    def test_no_level_is_skipped(self):
        bad = []
        for path, levels in self.outlines():
            previous = levels[0]
            for level in levels[1:]:
                if level > previous + 1:
                    bad.append(f"{path}: h{previous}->h{level}")
                    break
                previous = level
        self.assertEqual(bad, [], f"skipped heading levels: {bad[:5]}")


class SkipLink(_Built):
    def test_every_page_has_one_pointing_at_a_real_target(self):
        for path, html in self.pages:
            found = re.search(r'<a class="skip-link" href="([^"]+)"', html)
            self.assertIsNotNone(found, f"no skip link on {path}")
            fragment = found.group(1).split("#")[-1]
            self.assertIn(f'id="{fragment}"', html,
                          f"skip link on {path} points at a missing target")

    def test_the_href_repeats_the_page_url(self):
        # A bare "#main" resolves against <base href>, not the current
        # document, so on every page but the homepage it navigated away to the
        # homepage — the opposite of what a skip link is for.
        for path, html in self.pages:
            href = re.search(r'<a class="skip-link" href="([^"]+)"', html).group(1)
            self.assertTrue(href.startswith("https://brnosaires.com/"),
                            f"skip link on {path} is base-relative: {href}")
            expected = "" if path == "index.html" else path[: -len("index.html")]
            self.assertEqual(href, f"https://brnosaires.com/{expected}#main", path)

    def test_the_target_can_take_focus(self):
        # Safari will not focus a non-focusable fragment target; it scrolls and
        # leaves focus on the link, so the next Tab returns to the nav.
        for path, html in self.pages:
            self.assertRegex(html, r'<main id="main"[^>]*tabindex="-1"',
                             f"main on {path} cannot receive focus")

    def test_it_is_the_first_link_in_the_body(self):
        # A skip link that is not first in tab order skips nothing.
        for path, html in self.pages:
            body = html.split("<body", 1)[-1]
            first = re.search(r"<a\b[^>]*>", body)
            self.assertIn("skip-link", first.group(0),
                          f"something is tabbable before the skip link on {path}")

    def test_it_is_localised(self):
        cs = dict(self.pages)["index.html"]
        en = dict(self.pages)["en/index.html"]
        self.assertIn("Přeskočit na obsah", cs)
        self.assertIn("Skip to content", en)


class Monolingual(_Built):
    """`translate: false` in a file's own front matter must suppress the /en/
    clone, not just the EXTRA_PATH_METADATA form.

    The marathon DJs used to get the flag from their folder path. Once they
    moved into the single content/people/ folder the flag had to travel in the
    front matter — where Pelican hands it over as the string "false", which the
    plugin's `is False` test quietly ignored. The result was four English pages
    duplicating an English-only sub-site.
    """

    DJS = ("balasz", "francesco", "veronika-kim", "vincent", "macka-siva")

    def test_a_marathon_dj_has_no_en_clone(self):
        for slug in self.DJS:
            self.assertFalse(
                os.path.isdir(os.path.join(self.output, "en", slug)),
                f"/en/{slug}/ exists — translate: false was not honoured")

    def test_the_czech_route_still_exists(self):
        # The flag suppresses the mirror, not the page itself.
        for slug in self.DJS:
            self.assertTrue(os.path.isfile(
                os.path.join(self.output, slug, "index.html")), slug)


class Categories(_Built):
    """A category is a section of the site, not a leftover of the folder tree.

    Pelican names the category after the deepest folder whenever the front
    matter does not, so the shape of `content/` leaks into public URLs. After
    events moved into `events/RRRR/MM/` that produced `/category/01/` through
    `/category/12/` — indexable, in the sitemap, linked from nothing.

    `/category/announcement/` is the one a reader actually reaches:
    content/pages/lenka-pise-oznamy.md links straight at it.
    """

    SECTIONS = {"announcement", "curiosity", "event", "people"}

    def built(self):
        root = os.path.join(self.output, "category")
        return {name for name in os.listdir(root)
                if os.path.isdir(os.path.join(root, name))}

    def test_none_is_a_leftover_folder_name(self):
        self.assertEqual(sorted(self.built() - self.SECTIONS), [])

    def test_the_one_the_site_links_to_is_built(self):
        self.assertTrue(os.path.isfile(os.path.join(
            self.output, "category", "announcement", "index.html")))


class MapLinks(_Built):
    def test_every_venue_link_carries_a_non_empty_query_and_a_label(self):
        found = 0
        for path, html in self.pages:
            for anchor in re.findall(
                    r'<a href="(https://www\.openstreetmap\.org/search\?[^"]*)"'
                    r'(.*?)</a>', html, re.DOTALL):
                found += 1
                url, rest = anchor
                query = parse_qs(urlsplit(unescape(url)).query)
                self.assertTrue(query.get("query", [""])[0].strip(),
                                f"empty map query on {path}")
                self.assertIn('rel="noopener"', rest, path)
                self.assertIn("aria-label=", rest, path)
        self.assertGreater(found, 100, "venue links disappeared")

    def test_no_venue_lookup_points_at_google_maps(self):
        # Ruled out by the ticket: the map must not hand the visitor to Google.
        # Driving directions (/maps/dir/) are allowed on purpose.
        for path, html in self.pages:
            self.assertNotIn("google.com/maps/search", html, path)
            self.assertNotIn("maps.google.", html, path)

    def test_a_city_only_location_is_not_linked(self):
        # A value with no venue name and no street would drop the visitor on
        # the whole city, so it stays plain text.
        for path, html in self.pages:
            for anchor in re.findall(
                    r'<a href="https://www\.openstreetmap\.org/search\?query='
                    r'([^"]*)"', html):
                query = unescape(anchor)
                self.assertNotIn("Brno%2C+Czechia", query,
                                 f"bare-city map link on {path}")


class WidgetArticleDescriptions(_Built):
    """Every `<widget-articles>` card truncates its description (issue #71):
    an unbounded paragraph runs across the whole card grid. Truncation lives
    in the template, so a regression is only visible in the built HTML.

    The template asks for 250 characters. Jinja's truncate lets a string up
    to five characters over that through untouched (its default leeway), so
    the longest legitimate paragraph is 255 characters.
    """

    LIMIT = 255
    DESCRIPTION = re.compile(
        r'<p class="widget-articles__description">(.*?)</p>', re.DOTALL)

    def descriptions(self):
        for path, html in self.pages:
            for match in self.DESCRIPTION.finditer(html):
                yield path, unescape(match.group(1))

    def test_descriptions_are_still_rendered(self):
        # Guards against the regex (or the widget itself) rotting to a
        # silent zero-match pass.
        found = sum(1 for _ in self.descriptions())
        self.assertGreater(found, 10, "widget article descriptions disappeared")

    def test_no_description_exceeds_the_limit(self):
        bad = [f"{path}: {len(text)} chars" for path, text in self.descriptions()
               if len(text) > self.LIMIT]
        self.assertEqual(bad, [], f"descriptions over {self.LIMIT} chars: {bad[:5]}")


class WidgetArticlesColumns(_Built):
    """`columns="3"` on <widget-articles> must reach the built HTML (issue #65):
    the template used to wrap the cards in .el-cluster no matter what, so the
    attribute was ignored and the last card stretched across the whole row.
    With `columns` the cards sit in .el-grid-N; without it they keep the
    organic cluster.
    """

    def test_a_columns_widget_builds_a_grid(self):
        html = dict(self.pages)["marathon-djs-team/index.html"]
        self.assertEqual(
            html.count('class="el-grid-3"'), 1,
            "columns=3 did not produce exactly one .el-grid-3 wrapper")

    def test_a_widget_without_columns_stays_a_cluster(self):
        html = dict(self.pages)["tango-pikosky/index.html"]
        self.assertNotIn("el-grid-", html,
                         "a widget without columns grew a grid wrapper")


class CzechLineBreaks(_Built):
    """A lone one-letter preposition never ends a line (issue #70).

    The Czech one-letter words — a, i, k, o, s, u, v, z — mean nothing
    alone, so plugins/czech_typography.py glues each to the word after it:
    as a Jinja filter where a title is visible text, and as a pass over
    every rendered body. What those two own is the page's content, so the
    invariant walks <main>. The chrome around it (nav rail, top-chip menu,
    footer, language switcher) renders labels from theme/i18n and
    content/navigation, which no title filter reaches — six strings live
    there today, and they are this issue's residue, not its regression.

    <head>, scripts, styles, pre and code are not visible prose and are
    skipped. Entities are decoded first, so a joined pair ("v&nbsp;Brně")
    does not count as a breakable space; an apostrophe does not start a
    word, so "it's" and "Brno's" on the English pages are not prepositions
    however their last letter reads.
    """

    NOT_PROSE = re.compile(r"<(script|style|pre|code)\b.*?</\1>",
                           re.DOTALL | re.IGNORECASE)
    MAIN = re.compile(r"<main\b.*</main>", re.DOTALL | re.IGNORECASE)
    TAG = re.compile(r"<[^>]+>")
    LONE_PREPOSITION = re.compile(r"(?<![\w'’])([aikousvzAIKOUSVZ]) (?=\S)")
    CARD_TITLE = re.compile(r'event-card__title">([^<]*)')
    BARE_AMPERSAND = re.compile(r"&(?!#\d+;|#x[0-9a-fA-F]+;|[A-Za-z][A-Za-z0-9]*;)")

    def test_no_visible_preposition_is_left_breakable(self):
        bad = []
        for path, html in self.pages:
            main = self.MAIN.search(html)
            if not main:
                continue
            prose = unescape(self.TAG.sub(
                " ", self.NOT_PROSE.sub(" ", main.group(0))))
            hit = self.LONE_PREPOSITION.search(prose)
            if hit:
                where = prose[max(0, hit.start() - 30):hit.end() + 30]
                bad.append(f"{path}: …{where.replace(chr(10), ' ')}…")
        self.assertEqual(
            bad, [],
            f"a lone preposition the browser may strand at a line end: {bad[:5]}")

    def test_no_card_title_carries_a_bare_ampersand(self):
        # The filter wraps its answer in Markup, which silences Jinja's own
        # escaping — so it has to escape a plain title itself, or "Tango &
        # Pizza" reaches the browser with a raw & and a "<" would inject
        # HTML outright. Card titles are where a plain-text title meets the
        # filter, so they are where the slip would show first.
        found = 0
        bad = []
        for path, html in self.pages:
            for match in self.CARD_TITLE.finditer(html):
                found += 1
                if self.BARE_AMPERSAND.search(match.group(1)):
                    bad.append(f"{path}: {match.group(1)}")
        self.assertGreater(found, 10, "event card titles disappeared")
        self.assertEqual(bad, [], f"bare & in an event-card__title: {bad[:5]}")

    def test_the_join_is_actually_in_the_build(self):
        # An invariant that matches nothing passes trivially, so the fix has
        # to show up too: the whole site is full of these, Czech being Czech.
        joined = sum(html.count("&nbsp;") for _path, html in self.pages)
        self.assertGreater(joined, 100, "the &nbsp; join vanished from the build")


class HomepageMetaDescription(_Built):
    """The homepage meta description is the snippet Google is supposed to
    show — and the old one it refused to use (issue #84). "Přehledně a
    aktuálně o argentinském tangu v Brně" said nothing about what the page
    actually leads with, so Google stitched its own snippet out of the intro
    paragraph and the first event card's price. The rewrite names it: milongas
    this week, the nearest lessons and workshops.

    What the build has to guarantee is that index.html carries the front
    matter's `description:` verbatim, exactly once. The source of truth stays
    content/pages/index.md, read here rather than restated, so the written
    copy and the served tag cannot drift apart silently.
    """

    SOURCE = os.path.join(REPO_ROOT, "content", "pages", "index.md")
    META = re.compile(r'<meta name="description" content="([^"]*)">')

    def front_matter_description(self):
        with open(self.SOURCE, encoding="utf-8") as handle:
            line = next(l for l in handle if l.startswith("description:"))
        return line[len("description:"):].strip()

    def test_the_homepage_carries_exactly_one_meta_description(self):
        found = self.META.findall(dict(self.pages)["index.html"])
        self.assertEqual(
            len(found), 1,
            f"expected one meta description tag, found {len(found)}")

    def test_it_is_the_front_matter_description_verbatim(self):
        found = self.META.findall(dict(self.pages)["index.html"])
        self.assertEqual(found, [self.front_matter_description()])


class Feed(_Built):
    """The feed is the only machine-readable answer to "what is new here".

    Anything echoing this site downstream reads it, so a feed that is missing,
    unparseable, or pointing at pages that are not in the build is worse than
    no feed: the failure happens on someone else's server.

    Parsed with the standard library on purpose. The input is the build this
    test just produced from the repo, not anything a stranger can send, and the
    suite deliberately needs nothing beyond the standard library.
    """

    def test_the_feed_exists_and_is_linked_from_every_page(self):
        self.assertTrue(os.path.isfile(
            os.path.join(self.output, "feeds", "all.atom.xml")))
        for path, html in self.pages:
            self.assertIn('type="application/atom+xml"', html, f"no feed link on {path}")

    def test_the_feed_parses_and_its_links_resolve(self):
        import xml.etree.ElementTree as ElementTree
        atom = "{http://www.w3.org/2005/Atom}"
        root = ElementTree.parse(
            os.path.join(self.output, "feeds", "all.atom.xml")).getroot()
        entries = root.findall(f"{atom}entry")
        self.assertGreater(len(entries), 5)
        for entry in entries:
            href = entry.find(f"{atom}link").get("href")
            relative = href.replace("https://brnosaires.com/", "").strip("/")
            self.assertTrue(
                os.path.isfile(os.path.join(self.output, relative, "index.html")),
                f"feed links to a page that is not in the build: {href}")

    def test_the_feed_carries_no_translated_twins(self):
        # i18n_fallback synthesizes an /en/ clone of every article, and Pelican
        # folds translations into the ALL feed regardless of
        # TRANSLATION_FEED_ATOM. Without plugins/feed_one_language.py half the
        # entries were the same article twice, which downstream reads as two
        # separate announcements.
        import xml.etree.ElementTree as ElementTree
        atom = "{http://www.w3.org/2005/Atom}"
        root = ElementTree.parse(
            os.path.join(self.output, "feeds", "all.atom.xml")).getroot()
        translated = [entry.find(f"{atom}link").get("href")
                      for entry in root.findall(f"{atom}entry")
                      if "/en/" in entry.find(f"{atom}link").get("href")]
        self.assertEqual(translated, [], "translated twins in the feed")


class MarathonNavSourceCarriesStudents(unittest.TestCase):
    """content/navigation/marathon.md is the single source of the marathon
    sub-site nav (read by plugins/nav_from_docs.py). Issue #107: a Students
    line, pointing at the existing marathon-students page, has to land
    exactly once, unhighlighted, immediately before Registration — without
    disturbing any of the other eight lines already there. Every one of
    those is a property of the *file*, so it is cheaper and more precise to
    check here than after a full Pelican build.
    """

    MARATHON_NAV_PATH = os.path.join(REPO_ROOT, "content", "navigation", "marathon.md")

    SLUG = "marathon-students"
    LABEL = "Students"
    NAV_LINES_AFTER = 9
    STUDENTS_INDEX = 7
    REGISTRATION_INDEX = 8

    # The 8 labels the nav carries today, in order, with Students filtered
    # out — i.e. what must still be there, unmoved, once Students lands.
    EXISTING_LABELS_IN_ORDER = [
        "Home", "DJs", "Venue", "Gallery", "Schedule", "Travel", "City",
        "Registration",
    ]

    @classmethod
    def setUpClass(cls):
        with open(cls.MARATHON_NAV_PATH, encoding="utf-8") as handle:
            raw_lines = [line.strip() for line in handle if line.strip()
                        and not line.lstrip().startswith("#")]
        cls.fields = [[field.strip() for field in line.split(",")]
                     for line in raw_lines]
        cls.labels = [f[0] for f in cls.fields if f and f[0]]
        cls.targets = [f[1] if len(f) > 1 else None for f in cls.fields]

    def _students_line(self):
        matches = [f for f in self.fields if len(f) > 1 and f[1] == self.SLUG]
        self.assertEqual(
            len(matches), 1,
            f"expected exactly one line targeting {self.SLUG!r}, found "
            f"{len(matches)}: {self.fields}")
        return matches[0]

    def test_the_file_has_nine_non_empty_lines(self):
        self.assertEqual(
            len(self.fields), self.NAV_LINES_AFTER,
            f"expected {self.NAV_LINES_AFTER} nav lines, found "
            f"{len(self.fields)}: {self.labels}")

    def test_marathon_students_is_declared_exactly_once(self):
        count = self.targets.count(self.SLUG)
        self.assertEqual(
            count, 1,
            f"expected exactly one line targeting {self.SLUG!r}, found "
            f"{count}: {self.fields}")

    def test_its_label_is_exactly_students(self):
        self.assertEqual(self._students_line()[0], self.LABEL)

    def test_it_declares_no_primary_flag_or_icon(self):
        # Exactly label + target — a 3rd or 4th field would be `primary`
        # and/or an icon, which would highlight it like DJs/Venue/Registration.
        line = self._students_line()
        self.assertEqual(
            len(line), 2,
            f"expected exactly 2 fields (label, target), got {line}")

    def test_it_stands_immediately_before_registration(self):
        self.assertIn(self.LABEL, self.labels,
                      f"no {self.LABEL} line in the nav yet: {self.labels}")
        self.assertIn("Registration", self.labels, self.labels)
        students_at = self.labels.index(self.LABEL)
        registration_at = self.labels.index("Registration")
        self.assertEqual(
            students_at, self.STUDENTS_INDEX,
            f"Students at index {students_at}, expected "
            f"{self.STUDENTS_INDEX}: {self.labels}")
        self.assertEqual(
            registration_at, self.REGISTRATION_INDEX,
            f"Registration at index {registration_at}, expected "
            f"{self.REGISTRATION_INDEX}: {self.labels}")
        self.assertEqual(
            registration_at, students_at + 1,
            f"Students and Registration are not adjacent: {self.labels}")

    def test_the_other_eight_labels_and_their_order_are_unchanged(self):
        self.assertIn(self.LABEL, self.labels,
                      f"no {self.LABEL} line in the nav yet: {self.labels}")
        others = [label for label in self.labels if label != self.LABEL]
        self.assertEqual(others, self.EXISTING_LABELS_IN_ORDER)


# The 8 marathon pages that must each carry the Students nav chip — the
# homepage's own inline price-block link (content/pages/marathon/index.md:101,
# "[Details](/marathon-students/)") is a *different* route to the same page
# and does not satisfy this: the contract is the nav, on every marathon page.
MARATHON_PAGES_WITH_NAV = {
    "Home": "marathon/index.html",
    "DJs": "marathon-djs-team/index.html",
    "Venue": "marathon-venue/index.html",
    "Gallery": "marathon-gallery/index.html",
    "Schedule": "marathon-schedule/index.html",
    "Travel": "marathon-getting-to-brno/index.html",
    "City": "marathon-stay-in-brno/index.html",
    "Students": "marathon-students/index.html",
}

# The exact anchor theme/templates/components/navigation.html emits for a
# resolved, internal (non-external) nav_from_docs item with no `primary`
# flag and no icon — byte-for-byte the same shape as the Gallery/Schedule/
# Travel/City chips already in the nav today. nav_page.url comes straight
# from Pelican's own page.url (PAGE_URL = "{slug}/") with no leading slash;
# the theme relies on <base href="https://brnosaires.com/"> in <head> to
# resolve it, the same as every other internal nav link on the site.
MARATHON_STUDENTS_NAV_ANCHOR = (
    '<a href="marathon-students/" class="aesthetic-chip chip-m">Students</a>')

STUDENTS_ANCHOR_HREF = re.compile(
    r'<a href="([^"]+)" class="aesthetic-chip chip-m">Students</a>')


class MarathonNavStudentsLink(_Built):
    """The Students nav item (issue #107) has to actually appear in the
    built HTML of every marathon page — not just be declared in the source —
    and it has to point at a page that really exists in the build.
    """

    def test_it_renders_in_the_nav_of_every_marathon_page(self):
        by_path = dict(self.pages)
        for label, relpath in MARATHON_PAGES_WITH_NAV.items():
            with self.subTest(page=relpath):
                html = by_path.get(relpath)
                self.assertIsNotNone(html, f"{relpath} was not built")
                # assertTrue, not assertIn: assertIn's failure message dumps
                # the whole (multi-KB) page HTML, which drowns the signal.
                self.assertTrue(
                    MARATHON_STUDENTS_NAV_ANCHOR in html,
                    f"Students nav chip missing from the {label} page "
                    f"({relpath})")

    def test_the_rendered_link_target_is_not_a_404(self):
        html = dict(self.pages)["marathon/index.html"]
        match = STUDENTS_ANCHOR_HREF.search(html)
        self.assertIsNotNone(
            match, "no Students nav chip on the marathon homepage — cannot "
                   "check where it points")
        target_dir = match.group(1).strip("/")
        self.assertTrue(
            os.path.isfile(os.path.join(self.output, target_dir, "index.html")),
            f"Students nav link href={match.group(1)!r} does not resolve "
            f"to a built page")


if __name__ == "__main__":
    unittest.main()
