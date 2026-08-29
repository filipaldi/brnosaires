"""Linking an event to the profiles of the people teaching it."""
import unittest

from tests import BUILD_CLOCK, build_site, plugin_path  # noqa: F401

import people_links


class Slugs(unittest.TestCase):
    """`instructor_slugs:` arrives from Pelican in four different shapes."""

    def parse(self, value):
        return people_links._instructor_slugs(type("C", (), {"metadata": {"instructor_slugs": value}}))

    def test_single_slug(self):
        self.assertEqual(self.parse("filip-paldia"), ["filip-paldia"])

    def test_comma_separated(self):
        self.assertEqual(self.parse("filip-paldia, lenka-platenikova"),
                         ["filip-paldia", "lenka-platenikova"])

    def test_yaml_style_brackets(self):
        self.assertEqual(self.parse("[filip-paldia, lenka-platenikova]"),
                         ["filip-paldia", "lenka-platenikova"])

    def test_multiline_metadata_arrives_as_a_list(self):
        self.assertEqual(self.parse(["filip-paldia", "lenka-platenikova"]),
                         ["filip-paldia", "lenka-platenikova"])

    def test_a_yaml_sequence_keeps_its_dashes(self):
        # What the CMS writes. Pelican's metadata reader does not strip the
        # list marker, so the raw lines arrive verbatim — with the empty first
        # element left over from the `instructor_slugs:` line itself.
        self.assertEqual(self.parse(["", "- filip-paldia", "- lenka-platenikova"]),
                         ["filip-paldia", "lenka-platenikova"])

    def test_empty_is_empty(self):
        for value in ("", None, [], ["", "-", "- "]):
            self.assertEqual(self.parse(value), [])


class Recognition(unittest.TestCase):
    def test_a_person_is_recognised_by_its_folder(self):
        person = type("C", (), {"source_path": "/repo/content/people/pavla-luzna.md"})
        event = type("C", (), {"source_path": "/repo/content/events/2026/08/x.md"})
        self.assertTrue(people_links._is_person(person))
        self.assertFalse(people_links._is_person(event))


class BuiltSite(unittest.TestCase):
    """A profile shows what its body says, and nothing the build added.

    Profiles used to grow a list of upcoming events on their own. It is gone:
    an author decides what stands on a profile, the same way they decide it on
    any other page. What is left to check is that the removal is complete —
    a leftover section would be invisible here and obvious on the live site.
    """

    @classmethod
    def setUpClass(cls):
        import os
        import re
        cls.output = build_site()
        cls.re = re
        cls.os = os

    def cards(self, slug):
        path = self.os.path.join(self.output, slug, "index.html")
        with open(path, encoding="utf-8") as handle:
            html = handle.read()
        return self.re.findall(r'<h3 class="event-card__title">([^<]*)</h3>', html)

    def test_a_profile_lists_no_events_of_its_own(self):
        # Filip teaches nine events ahead of BUILD_CLOCK and his body mentions
        # none of them, so anything here came from the build.
        self.assertEqual(self.cards("filip-paldia"), [],
                         f"a profile is still generating its own list; clock {BUILD_CLOCK}")

    def test_the_english_twin_lists_none_either(self):
        self.assertEqual(self.cards("en/filip-paldia"), [])

    def test_the_heading_of_the_old_section_is_gone_from_the_site(self):
        # Both language tables lost the key; this catches a hard-coded copy.
        for slug in ("filip-paldia", "pavla-luzna", "en/filip-paldia"):
            path = self.os.path.join(self.output, slug, "index.html")
            with open(path, encoding="utf-8") as handle:
                html = handle.read()
            self.assertNotIn("Nejbližší lekce a workshopy", html, slug)
            self.assertNotIn("Upcoming classes and workshops", html, slug)
