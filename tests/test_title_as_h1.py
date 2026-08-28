"""The h1 an editor cannot forget."""
import unittest

from tests import build_site, plugin_path  # noqa: F401

import title_as_h1


class _Article:
    def __init__(self, content, title="Milonga na Náplavce"):
        self._content = content
        self.title = title


class Heading(unittest.TestCase):
    def test_a_body_without_one_gets_the_title(self):
        article = _Article("<p>Přijď tancovat.</p>")
        title_as_h1._ensure(article)
        self.assertEqual(article._content,
                         "<h1>Milonga na Náplavce</h1>\n<p>Přijď tancovat.</p>")

    def test_a_body_that_has_one_is_left_alone(self):
        # The heading an author wrote deliberately differs from the title on
        # about a hundred events; replacing or doubling it would rewrite them.
        article = _Article("<h1>Letní workshopy</h1>\n<p>Text.</p>")
        title_as_h1._ensure(article)
        self.assertEqual(article._content, "<h1>Letní workshopy</h1>\n<p>Text.</p>")

    def test_an_h1_with_attributes_still_counts(self):
        article = _Article('<h1 id="x">Nadpis</h1>')
        title_as_h1._ensure(article)
        self.assertEqual(article._content, '<h1 id="x">Nadpis</h1>')

    def test_a_lower_heading_is_not_mistaken_for_one(self):
        article = _Article("<h2>Podnadpis</h2>")
        title_as_h1._ensure(article)
        self.assertTrue(article._content.startswith("<h1>Milonga na Náplavce</h1>"))

    def test_the_title_is_escaped(self):
        article = _Article("<p>Text.</p>", title="Tango & vino <2026>")
        title_as_h1._ensure(article)
        self.assertIn("<h1>Tango &amp; vino &lt;2026&gt;</h1>", article._content)

    def test_an_empty_body_is_left_alone(self):
        # Nothing is rendered for it either, so a heading would stand alone.
        article = _Article("")
        title_as_h1._ensure(article)
        self.assertEqual(article._content, "")


if __name__ == "__main__":
    unittest.main()
