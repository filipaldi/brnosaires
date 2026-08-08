"""Images that live beside their .md, and the guard that stops the footgun.

The guard is the reason this file exists. An event with `recurrence:` or
`series:` becomes many pages from one source file; a co-located image would be
copied next to exactly one of them and 404 on the rest — silently, on a page
nobody opens until the event is next week.
"""
import os
import shutil
import tempfile
import unittest

from tests import build_site, plugin_path  # noqa: F401

import colocated_images


class _Content:
    """The attributes the plugin reads off a Pelican Article."""

    def __init__(self, source_path, preview_image, url="slug/", **metadata):
        self.source_path = source_path
        self.preview_image = preview_image
        self.url = url
        self.metadata = dict(metadata, preview_image=preview_image)


class _Generator:
    def __init__(self, articles):
        self.articles = articles


class BareFilename(unittest.TestCase):
    def test_recognises_a_bare_filename(self):
        self.assertTrue(colocated_images._is_bare_filename("poster.avif"))

    def test_rejects_anything_with_a_path(self):
        for value in ("/images/poster.avif", "images/poster.avif",
                      "sub/poster.avif", "", None, 3):
            self.assertFalse(colocated_images._is_bare_filename(value), repr(value))


class Guard(unittest.TestCase):
    def test_recurrence_blocks(self):
        self.assertEqual(_Content("a.md", "p.avif", recurrence="weekly monday")
                         and colocated_images._blocking_field(
                             _Content("a.md", "p.avif", recurrence="weekly monday")),
                         "recurrence")

    def test_series_blocks(self):
        self.assertEqual(colocated_images._blocking_field(
            _Content("a.md", "p.avif", series="milonga-u-draka")), "series")

    def test_a_plain_article_does_not_block(self):
        self.assertIsNone(colocated_images._blocking_field(_Content("a.md", "p.avif")))


class Resolve(unittest.TestCase):
    def setUp(self):
        colocated_images._COPIES.clear()
        colocated_images.SOURCE_BY_REF.clear()
        self.root = tempfile.mkdtemp()

    def tearDown(self):
        colocated_images._COPIES.clear()
        colocated_images.SOURCE_BY_REF.clear()
        shutil.rmtree(self.root, ignore_errors=True)

    def article(self, name="poster.avif", create=True, **metadata):
        source_md = os.path.join(self.root, "a.md")
        open(source_md, "w").close()
        if create:
            open(os.path.join(self.root, name), "wb").close()
        return _Content(source_md, name, **metadata)

    def test_rewrites_to_the_article_url_and_queues_a_copy(self):
        content = self.article()
        colocated_images._resolve(_Generator([content]))
        self.assertEqual(content.preview_image, "/slug/poster.avif")
        self.assertEqual(content.metadata["preview_image"], "/slug/poster.avif")
        self.assertIn("slug/poster.avif", colocated_images._COPIES)

    def test_writes_metadata_too_so_english_clones_inherit_it(self):
        # i18n_fallback builds the /en/ clone from `metadata`, not from the
        # attribute, so a value written only onto the attribute never arrives.
        content = self.article()
        colocated_images._resolve(_Generator([content]))
        self.assertEqual(content.metadata["preview_image"], content.preview_image)

    def test_registers_the_real_source_for_og_image(self):
        content = self.article()
        colocated_images._resolve(_Generator([content]))
        self.assertEqual(
            colocated_images.SOURCE_BY_REF["/slug/poster.avif"],
            os.path.join(self.root, "poster.avif"))

    def test_recurrence_article_is_left_untouched_and_warns(self):
        content = self.article(recurrence="weekly monday")
        with self.assertLogs("colocated_images", level="WARNING") as captured:
            colocated_images._resolve(_Generator([content]))
        self.assertEqual(content.preview_image, "poster.avif")
        self.assertEqual(colocated_images._COPIES, {})
        self.assertIn("recurrence", captured.output[0])

    def test_series_article_is_left_untouched(self):
        content = self.article(series="milonga-u-draka")
        with self.assertLogs("colocated_images", level="WARNING"):
            colocated_images._resolve(_Generator([content]))
        self.assertEqual(content.preview_image, "poster.avif")
        self.assertEqual(colocated_images._COPIES, {})

    def test_missing_sibling_warns_and_changes_nothing(self):
        content = self.article(create=False)
        with self.assertLogs("colocated_images", level="WARNING"):
            colocated_images._resolve(_Generator([content]))
        self.assertEqual(content.preview_image, "poster.avif")
        self.assertEqual(colocated_images._COPIES, {})

    def test_absolute_paths_are_ignored_entirely(self):
        content = _Content(os.path.join(self.root, "a.md"), "/images/x.avif")
        colocated_images._resolve(_Generator([content]))
        self.assertEqual(content.preview_image, "/images/x.avif")
        self.assertEqual(colocated_images._COPIES, {})


class BuiltSite(unittest.TestCase):
    """The piloted article, end to end in a real build."""

    @classmethod
    def setUpClass(cls):
        cls.output = build_site()

    def test_the_colocated_image_was_copied_next_to_its_page(self):
        self.assertTrue(os.path.isfile(os.path.join(
            self.output, "dvacet-let-s-blancou", "dvacet-let-s-blancou.avif")))

    def test_the_page_and_its_english_twin_both_reference_a_real_file(self):
        import re
        for page in ("dvacet-let-s-blancou/index.html",
                     "en/dvacet-let-s-blancou/index.html"):
            with open(os.path.join(self.output, page), encoding="utf-8") as handle:
                html = handle.read()
            refs = re.findall(r'<img src="([^"]*dvacet[^"]*)"', html)
            self.assertTrue(refs, f"no image on {page}")
            for ref in refs:
                self.assertTrue(os.path.isfile(os.path.join(self.output, ref)),
                                f"{page} points at missing {ref}")

    def test_the_english_twin_still_gets_a_social_preview(self):
        import re
        with open(os.path.join(self.output, "en/dvacet-let-s-blancou/index.html"),
                  encoding="utf-8") as handle:
            found = re.search(r'<meta property="og:image" content="([^"]+)"',
                              handle.read())
        self.assertIsNotNone(found, "en twin lost its og:image")
        relative = found.group(1).replace("https://brnosaires.com/", "")
        self.assertTrue(os.path.isfile(os.path.join(self.output, relative)))


if __name__ == "__main__":
    unittest.main()
