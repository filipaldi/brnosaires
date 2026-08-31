"""The weekly schedule: every regular class once, under the day it runs on.

The page section is called „Pravidelné lekce" and showed a six-day window of
the calendar. A course starting in a fortnight was therefore absent from the
list of courses, which is how six of Lenka's classes could be created, built
and published without appearing anywhere a reader looks for classes.

Widening the window does not fix it: with `group_by="week day"` a longer span
repeats the same grid for every week in it. A schedule is not a window. It
answers a different question — which classes run, and on which day — so it
groups by day of the week, shows each class once, and ignores dates beyond
the one it needs to know the class is still running.

That is what `group_by="weekday"` is. Only repeating events take part: a
one-off lesson under „Úterý" would read as a weekly commitment that is not
there.
"""
import os
import re
import unittest
from html import unescape

from tests import BUILD_CLOCK, build_site, plugin_path  # noqa: F401

from calendarium.grouping import group_events

LESSONS_PAGE = "tango-lekce-brno"

# Every `recurrence:` in content/events with `event-type: class`, at the clock
# the suite builds on. The schedule has to show all of them, once each.
RECURRING_CLASSES = {
    "kurz-tango-1": "Úterý",
    "kurz-tango-2-3": "Neděle",
    "pravidelny-kurz-tango-2": "Pondělí",
    "tango-pro-zacatecniky": "Středa",
    "tango-pro-mirne-pokrocile": "Středa",
    "tango-pro-pokrocile": "Středa",
    "tango-javier-stredne-pokrocili-a-pokrocili": "Středa",
    "stolarna-tangomania": "Pondělí",
    "stolarna-tangomania-basic": "Pondělí",
    "tango-4-a-vys-moderni-variace-09-2026": "Čtvrtek",
}
# `event-type: class` but no `recurrence:` — a one-off, and not a schedule row.
ONE_OFF_CLASSES = ("07-neotango-cedric-pavla", "tanguj-za-jeden-den")


class _Event:
    def __init__(self, slug, start, recurrence=None):
        self.slug = slug
        self.metadata = {"event-start": start}
        if recurrence:
            self.metadata["recurrence"] = recurrence


class Grouping(unittest.TestCase):
    def group(self, events, lang="cs"):
        return group_events(events, "weekday", lang)

    def test_events_land_under_the_day_they_repeat_on(self):
        grouped = self.group([
            _Event("a", "2026-09-15 19:15:00", "weekly tuesday"),
            _Event("b", "2026-09-14 17:45:00", "weekly monday"),
        ])
        self.assertEqual([headline for headline, _events, _meta in grouped],
                         ["Pondělí", "Úterý"])

    def test_the_days_run_monday_to_sunday(self):
        grouped = self.group([
            _Event("sun", "2026-09-20 18:45:00", "weekly sunday"),
            _Event("wed", "2026-09-16 18:00:00", "weekly wednesday"),
            _Event("mon", "2026-09-14 17:45:00", "weekly monday"),
        ])
        self.assertEqual([headline for headline, _e, _m in grouped],
                         ["Pondělí", "Středa", "Neděle"])

    def test_a_day_nobody_teaches_on_is_not_printed(self):
        grouped = self.group([_Event("a", "2026-09-15 19:15:00", "weekly tuesday")])
        self.assertEqual(len(grouped), 1)

    def test_one_card_per_class_however_many_occurrences_arrive(self):
        # What the calendar hands over: the same course, once per week.
        grouped = self.group([
            _Event("kurz", "2026-09-15 19:15:00", "weekly tuesday"),
            _Event("kurz", "2026-09-22 19:15:00", "weekly tuesday"),
            _Event("kurz", "2026-09-29 19:15:00", "weekly tuesday"),
        ])
        self.assertEqual(len(grouped[0][1]), 1)

    def test_the_earliest_occurrence_is_the_one_kept(self):
        grouped = self.group([
            _Event("kurz", "2026-09-22 19:15:00", "weekly tuesday"),
            _Event("kurz", "2026-09-15 19:15:00", "weekly tuesday"),
        ])
        self.assertEqual(grouped[0][1][0].metadata["event-start"], "2026-09-15 19:15:00")

    def test_a_one_off_is_not_a_schedule_row(self):
        grouped = self.group([
            _Event("jednorazova", "2026-09-15 19:15:00"),
            _Event("kurz", "2026-09-15 19:15:00", "weekly tuesday"),
        ])
        self.assertEqual([event.slug for event in grouped[0][1]], ["kurz"])

    def test_within_a_day_the_earlier_class_comes_first(self):
        grouped = self.group([
            _Event("late", "2026-09-16 19:15:00", "weekly wednesday"),
            _Event("early", "2026-09-16 18:00:00", "weekly wednesday"),
        ])
        self.assertEqual([event.slug for event in grouped[0][1]], ["early", "late"])

    def test_the_hour_orders_the_day_even_when_the_courses_started_months_apart(self):
        # A course running since March and one starting in September share a
        # Wednesday. Sorting by the occurrence puts March first whatever the
        # clock says; a reader of a schedule reads down the evening.
        grouped = self.group([
            _Event("since-march", "2026-03-04 19:00:00", "weekly wednesday"),
            _Event("from-september", "2026-09-16 18:00:00", "weekly wednesday"),
        ])
        self.assertEqual([event.slug for event in grouped[0][1]],
                         ["from-september", "since-march"])

    def test_english_names_the_days_in_english(self):
        grouped = self.group([_Event("a", "2026-09-15 19:15:00", "weekly tuesday")], "en")
        self.assertEqual(grouped[0][0], "Tuesday")

    def test_nothing_to_schedule_is_no_schedule(self):
        self.assertEqual(self.group([]), [])
        self.assertEqual(self.group([_Event("a", "2026-09-15 19:15:00")]), [])


class BuiltPage(unittest.TestCase):
    """The section a reader actually opens."""

    @classmethod
    def setUpClass(cls):
        cls.output = build_site()
        with open(os.path.join(cls.output, LESSONS_PAGE, "index.html"),
                  encoding="utf-8") as handle:
            cls.html = handle.read()

    def links(self, slug):
        return len(re.findall(rf'href="[^"]*/{re.escape(slug)}/"', self.html))

    def test_every_regular_class_is_on_the_page(self):
        missing = [slug for slug in RECURRING_CLASSES if not self.links(slug)]
        self.assertEqual(missing, [],
                         f"regular classes missing from the schedule; clock {BUILD_CLOCK}")

    def test_no_class_is_listed_twice(self):
        twice = {slug: self.links(slug) for slug in RECURRING_CLASSES
                 if self.links(slug) > 1}
        self.assertEqual(twice, {}, f"a class repeats in the schedule: {twice}")

    def test_the_day_headings_are_there(self):
        text = " ".join(unescape(re.sub(r"<[^>]+>", " ", self.html)).split())
        for day in sorted(set(RECURRING_CLASSES.values())):
            with self.subTest(day):
                self.assertIn(day, text)

    def test_a_one_off_lesson_is_not_in_the_schedule(self):
        for slug in ONE_OFF_CLASSES:
            with self.subTest(slug):
                self.assertEqual(self.links(slug), 0,
                                 "a one-off reads as a weekly commitment")


if __name__ == "__main__":
    unittest.main()
