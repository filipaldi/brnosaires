"""Recurrence expansion, especially the from/until/count modifiers.

These lock in behaviour that has no other guard: a wrong rrule does not fail
the build, it silently produces the wrong number of dates on a calendar page,
which nobody notices until someone turns up to a class that is not running.
"""
import unittest

from tests import plugin_path  # noqa: F401  (side effect: puts plugins/ on sys.path)

import recurring_events as re_


class _Event:
    """The bits of a Pelican Article that _expand_event actually reads."""

    def __init__(self, **metadata):
        self.metadata = metadata
        self.slug = "test-event"
        self.url = "test-event/"
        self.lang = "cs"
        self.title = "Test"
        self.preview_image = None


def expand(recurrence, start="2026-09-07 19:00:00", end="2026-09-07 21:00:00",
           window=("2026-09-01", "2027-03-31")):
    event = _Event(**{"event-start": start, "event-end": end,
                      "recurrence": recurrence})
    return [o.date.strftime("%Y-%m-%d %H:%M") for o in
            re_.expand_recurring([event], *window)]


class BaseGrammar(unittest.TestCase):
    """The two forms that existed before the modifiers were added."""

    def test_weekly_repeats_until_the_window_ends(self):
        dates = expand("weekly monday")
        self.assertEqual(dates[:3],
                         ["2026-09-07 19:00", "2026-09-14 19:00", "2026-09-21 19:00"])
        self.assertEqual(len(dates), 30)

    def test_monthly_ordinal(self):
        dates = expand("monthly 1 monday", window=("2026-09-01", "2026-12-31"))
        self.assertEqual(dates, ["2026-09-07 19:00", "2026-10-05 19:00",
                                 "2026-11-02 19:00", "2026-12-07 19:00"])

    def test_unparseable_recurrence_yields_the_single_occurrence(self):
        self.assertEqual(expand("weekly bogus"), ["2026-09-07 19:00"])

    def test_no_recurrence_yields_the_single_occurrence(self):
        self.assertEqual(expand(""), ["2026-09-07 19:00"])


class Until(unittest.TestCase):
    def test_until_is_inclusive_of_the_named_day(self):
        dates = expand("weekly monday until 2026-09-28")
        self.assertEqual(dates[-1], "2026-09-28 19:00")
        self.assertEqual(len(dates), 4)

    def test_until_before_the_first_occurrence_yields_nothing(self):
        self.assertEqual(expand("weekly monday until 2026-09-01"), [])

    def test_malformed_until_is_dropped_not_fatal(self):
        # A course that silently collapses to one date is worse for a reader
        # than one that runs past its end, so a bad modifier must not stop the
        # series — it is only a warning.
        self.assertEqual(len(expand("weekly monday until 2026-13-99")), 30)


class Count(unittest.TestCase):
    def test_count_limits_the_series(self):
        self.assertEqual(len(expand("weekly monday count 3")), 3)

    def test_count_zero_is_dropped(self):
        self.assertEqual(len(expand("weekly monday count 0")), 30)

    def test_count_non_numeric_is_dropped(self):
        self.assertEqual(len(expand("weekly monday count many")), 30)


class From(unittest.TestCase):
    def test_from_moves_the_first_occurrence(self):
        dates = expand("weekly monday from 2026-10-05")
        self.assertEqual(dates[0], "2026-10-05 19:00")

    def test_from_keeps_the_time_of_day_from_event_start(self):
        dates = expand("weekly monday from 2026-10-05",
                       start="2026-09-07 17:45:00", end="2026-09-07 19:00:00")
        self.assertTrue(all(d.endswith("17:45") for d in dates))

    def test_from_preserves_the_duration(self):
        event = _Event(**{"event-start": "2026-09-07 19:00:00",
                          "event-end": "2026-09-07 21:30:00",
                          "recurrence": "weekly monday from 2026-10-05 count 1"})
        occurrence = re_.expand_recurring([event], "2026-09-01", "2027-03-31")[0]
        span = occurrence.metadata["event-end"] - occurrence.metadata["event-start"]
        self.assertEqual(span.total_seconds(), 2.5 * 3600)

    def test_from_and_until_combine(self):
        self.assertEqual(expand("weekly monday from 2026-10-05 until 2026-10-26"),
                         ["2026-10-05 19:00", "2026-10-12 19:00",
                          "2026-10-19 19:00", "2026-10-26 19:00"])

    def test_from_snaps_forward_to_the_named_weekday(self):
        # 2026-10-07 is a Wednesday; a weekly-monday series starting "from"
        # there must begin on the next Monday, not on the Wednesday.
        self.assertEqual(expand("weekly monday from 2026-10-07 count 1"),
                         ["2026-10-12 19:00"])

    def test_from_onto_a_short_month_does_not_crash(self):
        # start day 31 shifted onto a 30-day month would be an invalid date if
        # the shift were done naively.
        dates = expand("weekly saturday from 2026-11-07 count 2",
                       start="2026-10-31 19:00:00", end="2026-10-31 22:00:00",
                       window=("2026-01-01", "2027-12-31"))
        self.assertEqual(dates, ["2026-11-07 19:00", "2026-11-14 19:00"])


class MutuallyExclusive(unittest.TestCase):
    def test_until_wins_over_count(self):
        # RFC 5545 forbids UNTIL and COUNT in the same rule.
        dates = expand("weekly monday until 2026-09-21 count 2")
        self.assertEqual(dates[-1], "2026-09-21 19:00")
        self.assertEqual(len(dates), 3)

    def test_rule_string_never_carries_both(self):
        rule, _from = re_._recurrence_to_rrule(
            {"recurrence": "weekly monday until 2026-09-21 count 2"})
        self.assertIn("UNTIL=", rule)
        self.assertNotIn("COUNT=", rule)


class TupleContract(unittest.TestCase):
    """_recurrence_to_rrule returns a pair; calendarium/ics.py unpacks it."""

    def test_returns_a_pair(self):
        self.assertEqual(re_._recurrence_to_rrule({}), (None, None))
        rule, from_date = re_._recurrence_to_rrule({"recurrence": "weekly monday"})
        self.assertEqual(rule, "FREQ=WEEKLY;BYDAY=MO")
        self.assertIsNone(from_date)

    def test_ics_writer_unpacks_it(self):
        from calendarium import ics
        self.assertEqual(ics._event_rrule(None), (None, None))
        self.assertEqual(ics._event_rrule({"recurrence": "weekly monday"}),
                         ("FREQ=WEEKLY;BYDAY=MO", None))

    def test_ics_writer_still_honours_a_raw_event_rrule(self):
        from calendarium import ics
        rule, from_date = ics._event_rrule({"event-rrule": "FREQ=DAILY;COUNT=3"})
        self.assertEqual(rule, "FREQ=DAILY;COUNT=3")
        self.assertIsNone(from_date)


if __name__ == "__main__":
    unittest.main()
