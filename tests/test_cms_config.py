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


class OneCollection(unittest.TestCase):
    """Everything with a date is an event; there is no second list of them."""

    def collections(self):
        return [re.match(r"^  - name: (\S+)", line).group(1)
                for line in lines() if re.match(r"^  - name: \S+\s*$", line)]

    def test_regular_lessons_are_not_a_collection_of_their_own(self):
        self.assertNotIn("classes", self.collections())

    def test_the_one_event_collection_holds_the_lot(self):
        self.assertIn("events", self.collections())
        folders = [line.strip() for line in lines()
                   if re.match(r"^    folder:\s*content/events", line)]
        self.assertEqual(folders, ["folder: content/events"])

    def test_the_editor_can_still_pick_out_the_regular_ones(self):
        filters = [line for line in lines() if "view_filters" in line or
                   re.match(r"^      - \{ label:", line)]
        self.assertTrue(any("recurrence" in line for line in filters),
                        "no way to list just the repeating entries")


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
        for field in ("event-venue", "event-street", "event-locality"):
            with self.subTest(field):
                self.assertEqual(len(list(field_blocks(field))), 1,
                                 f"{field} is missing from the event collection")

    def test_no_place_field_is_a_closed_list(self):
        for field in ("event-venue", "event-street", "event-locality"):
            for number, block in field_blocks(field):
                with self.subTest(f"{field}:{number}"):
                    self.assertFalse(any(re.match(r"^\s*options:", line) for line in block),
                                     f"{field} is back on a fixed list of options")


class Slug(unittest.TestCase):
    """The URL is decided once, at creation, and never by hand.

    A slug typed into a form is a URL typed into a form: a diacritic or a
    capital makes an ugly address, and editing it later moves a page that is
    already linked from elsewhere. So nobody has to fill it in — it is optional
    and stands last, under the body, where it can be ignored. A new entry
    leaves it empty, the empty optional field is not written, and Pelican falls
    back to the filename (`SLUGIFY_SOURCE = "basename"`), which Sveltia writes
    once at creation from the collection's slug template and never rewrites
    when the title is corrected later.

    Filling it in still wins, and that is the escape hatch: someone who knows
    what they are doing sets the address by hand. The field also has to stay
    *declared* even though it is meant to be left blank — Sveltia writes only
    the fields a collection declares, so removing it would strip `slug:` from
    the 178 files that carry one the moment their author saves them, and every
    one of those pages would move.
    """

    def test_nobody_has_to_fill_the_slug_in(self):
        bad = [f"config.yml:{number}" for number, block in field_blocks("slug")
               if not any(re.match(r"^\s*required:\s*false\s*$", line) for line in block)]
        self.assertEqual(bad, [], f"slug is a required field: {bad}")

    def test_the_slug_stands_last_so_it_can_be_ignored(self):
        # Under the body, out of the path an editor takes through the form.
        collection = None
        last_field = {}
        for line in lines():
            match = re.match(r"^  - name: (\S+)\s*$", line)
            if match:
                collection = match.group(1)
                continue
            match = re.match(r"^      - \{?\s*name: ([\w-]+)", line)
            if match and collection:
                last_field[collection] = match.group(1)
        bad = [f"{name}: last field is {last_field.get(name)}"
               for name in ("events",) if last_field.get(name) != "slug"]
        self.assertEqual(bad, [], f"slug is not the last field: {bad}")

    def test_the_slug_field_is_still_declared_where_it_was(self):
        # Undeclared means erased on save. Both event collections carry files
        # with a hand-written slug, so both have to keep declaring it.
        self.assertEqual(len(list(field_blocks("slug"))), 1,
                         "the collection stopped declaring slug; its files would lose theirs")

    def test_a_new_entry_gets_its_url_from_a_template(self):
        # Without one the filename is the bare title, and two milongas of the
        # same name in different months would claim one address.
        templates = [line for line in lines() if re.match(r"^    slug:\s*\S", line)]
        self.assertEqual(len(templates), 1, f"expected one slug template: {templates}")
        self.assertIn("event-start", templates[0],
                      "the template must include the date, or same-named events collide")

    def test_generated_slugs_are_ascii(self):
        # Otherwise the address reads /milonga-na-náplavce/ — the filenames in
        # the repo already look like that, they are just overridden today.
        self.assertTrue(any(re.match(r"^\s*encoding:\s*ascii\s*$", line) for line in lines()),
                        "slug.encoding must be ascii")
        self.assertTrue(any(re.match(r"^\s*clean_accents:\s*true\s*$", line) for line in lines()),
                        "slug.clean_accents must be true")


class Recurrence(unittest.TestCase):
    """One file with `recurrence:` becomes many pages, so its shape is load-bearing."""

    def block(self):
        blocks = list(field_blocks("recurrence"))
        self.assertEqual(len(blocks), 1, "expected one recurrence field")
        return blocks[0][1]

    def test_the_editor_picks_from_a_list_and_types_nothing(self):
        self.assertTrue(any(re.match(r"^\s*widget:\s*select\s*$", line)
                            for line in self.block()),
                        "recurrence is not a dropdown")

    def test_the_list_is_exactly_the_three_answers(self):
        values = [re.search(r"value:\s*('' |'')|value:\s*(\w+)", line)
                  for line in self.block() if "value:" in line]
        found = [(m.group(1) or m.group(2) or "").strip().strip("'")
                 for m in values if m]
        self.assertEqual(found, ["", "weekly", "monthly"])

    def test_nobody_writes_a_weekday(self):
        # The day is in `event-start`. Offering it again is the contradiction
        # `stolarna-tangomania.md` carried for months.
        for day in ("monday", "tuesday", "wednesday", "thursday",
                    "friday", "saturday", "sunday"):
            self.assertNotIn(day, "\n".join(self.block()).lower(),
                             f"the form still asks for a weekday ({day})")

    def test_the_end_of_a_series_is_a_date_picker(self):
        blocks = list(field_blocks("recurrence-until"))
        self.assertEqual(len(blocks), 1, "no end-of-series field")
        block = "\n".join(blocks[0][1])
        self.assertIn("widget: datetime", block)
        self.assertIn("format: YYYY-MM-DD", block)
        self.assertIn("required: false", block)


class OptionalPatterns(unittest.TestCase):
    """A pattern is checked even when the field is blank.

    So `required: false` plus a pattern that does not match the empty string
    is a field nobody can leave empty — the form refuses to save with a
    validation error under an untouched input. That is what happened to
    `event-url` and to `recurrence` on events: an ordinary milonga has neither,
    and could not be saved at all.
    """

    def optional_patterns(self):
        """(where, regex) for every field that has a pattern and is optional."""
        for name in ("event-url", "recurrence", "slug", "event-venue",
                     "event-street", "event-locality", "entry", "event-organiser"):
            for number, block in field_blocks(name):
                if not any(re.match(r"^\s*required:\s*false\s*$", line) for line in block):
                    continue
                for line in block:
                    match = re.match(r"^\s*pattern:\s*\['(.*?)',\s*'", line)
                    if match:
                        yield f"{name} (config.yml:{number})", match.group(1)

    def test_every_optional_pattern_accepts_an_empty_value(self):
        bad = [where for where, pattern in self.optional_patterns()
               if not re.match(pattern, "")]
        self.assertEqual(bad, [], f"optional fields that cannot be left blank: {bad}")


class ExternalLink(unittest.TestCase):
    """`event-url` is printed straight into an href."""

    def test_every_event_url_field_demands_a_scheme(self):
        # Asserted by behaviour, not by the literal regex: the pattern also has
        # to accept an empty value, and pinning its exact text made the two
        # requirements fight over one string.
        blocks = list(field_blocks("event-url"))
        self.assertTrue(blocks, "no event-url field in the CMS config at all")
        for number, block in blocks:
            with self.subTest(f"config.yml:{number}"):
                pattern = next((re.match(r"^\s*pattern:\s*\['(.*?)',\s*'", line).group(1)
                                for line in block
                                if re.match(r"^\s*pattern:\s*\['", line)), None)
                self.assertIsNotNone(pattern, "event-url accepts anything")
                self.assertIsNone(re.match(pattern, "www.studiostolarna.cz"),
                                  "a link without a scheme is accepted")
                self.assertIsNotNone(re.match(pattern, "https://www.studiostolarna.cz"))


if __name__ == "__main__":
    unittest.main()


class AuthorFromPeople(unittest.TestCase):

    def blocks(self):
        return [block for _number, block in field_blocks("author")]

    def test_no_author_is_a_typed_out_list_of_names(self):
        bad = ["\n".join(b) for b in self.blocks() if any("options:" in l for l in b)]
        self.assertEqual(bad, [], "an author field still carries a fixed list of names")

    def test_every_author_reads_the_people_collection(self):
        blocks = self.blocks()
        self.assertTrue(blocks, "no author field in the CMS config at all")
        for block in blocks:
            text = "\n".join(block)
            self.assertIn("widget: relation", text)
            self.assertIn("collection: people", text)
            self.assertIn("value_field: title", text)

    def test_no_relation_forces_the_dropdown_with_zero(self):
        # dropdown_threshold: 0 renders the dropdown and then drops whatever is
        # picked in it; 1 renders the same dropdown and keeps the selection.
        bad = [l.strip() for l in lines()
               if re.match(r"^\s*dropdown_threshold:\s*0\s*$", l)]
        self.assertEqual(bad, [], "dropdown_threshold: 0 loses the selection")

    def test_the_author_is_offered_as_a_searchable_dropdown(self):
        bad = ["\n".join(b) for b in self.blocks()
               if not any(re.match(r"^\s*dropdown_threshold:\s*[1-9]", l) for l in b)]
        self.assertEqual(bad, [], "an author field falls back to radio buttons")
