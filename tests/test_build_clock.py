"""The build clock, and the override the test suite pins it with.

Every time-aware thing in the build reads one value, `NOW` in pelicanconf:
`settings["NOW"]` reaches the plugins, `JINJA_GLOBALS` and the `calendarium`
filter reach the templates. `BRNOSAIRES_NOW` overrides that value so a test
build is a function of the repo instead of the calendar.

That makes the override load-bearing: if it silently stopped working, every
integration test would quietly go back to the wall clock and start rotting
again. Hence this module. It imports pelicanconf in a subprocess, because the
config is a heavyweight module-level singleton and each case needs a fresh one
with a different environment.
"""
import os
import subprocess
import sys
import unittest

from tests import BUILD_CLOCK, REPO_ROOT


def _now_for(value):
    """Import pelicanconf with BRNOSAIRES_NOW=value; return (returncode, text).

    `text` is NOW in ISO form on success, or the captured stderr on failure.
    """
    environment = dict(os.environ, PYTHONPATH=REPO_ROOT)
    if value is None:
        environment.pop("BRNOSAIRES_NOW", None)
    else:
        environment["BRNOSAIRES_NOW"] = value
    result = subprocess.run(
        [sys.executable, "-c",
         "import pelicanconf; print(pelicanconf.NOW.isoformat())"],
        cwd=REPO_ROOT, env=environment, capture_output=True, text=True)
    if result.returncode != 0:
        return result.returncode, result.stderr
    return 0, result.stdout.strip()


class Override(unittest.TestCase):
    def test_a_pinned_datetime_becomes_now(self):
        code, now = _now_for("2026-08-01 12:00:00")
        self.assertEqual(code, 0, now)
        self.assertTrue(now.startswith("2026-08-01T12:00:00"), now)

    def test_the_pin_is_localised_not_naive(self):
        # A naive NOW compares badly against the timezone-aware dates Pelican
        # builds from front matter, so the override has to localise.
        code, now = _now_for("2026-08-01 12:00:00")
        self.assertEqual(code, 0, now)
        self.assertTrue(now.endswith("+02:00"), f"not Europe/Prague: {now}")

    def test_a_date_alone_is_enough(self):
        code, now = _now_for("2026-08-01")
        self.assertEqual(code, 0, now)
        self.assertTrue(now.startswith("2026-08-01T00:00:00"), now)

    def test_an_iso_t_separator_is_accepted(self):
        code, now = _now_for("2026-08-01T12:00:00")
        self.assertEqual(code, 0, now)
        self.assertTrue(now.startswith("2026-08-01T12:00:00"), now)

    def test_a_malformed_pin_fails_loudly(self):
        # Falling back to the wall clock here would silently restore the very
        # flakiness the pin removes, so a bad value has to stop the build.
        code, error = _now_for("last tuesday")
        self.assertNotEqual(code, 0, "a malformed clock built anyway")
        self.assertIn("BRNOSAIRES_NOW", error)

    def test_an_empty_pin_is_treated_as_unset(self):
        code, now = _now_for("")
        self.assertEqual(code, 0, now)

    def test_without_the_variable_the_wall_clock_is_used(self):
        # Compared as instants with a tolerance, not as formatted strings: NOW
        # is Europe/Prague while the CI runner is UTC, so a string compare
        # disagrees for the hour or two after Prague midnight, and would do it
        # across a month boundary too. That is the same kind of clock-shaped
        # trap this whole change exists to remove.
        from datetime import datetime, timedelta, timezone
        code, now = _now_for(None)
        self.assertEqual(code, 0, now)
        parsed = datetime.fromisoformat(now)
        self.assertIsNotNone(parsed.tzinfo, f"NOW is naive: {now}")
        self.assertLess(abs(parsed - datetime.now(timezone.utc)),
                        timedelta(hours=1),
                        f"production build is not on the real clock: {now}")


class SuiteConstant(unittest.TestCase):
    def test_the_pin_the_suite_uses_is_a_value_the_build_accepts(self):
        # A typo in BUILD_CLOCK would otherwise surface as every build-based
        # test failing at once, with the reason buried in Pelican's output.
        code, now = _now_for(BUILD_CLOCK)
        self.assertEqual(code, 0, now)
        self.assertTrue(now.startswith(BUILD_CLOCK[:10]), now)
