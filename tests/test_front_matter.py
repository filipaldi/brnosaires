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


if __name__ == "__main__":
    unittest.main()
