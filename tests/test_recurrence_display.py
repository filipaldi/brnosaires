"""What a repeating event tells a reader, and what it tells a search engine.

`recurrence: weekly tuesday` reaches the calendar, the `.ics` feed and the LLM
mirror. It never reached the event's own page, which printed `event-start` and
stopped:

    Kdy: 15. 09. 2026 19:15 – 15. 09. 2026 20:30

A weekly course reads as a single evening in September. The structured data
says the same thing to Google — one `startDate`, no schedule — so a course
that runs every Tuesday until Christmas is indexed as an evening that has
already passed the week after it starts.

The rule is in the file. These tests are about saying it out loud.
"""
import json
import os
import re
import unittest
from html import unescape

from tests import REPO_ROOT, build_site, plugin_path  # noqa: F401

import pelicanconf
import recurring_events

# A weekly class in both languages: `recurrence: weekly tuesday`, starting
# Tuesday 15 September 2026 at 19:15.
WEEKLY = "kurz-tango-1"
# No `recurrence:` at all — the row it prints today must not change.
ONE_OFF = "milonga-naplavka-09-2026"


def read(output, *parts):
    with open(os.path.join(output, *parts, "index.html"), encoding="utf-8") as handle:
        return handle.read()


def when_row(html, label):
    match = re.search(r"<dt>\s*" + re.escape(label) + r"\s*</dt>\s*<dd>(.*?)</dd>",
                      html, re.DOTALL)
    if match is None:
        return None
    return " ".join(unescape(re.sub(r"<[^>]+>", " ", match.group(1))).split())


def event_ld(html):
    for block in re.findall(r'<script type="application/ld\+json">(.*?)</script>',
                            html, re.DOTALL):
        data = json.loads(block)
        if data.get("@type") == "Event":
            return data
    return None


class Parts(unittest.TestCase):
    """The rule, read into the pieces a sentence and a schema need."""

    def parts(self, value):
        return recurring_events.recurrence_parts({"recurrence": value})

    def test_a_weekly_rule_names_its_weekday(self):
        parts = self.parts("weekly tuesday")
        self.assertIsNotNone(parts)
        self.assertEqual(parts["freq"], "weekly")
        self.assertEqual(parts["weekday"], 1)  # Monday is 0, like datetime

    def test_an_until_date_comes_back_as_a_date(self):
        parts = self.parts("weekly monday until 2026-12-16")
        self.assertEqual(parts["until"].strftime("%Y-%m-%d"), "2026-12-16")

    def test_no_recurrence_is_nothing(self):
        for value in (None, "", "   "):
            self.assertIsNone(self.parts(value))

    def test_a_rule_nobody_recognises_is_nothing(self):
        # Same answer as the calendar gives it: the event keeps its one date,
        # and the page must not invent a repetition the build does not honour.
        self.assertIsNone(self.parts("kazdy tyden v utery"))

    def test_a_monthly_rule_is_read_but_not_weekly(self):
        parts = self.parts("monthly 1 sunday")
        self.assertIsNotNone(parts)
        self.assertEqual(parts["freq"], "monthly")


class Sentence(unittest.TestCase):
    """The line a reader gets instead of a single date."""

    def line(self, value, lang="cs", start="2026-09-15 19:15:00", end="2026-09-15 20:30:00"):
        return pelicanconf.recurrence_line(
            {"recurrence": value, "event-start": start, "event-end": end}, lang)

    def test_czech_names_the_weekday_in_the_right_case(self):
        # "každé úterý" but "každou středu": Czech weekday nouns differ in
        # gender, so the whole phrase lives in the string table rather than
        # being assembled from a word and a template.
        self.assertEqual(self.line("weekly tuesday"),
                         "každé úterý 19:15 – 20:30, od 15. 09. 2026")
        self.assertTrue(self.line("weekly wednesday").startswith("každou středu"))

    def test_english_says_every_weekday(self):
        self.assertEqual(self.line("weekly tuesday", "en"),
                         "every Tuesday 19:15 – 20:30, from 15 September 2026")

    def test_an_end_of_series_is_said_too(self):
        self.assertEqual(self.line("weekly tuesday until 2026-12-16"),
                         "každé úterý 19:15 – 20:30, od 15. 09. 2026 do 16. 12. 2026")

    def test_an_event_that_does_not_repeat_gets_no_line(self):
        self.assertEqual(self.line(None), "")

    def test_a_rule_the_build_ignores_gets_no_line(self):
        self.assertEqual(self.line("monthly 1 sunday"), "")


class Schedule(unittest.TestCase):
    """The schema.org shape for a repeating event."""

    def schedule(self, value):
        return pelicanconf.event_schedule({
            "recurrence": value,
            "event-start": "2026-09-15 19:15:00",
            "event-end": "2026-09-15 20:30:00"})

    def test_a_weekly_event_gets_a_weekly_schedule(self):
        schedule = self.schedule("weekly tuesday")
        self.assertEqual(schedule["@type"], "Schedule")
        self.assertEqual(schedule["repeatFrequency"], "P1W")
        self.assertEqual(schedule["byDay"], "https://schema.org/Tuesday")
        self.assertEqual(schedule["startDate"], "2026-09-15")
        self.assertEqual(schedule["startTime"], "19:15")
        self.assertEqual(schedule["endTime"], "20:30")
        self.assertEqual(schedule["scheduleTimezone"], "Europe/Prague")

    def test_the_end_of_the_series_is_the_schedule_end(self):
        self.assertEqual(self.schedule("weekly tuesday until 2026-12-16")["endDate"],
                         "2026-12-16")

    def test_an_event_that_does_not_repeat_gets_none(self):
        self.assertIsNone(self.schedule(None))


class BuiltSite(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.output = build_site()

    def test_the_czech_page_says_it_repeats(self):
        self.assertEqual(when_row(read(self.output, WEEKLY), "Kdy"),
                         "každé úterý 19:15 – 20:30, od 15. 09. 2026")

    def test_the_english_page_says_it_repeats(self):
        self.assertEqual(when_row(read(self.output, "en", WEEKLY), "When"),
                         "every Tuesday 19:15 – 20:30, from 15 September 2026")

    def test_the_structured_data_carries_the_schedule(self):
        schedule = event_ld(read(self.output, WEEKLY)).get("eventSchedule")
        self.assertIsNotNone(schedule, "Google is still told this is one evening")
        self.assertEqual(schedule["repeatFrequency"], "P1W")
        self.assertEqual(schedule["byDay"], "https://schema.org/Tuesday")

    def test_a_one_off_event_is_untouched(self):
        html = read(self.output, ONE_OFF)
        self.assertNotIn("eventSchedule", html)
        row = when_row(html, "Kdy")
        self.assertIsNotNone(row, f"{ONE_OFF} lost its date row")
        self.assertRegex(row, r"^\d{1,2}\. \d{2}\. \d{4}")


if __name__ == "__main__":
    unittest.main()
