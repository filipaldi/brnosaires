"""The fediverse/Nostr echo. It posts publicly and cannot un-post.

So the tests that matter are the ones about not posting: the first-run guard,
the flood guard, and never announcing the same article twice.
"""
import json
import os
import shutil
import tempfile
import unittest
from unittest import mock

from tests import script_path  # noqa: F401

import publish_social


FEED = """<?xml version="1.0" encoding="utf-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
{entries}
</feed>"""

ENTRY = """<entry>
  <title>{title}</title>
  <link href="https://brnosaires.com/{slug}/" rel="alternate"/>
  <id>tag:brnosaires.com,2026-01-0{n}:/{slug}/</id>
  <published>2026-01-0{n}T19:00:00+01:00</published>
</entry>"""


def feed(count):
    """Newest first, as Pelican writes it."""
    return FEED.format(entries="\n".join(
        ENTRY.format(title=f"Akce {n}", slug=f"akce-{n}", n=n)
        for n in range(count, 0, -1)))


class Parsing(unittest.TestCase):
    def test_entries_come_out_newest_first(self):
        entries = publish_social.parse_feed(feed(3))
        self.assertEqual([e["title"] for e in entries], ["Akce 3", "Akce 2", "Akce 1"])
        self.assertEqual(entries[0]["url"], "https://brnosaires.com/akce-3/")


class Compose(unittest.TestCase):
    def test_title_blank_line_url(self):
        text = publish_social.compose(
            {"title": "Milonga u Draka", "url": "https://brnosaires.com/x/"})
        self.assertEqual(text, "Milonga u Draka\n\nhttps://brnosaires.com/x/")

    def test_long_title_is_truncated_to_fit(self):
        url = "https://brnosaires.com/" + "x" * 40 + "/"
        text = publish_social.compose({"title": "á" * 900, "url": url})
        self.assertLessEqual(len(text), publish_social.MASTODON_LIMIT)
        self.assertIn(url, text)
        self.assertTrue(text.split("\n")[0].endswith("…"))

    def test_the_url_always_survives(self):
        # A post whose link got truncated is worse than no post at all.
        url = "https://brnosaires.com/" + "y" * 480 + "/"
        text = publish_social.compose({"title": "Nadpis", "url": url})
        self.assertIn(url, text)


class _Harness(unittest.TestCase):
    """Runs main() against a local feed file with the senders stubbed out."""

    def setUp(self):
        self.dir = tempfile.mkdtemp()
        self.state = os.path.join(self.dir, "state.json")
        self.feed_path = os.path.join(self.dir, "feed.xml")
        self.sent = []

    def tearDown(self):
        shutil.rmtree(self.dir, ignore_errors=True)

    def write_feed(self, count):
        with open(self.feed_path, "w", encoding="utf-8") as handle:
            handle.write(feed(count))

    def write_state(self, ids):
        with open(self.state, "w", encoding="utf-8") as handle:
            json.dump({"published": list(ids)}, handle)

    def read_state(self):
        """{entry id -> set of networks it went to}, or None if never written."""
        if not os.path.exists(self.state):
            return None
        with open(self.state, encoding="utf-8") as handle:
            published = json.load(handle)["published"]
        return {key: set(value) for key, value in published.items()}

    def run_main(self, mastodon=True, nostr=False, argv=None):
        def fake_mastodon(text, dry_run, created_at=None):
            if not mastodon:
                return None
            self.sent.append(text)
            return True

        def fake_nostr(text, dry_run, created_at=None):
            return True if nostr else None

        with mock.patch.object(publish_social, "post_mastodon", fake_mastodon), \
             mock.patch.object(publish_social, "post_nostr", fake_nostr), \
             mock.patch.object(publish_social, "log", lambda message: None), \
             mock.patch("sys.argv", ["publish_social.py",
                                     "--feed-url", self.feed_path,
                                     "--state", self.state] + (argv or [])):
            return publish_social.main()


class FirstRun(_Harness):
    def test_records_everything_without_posting(self):
        # Switching this on must not dump the whole back catalogue into a
        # timeline.
        self.write_feed(5)
        self.assertEqual(self.run_main(), 0)
        self.assertEqual(self.sent, [])
        self.assertEqual(len(self.read_state()), 5)

    def test_the_next_new_article_is_then_announced(self):
        self.write_feed(5)
        self.run_main()
        self.write_feed(6)
        self.run_main()
        self.assertEqual(len(self.sent), 1)
        self.assertIn("Akce 6", self.sent[0])


class Idempotence(_Harness):
    def test_nothing_new_posts_nothing(self):
        self.write_feed(3)
        self.run_main()
        self.assertEqual(self.run_main(), 0)
        self.assertEqual(self.sent, [])

    def test_an_article_is_never_posted_twice(self):
        self.write_feed(3)
        self.run_main()
        self.write_feed(4)
        self.run_main()
        self.run_main()
        self.run_main()
        self.assertEqual(len(self.sent), 1)

    def test_new_entries_go_out_oldest_first(self):
        self.write_feed(2)
        self.run_main()
        self.write_feed(4)
        self.run_main()
        self.assertEqual([t.split("\n")[0] for t in self.sent], ["Akce 3", "Akce 4"])


class Guards(_Harness):
    def test_never_more_than_max_per_run(self):
        self.write_feed(1)
        self.run_main()
        self.write_feed(20)
        self.run_main()
        self.assertEqual(len(self.sent), publish_social.MAX_PER_RUN)

    def test_the_overflow_waits_rather_than_being_dropped(self):
        # An editor adding a month of milongas in one push is normal here. The
        # overflow used to be recorded as sent and then never announced.
        self.write_feed(1)
        self.run_main()
        self.write_feed(9)
        self.run_main()
        self.run_main()
        titles = sorted(t.split("\n")[0] for t in self.sent)
        self.assertEqual(titles, sorted(f"Akce {n}" for n in range(2, 10)))

    def test_the_soonest_events_go_first(self):
        # The feed is newest-first and "newest" here is the furthest-future
        # event, so slicing it as-is announced the far ones and dropped the
        # imminent ones.
        self.write_feed(1)
        self.run_main()
        self.write_feed(9)
        self.run_main()
        self.assertEqual([t.split("\n")[0] for t in self.sent],
                         [f"Akce {n}" for n in range(2, 7)])

    def test_no_network_configured_sends_nothing(self):
        self.write_feed(3)
        self.run_main()
        self.write_feed(4)
        self.assertEqual(self.run_main(mastodon=False), 0)
        self.assertEqual(self.sent, [])

    def test_an_unconfigured_network_does_not_starve_the_per_run_budget(self):
        # Nostr is not configured here. Leaving it pending kept every entry
        # "fresh" forever, so the five slots went to entries that had nothing
        # left to do and the ones behind them were never announced.
        self.write_feed(1)
        self.run_main()
        self.write_feed(9)
        self.run_main()
        self.run_main()
        self.assertEqual(sorted(t.split("\n")[0] for t in self.sent),
                         sorted(f"Akce {n}" for n in range(2, 10)))


class Failure(_Harness):
    ENTRY_2 = "tag:brnosaires.com,2026-01-02:/akce-2/"

    def test_a_failed_send_is_retried_next_run(self):
        self.write_feed(1)
        self.run_main()
        self.write_feed(2)

        calls = []

        def flaky(text, dry_run, created_at=None):
            calls.append(text)
            return len(calls) > 1  # fails the first time, succeeds after

        with mock.patch.object(publish_social, "post_mastodon", flaky), \
             mock.patch.object(publish_social, "post_nostr", lambda t, d, c=None: None), \
             mock.patch.object(publish_social, "log", lambda message: None), \
             mock.patch("sys.argv", ["publish_social.py", "--feed-url",
                                     self.feed_path, "--state", self.state]):
            publish_social.main()
            self.assertNotIn("Mastodon", self.read_state()[self.ENTRY_2],
                             "a failed send was recorded as delivered")
            publish_social.main()
        self.assertEqual(len(calls), 2, "the failed entry was not retried")
        # Nostr is unconfigured in this harness and is recorded as settled.
        self.assertIn("Mastodon", self.read_state()[self.ENTRY_2])

    def test_partial_success_is_recorded_per_network(self):
        # "Mastodon took it, every Nostr relay was down" is a real state.
        # Collapsing it to "not sent" made the next run post to Mastodon twice.
        self.write_feed(1)
        self.run_main()
        self.write_feed(2)
        mastodon_calls = []

        def mastodon(text, dry_run, created_at=None):
            mastodon_calls.append(text)
            return True

        nostr_up = {"value": False}

        def nostr(text, dry_run, created_at=None):
            return nostr_up["value"]

        def run():
            with mock.patch.object(publish_social, "post_mastodon", mastodon), \
                 mock.patch.object(publish_social, "post_nostr", nostr), \
                 mock.patch.object(publish_social, "log", lambda message: None), \
                 mock.patch("sys.argv", ["publish_social.py", "--feed-url",
                                         self.feed_path, "--state", self.state]):
                publish_social.main()

        run()   # Nostr's relays are all down
        self.assertEqual(self.read_state()[self.ENTRY_2], {"Mastodon"})
        run()   # still down: nothing repeats on Mastodon
        self.assertEqual(self.read_state()[self.ENTRY_2], {"Mastodon"})

        nostr_up["value"] = True
        run()   # back up: only the Nostr half is retried
        self.assertEqual(len(mastodon_calls), 1, "posted to Mastodon more than once")
        self.assertEqual(self.read_state()[self.ENTRY_2], {"Mastodon", "Nostr"})

    def test_dry_run_never_writes_state(self):
        self.write_feed(2)
        self.run_main(argv=["--dry-run"])
        self.assertIsNone(self.read_state())


class StableTimestamp(unittest.TestCase):
    """Nostr has no idempotency key; the event id hashes created_at, so a
    wall-clock timestamp turns every retry into a second public note."""

    def test_derived_from_the_articles_published_date(self):
        stamp = publish_social.stable_created_at("2026-01-02T19:00:00+01:00",
                                                 now=2_000_000_000)
        self.assertEqual(stamp, publish_social.stable_created_at(
            "2026-01-02T19:00:00+01:00", now=2_000_000_001))

    def test_never_in_the_future(self):
        # Relays reject far-future events; the marathon pages are dated ahead
        # of today, and their feed entries carry those dates.
        now = 1_000_000_000
        self.assertLessEqual(
            publish_social.stable_created_at("2099-01-01T00:00:00+00:00", now=now), now)

    def test_a_future_date_falls_back_to_the_start_of_the_day(self):
        # This site announces events before they happen, so `published` is
        # usually in the future and relays reject a future timestamp. Clamping
        # to `now` would move every second and defeat the point.
        now = 1_000_000_000
        first = publish_social.stable_created_at("2099-01-01T00:00:00+00:00", now=now)
        second = publish_social.stable_created_at("2099-01-01T00:00:00+00:00",
                                                  now=now + 3600)
        self.assertEqual(first, second)
        self.assertLessEqual(first, now)

    def test_a_missing_or_unparseable_date_also_gets_a_stable_value(self):
        now = 1_000_000_000
        for value in ("", None, "not a date"):
            self.assertEqual(publish_social.stable_created_at(value, now=now),
                             publish_social.stable_created_at(value, now=now + 60))


class Bech32(unittest.TestCase):
    def test_decodes_a_known_nsec(self):
        # nsec for the all-0x11 key, produced by a reference bech32 encoder.
        nsec = ("nsec1zyg3zyg3zyg3zyg3zyg3zyg3zyg3zyg3zyg3zyg3zyg3zyg3zygs4rm7hz")
        self.assertEqual(publish_social._bech32_decode_to_bytes(nsec).hex(),
                         "11" * 32)

    def test_a_non_bech32_string_raises(self):
        with self.assertRaises(ValueError):
            publish_social._bech32_decode_to_bytes("not-a-key")


class NostrEvent(unittest.TestCase):
    """NIP-01: the id is sha256 over a compact JSON array, signed Schnorr."""

    def test_id_and_signature_are_valid(self):
        try:
            from coincurve import PrivateKey, PublicKeyXOnly
        except ImportError:
            self.skipTest("coincurve not installed (requirements-social.txt)")
        import hashlib

        key = PrivateKey(bytes.fromhex("11" * 32))
        pubkey = key.public_key_xonly.format().hex()
        text = "Milonga u Draka\n\nhttps://brnosaires.com/x/ — ěščř"
        serialised = json.dumps([0, pubkey, 1760000000, 1, [], text],
                                separators=(",", ":"), ensure_ascii=False)
        event_id = hashlib.sha256(serialised.encode()).hexdigest()
        signature = key.sign_schnorr(bytes.fromhex(event_id))
        self.assertTrue(PublicKeyXOnly(bytes.fromhex(pubkey)).verify(
            signature, bytes.fromhex(event_id)))

    def test_the_event_the_script_builds_hashes_its_own_tags(self):
        """The id must cover the tags the event actually carries.

        Built through publish_social.build_nostr_event rather than rebuilt
        here: the other tests in this class hand-roll the serialisation, so
        they would pass unchanged while the script hashed `[]` and shipped
        tags — an id that does not match its own event, which every relay
        rejects and no amount of local testing would show.
        """
        try:
            from coincurve import PublicKeyXOnly
        except ImportError:
            self.skipTest("coincurve not installed (requirements-social.txt)")
        import hashlib

        import publish_social

        event = publish_social.build_nostr_event(
            "Milonga u Draka\n\nhttps://brnosaires.com/x/ — ěščř",
            bytes.fromhex("11" * 32), created_at=1760000000)

        self.assertEqual(event["tags"],
                         [["t", t] for t in publish_social.NOSTR_HASHTAGS])
        self.assertTrue(event["tags"], "an untagged note is invisible on Nostr")

        recomputed = hashlib.sha256(json.dumps(
            [0, event["pubkey"], event["created_at"], event["kind"],
             event["tags"], event["content"]],
            separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()
        self.assertEqual(event["id"], recomputed, "id does not cover the tags")
        self.assertTrue(PublicKeyXOnly(bytes.fromhex(event["pubkey"])).verify(
            bytes.fromhex(event["sig"]), bytes.fromhex(event["id"])))

    def test_serialisation_keeps_non_ascii_unescaped(self):
        # ensure_ascii=True would change the bytes hashed and every relay would
        # reject the event id.
        serialised = json.dumps([0, "pub", 1, 1, [], "ěščř"],
                                separators=(",", ":"), ensure_ascii=False)
        self.assertIn("ěščř", serialised)
        self.assertNotIn(" ", serialised)


if __name__ == "__main__":
    unittest.main()
