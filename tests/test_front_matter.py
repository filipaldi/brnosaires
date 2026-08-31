"""Front matter the CMS has to be able to read.

Pelican's metadata reader is forgiving: it splits each line on the first colon
and stops at the first blank line. Sveltia parses the same block as YAML. Every
gap between those two readings is a file that builds perfectly and is invisible
or uneditable in the editor — and nothing says so. Three separate shapes of that
bug turned up in one week, so they get a test each.

Scope is the four folders the CMS declares as collections. Content outside them
(navigation, the monthly milonga pages) is Pelican-only and deliberately not
covered.
"""
import os
import re
import unittest

from tests import REPO_ROOT

# Mirrors `folder:` in content/extra/admin/config.yml. `classes` sits inside
# `events`, so walking `events` covers it.
COLLECTION_FOLDERS = (
    "content/events",
    "content/announcements",
    "content/curiosities",
    "content/people",
)

KEY_LINE = re.compile(r"^([A-Za-z_][\w-]*): ?(.*)$")


def entries():
    """(path relative to the repo, list of lines) for every collection file."""
    for folder in COLLECTION_FOLDERS:
        root_dir = os.path.join(REPO_ROOT, folder)
        for root, _dirs, files in os.walk(root_dir):
            for name in sorted(files):
                if not name.endswith(".md"):
                    continue
                full = os.path.join(root, name)
                with open(full, encoding="utf-8", errors="replace") as handle:
                    yield os.path.relpath(full, REPO_ROOT), handle.read().split("\n")


def front_matter(lines):
    """The lines between the fences, or None if the file is not fenced."""
    if not lines or lines[0].strip() != "---":
        return None
    for index, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            return lines[1:index]
    return None


class Delimiters(unittest.TestCase):
    """Without `---` on both sides the CMS reads the whole file as body, shows
    the metadata as text, and overwrites it with an empty form on first save."""

    def test_every_entry_is_fenced_top_and_bottom(self):
        bad = [path for path, lines in entries() if front_matter(lines) is None]
        self.assertEqual(bad, [], f"unfenced or unclosed front matter: {bad[:5]}")


class Comments(unittest.TestCase):
    """A `#` line ends Pelican's metadata parsing, so every field below it is
    dropped while still sitting in the file. Found the hard way: a
    `translate: false` written under a comment simply never took effect."""

    def test_no_comment_lines_inside_front_matter(self):
        bad = []
        for path, lines in entries():
            block = front_matter(lines) or []
            for offset, line in enumerate(block):
                if line.lstrip().startswith("#"):
                    bad.append(f"{path}:{offset + 2}")
        self.assertEqual(bad, [], f"comments inside front matter: {bad[:5]}")


class YamlSafety(unittest.TestCase):
    """The block must survive a YAML reading, not just Pelican's.

    An unquoted value containing a colon followed by a space reads as a nested
    mapping and the whole entry fails to parse — Sveltia then skips it, so the
    article is uneditable in the CMS while the site builds fine. Three
    descriptions were in that state ("La Cumparsita: poslední skladba…").

    Checked by hand rather than with a YAML library so the suite keeps needing
    no dependency beyond the standard library.
    """

    def test_no_unquoted_colon_space_in_a_value(self):
        bad = []
        for path, lines in entries():
            for offset, line in enumerate(front_matter(lines) or []):
                match = KEY_LINE.match(line)
                if not match:
                    continue  # indented continuation, e.g. a second instructor
                value = match.group(2).strip()
                if not value or value[0] in "\"'":
                    continue
                if ": " in value:
                    bad.append(f"{path}:{offset + 2} -> {match.group(1)}")
        self.assertEqual(bad, [], f"unquoted colon in a value: {bad[:5]}")

    def test_no_tab_indentation(self):
        # YAML forbids tabs for indentation outright; Pelican does not care.
        bad = [f"{path}:{offset + 2}"
               for path, lines in entries()
               for offset, line in enumerate(front_matter(lines) or [])
               if line.startswith("\t")]
        self.assertEqual(bad, [], f"tab-indented front matter: {bad[:5]}")

    def test_no_value_is_a_bare_pair_of_quotes(self):
        # Sveltia writes `series: ''` for an empty optional field. Pelican's
        # reader does not unquote, so the site gets the two-character string
        # `''` and renders it as a real value — a link to /series/''. The CMS
        # is told to leave empty optional fields out entirely
        # (`omit_empty_optional_fields`), and this keeps it that way.
        bad = []
        for path, lines in entries():
            for offset, line in enumerate(front_matter(lines) or []):
                match = KEY_LINE.match(line)
                if match and match.group(2).strip() in ("''", '""'):
                    bad.append(f"{path}:{offset + 2} -> {match.group(1)}")
        self.assertEqual(bad, [], f"empty quotes as a value: {bad[:5]}")


class Sequences(unittest.TestCase):
    """A YAML list has to be indented by four spaces, not two.

    Pelican reads metadata with Markdown's `meta` extension, whose
    continuation pattern is `^[ ]{4,}`. A two-space list item matches neither
    that nor a `key: value` line, so parsing *stops there* — the remaining
    keys never become metadata and leak into the page body instead. Sveltia
    indents by `output.yaml.indent_size`, which is why that option is 4.
    """

    def test_every_continuation_line_is_indented_four_spaces(self):
        bad = []
        for path, lines in entries():
            for offset, line in enumerate(front_matter(lines) or []):
                if not line.strip() or KEY_LINE.match(line):
                    continue
                if len(line) - len(line.lstrip(" ")) < 4:
                    bad.append(f"{path}:{offset + 2} -> {line!r}")
        self.assertEqual(bad, [], f"under-indented front matter: {bad[:5]}")


class References(unittest.TestCase):
    """Two values that point outside the file, and both shapes the site can follow.

    `preview_image` is either a path under the media folder or a bare filename
    sitting next to the .md — `colocated_images` recognises nothing in between,
    so an editor upload landing in a sub-folder resolved to a 404 nobody saw
    until the link checker ran. `event-url` is printed straight into an href,
    where a value without a scheme is a relative link into our own site.
    """

    def values(self, key):
        for path, lines in entries():
            for offset, line in enumerate(front_matter(lines) or []):
                match = KEY_LINE.match(line)
                if match and match.group(1) == key and match.group(2).strip():
                    yield f"{path}:{offset + 2}", match.group(2).strip()

    def test_every_preview_image_is_absolute_or_a_bare_filename(self):
        bad = [f"{where} -> {value}" for where, value in self.values("preview_image")
               if not value.startswith("/images/") and "/" in value]
        self.assertEqual(bad, [], f"preview images the site cannot resolve: {bad[:5]}")

    def test_every_event_url_carries_its_scheme(self):
        bad = [f"{where} -> {value}" for where, value in self.values("event-url")
               if not value.startswith("https://")]
        self.assertEqual(bad, [], f"external links without https://: {bad[:5]}")


class Place(unittest.TestCase):
    """The address is three fields, and none of them is parsed.

    `event-location` held "HEX Gallery, Lidická 63a, Brno" and the address was
    recovered by splitting on commas, so the shape of one string carried the
    whole weight — and to keep that shape safe the CMS froze the venue list at
    twenty, which made the twenty-first event impossible to create. A file that
    brings the old field back reintroduces both problems at once.
    """

    def test_no_entry_still_carries_the_old_single_field(self):
        bad = [f"{path}:{offset + 2}"
               for path, lines in entries()
               for offset, line in enumerate(front_matter(lines) or [])
               if line.startswith("event-location:")]
        self.assertEqual(bad, [], f"event-location is gone; split it: {bad[:5]}")

    def test_an_event_that_names_a_venue_says_where_it_is(self):
        # A venue with no locality renders as a bare name and gives the map
        # link nothing to point at.
        bad = []
        for path, lines in entries():
            fields = {}
            for line in front_matter(lines) or []:
                match = KEY_LINE.match(line)
                if match:
                    fields[match.group(1)] = match.group(2).strip()
            if fields.get("event-venue") and not fields.get("event-locality"):
                bad.append(path)
        self.assertEqual(bad, [], f"venue without a locality: {bad[:5]}")


class Language(unittest.TestCase):
    """`lang:` is what pairs a file with its translation.

    Pelican links `foo.md` and `foo.en.md` by slug plus `lang`. When the
    English twin claims `lang: cs` both count as originals with the same slug,
    and the build dies with FileOverwriteFailedError before it writes a single
    page. The CMS produced exactly that for five entries, because a hidden
    field can only carry one default — hence `default: '{{locale}}'`.
    """

    def language(self, lines):
        for line in front_matter(lines) or []:
            match = KEY_LINE.match(line)
            if match and match.group(1) == "lang":
                return match.group(2).strip()
        return None

    def test_every_english_entry_says_english(self):
        bad = [f"{path} -> {self.language(lines)!r}"
               for path, lines in entries()
               if path.endswith(".en.md") and self.language(lines) != "en"]
        self.assertEqual(bad, [], f"English files not declaring lang: en: {bad[:5]}")

    def test_no_other_entry_says_english(self):
        # The mirror image: a Czech file marked `en` would collide the same way.
        bad = [path for path, lines in entries()
               if not path.endswith(".en.md") and self.language(lines) == "en"]
        self.assertEqual(bad, [], f"Czech files declaring lang: en: {bad[:5]}")


if __name__ == "__main__":
    unittest.main()


class Recurrence(unittest.TestCase):
    """The rule and `event-start` are one fact, and used to be two.

    `stolarna-tangomania.md` said `weekly monday` with a Thursday start: the
    file disagreed with the page for months, on a green build.
    """

    WEEKDAYS = ("monday", "tuesday", "wednesday", "thursday",
                "friday", "saturday", "sunday")

    def values(self, key):
        for path, lines in entries():
            block = front_matter(lines) or []
            found = {}
            for line in block:
                match = KEY_LINE.match(line)
                if match:
                    found.setdefault(match.group(1), match.group(2).strip())
            if found.get(key):
                yield path, found

    def test_a_named_weekday_matches_the_day_the_event_starts_on(self):
        from datetime import datetime
        bad = []
        for path, found in self.values("recurrence"):
            named = [word for word in found["recurrence"].lower().split()
                     if word in self.WEEKDAYS]
            start = found.get("event-start", "")
            if not named or not start:
                continue
            try:
                weekday = datetime.strptime(start[:19], "%Y-%m-%d %H:%M:%S").weekday()
            except ValueError:
                continue
            if named[0] != self.WEEKDAYS[weekday]:
                bad.append(f"{path}: rule says {named[0]}, event-start is a "
                           f"{self.WEEKDAYS[weekday]} ({start})")
        self.assertEqual(bad, [], f"the file disagrees with itself: {bad}")

    def test_the_end_of_a_series_is_a_date(self):
        bad = [f"{path}: {found['recurrence-until']!r}"
               for path, found in self.values("recurrence-until")
               if not re.match(r"^\d{4}-\d{2}-\d{2}$", found["recurrence-until"])]
        self.assertEqual(bad, [], f"unreadable end of series: {bad}")
