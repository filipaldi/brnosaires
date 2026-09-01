"""Invariants of the rendered HTML: structure, accessibility, structured data.

These are the things that only break in the output — no template diff shows
them, and nobody notices until a screen reader user cannot navigate or Google
silently drops a rich result.
"""
import os
import re
import unittest
from html import unescape
from urllib.parse import parse_qs, urlsplit

from tests import build_site

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

    DJS = ("balasz", "francesco", "veronika-kim", "vincent")

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

    def test_no_venue_link_points_at_google_maps(self):
        # Ruled out by the ticket: the map must not hand the visitor to Google.
        for path, html in self.pages:
            self.assertNotIn("google.com/maps", html, path)

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


if __name__ == "__main__":
    unittest.main()
