#!/usr/bin/env python3
"""
check_links.py — fail the build when a generated page points at something that
is not in the build.

WHY
---
Every internal reference on this site is a string typed into front-matter or a
Markdown body. Nothing validates it: a wrong `preview_image`, a renamed page, a
link to `/venue/` that never existed — all of them render happily and 404 only
in a visitor's browser. With deploys now firing on push, a check that runs
against the finished `output/` tree turns that into a red build instead.

The check deliberately looks at the *output*, not the sources. It is the only
place where slug rules, the /en/ mirror, widget expansion and static copying
have all already happened, so it cannot disagree with what visitors get.

WHAT COUNTS AS BROKEN
---------------------
An internal target (site-root-relative, SITEURL-absolute, or plain relative)
that resolves to no file in `output/`. Directory URLs resolve through
`index.html`, matching how GitHub Pages serves them.

External URLs, `mailto:`, `tel:`, `data:`, and pure `#fragment` links are not
checked — that would need the network and would make the build flaky.

USAGE
-----
    python scripts/check_links.py [output_dir]

Exit status 1 with a grouped report if anything is broken, 0 otherwise.
"""
import os
import re
import sys
from collections import defaultdict
from urllib.parse import unquote, urlsplit

SITEURL = "https://brnosaires.com"

# Attributes whose value is a URL we can resolve locally.
_ATTR_PATTERN = re.compile(
    r"""<(?P<tag>a|img|link|script|source|iframe|video|audio)\b[^>]*?"""
    r"""\s(?P<attr>href|src)\s*=\s*["'](?P<url>[^"']*)["']""",
    re.IGNORECASE | re.DOTALL,
)

# og:image / twitter:image carry their URL in `content=`, so they need their own
# pattern — they are the references that break most silently, since nothing on
# the page renders them.
_META_PATTERN = re.compile(
    r"""<meta\b[^>]*?(?:property|name)\s*=\s*["'](?:og:image|twitter:image)["']"""
    r"""[^>]*?\scontent\s*=\s*["'](?P<url>[^"']*)["']""",
    re.IGNORECASE | re.DOTALL,
)

# schema.org "image" inside the JSON-LD blocks.
_LD_IMAGE_PATTERN = re.compile(r'"image"\s*:\s*"(?P<url>[^"]+)"')

# The theme emits `<base href="https://brnosaires.com/">`, which makes every
# relative href on the page resolve against the site root instead of the
# directory the page sits in. Resolving without it reports the whole site as
# broken, so it has to be read per page rather than assumed.
_BASE_PATTERN = re.compile(
    r"""<base\b[^>]*?\shref\s*=\s*["'](?P<url>[^"']+)["']""", re.IGNORECASE
)

_SKIP_SCHEMES = ("http://", "https://", "mailto:", "tel:", "data:", "javascript:",
                 "webcal://", "//")


def _is_internal(url):
    if not url or url.startswith("#"):
        return False
    if url.startswith(SITEURL):
        return True
    return not url.lower().startswith(_SKIP_SCHEMES)


def _base_dir(html, page_rel):
    """The directory relative references on this page resolve against."""
    match = _BASE_PATTERN.search(html)
    if not match:
        return os.path.dirname(page_rel)
    href = match.group("url")
    if href.startswith(SITEURL):
        href = href[len(SITEURL):]
    # `<base href>` is a document URL: everything after the last "/" is the
    # document name and is dropped, so "https://host/" means the root.
    return urlsplit(href).path.rsplit("/", 1)[0].lstrip("/")


def _to_relative(url, base_dir):
    """Map a reference to a path relative to the output root."""
    if url.startswith(SITEURL):
        url = url[len(SITEURL):]
    path = urlsplit(url).path
    if not path:
        return None
    if path.startswith("/"):
        return path.lstrip("/")
    return os.path.normpath(os.path.join(base_dir, path))


def _resolves(output_dir, rel):
    """True if `rel` is served by the finished tree.

    Tries the literal spelling and the percent-decoded one: a filename may
    legitimately contain `%`, and some values came out of the Notion import
    already encoded.
    """
    for candidate in dict.fromkeys((rel, unquote(rel))):
        full = os.path.join(output_dir, candidate)
        if os.path.isfile(full):
            return True
        # `/foo/` and `/foo` are both served as `/foo/index.html`.
        if os.path.isfile(os.path.join(full, "index.html")):
            return True
    return False


def _references(html):
    for match in _ATTR_PATTERN.finditer(html):
        yield match.group("url")
    for match in _META_PATTERN.finditer(html):
        yield match.group("url")
    for match in _LD_IMAGE_PATTERN.finditer(html):
        yield match.group("url")


def check(output_dir):
    broken = defaultdict(list)  # target -> [pages referencing it]
    pages = 0

    for root, _dirs, files in os.walk(output_dir):
        for name in files:
            if not name.endswith(".html"):
                continue
            pages += 1
            full = os.path.join(root, name)
            page_rel = os.path.relpath(full, output_dir)
            with open(full, encoding="utf-8", errors="replace") as handle:
                html = handle.read()
            base_dir = _base_dir(html, page_rel)
            for url in _references(html):
                if not _is_internal(url):
                    continue
                rel = _to_relative(url, base_dir)
                if rel is None or rel in ("", "."):
                    continue
                if not _resolves(output_dir, rel):
                    broken[url].append(page_rel)

    return pages, broken


def main():
    output_dir = sys.argv[1] if len(sys.argv) > 1 else "output"
    if not os.path.isdir(output_dir):
        print(f"check_links: no such directory: {output_dir}", file=sys.stderr)
        return 2

    pages, broken = check(output_dir)

    if not broken:
        print(f"check_links: {pages} pages, every internal reference resolves.")
        return 0

    occurrences = sum(len(v) for v in broken.values())
    print(f"check_links: {len(broken)} broken target(s) across {occurrences} "
          f"reference(s) in {pages} pages\n", file=sys.stderr)
    for target in sorted(broken):
        referrers = sorted(set(broken[target]))
        print(f"  {target}", file=sys.stderr)
        for referrer in referrers[:5]:
            print(f"      referenced by {referrer}", file=sys.stderr)
        if len(referrers) > 5:
            print(f"      ... and {len(referrers) - 5} more", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
