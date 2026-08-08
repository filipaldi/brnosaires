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
DEFAULT_RELAYS = "wss://relay.damus.io,wss://nos.lol,wss://relay.nostr.band"

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
    title = entry["title"]
    room = MASTODON_LIMIT - len(entry["url"]) - 2
    if len(title) > room:
        title = title[: max(0, room - 1)].rstrip() + "…"
    return f"{title}\n\n{entry['url']}"


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


def _bech32_decode_to_bytes(value):
    """Minimal bech32 -> 32 raw bytes, enough to read an `nsec1...` key.

    Not a general decoder: it skips the checksum check, because a malformed key
    fails at signing anyway and a wrong key cannot be made right by validating
    it more politely.
    """
    if "1" not in value:
        raise ValueError("not bech32")
    data = value.rsplit("1", 1)[1]
    values = [_BECH32_CHARSET.index(c) for c in data[:-6]]
    accumulator = bits = 0
    out = bytearray()
    for value5 in values:
        accumulator = (accumulator << 5) | value5
        bits += 5
        while bits >= 8:
            bits -= 8
            out.append((accumulator >> bits) & 0xFF)
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
    stamp = now
    if published:
        try:
            stamp = int(datetime.fromisoformat(published).timestamp())
        except ValueError:
            pass
    return min(stamp, now)


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
        from coincurve import PrivateKey
        from websocket import create_connection
    except ImportError:
        log("coincurve / websocket-client not installed — skipping Nostr")
        return False

    key = PrivateKey(secret)
    pubkey = key.public_key_xonly.format().hex()
    # NOT the clock. Nostr has no idempotency key: the event id hashes
    # (pubkey, created_at, content), so a wall-clock timestamp makes a re-send
    # a different event that every relay happily accepts a second time. Pinning
    # it to the article's publication date means a repeat run — after a lost
    # state file or a rejected push — produces the identical id, which relays
    # already hold and drop.
    created_at = int(created_at if created_at is not None else time.time())

    # NIP-01: the id is sha256 over a compact JSON array in exactly this shape.
    serialised = json.dumps([0, pubkey, created_at, 1, [], text],
                            separators=(",", ":"), ensure_ascii=False)
    event_id = hashlib.sha256(serialised.encode()).hexdigest()
    event = {
        "id": event_id,
        "pubkey": pubkey,
        "created_at": created_at,
        "kind": 1,
        "tags": [],
        "content": text,
        "sig": key.sign_schnorr(bytes.fromhex(event_id)).hex(),
    }

    relays = [r.strip() for r in
              (os.environ.get("NOSTR_RELAYS") or DEFAULT_RELAYS).split(",") if r.strip()]
    if dry_run:
        log(f"[dry-run] would publish event {event_id[:12]}… to {len(relays)} relay(s)")
        return True

    delivered = 0
    for relay in relays:
        try:
            connection = create_connection(relay, timeout=15)
            connection.send(json.dumps(["EVENT", event]))
            connection.recv()  # relay replies with ["OK", id, true/false, msg]
            connection.close()
            delivered += 1
        except Exception as exc:  # noqa: BLE001 — one bad relay is not a failure
            log(f"relay {relay} refused: {exc}")
    # Nostr has no single authority; one relay that took it is published.
    return delivered > 0


# ---------------------------------------------------------------- main


def load_state(path):
    if not os.path.exists(path):
        return None
    with open(path, encoding="utf-8") as handle:
        return set(json.load(handle).get("published", []))


def save_state(path, ids, dry_run):
    if dry_run:
        return
    with open(path, "w", encoding="utf-8") as handle:
        json.dump({"published": sorted(ids)}, handle, indent=2, ensure_ascii=False)
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
        save_state(args.state, {e["id"] for e in entries}, args.dry_run)
        log(f"first run — recorded {len(entries)} existing entries without posting. "
            "The next new article is the first one announced.")
        return 0

    fresh = [e for e in entries if e["id"] not in known]
    if not fresh:
        log("nothing new since the last run.")
        return 0
    if len(fresh) > MAX_PER_RUN:
        log(f"{len(fresh)} new entries, posting the newest {MAX_PER_RUN} "
            f"and recording the rest — refusing to flood.")
        known |= {e["id"] for e in fresh[MAX_PER_RUN:]}
        fresh = fresh[:MAX_PER_RUN]

    configured = False
    for entry in reversed(fresh):  # oldest first, so timelines read in order
        text = compose(entry)
        results = []
        created_at = stable_created_at(entry.get("published"))
        for name, sender in (("Mastodon", post_mastodon), ("Nostr", post_nostr)):
            try:
                outcome = sender(text, args.dry_run, created_at)
            except Exception as exc:  # noqa: BLE001
                log(f"{name} failed for {entry['url']}: {exc}")
                outcome = False
            if outcome is None:
                continue  # not configured
            configured = True
            results.append(outcome)
            log(f"{name}: {'ok' if outcome else 'FAILED'} — {entry['title']}")

        if not results:
            continue
        if all(results):
            known.add(entry["id"])
        # A partial success is left unmarked on purpose: a duplicate on the
        # network that already took it is a smaller harm than an announcement
        # that silently never goes out.

    if not configured:
        log("no network is configured (MASTODON_INSTANCE/MASTODON_TOKEN, "
            "NOSTR_SECRET_KEY) — nothing was sent.")
        return 0

    save_state(args.state, known, args.dry_run)
    return 0


if __name__ == "__main__":
    sys.exit(main())
