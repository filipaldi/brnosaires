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
SAMPLE_PEOPLE = {"filip-paldia": "Filip Paldia",
                 "lenka-platenikova": "Lenka Pláteníková"}

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
                    "event-location: Taneční studio Stolárna, Olomoucká 14, Brno\n"
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
            "Filip Paldia a Lenka Pláteníková")

    def test_the_english_header_joins_the_profile_titles_with_and(self):
        self.assertEqual(
            instructor_names(read(self.output, "en", SAMPLE_PAGE), "en"),
            "Filip Paldia and Lenka Pláteníková")


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
                         list(SAMPLE_PEOPLE.values()), f"performer: {performer}")

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
                self.assertIn("Ondra Martinák", names)
                self.assertIn("Pavla Lužná", names)


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

    @classmethod
    def setUpClass(cls):
        cls.output = build_site()

    def test_every_event_mirror_names_its_teachers_instead_of_their_slugs(self):
        bad, checked = [], 0
        for path, block in markdown_files():
            if not path.startswith("content/events") or path.endswith(".en.md"):
                continue
            expected = slugs(block)
            if not expected:
                continue
            slug = fields(block).get("slug", [""])[0]
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


if __name__ == "__main__":
    unittest.main()
