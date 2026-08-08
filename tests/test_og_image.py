"""The JPEG twin that link scrapers can actually decode.

The whole point is that og:image never again points at a format Facebook
cannot read, and never at a file that is not there.
"""
import os
import re
import shutil
import tempfile
import unittest

from tests import build_site, plugin_path  # noqa: F401

import og_image


class Passthrough(unittest.TestCase):
    def test_lowercase_raster_extensions_pass_through(self):
        for ref in ("/images/a.jpg", "/images/a.jpeg", "/images/a.png"):
            self.assertTrue(og_image._passthrough(ref), ref)

    def test_avif_and_webp_do_not(self):
        for ref in ("/images/a.avif", "/images/a.webp", "/images/a.jfif"):
            self.assertFalse(og_image._passthrough(ref), ref)

    def test_uppercase_jpeg_does_not_pass_through(self):
        # Deliberate: GitHub Pages does not reliably set image/jpeg for `.JPEG`
        # and the stricter scrapers refuse it.
        for ref in ("/images/a.JPEG", "/images/a.JPG", "/images/a.PNG"):
            self.assertFalse(og_image._passthrough(ref), ref)


class DerivativePath(unittest.TestCase):
    def test_mirrors_the_source_tree(self):
        self.assertEqual(og_image._derivative_path("images/events/2026/a.avif"),
                         os.path.join("og", "images/events/2026/a.jpg"))

    def test_same_basename_in_two_folders_does_not_collide(self):
        first = og_image._derivative_path("images/a/photo.avif")
        second = og_image._derivative_path("images/b/photo.avif")
        self.assertNotEqual(first, second)


class SourceResolution(unittest.TestCase):
    def setUp(self):
        self.root = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.root, ignore_errors=True)

    def touch(self, relative):
        full = os.path.join(self.root, relative)
        os.makedirs(os.path.dirname(full), exist_ok=True)
        open(full, "wb").close()

    def test_leading_slash_is_optional(self):
        self.touch("images/a.avif")
        for ref in ("/images/a.avif", "images/a.avif"):
            source, rel = og_image._resolve_source(ref, self.root)
            self.assertIsNotNone(source, ref)
            self.assertEqual(rel, "images/a.avif")

    def test_literal_spelling_wins_over_the_decoded_one(self):
        # A filename may legitimately contain a percent sign, so the literal
        # path must be tried first.
        self.touch("images/a%20b.avif")
        source, _rel = og_image._resolve_source("/images/a%20b.avif", self.root)
        self.assertTrue(source.endswith("a%20b.avif"))

    def test_falls_back_to_the_decoded_spelling(self):
        self.touch("images/a b.avif")
        source, rel = og_image._resolve_source("/images/a%20b.avif", self.root)
        self.assertTrue(source.endswith("a b.avif"))
        self.assertEqual(rel, "images/a b.avif")

    def test_missing_file_resolves_to_none(self):
        source, _rel = og_image._resolve_source("/images/nope.avif", self.root)
        self.assertIsNone(source)

    def test_traversal_out_of_the_content_root_is_refused(self):
        outside = os.path.join(os.path.dirname(self.root), "secret.avif")
        open(outside, "wb").close()
        try:
            source, _rel = og_image._resolve_source(
                "/../" + os.path.basename(outside), self.root)
            self.assertIsNone(source, "escaped the content root")
        finally:
            os.remove(outside)


class BuiltSite(unittest.TestCase):
    """The invariant that matters, asserted against the real output."""

    @classmethod
    def setUpClass(cls):
        cls.output = build_site()
        cls.refs = []
        for root, _dirs, files in os.walk(cls.output):
            for name in files:
                if not name.endswith(".html"):
                    continue
                with open(os.path.join(root, name), encoding="utf-8",
                          errors="replace") as handle:
                    cls.refs += re.findall(
                        r'<meta property="og:image" content="([^"]+)"', handle.read())

    def test_every_og_image_is_a_format_scrapers_decode(self):
        bad = sorted({r for r in self.refs
                      if os.path.splitext(r)[1] not in (".jpg", ".jpeg", ".png")})
        self.assertEqual(bad, [], f"undecodable og:image formats still shipped: {bad}")

    def test_every_og_image_exists_in_the_output_tree(self):
        prefix = "https://brnosaires.com/"
        missing = sorted({r for r in self.refs if r.startswith(prefix)
                          and not os.path.isfile(
                              os.path.join(self.output, r[len(prefix):]))})
        self.assertEqual(missing, [], f"og:image 404s: {missing}")

    def test_most_pages_carry_one(self):
        self.assertGreater(len(self.refs), 300)


if __name__ == "__main__":
    unittest.main()
