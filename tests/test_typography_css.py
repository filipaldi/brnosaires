"""Guards the "logo does not underline on hover" contract (issue #69).

`.logo` on the site's wordmark anchors sets only `font-family`. Without a
dedicated `.logo:hover` rule, the generic `a:hover` rule underlines it too:
`a:hover` has specificity (0,1,1) against `.logo`'s (0,1,0), so it wins on
hover regardless of where either rule sits in the file. A fix that edits the
bare `.logo` rule instead of adding a `:hover` selector looks right in the
source but loses that specificity fight and the underline comes back.

These tests fail if the dedicated `.logo:hover` rule goes missing, if it is
satisfied by a selector that does not carry `:hover`, if the generic `a` /
`a:hover` rules are weakened to make it pass, or if the fix does not survive
the Pelican build.

Deliberately out of reach: whether a real browser, resolving the full
cascade across every stylesheet the page loads, actually paints no underline
under the pointer. A later rule in another sheet could still win that fight;
only a live click-through can prove it, not a static read of this file.
"""
import os
import re
import unittest

from tests import REPO_ROOT, build_site

SOURCE_CSS = os.path.join(REPO_ROOT, "theme", "static", "css", "typography.css")

COMMENT = re.compile(r"/\*.*?\*/", re.DOTALL)
RULE = re.compile(r"([^{}]+)\{([^{}]*)\}")
UNDERLINE = re.compile(r"text-decoration\s*:\s*underline\b")


def read(path):
    with open(path, encoding="utf-8") as handle:
        return handle.read()


def rule_blocks(css):
    """Yield (selector_parts, body) for every flat rule in a stylesheet.

    Comments are stripped first so a `/* LOGO */` section header never
    glues onto the next selector. `selector_parts` is the comma-separated
    selector list, stripped, so `.logo:hover` is found whether it sits
    alone or combined with other selectors. Tolerant of whitespace and
    rule order; assumes no nested at-rules and no descendant/combinator
    selectors, true of typography.css today.
    """
    clean = COMMENT.sub("", css)
    for selector, body in RULE.findall(clean):
        parts = [part.strip() for part in selector.split(",") if part.strip()]
        if parts:
            yield parts, body


def declares(body, prop, value):
    """True if `body` sets `prop: value`, tolerant of surrounding
    whitespace/newlines and an optional trailing semicolon."""
    pattern = re.compile(
        r"(?:^|;)\s*" + re.escape(prop) + r"\s*:\s*" + re.escape(value) + r"\s*(?:;|$)")
    return bool(pattern.search(body.strip()))


class LogoHoverRule(unittest.TestCase):
    """Source-level checks: the dedicated `.logo:hover` rule must exist
    exactly once, must be the selector that carries `:hover` rather than a
    rewritten bare `.logo`, and must sit beside untouched generic `a` /
    `a:hover` rules rather than replacing what they do."""

    @classmethod
    def setUpClass(cls):
        cls.css = read(SOURCE_CSS)
        cls.blocks = list(rule_blocks(cls.css))

    def test_logo_hover_rule_exists_exactly_once_and_kills_the_underline(self):
        hover_rules = [body for parts, body in self.blocks if ".logo:hover" in parts]
        self.assertEqual(
            len(hover_rules), 1,
            f"expected exactly one .logo:hover rule in {SOURCE_CSS}, "
            f"found {len(hover_rules)}")
        self.assertTrue(
            declares(hover_rules[0], "text-decoration", "none"),
            ".logo:hover does not set text-decoration: none")

    def test_the_underline_killing_rule_must_carry_hover_not_bare_logo(self):
        # A rule counts as a candidate fix if its selector is `.logo` or
        # `.logo:hover` and its body sets text-decoration: none. Only the
        # `:hover` selector actually beats a:hover's (0,1,1) specificity on
        # hover; a bare `.logo` is (0,1,0) and loses regardless of source
        # order, so the underline would return. A bare
        # `.logo { text-decoration: none }` fails this test: it is a
        # candidate (selector ".logo", body sets text-decoration: none),
        # but its selector parts do not include ".logo:hover", so it lands
        # in `offenders` below and the assertEqual fails.
        candidates = [parts for parts, body in self.blocks
                      if any(part in (".logo", ".logo:hover") for part in parts)
                      and declares(body, "text-decoration", "none")]
        self.assertTrue(
            candidates, "no .logo (or .logo:hover) rule sets text-decoration: none yet")
        offenders = [parts for parts in candidates
                     if not any(part == ".logo:hover" for part in parts)]
        self.assertEqual(
            offenders, [],
            f"a rule kills the logo underline without :hover in its selector: {offenders}")

    def test_a_hover_still_underlines_and_stays_the_only_underline(self):
        hover_bodies = [body for parts, body in self.blocks if "a:hover" in parts]
        self.assertEqual(len(hover_bodies), 1, "expected exactly one a:hover rule")
        self.assertTrue(declares(hover_bodies[0], "text-decoration", "underline"),
                         "a:hover no longer sets text-decoration: underline")
        self.assertEqual(
            len(UNDERLINE.findall(self.css)), 1,
            "text-decoration: underline should appear exactly once in the source file")

    def test_the_bare_a_rule_is_untouched(self):
        a_bodies = [body for parts, body in self.blocks if "a" in parts]
        self.assertEqual(len(a_bodies), 1, "expected exactly one bare `a` rule")
        self.assertTrue(declares(a_bodies[0], "color", "var(--color-accent-2)"),
                         "a lost its color: var(--color-accent-2)")
        self.assertTrue(declares(a_bodies[0], "text-decoration", "none"),
                         "a lost its text-decoration: none")


class BuiltStylesheet(unittest.TestCase):
    """The fix has to survive the Pelican build, not just exist in source.
    Theme static files are copied close to verbatim, but this is the seam
    every built-output test in this repo goes through rather than trusting
    that a source change ships unchanged."""

    @classmethod
    def setUpClass(cls):
        cls.output = build_site()
        css_path = os.path.join(cls.output, "theme", "css", "typography.css")
        if not os.path.isfile(css_path):
            raise AssertionError(f"built stylesheet missing at {css_path}")
        cls.css = read(css_path)
        cls.blocks = list(rule_blocks(cls.css))

    def test_built_stylesheet_carries_the_hover_rule_and_still_one_underline(self):
        hover_rules = [body for parts, body in self.blocks if ".logo:hover" in parts]
        self.assertEqual(
            len(hover_rules), 1,
            "the built stylesheet does not carry exactly one .logo:hover rule")
        self.assertTrue(
            declares(hover_rules[0], "text-decoration", "none"),
            "built .logo:hover does not set text-decoration: none")
        self.assertEqual(
            len(UNDERLINE.findall(self.css)), 1,
            "the built stylesheet does not carry exactly one text-decoration: underline")

    def test_both_logo_anchors_reach_the_built_homepage(self):
        # base.html's aside carries the header/rail logo anchor only on a
        # non-marathon page, so the homepage is the page that exercises
        # both instances (aside + footer) at once.
        html = read(os.path.join(self.output, "index.html"))
        aside = re.search(r"<aside\b.*?</aside>", html, re.DOTALL)
        footer = re.search(r"<footer\b.*?</footer>", html, re.DOTALL)
        self.assertIsNotNone(aside, "no <aside> on the built homepage")
        self.assertIsNotNone(footer, "no <footer> on the built homepage")
        self.assertRegex(
            aside.group(0), r'class="[^"]*\blogo\b[^"]*"',
            "header/aside logo anchor lost its .logo class")
        self.assertRegex(
            footer.group(0), r'class="[^"]*\blogo\b[^"]*"',
            "footer logo anchor lost its .logo class")


if __name__ == "__main__":
    unittest.main()
