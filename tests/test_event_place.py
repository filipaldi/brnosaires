"""The place an event happens, read from fields instead of parsed from prose.

`event-location` used to be one string - "HEX Gallery, Lidická 63a, Brno" - and
the address was recovered by splitting it on commas. That made the *shape* of
the value load-bearing, and to guarantee the shape someone froze the list of
venues in the CMS to twenty options. An editor could not add the twenty-first.

Three fields carry the same information without either problem: nothing is
parsed, so nothing degrades silently, and nothing has to be on a list.
"""
import unittest

from tests import plugin_path  # noqa: F401

import event_place


class Address(unittest.TestCase):
    """The schema.org half: what article.html turns into a Place."""

    def test_all_three_fields(self):
        self.assertEqual(
            event_place.place({"event-venue": "HEX Gallery",
                               "event-street": "Lidická 63a",
                               "event-locality": "Brno"}),
            {"name": "HEX Gallery", "streetAddress": "Lidická 63a",
             "addressLocality": "Brno", "line": "HEX Gallery, Lidická 63a, Brno"})

    def test_a_venue_with_no_street(self):
        # "Park Moravské náměstí, Brno" — a place with no house number.
        self.assertEqual(
            event_place.place({"event-venue": "Park Moravské náměstí",
                               "event-locality": "Brno"}),
            {"name": "Park Moravské náměstí", "addressLocality": "Brno",
             "line": "Park Moravské náměstí, Brno"})

    def test_a_bare_locality(self):
        self.assertEqual(event_place.place({"event-locality": "Brno"}),
                         {"addressLocality": "Brno", "line": "Brno"})

    def test_nothing_at_all(self):
        for metadata in ({}, None, {"event-venue": "", "event-locality": "  "}):
            self.assertEqual(event_place.place(metadata), {})

    def test_no_half_built_address(self):
        # An empty field is left out rather than written as an empty string:
        # schema.org validators read `"streetAddress": ""` as a claim.
        self.assertNotIn("streetAddress",
                         event_place.place({"event-venue": "Skleněnka",
                                            "event-street": "",
                                            "event-locality": "Brno"}))


class Line(unittest.TestCase):
    """The display half: what the card, the ICS export and the LLM mirror print.

    Reproduces the old one-string spelling exactly, so nothing downstream of it
    had to change and the migration is invisible in the output.
    """

    def test_it_reads_like_the_old_single_value(self):
        self.assertEqual(
            event_place.place({"event-venue": "Adrinela Cafe",
                               "event-street": "Životského 14",
                               "event-locality": "Brno-Židenice"})["line"],
            "Adrinela Cafe, Životského 14, Brno-Židenice")

    def test_a_street_with_its_own_comma_survives(self):
        # "Dominikánská 264/2" has none, but a street written "Ulice 1, vchod B"
        # used to round-trip through the comma parser and still has to.
        self.assertEqual(
            event_place.place({"event-venue": "Sál",
                               "event-street": "Ulice 1, vchod B",
                               "event-locality": "Brno"})["line"],
            "Sál, Ulice 1, vchod B, Brno")

    def test_whitespace_is_not_carried_into_the_output(self):
        self.assertEqual(
            event_place.place({"event-venue": "  Rockwine  ",
                               "event-locality": " Brno "})["line"],
            "Rockwine, Brno")


if __name__ == "__main__":
    unittest.main()
