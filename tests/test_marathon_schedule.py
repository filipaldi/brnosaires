"""The marathon schedule page: a calendar that stays, and says who plays.

The schedule widget opts out of the card link (`link="false"`) — the reader is
already on the page the card would lead to — and trades the per-card venue
lines for one paragraph under the widget, because every milonga of the weekend
sits in the same hall. What each card carries instead is the DJ, which is the
only thing telling the days apart. These tests pin that contract from the
built HTML, and that no other calendar lost its links on the way.
"""
import os
import re
import unittest

from tests import build_site

DJS = ["DJ Veronika Kim", "DJ Balázs Gyenis", "DJ Francesco Cieschi", "DJ Vincent van 't Laar", "DJ Mačka"]
LINKED_CARD = re.compile(r'<a [^>]*class="event-card"')
DESCRIPTION = re.compile(r'<p class="event-card__description">([^<]*)</p>')


class MarathonSchedule(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.output = build_site()
        cls.schedule = cls.read("marathon-schedule/index.html")

    @classmethod
    def read(cls, relative):
        with open(os.path.join(cls.output, relative), encoding="utf-8") as handle:
            return handle.read()

    def test_the_cards_do_not_link_to_the_milongas(self):
        self.assertEqual(LINKED_CARD.findall(self.schedule), [])

    def test_each_card_names_its_dj(self):
        # The Sunday afterparty card carries more text after the name,
        # so this is a look inside the descriptions, not an equality.
        described = " | ".join(DESCRIPTION.findall(self.schedule))
        for dj in DJS:
            self.assertIn(dj, described, f"no card description says {dj}")

    def test_one_card_per_slot(self):
        # The Sunday evening slot once had two events: a marathon file and the
        # afterparty entered through the CMS. Five slots, five cards.
        self.assertEqual(self.schedule.count('class="event-card"'), 5)

    def test_the_venue_is_said_once_under_the_widget_not_per_card(self):
        self.assertNotIn("event-card__location", self.schedule)
        self.assertNotIn("event-card__organiser", self.schedule)
        self.assertNotIn("event-card__date", self.schedule)
        self.assertIn("el-frame-2x1", self.schedule)
        self.assertIn("Jamborova 3323/65", self.schedule)

    def test_every_other_calendar_still_links_its_cards(self):
        # The home page runs three default widgets through the same card
        # template; if the link opt-out leaked into them, this goes red.
        self.assertRegex(self.read("index.html"), r'<a href="[^"]*" class="event-card"')
