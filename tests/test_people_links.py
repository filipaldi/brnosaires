"""Linking an event to the profiles of the people teaching it."""
import unittest

from tests import build_site, plugin_path  # noqa: F401

import people_links


class Slugs(unittest.TestCase):
    """`instructor_slugs:` arrives from Pelican in three different shapes."""

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

    def test_empty_is_empty(self):
        for value in ("", None, []):
            self.assertEqual(self.parse(value), [])


class Recognition(unittest.TestCase):
    def test_a_person_is_recognised_by_its_folder(self):
        person = type("C", (), {"source_path": "/repo/content/people/pavla-luzna.md"})
        event = type("C", (), {"source_path": "/repo/content/events/2026/08/x.md"})
        self.assertTrue(people_links._is_person(person))
        self.assertFalse(people_links._is_person(event))


class BuiltSite(unittest.TestCase):
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

    def test_a_lecturer_page_lists_their_upcoming_dates(self):
        self.assertTrue(self.cards("filip-paldia"),
                        "no upcoming events on a profile that teaches")

    def test_a_weekly_class_counts_as_upcoming(self):
        # Its event-start is the FIRST session, months in the past. Filtering
        # on that value hid every class that is actually running.
        self.assertTrue(self.cards("pavla-luzna"),
                        "a running weekly class did not reach its lecturer's page")

    def test_a_profile_that_teaches_nothing_upcoming_shows_no_section(self):
        path = self.os.path.join(self.output, "irena-babilonova", "index.html")
        with open(path, encoding="utf-8") as handle:
            self.assertNotIn("Nejbližší lekce a workshopy", handle.read())

    def test_the_english_twin_gets_the_same_list(self):
        cs = self.cards("filip-paldia")
        en = self.cards("en/filip-paldia")
        self.assertEqual(len(cs), len(en))

    def test_each_event_appears_once_despite_the_en_mirror(self):
        cards = self.cards("filip-paldia")
        self.assertEqual(len(cards), len(set(cards)), f"duplicated: {cards}")

    def test_ordinary_articles_are_untouched(self):
        path = self.os.path.join(self.output, "2160-objeti", "index.html")
        with open(path, encoding="utf-8") as handle:
            self.assertNotIn("Nejbližší lekce a workshopy", handle.read())
