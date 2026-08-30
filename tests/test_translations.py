"""The English twin of a Czech file, and the address the two have to share.

Pelican pairs translations by slug and by nothing else: same slug, different
`lang:`, one set of translations (`plugins/i18n_fallback.py` explains the rest
of that machinery). Both halves of a pair used to say the slug out loud,
because the CMS wrote `slug:` into everything it saved. Since it stopped (#97)
they agree about nothing: Pelican slugifies the basename, the English half
keeps its `.en` inside that basename, and `kurz-tango-1.en.md` becomes
`kurz-tango-1en` — a different article, in a different language, about the
same evening.

    /kurz-tango-1/        the Czech text
    /en/kurz-tango-1/     the Czech text again, cloned by i18n_fallback
    /en/kurz-tango-1en/   the English text, at an address nothing links to

Nothing fails while that happens. The English page is written, it is simply
unreachable; the Czech one is served in its place under a URL that promises
English; and `calendars/*.ics` points at `/kurz-tango-1en/`, which was never
written at all. That last one is the only symptom the suite ever saw, three
days after the cause.
"""
import os
import unittest
from html import unescape

from pelican.settings import DEFAULT_CONFIG
from pelican.utils import slugify

from tests import REPO_ROOT, build_site, plugin_path  # noqa: F401

import i18n_fallback

CONTENT = os.path.join(REPO_ROOT, "content")

# Rendered from content/navigation/ by nav_from_docs; the folder is in neither
# ARTICLE_PATHS nor PAGE_PATHS, so its files are read and never written.
UNRENDERED = ("navigation",)


def front_matter_lines(path):
    with open(os.path.join(REPO_ROOT, path), encoding="utf-8") as handle:
        lines = handle.read().split("\n")
    if not lines or lines[0].strip() != "---":
        return lines[:40]
    end = lines.index("---", 1) if "---" in lines[1:] else len(lines)
    return lines[1:end]


def field(path, name):
    for line in front_matter_lines(path):
        if line.startswith(f"{name}:"):
            return line.split(":", 1)[1].strip()
    return None


def derived_slug(path):
    """What Pelican makes of a filename under `SLUGIFY_SOURCE = "basename"`."""
    stem = os.path.splitext(os.path.basename(path))[0]
    return slugify(stem, regex_subs=DEFAULT_CONFIG["SLUG_REGEX_SUBSTITUTIONS"])


def twins():
    """(czech path, english path) for every pair that the build renders."""
    for dirpath, _dirs, files in os.walk(CONTENT):
        relative = os.path.relpath(dirpath, CONTENT).split(os.sep)[0]
        if relative in UNRENDERED:
            continue
        for name in sorted(files):
            if not name.endswith(".en.md"):
                continue
            english = os.path.relpath(os.path.join(dirpath, name), REPO_ROOT)
            czech = english[: -len(".en.md")] + ".md"
            if not os.path.isfile(os.path.join(REPO_ROOT, czech)):
                continue
            # The homepage pins its own `url:`/`save_as:`; the slug rule does
            # not decide where it lands and this says nothing about it.
            if field(czech, "url") is not None or field(czech, "save_as") is not None:
                continue
            yield czech, english


def address(czech):
    return field(czech, "slug") or derived_slug(czech)


class Rule(unittest.TestCase):
    """The slug an English file gets when nobody wrote one down."""

    class _Content:
        def __init__(self, source_path, slug, metadata=None):
            self.source_path = source_path
            self.slug = slug
            self.metadata = metadata or {}
            # The real thing always carries them, and the slug rule reads
            # three of them; a bare dict here would test a different rule.
            self.settings = DEFAULT_CONFIG

    def test_an_english_file_without_a_slug_takes_its_czech_twin_s(self):
        content = self._Content("content/events/classes/kurz-tango-1.en.md",
                                "kurz-tango-1en")
        i18n_fallback.pair_by_filename(content)
        self.assertEqual(content.slug, "kurz-tango-1")

    def test_a_declared_slug_is_left_alone(self):
        # 63 pairs in the repo name the same slug in both files. Overriding
        # them would move 63 published pages.
        content = self._Content("content/events/classes/x.en.md", "chosen",
                                {"slug": "chosen"})
        i18n_fallback.pair_by_filename(content)
        self.assertEqual(content.slug, "chosen")

    def test_a_czech_file_is_left_alone(self):
        content = self._Content("content/events/classes/kurz-tango-1.md",
                                "kurz-tango-1")
        i18n_fallback.pair_by_filename(content)
        self.assertEqual(content.slug, "kurz-tango-1")

    def test_a_file_with_no_source_path_is_left_alone(self):
        # i18n_fallback's own clones are built without one.
        content = self._Content(None, "kurz-tango-1")
        i18n_fallback.pair_by_filename(content)
        self.assertEqual(content.slug, "kurz-tango-1")


class BuiltSite(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.output = build_site()
        cls.pairs = list(twins())

    def test_there_are_twins_to_check(self):
        self.assertGreater(len(self.pairs), 50,
                           "the pairs are not being found; this suite is guarding nothing")

    def test_the_english_page_carries_the_english_title(self):
        bad = []
        for czech, english in self.pairs:
            title = field(english, "title")
            path = os.path.join(self.output, "en", address(czech), "index.html")
            if not os.path.isfile(path):
                bad.append(f"{english}: nothing built at /en/{address(czech)}/")
                continue
            with open(path, encoding="utf-8") as handle:
                page = unescape(handle.read())
            if title and title not in page:
                bad.append(f"{english}: /en/{address(czech)}/ does not carry {title!r}")
        self.assertEqual(bad, [], f"English twins not served at their address: {bad[:5]}")

    def test_no_twin_is_built_at_an_address_of_its_own(self):
        # The people pages are why this is asked separately: a profile's title
        # is a person's name and reads the same in both languages, so the test
        # above cannot tell the English page from the Czech one standing in
        # for it. The orphan directory can.
        bad = []
        for czech, english in self.pairs:
            orphan = derived_slug(english)
            if orphan == address(czech):
                continue
            for candidate in (os.path.join(self.output, "en", orphan),
                              os.path.join(self.output, orphan)):
                if os.path.isdir(candidate):
                    bad.append(os.path.relpath(candidate, self.output))
        self.assertEqual(bad, [], f"English twins built at an orphan address: {bad[:9]}")


if __name__ == "__main__":
    unittest.main()
