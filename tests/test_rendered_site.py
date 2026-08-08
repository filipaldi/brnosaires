"""Invariants of the rendered HTML: structure, accessibility, structured data.

These are the things that only break in the output — no template diff shows
them, and nobody notices until a screen reader user cannot navigate or Google
silently drops a rich result.
"""
import json
import os
import re
import unittest
from html import unescape
from urllib.parse import parse_qs, urlsplit

from tests import build_site

HEADING = re.compile(r"<h([1-6])\b", re.IGNORECASE)
SCRIPT_OR_STYLE = re.compile(r"<(script|style)\b.*?</\1>", re.DOTALL | re.IGNORECASE)
LD_JSON = re.compile(
    r'<script type="application/ld\+json">(.*?)</script>', re.DOTALL)


# Every page the theme rendered carries this. The CMS shell at /admin/ is a
# standalone SPA served as a static file and is deliberately not themed, so it
# has no skip link, no feed link and no headings — testing it against the
# theme's invariants would be testing the wrong thing.
THEMED = '<base href="https://brnosaires.com/">'


def pages(output):
    for root, _dirs, files in os.walk(output):
        for name in sorted(files):
            if name.endswith(".html"):
                full = os.path.join(root, name)
                with open(full, encoding="utf-8", errors="replace") as handle:
                    html = handle.read()
                if THEMED in html:
                    yield os.path.relpath(full, output), html


class _Built(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.output = build_site()
        cls.pages = list(pages(cls.output))
        assert len(cls.pages) > 100, "suspiciously small build"


class Headings(_Built):
    """One h1, first, and no skipped levels — the document outline a screen
    reader navigates by."""

    def outlines(self):
        for path, html in self.pages:
            levels = [int(m) for m in HEADING.findall(SCRIPT_OR_STYLE.sub("", html))]
            if levels:
                yield path, levels

    def test_the_first_heading_is_always_h1(self):
        bad = [p for p, levels in self.outlines() if levels[0] != 1]
        self.assertEqual(bad, [], f"pages not starting at h1: {bad[:5]}")

    def test_there_is_exactly_one_h1(self):
        bad = [p for p, levels in self.outlines() if levels.count(1) != 1]
        self.assertEqual(bad, [], f"pages with 0 or 2+ h1: {bad[:5]}")

    def test_no_level_is_skipped(self):
        bad = []
        for path, levels in self.outlines():
            previous = levels[0]
            for level in levels[1:]:
                if level > previous + 1:
                    bad.append(f"{path}: h{previous}->h{level}")
                    break
                previous = level
        self.assertEqual(bad, [], f"skipped heading levels: {bad[:5]}")


class SkipLink(_Built):
    def test_every_page_has_one_pointing_at_a_real_target(self):
        for path, html in self.pages:
            found = re.search(r'<a class="skip-link" href="([^"]+)"', html)
            self.assertIsNotNone(found, f"no skip link on {path}")
            fragment = found.group(1).split("#")[-1]
            self.assertIn(f'id="{fragment}"', html,
                          f"skip link on {path} points at a missing target")

    def test_the_href_repeats_the_page_url(self):
        # A bare "#main" resolves against <base href>, not the current
        # document, so on every page but the homepage it navigated away to the
        # homepage — the opposite of what a skip link is for.
        for path, html in self.pages:
            href = re.search(r'<a class="skip-link" href="([^"]+)"', html).group(1)
            self.assertTrue(href.startswith("https://brnosaires.com/"),
                            f"skip link on {path} is base-relative: {href}")
            expected = "" if path == "index.html" else path[: -len("index.html")]
            self.assertEqual(href, f"https://brnosaires.com/{expected}#main", path)

    def test_the_target_can_take_focus(self):
        # Safari will not focus a non-focusable fragment target; it scrolls and
        # leaves focus on the link, so the next Tab returns to the nav.
        for path, html in self.pages:
            self.assertRegex(html, r'<main id="main"[^>]*tabindex="-1"',
                             f"main on {path} cannot receive focus")

    def test_it_is_the_first_link_in_the_body(self):
        # A skip link that is not first in tab order skips nothing.
        for path, html in self.pages:
            body = html.split("<body", 1)[-1]
            first = re.search(r"<a\b[^>]*>", body)
            self.assertIn("skip-link", first.group(0),
                          f"something is tabbable before the skip link on {path}")

    def test_it_is_localised(self):
        cs = dict(self.pages)["index.html"]
        en = dict(self.pages)["en/index.html"]
        self.assertIn("Přeskočit na obsah", cs)
        self.assertIn("Skip to content", en)


class StructuredData(_Built):
    """Every JSON-LD block must parse. A trailing comma silently voids the
    whole rich result and nothing on the page looks different."""

    def test_every_json_ld_block_is_valid_json(self):
        checked = 0
        for path, html in self.pages:
            for block in LD_JSON.findall(html):
                checked += 1
                try:
                    json.loads(block)
                except ValueError as exc:
                    self.fail(f"invalid JSON-LD on {path}: {exc}\n{block[:400]}")
        self.assertGreater(checked, 100, "suspiciously few JSON-LD blocks")

    def test_event_places_carry_a_name_not_a_street(self):
        # `event_address()` puts the first comma-separated part in `name`, so a
        # value with no venue name makes JSON-LD claim the milonga happens at a
        # place called "Přízova 216/18".
        offenders = set()
        street_like = re.compile(r"\d")
        for path, html in self.pages:
            for block in LD_JSON.findall(html):
                data = json.loads(block)
                location = data.get("location") if isinstance(data, dict) else None
                if not isinstance(location, dict):
                    continue
                name = location.get("name")
                address = location.get("address") or {}
                if (name and street_like.search(name)
                        and not address.get("streetAddress")):
                    offenders.add(f"{path}: {name}")
        self.assertEqual(sorted(offenders), [], f"street used as venue name: {offenders}")


class SocialPreviews(_Built):
    def test_og_and_twitter_image_always_agree(self):
        for path, html in self.pages:
            og = re.search(r'<meta property="og:image" content="([^"]+)"', html)
            twitter = re.search(r'<meta name="twitter:image" content="([^"]+)"', html)
            self.assertEqual(bool(og), bool(twitter), f"only one image tag on {path}")
            if og:
                self.assertEqual(og.group(1), twitter.group(1), path)


class MapLinks(_Built):
    def test_every_venue_link_carries_a_non_empty_query_and_a_label(self):
        found = 0
        for path, html in self.pages:
            for anchor in re.findall(
                    r'<a href="(https://www\.openstreetmap\.org/search\?[^"]*)"'
                    r'(.*?)</a>', html, re.DOTALL):
                found += 1
                url, rest = anchor
                query = parse_qs(urlsplit(unescape(url)).query)
                self.assertTrue(query.get("query", [""])[0].strip(),
                                f"empty map query on {path}")
                self.assertIn('rel="noopener"', rest, path)
                self.assertIn("aria-label=", rest, path)
        self.assertGreater(found, 100, "venue links disappeared")

    def test_no_venue_link_points_at_google_maps(self):
        for path, html in self.pages:
            self.assertNotIn("google.com/maps", html, path)


class Feed(_Built):
    def test_the_feed_exists_and_is_linked_from_every_page(self):
        self.assertTrue(os.path.isfile(
            os.path.join(self.output, "feeds", "all.atom.xml")))
        for path, html in self.pages:
            self.assertIn('type="application/atom+xml"', html, f"no feed link on {path}")

    def test_the_feed_parses_and_its_links_resolve(self):
        import xml.etree.ElementTree as ElementTree
        atom = "{http://www.w3.org/2005/Atom}"
        root = ElementTree.parse(
            os.path.join(self.output, "feeds", "all.atom.xml")).getroot()
        entries = root.findall(f"{atom}entry")
        self.assertGreater(len(entries), 5)
        for entry in entries:
            href = entry.find(f"{atom}link").get("href")
            relative = href.replace("https://brnosaires.com/", "").strip("/")
            self.assertTrue(
                os.path.isfile(os.path.join(self.output, relative, "index.html")),
                f"feed links to a page that is not in the build: {href}")


class Admin(_Built):
    def test_the_cms_is_served_and_kept_out_of_search(self):
        self.assertTrue(os.path.isfile(os.path.join(self.output, "admin", "index.html")))
        self.assertTrue(os.path.isfile(os.path.join(self.output, "admin", "config.yml")))
        with open(os.path.join(self.output, "robots.txt"), encoding="utf-8") as handle:
            self.assertIn("Disallow: /admin/", handle.read())

    def test_the_cms_config_is_valid_yaml_with_raw_markdown_bodies(self):
        try:
            import yaml
        except ImportError:
            self.skipTest("PyYAML not installed")
        with open(os.path.join(self.output, "admin", "config.yml"),
                  encoding="utf-8") as handle:
            config = yaml.safe_load(handle)

        def body_fields(fields):
            for field in fields:
                if field.get("widget") in ("markdown", "richtext"):
                    yield field

        for collection in config["collections"]:
            for field in body_fields(collection["fields"]):
                # Rich text would rewrite the 125 custom widget tags in the
                # content on first save.
                self.assertEqual(field.get("modes"), ["raw"],
                                 f"{collection['name']}.{field['name']} is not raw")


if __name__ == "__main__":
    unittest.main()
