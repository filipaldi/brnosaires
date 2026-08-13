"""The image converter, which deletes originals and rewrites content.

The dangerous part is not the encoding, it is the path bookkeeping: a mispaired
old->new rewrite silently points an article at a file that is not there, and
the original is gone by then. Every test here is about that bookkeeping.
"""
import os
import shutil
import tempfile
import unittest

from tests import script_path  # noqa: F401

import convert_images


class Spellings(unittest.TestCase):
    """reference_spellings() feeds a positional zip() in rewrite_markdown, so
    the old and new lists must stay aligned for every possible path shape."""

    def test_plain_path_has_two_spellings(self):
        self.assertEqual(convert_images.reference_spellings("images/a.jpg"),
                         ["/images/a.jpg", "images/a.jpg"])

    def test_path_needing_encoding_has_four(self):
        self.assertEqual(convert_images.reference_spellings("images/a b.jpg"),
                         ["/images/a b.jpg", "/images/a%20b.jpg",
                          "images/a b.jpg", "images/a%20b.jpg"])

    def test_old_and_new_spelling_lists_stay_aligned(self):
        # The failure this guards against: a source path that needs encoding
        # (4 spellings) mapping to a target that does not (2), so zip() pairs
        # "/images/a b.jpg" -> "/images/a b.avif" and then
        # "/images/a%20b.jpg" -> "images/a b.avif" — dropping the leading slash
        # and corrupting the reference.
        for source in ["images/a.jpg", "images/a b.jpg", "images/á.jpg",
                       "images/a(1).jpg", "images/dir name/a b.jpg",
                       "images/100%.jpg"]:
            target = os.path.splitext(source)[0] + ".avif"
            old = convert_images.reference_spellings(source)
            new = convert_images.reference_spellings(target)
            self.assertEqual(len(old), len(new),
                             f"spelling lists differ in length for {source!r}: "
                             f"{old} vs {new}")
            for o, n in zip(old, new):
                self.assertEqual(o.startswith("/"), n.startswith("/"),
                                 f"leading slash mismatch: {o!r} -> {n!r}")
                # Only the extension may differ; everything before it must be
                # the same spelling on both sides of the pair.
                self.assertEqual(o[: o.rindex(".")], n[: n.rindex(".")],
                                 f"stem mismatch: {o!r} -> {n!r}")


class Planning(unittest.TestCase):
    """plan() must refuse rather than guess whenever it could destroy data."""

    def setUp(self):
        self.root = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.root, ignore_errors=True)

    def touch(self, relative):
        full = os.path.join(self.root, relative)
        os.makedirs(os.path.dirname(full), exist_ok=True)
        open(full, "wb").close()
        return full

    def test_ordinary_source_is_planned(self):
        self.touch("images/a.jpg")
        jobs, conflicts = convert_images.plan(
            convert_images.find_sources(self.root), self.root)
        self.assertEqual(conflicts, [])
        self.assertEqual(len(jobs), 1)
        self.assertTrue(jobs[0][1].endswith("images/a.avif"))

    def test_existing_avif_blocks_the_whole_run(self):
        self.touch("images/a.jpg")
        self.touch("images/a.avif")
        jobs, conflicts = convert_images.plan(
            convert_images.find_sources(self.root), self.root)
        self.assertEqual(jobs, [])
        self.assertEqual(len(conflicts), 1)
        self.assertIn("already exists", conflicts[0])

    def test_two_sources_collapsing_onto_one_target_block_the_run(self):
        self.touch("images/a.jpg")
        self.touch("images/a.png")
        jobs, conflicts = convert_images.plan(
            convert_images.find_sources(self.root), self.root)
        self.assertEqual(jobs, [])
        self.assertIn("2 sources", conflicts[0])

    def test_avif_svg_and_gif_are_left_alone(self):
        for name in ("images/a.avif", "images/b.svg", "images/c.gif"):
            self.touch(name)
        self.assertEqual(convert_images.find_sources(self.root), [])

    def test_uppercase_extensions_are_found(self):
        self.touch("images/a.JPG")
        self.assertEqual(len(convert_images.find_sources(self.root)), 1)


class Rewriting(unittest.TestCase):
    def setUp(self):
        self.root = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.root, ignore_errors=True)

    def write(self, relative, text):
        full = os.path.join(self.root, relative)
        os.makedirs(os.path.dirname(full), exist_ok=True)
        with open(full, "w", encoding="utf-8") as handle:
            handle.write(text)
        return full

    def read(self, relative):
        with open(os.path.join(self.root, relative), encoding="utf-8") as handle:
            return handle.read()

    def test_front_matter_and_body_references_are_rewritten(self):
        self.write("a.md", "preview_image: /images/a.jpg\n\n![alt](/images/a.jpg)\n")
        convert_images.rewrite_markdown(self.root, {"images/a.jpg": "images/a.avif"},
                                        dry_run=False)
        self.assertEqual(self.read("a.md"),
                         "preview_image: /images/a.avif\n\n![alt](/images/a.avif)\n")

    def test_percent_encoded_reference_is_rewritten_too(self):
        self.write("a.md", "preview_image: /images/a%20b.jpg\n")
        convert_images.rewrite_markdown(self.root,
                                        {"images/a b.jpg": "images/a b.avif"},
                                        dry_run=False)
        self.assertEqual(self.read("a.md"), "preview_image: /images/a%20b.avif\n")

    def test_prose_mentioning_an_extension_is_untouched(self):
        # The blanket sed this script exists to avoid would break this line.
        prose = "Ulož to jako .jpg nebo .png, na formátu nezáleží.\n"
        self.write("a.md", prose)
        convert_images.rewrite_markdown(self.root, {"images/a.jpg": "images/a.avif"},
                                        dry_run=False)
        self.assertEqual(self.read("a.md"), prose)

    def test_a_path_that_is_a_suffix_of_another_is_not_stolen(self):
        self.write("a.md", "one: /images/photo.jpg\ntwo: /images/sub/photo.jpg\n")
        convert_images.rewrite_markdown(self.root, {
            "images/photo.jpg": "images/photo.avif",
            "images/sub/photo.jpg": "images/sub/photo.avif",
        }, dry_run=False)
        self.assertEqual(self.read("a.md"),
                         "one: /images/photo.avif\ntwo: /images/sub/photo.avif\n")

    def test_dry_run_writes_nothing(self):
        self.write("a.md", "preview_image: /images/a.jpg\n")
        touched, replacements = convert_images.rewrite_markdown(
            self.root, {"images/a.jpg": "images/a.avif"}, dry_run=True)
        self.assertEqual(touched, ["a.md"])
        self.assertEqual(replacements, 1)
        self.assertEqual(self.read("a.md"), "preview_image: /images/a.jpg\n")

    def test_non_markdown_files_are_not_rewritten(self):
        self.write("a.html", '<img src="/images/a.jpg">')
        convert_images.rewrite_markdown(self.root, {"images/a.jpg": "images/a.avif"},
                                        dry_run=False)
        self.assertEqual(self.read("a.html"), '<img src="/images/a.jpg">')


class EndToEnd(unittest.TestCase):
    """A real conversion, so the encoder path is exercised, not just the maths."""

    def setUp(self):
        self.root = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.root, ignore_errors=True)

    def test_convert_rewrite_and_delete(self):
        try:
            from PIL import Image
        except ImportError:
            self.skipTest("Pillow not installed")
        os.makedirs(os.path.join(self.root, "images"))
        source = os.path.join(self.root, "images", "a.png")
        Image.new("RGBA", (40, 30), (10, 20, 30, 255)).save(source)
        with open(os.path.join(self.root, "a.md"), "w", encoding="utf-8") as handle:
            handle.write("preview_image: /images/a.png\n")

        jobs, conflicts = convert_images.plan(
            convert_images.find_sources(self.root), self.root)
        self.assertEqual(conflicts, [])
        written, failed = convert_images.convert(jobs, quality=60, dry_run=False)
        self.assertEqual(failed, [])
        self.assertEqual(len(written), 1)

        convert_images.rewrite_markdown(self.root, {"images/a.png": "images/a.avif"},
                                        dry_run=False)
        os.remove(source)

        self.assertTrue(os.path.isfile(os.path.join(self.root, "images", "a.avif")))
        self.assertFalse(os.path.exists(source))
        with open(os.path.join(self.root, "a.md"), encoding="utf-8") as handle:
            self.assertEqual(handle.read(), "preview_image: /images/a.avif\n")
        with Image.open(os.path.join(self.root, "images", "a.avif")) as result:
            self.assertEqual(result.size, (40, 30))


if __name__ == "__main__":
    unittest.main()
