"""The CI gate that resolves every internal reference against output/.

Both directions are bugs and both are tested: a miss ships a 404, a false
positive blocks a good deploy. The `<base href>` case is here because getting
it wrong once reported the entire site as broken.
"""
import os
import shutil
import tempfile
import unittest

from tests import build_site, script_path  # noqa: F401

import check_links


BASE = '<base href="https://brnosaires.com/">'


class _Tree:
    """A throwaway output/ tree written from a {path: content} dict."""

    def __init__(self, files):
        self.root = tempfile.mkdtemp()
        for relative, content in files.items():
            full = os.path.join(self.root, relative)
            os.makedirs(os.path.dirname(full), exist_ok=True)
            with open(full, "w", encoding="utf-8") as handle:
                handle.write(content)

    def check(self):
        _pages, broken = check_links.check(self.root)
        return {target: sorted(set(pages)) for target, pages in broken.items()}

    def close(self):
        shutil.rmtree(self.root, ignore_errors=True)


def page(body):
    return f"<html><head>{BASE}</head><body>{body}</body></html>"


class Resolution(unittest.TestCase):
    def tearDown(self):
        if getattr(self, "tree", None):
            self.tree.close()

    def build(self, files):
        self.tree = _Tree(files)
        return self.tree.check()

    def test_directory_url_resolves_through_index_html(self):
        self.assertEqual(self.build({
            "index.html": page('<a href="/akce/">akce</a>'),
            "akce/index.html": page("ok"),
        }), {})

    def test_relative_href_resolves_against_base_not_the_page_directory(self):
        # Without honouring <base href>, "akce/" on /category/x/ would resolve
        # to /category/x/akce/ and the whole site reads as broken.
        self.assertEqual(self.build({
            "category/x/index.html": page('<a href="akce/">akce</a>'),
            "akce/index.html": page("ok"),
        }), {})

    def test_relative_href_without_base_resolves_against_the_page_directory(self):
        files = {
            "category/x/index.html": '<html><body><a href="sibling/">s</a></body></html>',
            "category/x/sibling/index.html": "ok",
        }
        self.assertEqual(self.build(files), {})

    def test_missing_target_is_reported_with_its_referrer(self):
        broken = self.build({"index.html": page('<a href="/nope/">x</a>')})
        self.assertEqual(broken, {"/nope/": ["index.html"]})

    def test_siteurl_absolute_link_is_treated_as_internal(self):
        broken = self.build({
            "index.html": page('<a href="https://brnosaires.com/nope/">x</a>')})
        self.assertEqual(list(broken), ["https://brnosaires.com/nope/"])

    def test_percent_encoded_reference_finds_the_literal_file(self):
        self.assertEqual(self.build({
            "index.html": page('<img src="/images/a%20b.avif">'),
            "images/a b.avif": "binary",
        }), {})

    def test_query_and_fragment_are_stripped_before_lookup(self):
        self.assertEqual(self.build({
            "index.html": page('<a href="/akce/?x=1#top">a</a>'),
            "akce/index.html": "ok",
        }), {})


class Coverage(unittest.TestCase):
    """Every attribute the site actually emits an internal URL in."""

    def tearDown(self):
        if getattr(self, "tree", None):
            self.tree.close()

    def build(self, files):
        self.tree = _Tree(files)
        return self.tree.check()

    def test_og_image_is_checked(self):
        broken = self.build({"index.html": page(
            '<meta property="og:image" content="https://brnosaires.com/og/x.jpg">')})
        self.assertIn("https://brnosaires.com/og/x.jpg", broken)

    def test_twitter_image_is_checked(self):
        broken = self.build({"index.html": page(
            '<meta name="twitter:image" content="/og/x.jpg">')})
        self.assertIn("/og/x.jpg", broken)

    def test_json_ld_image_is_checked(self):
        broken = self.build({"index.html": page(
            '<script type="application/ld+json">{"image": "/og/x.jpg"}</script>')})
        self.assertIn("/og/x.jpg", broken)

    def test_img_and_link_and_script_are_checked(self):
        broken = self.build({"index.html": page(
            '<img src="/a.avif"><link rel="stylesheet" href="/b.css">'
            '<script src="/c.js"></script>')})
        self.assertEqual(sorted(broken), ["/a.avif", "/b.css", "/c.js"])


class Skipping(unittest.TestCase):
    """Things that must NOT be reported, or the gate blocks good deploys."""

    def tearDown(self):
        if getattr(self, "tree", None):
            self.tree.close()

    def build(self, files):
        self.tree = _Tree(files)
        return self.tree.check()

    def test_external_schemes_are_skipped(self):
        self.assertEqual(self.build({"index.html": page(
            '<a href="https://example.com/x">e</a>'
            '<a href="mailto:a@b.cz">m</a>'
            '<a href="tel:+420123">t</a>'
            '<a href="webcal://brnosaires.com/calendars/x.ics">w</a>'
            '<img src="data:image/gif;base64,R0lGOD">')}), {})

    def test_bare_fragment_is_skipped(self):
        self.assertEqual(self.build({"index.html": page('<a href="#main">skip</a>')}), {})

    def test_protocol_relative_url_is_skipped(self):
        self.assertEqual(self.build({"index.html": page(
            '<script src="//cdn.example.com/x.js"></script>')}), {})


class RealBuild(unittest.TestCase):
    """The gate against the actual site, if it has been built."""

    def test_built_output_has_no_broken_references(self):
        pages, broken = check_links.check(build_site())
        self.assertGreater(pages, 100, "suspiciously few pages — bad build?")
        self.assertEqual(broken, {},
                         f"{len(broken)} broken target(s): {sorted(broken)[:5]}")


if __name__ == "__main__":
    unittest.main()
