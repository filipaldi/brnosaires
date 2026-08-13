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


if __name__ == "__main__":
    unittest.main()
