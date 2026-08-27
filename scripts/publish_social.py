#!/usr/bin/env python3
"""
publish_social.py — echo newly published articles to Mastodon and Nostr.

The web is the source of truth; these networks are the echo. So this reads the
site's own Atom feed rather than the content tree: if a post went out, the page
is already live, already has its canonical URL, and already has a working
og:image for the link preview. Nothing can be announced that a reader cannot
open.

STATE
-----
`.published-feeds.json` in the repo root records the Atom entry IDs already
sent, and is committed back by the workflow. On the very first run — no state
file — everything in the feed is recorded as published WITHOUT posting, so
turning this on does not dump thirty back-dated announcements into anyone's
timeline.

FAILURE
-------
A network that errors is logged and its entries are simply not marked, so the
next run retries them. Nothing here fails the build; the site is already
deployed by the time this runs.

CONFIGURATION (environment, all optional)
-----------------------------------------
    MASTODON_INSTANCE   e.g. https://mastodonczech.cz
    MASTODON_TOKEN      access token with `write:statuses`
    NOSTR_SECRET_KEY    nsec1... or 64 hex chars
    NOSTR_RELAYS        comma-separated wss:// URLs (defaults below)

A network with no credentials is skipped with a log line. With neither
configured the script is a no-op, which is its state until someone decides
which account this site posts as.

USAGE
-----
    python scripts/publish_social.py --dry-run
    python scripts/publish_social.py --feed-url https://brnosaires.com/feeds/all.atom.xml
"""
import argparse
import hashlib
import json
import os
import sys
import time
import urllib.request
import xml.etree.ElementTree as ElementTree
from datetime import datetime

ATOM = "{http://www.w3.org/2005/Atom}"
STATE_FILE = ".published-feeds.json"
DEFAULT_FEED = "https://brnosaires.com/feeds/all.atom.xml"
# Eight, not three, and every one of them answered when this list was written
# (2026-08-27). Three was too thin: on the first real send two of the three
# were down at the same moment — relay.damus.io returned 503 and
# relay.nostr.band refused the connection — and the post survived only because
# nos.lol happened to be up. One relay is enough for the event to exist, so the
# list is redundancy, not a broadcast requirement.
#
# It is also reach: Nostr has no global delivery, a reader's client pulls from
# the relay list *they* configured, so the more well-populated relays carry the
# event, the likelier an overlap. NOSTR_RELAYS overrides this whenever the list
# rots — relays come and go, and this one is a snapshot, not a fact.
DEFAULT_RELAYS = ",".join((
    "wss://relay.damus.io",
    "wss://nos.lol",
    "wss://relay.primal.net",
    "wss://nostr.mom",
    "wss://offchain.pub",
    "wss://nostr.oxtr.dev",
    "wss://relay.nostrplebs.com",
    "wss://nostr-pub.wellorder.net",
))

# Nostr has no local timeline and no account directory: an untagged note is
# reachable only by someone who already follows the key, and a new key is
# followed by nobody. Without these the posts would be invisible by
# construction — published, accepted by the relays, and read by no one.
#
# Fixed, not derived: the feed's categories are build folders ("07",
# "classes", "2026-marathon") and say nothing to a reader. The site is about
# one subject, so the subject is the same on every post.
NOSTR_HASHTAGS = ("tango", "milonga", "brno")

# Mastodon's default limit. Leave room for the URL and the separator.
MASTODON_LIMIT = 500

# Newest first in the feed; never send more than this in one run even if the
# state file is stale, so a mistake cannot become a flood.
MAX_PER_RUN = 5


def log(message):
    print(f"publish_social: {message}", flush=True)


# ---------------------------------------------------------------- feed


def fetch_feed(source):
    if source.startswith(("http://", "https://")):
        with urllib.request.urlopen(source, timeout=30) as response:
            return response.read()
    with open(source, "rb") as handle:
        return handle.read()


def parse_feed(raw):
    root = ElementTree.fromstring(raw)
    entries = []
    for node in root.findall(f"{ATOM}entry"):
        link = node.find(f"{ATOM}link")
        entries.append({
            "id": (node.findtext(f"{ATOM}id") or "").strip(),
            "title": (node.findtext(f"{ATOM}title") or "").strip(),
            "url": (link.get("href") if link is not None else "") or "",
            "published": (node.findtext(f"{ATOM}published") or "").strip(),
        })
    return [e for e in entries if e["id"] and e["url"]]


def compose(entry):
    """Title, blank line, canonical URL. Deliberately plain.

    No summary: the feed carries the rendered article body, and every consumer
    that matters unfurls the link into a card with the title, description and
    image the page already declares. Repeating that in the post text would show
    it twice.
    """
    url = entry["url"]
    room = MASTODON_LIMIT - len(url) - 2
    if room < 1:
        # Nothing sensible to say alongside a URL this long; the link is the
        # payload, so send it alone rather than a post the server will reject.
        return url
    title = entry["title"]
    if len(title) > room:
        title = title[: room - 1].rstrip() + "…"
    return f"{title}\n\n{url}"


# ---------------------------------------------------------------- mastodon


def post_mastodon(text, dry_run, created_at=None):
    instance = (os.environ.get("MASTODON_INSTANCE") or "").rstrip("/")
    token = os.environ.get("MASTODON_TOKEN")
    if not instance or not token:
        return None  # not configured

    if dry_run:
        log(f"[dry-run] would POST to {instance}/api/v1/statuses")
        return True

    payload = json.dumps({"status": text, "language": "cs",
                          "visibility": "public"}).encode()
    request = urllib.request.Request(
        f"{instance}/api/v1/statuses",
        data=payload,
        headers={"Authorization": f"Bearer {token}",
                 "Content-Type": "application/json",
                 # Same text twice is the same post, not two posts — this makes
                 # a retry after a timeout safe.
                 "Idempotency-Key": hashlib.sha256(text.encode()).hexdigest()},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        return 200 <= response.status < 300


# ---------------------------------------------------------------- nostr


_BECH32_CHARSET = "qpzry9x8gf2tvdw0s3jn54khce6mua7l"


def _bech32_polymod(values):
    generator = (0x3B6A57B2, 0x26508E6D, 0x1EA119FA, 0x3D4233DD, 0x2A1462B3)
    checksum = 1
    for value in values:
        top = checksum >> 25
        checksum = ((checksum & 0x1FFFFFF) << 5) ^ value
        for bit in range(5):
            checksum ^= generator[bit] if ((top >> bit) & 1) else 0
    return checksum


def _bech32_decode_to_bytes(value):
    """bech32 `nsec1...` -> 32 raw bytes, checksum verified.

    The checksum is the whole point of bech32 and skipping it is not harmless:
    a single mistyped character yields 32 different but perfectly valid key
    bytes, so signing succeeds and every announcement goes out under a key
    nobody controls and nobody can claim back. It looks like success in the log
    and only surfaces months later, when someone opens the account.
    """
    value = value.strip()
    if "1" not in value:
        raise ValueError("not bech32")
    human_readable, data = value.rsplit("1", 1)
    if len(data) < 7 or any(c not in _BECH32_CHARSET for c in data):
        raise ValueError("not bech32")
    values = [_BECH32_CHARSET.index(c) for c in data]
    expanded = ([ord(c) >> 5 for c in human_readable] + [0]
                + [ord(c) & 31 for c in human_readable])
    if _bech32_polymod(expanded + values) != 1:
        raise ValueError("bech32 checksum does not match — the key is mistyped")

    accumulator = bits = 0
    out = bytearray()
    for value5 in values[:-6]:
        accumulator = (accumulator << 5) | value5
        bits += 5
        while bits >= 8:
            bits -= 8
            out.append((accumulator >> bits) & 0xFF)
    if len(out) < 32:
        raise ValueError("bech32 payload is too short for a key")
    return bytes(out[:32])


def _nostr_key():
    raw = (os.environ.get("NOSTR_SECRET_KEY") or "").strip()
    if not raw:
        return None
    if raw.startswith("nsec"):
        return _bech32_decode_to_bytes(raw)
    return bytes.fromhex(raw)


def stable_created_at(published, now=None):
    """A Nostr timestamp that is identical on every re-send of the same entry.

    Derived from the article's own `published` date — not the clock — so a
    repeat run days later still produces the same event id. Falls back to the
    current time only when the feed gave no date, and is clamped to never be in
    the future, which relays reject.
    """
    now = int(now if now is not None else time.time())
    stamp = None
    if published:
        try:
            stamp = int(datetime.fromisoformat(published).timestamp())
        except ValueError:
            stamp = None
    if stamp is not None and stamp <= now:
        return stamp
    # This site announces events BEFORE they happen, so `published` is usually
    # in the future and relays reject a future timestamp. Clamping to `now`
    # would move on every run and defeat the whole point, so fall back to the
    # start of the current UTC day: stable across a day of retries, which is
    # the window a retry actually happens in (the next push, or the 12-hour
    # cron). A retry the day after does differ — that is the honest limit.
    return now - (now % 86400)


def _relay_accepted(reply, event_id):
    """True only if the relay explicitly said it took this event."""
    try:
        message = json.loads(reply)
    except (TypeError, ValueError):
        return False
    if not isinstance(message, list) or len(message) < 3:
        return False  # a NOTICE, or anything else that is not an answer
    return (message[0] == "OK" and message[1] == event_id
            and message[2] is True)


def build_nostr_event(text, secret, created_at=None):
    """The signed NIP-01 event, built in one place so the id can be tested.

    The id is a hash over the tags as well as the content, so tags added to
    the event dict but not to the hashed array produce an id that does not
    match its own event — which every relay rejects, and which no test that
    rebuilds the serialisation by hand would catch.
    """
    from coincurve import PrivateKey

    key = PrivateKey(secret)
    pubkey = key.public_key_xonly.format().hex()
    # NOT the clock. Nostr has no idempotency key: the event id hashes
    # (pubkey, created_at, content), so a wall-clock timestamp makes a re-send
    # a different event that every relay happily accepts a second time. Pinning
    # it to the article's publication date means a repeat run — after a lost
    # state file or a rejected push — produces the identical id, which relays
    # already hold and drop.
    created_at = int(created_at if created_at is not None else time.time())
    tags = [["t", tag] for tag in NOSTR_HASHTAGS]

    # NIP-01: the id is sha256 over a compact JSON array in exactly this shape.
    serialised = json.dumps([0, pubkey, created_at, 1, tags, text],
                            separators=(",", ":"), ensure_ascii=False)
    event_id = hashlib.sha256(serialised.encode()).hexdigest()
    return {
        "id": event_id,
        "pubkey": pubkey,
        "created_at": created_at,
        "kind": 1,
        "tags": tags,
        "content": text,
        "sig": key.sign_schnorr(bytes.fromhex(event_id)).hex(),
    }


def post_nostr(text, dry_run, created_at=None):
    secret = None
    try:
        secret = _nostr_key()
    except ValueError as exc:
        log(f"NOSTR_SECRET_KEY is not readable ({exc}) — skipping Nostr")
        return False
    if not secret:
        return None  # not configured

    try:
        from coincurve import PrivateKey  # noqa: F401 — build_nostr_event needs it
        from websocket import create_connection
    except ImportError:
        log("coincurve / websocket-client not installed — skipping Nostr")
        return False

    event = build_nostr_event(text, secret, created_at)
    event_id = event["id"]

    relays = [r.strip() for r in
              (os.environ.get("NOSTR_RELAYS") or DEFAULT_RELAYS).split(",") if r.strip()]
    if dry_run:
        log(f"[dry-run] would publish event {event_id[:12]}… to {len(relays)} relay(s)")
        return True

    delivered = 0
    for relay in relays:
        try:
            # 8s, not 15: in the probe every live relay answered inside 1.5s and the
            # dead ones failed by 7s, so a longer wait only buys dead air —
            # and it is paid per relay, per post.
            connection = create_connection(relay, timeout=8)
            connection.send(json.dumps(["EVENT", event]))
            reply = connection.recv()
            connection.close()
        except Exception as exc:  # noqa: BLE001 — one bad relay is not a failure
            log(f"relay {relay} unreachable: {exc}")
            continue
        # NIP-01 answers ["OK", <id>, <accepted>, <reason>]. Discarding that
        # boolean turned every rejection — rate limit, paid relay, spam filter,
        # a key the relay does not admit — into a silent success: the entry was
        # marked published and never retried, so it simply never appeared.
        if _relay_accepted(reply, event["id"]):
            delivered += 1
        else:
            log(f"relay {relay} rejected the event: {str(reply)[:200]}")
    # Nostr has no single authority; one relay that took it is published.
    return delivered > 0


# ---------------------------------------------------------------- main


def load_state(path):
    """{entry id -> sorted list of networks it already went to}, or None.

    The older shape was a flat list of ids. Both are read; the richer one is
    what gets written, because "posted to Mastodon but Nostr's relays were all
    down" is a real state and collapsing it to "not posted" made the next run
    duplicate the Mastodon post.
    """
    if not os.path.exists(path):
        return None
    with open(path, encoding="utf-8") as handle:
        raw = json.load(handle)
    published = raw.get("published", [])
    if isinstance(published, dict):
        return {key: set(value) for key, value in published.items()}
    return {entry_id: set() for entry_id in published}


def save_state(path, state, dry_run):
    if dry_run:
        return
    with open(path, "w", encoding="utf-8") as handle:
        json.dump({"published": {key: sorted(value)
                                 for key, value in sorted(state.items())}},
                  handle, indent=2, ensure_ascii=False)
        handle.write("\n")


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--feed-url", default=DEFAULT_FEED,
                        help=f"Atom feed URL or local path (default: {DEFAULT_FEED})")
    parser.add_argument("--state", default=STATE_FILE)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    try:
        entries = parse_feed(fetch_feed(args.feed_url))
    except Exception as exc:  # noqa: BLE001
        log(f"could not read the feed at {args.feed_url}: {exc}")
        return 1
    if not entries:
        log("feed is empty — nothing to do.")
        return 0

    known = load_state(args.state)
    if known is None:
        # First run. Record, do not post.
        save_state(args.state, {e["id"]: {"bootstrap"} for e in entries}, args.dry_run)
        log(f"first run — recorded {len(entries)} existing entries without posting. "
            "The next new article is the first one announced.")
        return 0

    networks = {"Mastodon": post_mastodon, "Nostr": post_nostr}
    fresh = [e for e in entries
             if (networks.keys() - known.get(e["id"], set()))
             and "bootstrap" not in known.get(e["id"], set())]
    if not fresh:
        log("nothing new since the last run.")
        return 0
    # Oldest first. The feed is newest-first and on this site "newest" means the
    # furthest-future event, so slicing it as-is posted the events furthest away
    # and dropped the ones happening next — exactly backwards.
    fresh.reverse()
    if len(fresh) > MAX_PER_RUN:
        log(f"{len(fresh)} new entries — posting {MAX_PER_RUN} now, the rest on "
            f"the next run.")
        # NOT marked as published: an editor adding a month of milongas in one
        # push is normal here, and the overflow used to be recorded as sent and
        # never announced at all.
        fresh = fresh[:MAX_PER_RUN]

    configured = False
    for entry in fresh:
        text = compose(entry)
        results = []
        created_at = stable_created_at(entry.get("published"))
        already = set(known.get(entry["id"], set()))
        for name, sender in networks.items():
            if name in already:
                continue  # this one already has it; only the other still owes
            try:
                outcome = sender(text, args.dry_run, created_at)
            except Exception as exc:  # noqa: BLE001
                log(f"{name} failed for {entry['url']}: {exc}")
                outcome = False
            if outcome is None:
                # Not configured. Recorded as settled rather than skipped: left
                # pending, every entry stayed "fresh" forever and ate the
                # per-run budget, so entries behind them were never announced.
                # It also means switching a network on later does not backfill
                # the archive, which is the behaviour you want.
                already.add(name)
                continue
            configured = True
            results.append(outcome)
            if outcome:
                already.add(name)
            log(f"{name}: {'ok' if outcome else 'FAILED'} — {entry['title']}")

        # Recorded per network, so a retry after "Mastodon fine, every Nostr
        # relay down" sends only the Nostr half. Written after each entry, not
        # once at the end, so a job killed mid-run loses nothing it already did.
        known[entry["id"]] = already
        save_state(args.state, known, args.dry_run)

    if not configured:
        log("no network is configured (MASTODON_INSTANCE/MASTODON_TOKEN, "
            "NOSTR_SECRET_KEY) — nothing was sent.")
        return 0

    save_state(args.state, known, args.dry_run)
    return 0


if __name__ == "__main__":
    sys.exit(main())
