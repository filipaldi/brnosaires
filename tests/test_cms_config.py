"""The CMS options that decide whether an editor can write a broken file.

Every guard here exists because the editor produced a file the build could not
read, and none of them is visible in the CMS interface — the editor fills in a
form and Sveltia decides the rest. tests/test_front_matter.py catches the
resulting file; this catches the option that would produce it again.

Read as lines rather than parsed as YAML, like the other config checks in the
suite, so the tests keep needing nothing beyond the standard library.
"""
import os
import re
import unittest

from tests import REPO_ROOT

CONFIG = os.path.join(REPO_ROOT, "content", "extra", "admin", "config.yml")


def lines():
    with open(CONFIG, encoding="utf-8") as handle:
        return handle.read().split("\n")


def field_blocks(name):
    """The lines of every `- name: <name>` field block in the config."""
    start = re.compile(rf"^(\s*)-\s*name:\s*{re.escape(name)}\s*$")
    for index, line in enumerate(lines()):
        match = start.match(line)
        if not match:
            continue
        indent = len(match.group(1))
        block = [line]
        for following in lines()[index + 1:]:
            if following.strip() and (len(following) - len(following.lstrip())) <= indent:
                break
            block.append(following)
        yield index + 1, block


class LanguageField(unittest.TestCase):
    """A hidden field carries one default for every locale.

    `default: cs` therefore wrote `lang: cs` into the English twin as well,
    both files counted as originals with the same slug, and the build stopped
    at FileOverwriteFailedError. `{{locale}}` is the documented way to make a
    hidden default differ per locale.
    """

    def test_every_lang_field_defaults_to_the_locale(self):
        blocks = list(field_blocks("lang"))
        self.assertTrue(blocks, "no lang field in the CMS config at all")
        bad = [f"config.yml:{number}" for number, block in blocks
               if not any(re.match(r"^\s*default:\s*'\{\{locale\}\}'\s*$", line)
                          for line in block)]
        self.assertEqual(bad, [], f"lang fields with a fixed default: {bad}")

    def test_every_lang_field_is_stored_per_locale(self):
        # Without this the English file keeps no `lang:` of its own, which is
        # the same collision by a different route.
        bad = [f"config.yml:{number}" for number, block in field_blocks("lang")
               if not any(re.match(r"^\s*i18n:\s*(true|translate)\s*$", line)
                          for line in block)]
        self.assertEqual(bad, [], f"lang fields not translated per locale: {bad}")


class Output(unittest.TestCase):
    """How Sveltia serialises a value decides whether Pelican can read it."""

    def test_yaml_lists_are_indented_four_spaces(self):
        # Markdown's meta extension continues a value on `^[ ]{4,}` only. At
        # the default 2 the parser stops at the first list item and every key
        # below it silently leaves the metadata for the page body.
        self.assertTrue(any(re.match(r"^\s*indent_size:\s*4\s*$", line)
                            for line in lines()),
                        "output.yaml.indent_size must be 4")

    def test_empty_optional_fields_are_omitted(self):
        # Otherwise an untouched optional field is written as `series: ''` and
        # Pelican, which does not unquote, hands the site the string `''`.
        self.assertTrue(any(re.match(r"^\s*omit_empty_optional_fields:\s*true\s*$", line)
                            for line in lines()),
                        "output.omit_empty_optional_fields must be true")


class Uploads(unittest.TestCase):
    """Where an uploaded image lands, and whether the site can find it again.

    Left to inherit the global setting, Sveltia put the file in a folder named
    after the entry and wrote `<slug>/<file>` into the front matter, which
    `colocated_images` does not recognise — the page linked an image that was
    never copied into the output. An absolute path has only one reading.
    """

    def test_every_collection_pins_an_absolute_media_folder(self):
        bad = []
        for line in lines():
            match = re.match(r"^\s{4}(media_folder|public_folder):\s*(\S+)\s*$", line)
            if match and not match.group(2).startswith("/"):
                bad.append(line.strip())
        self.assertEqual(bad, [], f"relative media paths: {bad}")

    def test_no_collection_leaves_the_media_folder_to_the_default(self):
        collections = [line for line in lines() if re.match(r"^  - name: \S+\s*$", line)]
        pinned = [line for line in lines() if re.match(r"^\s{4}media_folder:", line)]
        self.assertEqual(len(pinned), len(collections),
                         f"{len(collections)} collections, {len(pinned)} with a media folder")


class Place(unittest.TestCase):
    """Deterministic shape, open set.

    The venue list used to be twenty options frozen in this file, because the
    single `event-location` string had to keep the shape its comma parser
    expected. Three fields make the shape safe without a list, so the editor
    can name a place nobody has used before.
    """

    def test_the_frozen_venue_list_is_gone(self):
        self.assertEqual([line for line in lines() if "event-location" in line], [],
                         "event-location is split into venue/street/locality")

    def test_all_three_place_fields_are_offered_everywhere(self):
        # Both event collections, or one of them writes an address the site
        # cannot assemble.
        for field in ("event-venue", "event-street", "event-locality"):
            with self.subTest(field):
                self.assertEqual(len(list(field_blocks(field))), 2,
                                 f"{field} is missing from an event collection")

    def test_no_place_field_is_a_closed_list(self):
        for field in ("event-venue", "event-street", "event-locality"):
            for number, block in field_blocks(field):
                with self.subTest(f"{field}:{number}"):
                    self.assertFalse(any(re.match(r"^\s*options:", line) for line in block),
                                     f"{field} is back on a fixed list of options")


class Recurrence(unittest.TestCase):
    """One file with `recurrence:` becomes many pages, so its grammar is load-bearing."""

    def test_both_collections_validate_the_grammar(self):
        blocks = list(field_blocks("recurrence"))
        self.assertTrue(blocks, "no recurrence field in the CMS config at all")
        bad = [f"config.yml:{number}" for number, block in blocks
               if not any("pattern:" in line for line in block)]
        self.assertEqual(bad, [], f"recurrence fields accepting anything: {bad}")


class ExternalLink(unittest.TestCase):
    """`event-url` is printed straight into an href."""

    def test_every_event_url_field_demands_a_scheme(self):
        blocks = list(field_blocks("event-url"))
        self.assertTrue(blocks, "no event-url field in the CMS config at all")
        bad = [f"config.yml:{number}" for number, block in blocks
               if not any("'^https://'" in line for line in block)]
        self.assertEqual(bad, [], f"event-url fields accepting anything: {bad}")


if __name__ == "__main__":
    unittest.main()
