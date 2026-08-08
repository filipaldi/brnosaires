#!/usr/bin/env python3
"""
check_links.py — fail the build when a generated page points at something that
is not in the build.

WHY
---
Every internal reference on this site is a string typed into front-matter or a
Markdown body. Nothing validates it: a wrong `preview_image`, a renamed page, a
link to `/venue/` that never existed — all of them render happily and 404 only
in a visitor's browser. With deploys firing on push, a check that runs against
the finished `output/` tree turns that into a red build instead.

The check deliberately looks at the *output*, not the sources. It is the only
place where slug rules, the /en/ mirror, widget expansion and static copying
have all already happened, so it cannot disagree with what visitors get.

HOW IT READS THE PAGES
----------------------
With `html.parser`, not regular expressions. A regex over HTML gets both
directions wrong and this is a deploy gate, so both are expensive:

  - It misses. `<video src="/ok" poster="/gone.jpg">` (only the first URL
    attribute per tag matches), `<source srcset>`, an unquoted `href=/x/`, an
    attribute whose value contains `>`.
  - It fires on things that are not markup. A `"image": "cover.jpg"` inside an
    article that documents front matter, or a commented-out `<a href>` a
    developer left in a template, would block every deploy.

The parser knows the difference between an attribute and a string that looks
like one, skips `<script>`, `<style>` and comments, and decodes entities.

WHAT COUNTS AS BROKEN
---------------------
An internal target (site-root-relative, SITEURL-absolute, or plain relative)
that resolves to no file under `output/`. Directory URLs resolve through
`index.html`, matching how GitHub Pages serves them. A reference that escapes
the output root with `../` is broken by definition — it is not deployed —
even though the file may exist in the repo.

External URLs, `mailto:`, `tel:`, `data:` and bare `#fragment` links are not
checked; that would need the network and would make the build flaky.

Non-HTML outputs (the sitemap, the .ics feeds, llms.txt, the Atom/RSS feeds)
are scanned too, for absolute site URLs only. A dead `URL:` in a calendar feed
is a link that lives in someone's phone forever and that nobody ever reloads.

USAGE
-----
    python scripts/check_links.py [output_dir]

Exit status 1 with a grouped report if anything is broken, 0 otherwise.
"""
import os
import re
import sys
from collections import defaultdict
from html.parser import HTMLParser
from urllib.parse import unquote, urlsplit

SITEURL = "https://brnosaires.com"

# Attribute names whose value is a single URL.
URL_ATTRIBUTES = {"href", "src", "poster", "data", "action", "formaction"}

# Attribute names holding a comma-separated candidate list ("url 2x, url 1x").
URL_SET_ATTRIBUTES = {"srcset", "imagesrcset"}

# `<meta>` tags whose `content` is a URL. Order-independent, unlike a regex
# that has to assume `property=` comes before `content=`.
URL_META_NAMES = {"og:image", "og:image:url", "og:image:secure_url",
                  "twitter:image", "og:audio", "og:video"}

# Tags whose text content is not markup and must not be scanned.
OPAQUE_TAGS = {"script", "style"}

_SKIP_SCHEMES = ("http://", "https://", "mailto:", "tel:", "data:", "javascript:",
                 "webcal://", "//")

# Absolute site URLs inside non-HTML output (sitemap.xml, *.ics, llms.txt, feeds).
_ABSOLUTE_URL = re.compile(re.escape(SITEURL) + r"(/[^\s\"'<>)\]]*)")
NON_HTML_SUFFIXES = (".xml", ".ics", ".txt")

# Keys under which JSON-LD carries a URL. Values may be a string, a list, or an
# object with a "url" — all three are produced by real schema.org markup.
LD_URL_KEYS = {"image", "logo", "contentUrl", "thumbnailUrl"}


class _Collector(HTMLParser):
    """Pulls every locally-resolvable URL out of one page.

    Also records the page's `<base href>`: the theme emits
    `<base href="https://brnosaires.com/">`, which makes relative hrefs resolve
    against the site root rather than the directory the page sits in. Resolving
    without it once reported all 606 targets on the site as broken.
    """

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.urls = []
        self.base = None
        self._opaque = []
        self._ld_json = False

    # -- markup -------------------------------------------------------------

    def handle_starttag(self, tag, attrs):
        attributes = {name.lower(): (value or "") for name, value in attrs}

        if tag in OPAQUE_TAGS:
            self._opaque.append(tag)
            self._ld_json = (
                tag == "script"
                and attributes.get("type", "").strip().lower() == "application/ld+json")
            # The tag's *contents* are opaque, but `<script src>` is a real
            # reference and a missing bundle is a broken page.
            if attributes.get("src"):
                self.urls.append(attributes["src"])
            return

        if tag == "base" and self.base is None and "href" in attributes:
            self.base = attributes["href"]
            return

        if tag == "meta":
            name = (attributes.get("property") or attributes.get("name") or "").lower()
            if name in URL_META_NAMES and attributes.get("content"):
                self.urls.append(attributes["content"])
            return

        for attribute in URL_ATTRIBUTES & attributes.keys():
            self.urls.append(attributes[attribute])
        for attribute in URL_SET_ATTRIBUTES & attributes.keys():
            for candidate in attributes[attribute].split(","):
                url = candidate.strip().split(" ")[0]
                if url:
                    self.urls.append(url)

    def handle_startendtag(self, tag, attrs):
        # `<img/>`; never opens a region, so it must not push onto _opaque.
        if tag in OPAQUE_TAGS:
            return
        self.handle_starttag(tag, attrs)

    def handle_endtag(self, tag):
        if self._opaque and self._opaque[-1] == tag:
            self._opaque.pop()
            self._ld_json = False

    def handle_data(self, data):
        # The only text worth reading is a JSON-LD block. Everything else
        # inside <script> is code, and prose outside it is prose.
        if self._ld_json:
            self.urls.extend(_ld_urls(data))


def _ld_urls(block):
    """URLs under the schema.org keys that hold one, from a JSON-LD block."""
    import json

    try:
        data = json.loads(block)
    except ValueError:
        return []

    found = []

    def walk(node, key=None):
        if isinstance(node, dict):
            for child_key, value in node.items():
                walk(value, child_key)
        elif isinstance(node, list):
            for value in node:
                walk(value, key)
        elif isinstance(node, str) and key in LD_URL_KEYS:
            found.append(node)

    walk(data)
    # `{"image": {"@type": "ImageObject", "url": "..."}}` — the url sits one
    # level down under a key that is not itself in LD_URL_KEYS.
    def walk_objects(node):
        if isinstance(node, dict):
            for child_key, value in node.items():
                if child_key in LD_URL_KEYS and isinstance(value, dict):
                    url = value.get("url") or value.get("contentUrl")
                    if isinstance(url, str):
                        found.append(url)
                walk_objects(value)
        elif isinstance(node, list):
            for value in node:
                walk_objects(value)

    walk_objects(data)
    return found


def _is_internal(url):
    url = url.strip()
    if not url or url.startswith("#"):
        return False
    if url.startswith(SITEURL):
        return True
    return not url.lower().startswith(_SKIP_SCHEMES)


def _base_dir(base_href, page_rel):
    """The directory relative references on this page resolve against."""
    if not base_href:
        return os.path.dirname(page_rel)
    if base_href.startswith(SITEURL):
        base_href = base_href[len(SITEURL):]
    # `<base href>` is a document URL: everything after the last "/" is the
    # document name and is dropped, so "https://host/" means the root.
    return urlsplit(base_href).path.rsplit("/", 1)[0].lstrip("/")


def _to_relative(url, base_dir):
    """Map a reference to a path relative to the output root, or None if it
    escapes the root — which makes it broken, whatever is on disk there."""
    url = url.strip()
    if url.startswith(SITEURL):
        url = url[len(SITEURL):]
    path = urlsplit(url).path
    if not path:
        return None
    relative = path.lstrip("/") if path.startswith("/") else os.path.join(base_dir, path)
    relative = os.path.normpath(relative)
    if relative.startswith("..") or os.path.isabs(relative):
        # `../AGENTS.md` resolves against the repo in CI, where output/ sits in
        # the repo root — so it "exists" and would pass while 404ing for every
        # visitor.
        return ".."
    return relative


def _resolves(output_dir, rel):
    """True if `rel` is served by the finished tree.

    Tries the literal spelling and the percent-decoded one: a filename may
    legitimately contain `%`, and some values came out of the Notion import
    already encoded.
    """
    if rel == "..":
        return False
    for candidate in dict.fromkeys((rel, unquote(rel))):
        full = os.path.join(output_dir, candidate)
        if os.path.isfile(full):
            return True
        # `/foo/` and `/foo` are both served as `/foo/index.html`.
        if os.path.isfile(os.path.join(full, "index.html")):
            return True
    return False


def _page_references(html):
    collector = _Collector()
    try:
        collector.feed(html)
        collector.close()
    except Exception:  # noqa: BLE001 — malformed markup should not stop the gate
        pass
    return collector.base, collector.urls


def check(output_dir):
    broken = defaultdict(list)  # target -> [pages referencing it]
    pages = 0

    for root, _dirs, files in os.walk(output_dir):
        for name in files:
            full = os.path.join(root, name)
            page_rel = os.path.relpath(full, output_dir)
            is_html = name.endswith(".html")
            if not is_html and not name.endswith(NON_HTML_SUFFIXES):
                continue
            with open(full, encoding="utf-8", errors="replace") as handle:
                text = handle.read()

            if is_html:
                pages += 1
                base_href, urls = _page_references(text)
                base_dir = _base_dir(base_href, page_rel)
            else:
                # Only absolute site URLs: a bare word in llms.txt is prose,
                # not a link, and there is no <base> to resolve against.
                urls = [SITEURL + path for path in _ABSOLUTE_URL.findall(text)]
                base_dir = ""

            for url in urls:
                if not _is_internal(url):
                    continue
                rel = _to_relative(url, base_dir)
                if rel is None or rel in ("", "."):
                    continue
                if not _resolves(output_dir, rel):
                    broken[url.strip()].append(page_rel)

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
