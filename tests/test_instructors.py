"""One field for the people teaching an event, not two (issue #75).

Until now an event carried both `instructor:` (free text, what the header
printed) and `instructor_slugs:` (a relation into `content/people/`, what put
the event on the lecturer's page). Nothing kept the two in step, and five files
disagreed with themselves. The free text goes; the header is rendered from the
profiles the slugs point at, joined by a conjunction that lives in the i18n
tables; an unknown slug stops being a warning and stops the build.

These tests are the contract. They read the repo's front matter directly (the
CMS writes it and Pelican reads it, so it is the real interface) and the built
site (the header and the structured data only exist there).
"""
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from html import unescape
from urllib.parse import urlsplit

# Pelican's own slug rule, not a copy of it: `source_slug` below has to give
# a slugless file the same address the build gives it, and the two drifting
# apart is precisely the failure it exists to stop.
from pelican.settings import DEFAULT_CONFIG
from pelican.utils import slugify

from tests import BUILD_CLOCK, REPO_ROOT, build_site, plugin_path  # noqa: F401
# The fence parser is shared rather than copied: if the front-matter convention
# ever moves, both suites move with it instead of one quietly going blind.
from tests.test_front_matter import front_matter

import people_links
from theme.i18n import cs as i18n_cs, en as i18n_en

KEY_LINE = re.compile(r"^([A-Za-z_][\w-]*):\s?(.*)$")

CMS_CONFIG = os.path.join(REPO_ROOT, "content", "extra", "admin", "config.yml")
PEOPLE_DIR = os.path.join(REPO_ROOT, "content", "people")

# The three July workshops taught by Ondra and Pavla whose `instructor_slugs:`
# named only Pavla.
JULY_WORKSHOPS = (
    "content/events/2026/07/2026-07-21-letni-workshopy-zacatecnici.md",
    "content/events/2026/07/2026-07-22-letni-workshopy-zacatecnici.md",
    "content/events/2026/07/2026-07-23-letni-workshopy-zacatecnici.md",
)
JULY_PAGES = (
    "letni-intenzivni-workshopy-zacatecnici-07-utery",
    "letni-intenzivni-workshopy-zacatecnici-07-streda",
    "letni-intenzivni-workshopy-zacatecnici-07-ctvrtek",
)

# The two guest teachers who have an event but no profile yet.
GUEST_EVENTS = (
    "content/events/2026/09/workshopy-s-rodrigo-a-majo.md",
    "content/events/2026/09/workshopy-s-rodrigo-a-majo.en.md",
)

# One event with two instructors, in both languages. Its `instructor_slugs:`
# already names both people, so the only thing that changes about it is where
# the header gets the names from.
SAMPLE_PAGE = "letni-intenzivni-workshopy-tango3-08-utery"
# Slugs, never names. A name belongs to the person it names and they rename
# themselves: `ondra-martinak` became "Ondřej" in the CMS and three tests went
# red over a spelling nobody in this repository gets to decide, with the whole
# deploy behind them. What the site owes a teacher is that the header, the
# JSON-LD and the LLM mirror all say whatever their profile says — so every
# name this file expects is read back out of `content/people/`, and the only
# words typed here are the ones the theme owns.
SAMPLE_PEOPLE = ("filip-paldia", "lenka-platenikova")

# `event_instructor_label` in theme/i18n/{cs,en}.py — the <dt> the names sit under.
INSTRUCTOR_LABEL = {"cs": "Lektoři", "en": "Teachers"}


def markdown_files():
    """(repo-relative path, front-matter lines) for every .md under content/."""
    for root, _dirs, files in os.walk(os.path.join(REPO_ROOT, "content")):
        for name in sorted(files):
            if not name.endswith(".md"):
                continue
            full = os.path.join(root, name)
            with open(full, encoding="utf-8", errors="replace") as handle:
                lines = handle.read().split("\n")
            yield os.path.relpath(full, REPO_ROOT), front_matter(lines) or []


def fields(block):
    """{key: [value, continuation, ...]} for one front-matter block.

    Multi-line metadata (an indented line under a key) is how `instructor:`
    spelled a second teacher, so continuations belong to the key above them.
    """
    parsed, current = {}, None
    for line in block:
        match = KEY_LINE.match(line)
        if match:
            current = match.group(1)
            parsed.setdefault(current, []).append(match.group(2).strip())
        elif current and line.strip():
            parsed[current].append(line.strip())
    return parsed


def slugs(block):
    """The `instructor_slugs:` of a front-matter block, read the way the build reads it.

    Deliberately routed through the plugin's own parser: a spelling the test
    accepts but `people_links` cannot read would be a green test over a broken
    page.
    """
    values = fields(block).get("instructor_slugs")
    if not values:
        return []
    raw = values[0] if len(values) == 1 else values
    return people_links._instructor_slugs(
        type("C", (), {"metadata": {"instructor_slugs": raw}}))


def profile_exists(slug):
    return os.path.isfile(os.path.join(PEOPLE_DIR, f"{slug}.md"))


def plain(fragment):
    """HTML fragment as the text a reader sees.

    Tags go (the names may or may not end up linked to their profiles — #75
    does not say, and either is a correct header), entities are resolved, and
    a non-breaking space counts as a space: Czech typography puts one after a
    one-letter conjunction, and that is a rendering detail, not a difference
    in the names.
    """
    text = unescape(re.sub(r"<[^>]+>", " ", fragment))
    return " ".join(text.replace("\u00a0", " ").split())


def read(output, *parts):
    with open(os.path.join(output, *parts, "index.html"), encoding="utf-8") as handle:
        return handle.read()


def instructor_names(html, lang):
    """The rendered text of the header's instructor row, or None if absent."""
    match = re.search(r"<dt>\s*" + re.escape(INSTRUCTOR_LABEL[lang])
                      + r"\s*</dt>\s*<dd>(.*?)</dd>", html, re.DOTALL)
    return None if match is None else plain(match.group(1))


def event_ld(html):
    """The page's Event JSON-LD block (a page also carries an Organization one)."""
    for block in re.findall(r'<script type="application/ld\+json">(.*?)</script>',
                            html, re.DOTALL):
        data = json.loads(block)
        if data.get("@type") == "Event":
            return data
    raise AssertionError("no Event JSON-LD on the page")


# In an LLM mirror these three can hold a person's name without a teacher
# being named at all — an organiser is sometimes a person, and matching one of
# them would pass the teacher check on the strength of somebody else's name.
MIRROR_NON_TEACHER_KEYS = ("title", "url", "event-organiser")


def profile_title(slug):
    """The `title:` of `content/people/<slug>.md` — the name a reader sees."""
    with open(os.path.join(PEOPLE_DIR, f"{slug}.md"), encoding="utf-8") as handle:
        block = front_matter(handle.read().split("\n")) or []
    return fields(block).get("title", [""])[0]


def joined(people, conjunction):
    """The profile titles as one line, the way the site joins them.

    `people_links.instructor_names` and article.html's instructor row both
    write this sentence; the comma rule ("X, Y a Z") is theirs and repeated
    here on purpose, so a change to the join has to be made in the test too.
    The conjunction is passed in rather than read from theme/i18n: which word
    sits in which table is `Conjunction`'s business, and a test that took the
    word from the same table the page did would agree with any word at all.
    """
    names = [profile_title(slug) for slug in people]
    if len(names) < 2:
        return names[0] if names else ""
    return f"{', '.join(names[:-1])} {conjunction} {names[-1]}"


def source_slug(path, block):
    """The address Pelican gives a source file, with or without `slug:`.

    Reading a missing `slug:` as `""` pointed every slugless entry at
    `output/index.md` — the homepage mirror, a file that exists, so nothing
    failed until an assertion about its contents did and blamed the events.
    Since the CMS stopped writing the field (#97) most new entries carry none,
    which is exactly when the test has to know the rule instead of the value:
    `SLUGIFY_SOURCE = "basename"`, borrowed from Pelican rather than retyped.
    """
    explicit = fields(block).get("slug")
    if explicit and explicit[0]:
        return explicit[0]
    stem = os.path.splitext(os.path.basename(path))[0]
    return slugify(stem, regex_subs=DEFAULT_CONFIG["SLUG_REGEX_SUBSTITUTIONS"])


def mirror_front_matter(text):
    """The fenced block `llm_ally` writes at the top of `<slug>/index.md`.

    Not the shared parser: a mirror opens with the llms.txt marker line, so
    the fence is not the first line of the file.
    """
    lines = text.split("\n")
    try:
        start = lines.index("---")
        end = lines.index("---", start + 1)
    except ValueError:
        return None
    return lines[start + 1:end]


def teacher_text(block):
    """The mirror front-matter lines in which a teacher could legitimately be named."""
    return "\n".join(line for line in block
                     if not any(line.startswith(f"{key}:")
                                for key in MIRROR_NON_TEACHER_KEYS))


THEME_TEMPLATES = os.path.join(REPO_ROOT, "theme", "templates")


def instructor_row_template():
    """The `<dd>` Jinja source of the header's instructor row, read from the theme.

    Rendered as it is written rather than reimplemented here: a copy of the
    join living in the test would agree with itself forever, which is the one
    thing this comparison must not do.
    """
    found = []
    for root, _dirs, files in os.walk(THEME_TEMPLATES):
        for name in sorted(files):
            if not name.endswith(".html"):
                continue
            with open(os.path.join(root, name), encoding="utf-8") as handle:
                for line in handle:
                    if "event_instructor_and" in line and "<dd>" in line:
                        found.append(os.path.join(root, name) + ": " + line)
    if len(found) != 1:
        raise AssertionError(
            "expected exactly one <dd> instructor row under theme/templates, "
            f"found {len(found)}. If the row moved, move this anchor with it.")
    line = found[0]
    return line[line.index("<dd>"):line.index("</dd>") + len("</dd>")]


def stripped(markup):
    """Rendered markup as the plain text it stands for, separators intact.

    Not `plain()`: that one leaves a space where a tag was, which is right
    when comparing a name but turns `</a>, <a>` into ` , ` — and the
    separators are exactly what this comparison is about.
    """
    return unescape(re.sub(r"<[^>]+>", "", markup)).replace("\u00a0", " ")


class FreeText(unittest.TestCase):
    """G1 — `instructor:` exists nowhere any more, in the content or in the CMS."""

    def test_no_content_file_carries_an_instructor_field(self):
        bad = [path for path, block in markdown_files() if "instructor" in fields(block)]
        self.assertEqual(bad, [], f"instructor: still in front matter: {bad[:5]}")

    def test_the_cms_config_offers_no_instructor_field(self):
        with open(CMS_CONFIG, encoding="utf-8") as handle:
            lines = handle.read().split("\n")
        bad = [f"config.yml:{number}" for number, line in enumerate(lines, start=1)
               if re.match(r"^\s*-\s*name:\s*instructor\s*$", line)]
        self.assertEqual(bad, [], f"instructor field still declared: {bad}")
        # The relation field is the one that survives; deleting the wrong half
        # would leave the CMS unable to name a teacher at all.
        self.assertTrue(any(re.match(r"^\s*-\s*name:\s*instructor_slugs\s*$", line)
                            for line in lines),
                        "instructor_slugs is gone from the CMS config")


class SlugsResolve(unittest.TestCase):
    """G2 — a slug is a promise that a profile exists."""

    def test_every_instructor_slug_names_an_existing_profile(self):
        bad = [f"{path} -> {slug}"
               for path, block in markdown_files()
               for slug in slugs(block) if not profile_exists(slug)]
        self.assertEqual(bad, [], f"slugs with no profile: {bad[:5]}")

    def test_the_two_guest_teachers_are_named_by_slug_like_everyone_else(self):
        # These two events named their teachers only in free text, so they are
        # the pair that vanishes from the header unless profiles are created
        # first. The slugs are not spelled out here: what matters is that there
        # are two of them and that both resolve.
        for path in GUEST_EVENTS:
            with self.subTest(path):
                with open(os.path.join(REPO_ROOT, path), encoding="utf-8") as handle:
                    block = front_matter(handle.read().split("\n")) or []
                found = slugs(block)
                self.assertEqual(len(found), 2,
                                 f"{path}: expected two instructor slugs, got {found}")
                for slug in found:
                    self.assertTrue(profile_exists(slug),
                                    f"{path}: no content/people/{slug}.md")


class UnknownSlug(unittest.TestCase):
    """G3 — an unknown slug stops the build instead of scrolling past in a warning.

    End-to-end on purpose: "the build fails" is a statement about the exit
    code, not about which function raises, and pinning the latter would pin an
    implementation the ticket does not prescribe.
    """

    # No hyphen: the build log is rendered in a narrow column and wraps, and a
    # hyphen is a place it may break the slug across two lines.
    BOGUS = "neexistujicilektor"

    def test_an_unknown_slug_fails_the_build(self):
        try:
            import pelican  # noqa: F401
        except ImportError:
            raise unittest.SkipTest("pelican not installed")

        workspace = tempfile.mkdtemp(prefix="brnosaires-badslug-")
        try:
            content = os.path.join(workspace, "content")
            shutil.copytree(os.path.join(REPO_ROOT, "content"), content)
            with open(os.path.join(content, "events", "2026", "09",
                                   "zzz-unknown-lector.md"),
                      "w", encoding="utf-8") as handle:
                handle.write(
                    "---\n"
                    "title: Akce s neznámým lektorem\n"
                    "slug: zzz-unknown-lector\n"
                    "date: 2026-09-01 10:00:00\n"
                    f"instructor_slugs: {self.BOGUS}\n"
                    "event-start: 2026-09-10 19:00:00\n"
                    "event-type: workshop\n"
                    "event-venue: Taneční studio Stolárna\n"
                    "event-street: Olomoucká 14\n"
                    "event-locality: Brno\n"
                    "---\n\n# Akce s neznámým lektorem\n\nTělo.\n")
            result = subprocess.run(
                [sys.executable, "-m", "pelican", content,
                 "-s", "publishconf.py", "-o", os.path.join(workspace, "out")],
                cwd=REPO_ROOT, capture_output=True, text=True,
                env=dict(os.environ, PYTHONPATH=REPO_ROOT,
                         BRNOSAIRES_NOW=BUILD_CLOCK))
        finally:
            shutil.rmtree(workspace, ignore_errors=True)

        log = "".join((result.stdout + result.stderr).split())
        # Named first: if the copy were incomplete the build would also fail,
        # and this is what tells the two apart.
        self.assertIn(self.BOGUS, log,
                      "the build never mentioned the unknown slug")
        self.assertNotEqual(result.returncode, 0,
                            "an unknown instructor slug still only warns")


class Conjunction(unittest.TestCase):
    """G4 — the word between two names is a UI string, not content.

    That is the whole reason `instructor:` needed `i18n: true`: the Czech file
    said "Filip a Lenka" and the English one "Filip and Lenka". With the
    conjunction in the string tables the data is language-free.
    """

    @staticmethod
    def normalised(table):
        return {key: " ".join(str(value).replace("\u00a0", " ").split())
                for key, value in table.items()}

    def test_one_i18n_key_holds_a_in_czech_and_and_in_english(self):
        czech = self.normalised(i18n_cs.STRINGS)
        english = self.normalised(i18n_en.STRINGS)
        keys = {key for key, value in czech.items() if value == "a"} & \
               {key for key, value in english.items() if value == "and"}
        self.assertTrue(
            keys,
            "no key in theme/i18n/{cs,en}.py holds the conjunction "
            "(expected one key whose Czech value is 'a' and English 'and')")


class Header(unittest.TestCase):
    """G4 — the header prints the title from each profile, joined by that word."""

    @classmethod
    def setUpClass(cls):
        cls.output = build_site()

    def test_the_czech_header_joins_the_profile_titles_with_a(self):
        self.assertEqual(
            instructor_names(read(self.output, SAMPLE_PAGE), "cs"),
            joined(SAMPLE_PEOPLE, "a"))

    def test_the_english_header_joins_the_profile_titles_with_and(self):
        self.assertEqual(
            instructor_names(read(self.output, "en", SAMPLE_PAGE), "en"),
            joined(SAMPLE_PEOPLE, "and"))


class StructuredData(unittest.TestCase):
    """G5 — one `Person` per human, each linked to their own page.

    Today the free text produces a single Person called "Filip a Lenka": a
    search engine is told two teachers are one person with an odd name, and is
    given nowhere to go to find out more.
    """

    @classmethod
    def setUpClass(cls):
        cls.output = build_site()

    def test_performer_holds_one_person_per_instructor(self):
        performer = event_ld(read(self.output, SAMPLE_PAGE)).get("performer")
        self.assertIsInstance(performer, list)
        self.assertEqual([entry.get("@type") for entry in performer],
                         ["Person", "Person"], f"performer: {performer}")
        self.assertEqual([entry.get("name") for entry in performer],
                         [profile_title(slug) for slug in SAMPLE_PEOPLE],
                         f"performer: {performer}")

    def test_each_performer_links_to_that_person_s_profile(self):
        performer = event_ld(read(self.output, SAMPLE_PAGE)).get("performer") or []
        urls = [entry.get("url") for entry in performer]
        self.assertEqual(len(urls), len(SAMPLE_PEOPLE), f"performer: {performer}")
        for slug, url in zip(SAMPLE_PEOPLE, urls):
            with self.subTest(slug):
                self.assertIsNotNone(url, f"no url on the Person for {slug}")
                self.assertTrue(url.startswith("https://"),
                                f"performer url is not absolute: {url}")
                self.assertEqual(urlsplit(url).path.strip("/"), slug,
                                 f"performer url does not point at {slug}: {url}")
                self.assertTrue(
                    os.path.isfile(os.path.join(self.output, slug, "index.html")),
                    f"the profile {url} points at was not built")


class OndraMartinak(unittest.TestCase):
    """G6 — the teacher the free text named and the slugs forgot.

    `instructor: Ondra a Pavla` with `instructor_slugs: pavla-luzna` is the
    contradiction that made #75 worth doing: deleting the free text without
    adding him would delete him from the site.
    """

    @classmethod
    def setUpClass(cls):
        cls.output = build_site()

    def test_the_three_july_workshops_list_ondra_alongside_pavla(self):
        for path in JULY_WORKSHOPS:
            with self.subTest(path):
                with open(os.path.join(REPO_ROOT, path), encoding="utf-8") as handle:
                    block = front_matter(handle.read().split("\n")) or []
                self.assertEqual(set(slugs(block)),
                                 {"ondra-martinak", "pavla-luzna"})

    def test_the_three_july_workshop_pages_name_both_teachers(self):
        for slug in JULY_PAGES:
            with self.subTest(slug):
                names = instructor_names(read(self.output, slug), "cs")
                self.assertIsNotNone(names, f"{slug}: no instructor row in the header")
                self.assertIn(profile_title("ondra-martinak"), names)
                self.assertIn(profile_title("pavla-luzna"), names)


class LlmMirror(unittest.TestCase):
    """G12 — the copy an LLM reads names the teachers, the way the page does.

    `plugins/llm_ally.py` writes an LLM-readable mirror of every article to
    `output/<slug>/index.md`, copying a chosen list of front-matter fields
    into it. That list named the field this ticket deleted, so every event's
    mirror quietly lost its teachers: the build stayed green, the suite stayed
    green, and nothing in `tests/` looked at that plugin at all.

    Names rather than slugs, because a slug in this corpus resolves to
    nothing: every profile in `content/people/` carries `llm_mirror: false`,
    so `output/filip-paldia/index.md` and its siblings are never written. Only
    the marathon DJs are mirrored. A name needs no lookup.
    """

    # 18 Czech event files carry instructor slugs (the `.en.md` twins get no
    # mirror of their own — the plugin writes one file per Czech article). The
    # floor is below that so ordinary content edits do not trip it, and high
    # enough that a broken source-to-mirror mapping cannot pass by checking
    # almost nothing.
    MINIMUM_CHECKED = 15

    # The sweep below asks only whether each name is somewhere in the front
    # matter and each slug is not. That is too little to be a guard: it cannot
    # tell the real line from "Filip PaldiaLenka Pláteníková" with no
    # separator, from an English conjunction on a Czech page, from a slash
    # standing in for the i18n lookup, or from the right value written under
    # `series:`. The whole line pins the key, the conjunction, the spacing and
    # the quoting together, and no rewriting of the join survives it.
    EXACT_LINES = {
        # Two teachers, and the case every mutation above was built from.
        "letni-intenzivni-workshopy-tango3-08-utery":
            ("filip-paldia", "lenka-platenikova"),
        # One teacher: the branch that must not reach for a conjunction at all.
        "femme-fatale-tango-03-2026": ("steky-yaku",),
    }

    @classmethod
    def setUpClass(cls):
        cls.output = build_site()

    def test_known_event_mirrors_pin_their_instructor_line_exactly(self):
        for slug, people in self.EXACT_LINES.items():
            expected = f'instructor: "{joined(people, "a")}"'
            with self.subTest(slug):
                path = os.path.join(self.output, slug, "index.md")
                self.assertTrue(os.path.isfile(path), f"no LLM mirror at {slug}/index.md")
                with open(path, encoding="utf-8") as handle:
                    front = mirror_front_matter(handle.read())
                self.assertIsNotNone(front, f"{slug}/index.md carries no front matter")
                # A list, not a lookup: two instructor lines — a leftover
                # `instructor_slugs:` beside the new one — is also a failure.
                self.assertEqual([line for line in front
                                  if line.startswith("instructor")], [expected])

    def test_every_event_mirror_names_its_teachers_instead_of_their_slugs(self):
        bad, checked = [], 0
        for path, block in markdown_files():
            if not path.startswith("content/events") or path.endswith(".en.md"):
                continue
            expected = slugs(block)
            if not expected:
                continue
            slug = source_slug(path, block)
            mirror = os.path.join(self.output, slug, "index.md")
            self.assertTrue(os.path.isfile(mirror),
                            f"{path}: no LLM mirror at {slug}/index.md")
            with open(mirror, encoding="utf-8") as handle:
                front = mirror_front_matter(handle.read())
            self.assertIsNotNone(front, f"{slug}/index.md carries no front matter")
            text = teacher_text(front)
            checked += 1
            for person in expected:
                if not profile_exists(person):
                    bad.append(f"{slug}: no profile for {person!r} to take a name from")
                    continue
                name = profile_title(person)
                if name not in text:
                    bad.append(f"{slug}: does not name {name!r}")
                if person in text:
                    bad.append(f"{slug}: still emits the slug {person!r}")
        self.assertGreaterEqual(
            checked, self.MINIMUM_CHECKED,
            f"only {checked} mirrors were checked; the mapping from source to "
            f"mirror is broken and this test is guarding nothing")
        self.assertEqual(bad, [], f"mirrors not naming their teachers: {bad[:6]}")


class JoinAgreement(unittest.TestCase):
    """The comma-and-conjunction rule is written twice, and has to stay one rule.

    `people_links.instructor_names()` joins the teachers into plain prose for
    the LLM mirror. `article.html`'s instructor row joins the same people with
    each name wrapped in a link to their profile. Neither can borrow the
    other: a plugin returning markup would be a template, and a template
    taking a finished string apart again to link its pieces would be worse. So
    the rule is duplicated deliberately, and this is what stops the two copies
    drifting — a comma added to one and not the other is a silent difference
    between what a reader sees and what an LLM is told.

    Unlike the rest of this file, it was green the day it was written: it pins
    an agreement that already holds rather than describing work still to do.
    """

    LANGS = ("cs", "en")
    # Real profiles, so the fixture is three names the site actually renders.
    # Three is one more than any event has, which is the point: the "X, Y a Z"
    # branch exists in both copies and nothing in the content reaches it.
    FIXTURE_SLUGS = ("filip-paldia", "lenka-platenikova", "ondra-martinak")

    def people(self, count):
        return [type("Person", (), {"name": profile_title(slug), "url": f"{slug}/"})
                for slug in self.FIXTURE_SLUGS[:count]]

    def test_the_template_and_the_plugin_join_the_same_names_the_same_way(self):
        try:
            import jinja2
        except ImportError:
            raise unittest.SkipTest("jinja2 not installed")

        tables = {"cs": i18n_cs.STRINGS, "en": i18n_en.STRINGS}
        # `JINJA_ENVIRONMENT` in pelicanconf.py, and the `t` filter it installs
        # including its fallback to Czech: the row has to render here the way
        # it renders in the build, autoescaping and all.
        environment = jinja2.Environment(extensions=["jinja2.ext.do"])
        environment.filters["t"] = lambda key, lang: (
            tables.get(lang, tables["cs"]).get(key, tables["cs"].get(key, key)))
        row = environment.from_string(instructor_row_template())

        for lang in self.LANGS:
            for count in range(len(self.FIXTURE_SLUGS) + 1):
                with self.subTest(lang=lang, names=count):
                    people = self.people(count)
                    rendered = stripped(row.render(
                        instructors=people, page_lang=lang,
                        SITEURL="https://brnosaires.com"))
                    self.assertEqual(
                        rendered, people_links.instructor_names(people, lang),
                        "the header and the LLM mirror join these names differently")


if __name__ == "__main__":
    unittest.main()
