"""The h1 an editor cannot forget."""
import unittest

from tests import build_site, plugin_path  # noqa: F401

import title_as_h1


class _Article:
    def __init__(self, content, title="Milonga na Náplavce", source_path="content/events/2026/09/x.md"):
        self._content = content
        self.title = title
        self.source_path = source_path


class _Generator:
    def __init__(self, articles):
        self.articles = articles
        self.translations = []


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


class Report(unittest.TestCase):
    """The build says whose text is missing a heading, and carries on.

    Stopping the build was the obvious alternative and the wrong one: the
    person who would have to fix it edits in the CMS and never sees a red
    Actions run, so the only thing a failure achieves is that nothing at all
    gets published. The page is made correct, the report says which text still
    wants a real heading, and it is addressed to whoever has to write it.
    """

    def test_it_names_every_file_it_had_to_fix(self):
        generator = _Generator([
            _Article("<p>Text.</p>", source_path="content/events/2026/09/milonga.md"),
            _Article("<h1>Má nadpis</h1>", source_path="content/events/2026/09/ok.md"),
            _Article("<p>Text.</p>", source_path="content/events/2026/09/milonga.en.md"),
        ])
        with self.assertLogs("title_as_h1", level="WARNING") as captured:
            title_as_h1._on_articles(generator)
        report = "\n".join(captured.output)
        self.assertIn("milonga.md", report)
        self.assertIn("milonga.en.md", report)
        self.assertNotIn("ok.md", report)

    def test_it_says_nothing_when_every_text_has_a_heading(self):
        generator = _Generator([_Article("<h1>Nadpis</h1>")])
        with self.assertNoLogs("title_as_h1", level="WARNING"):
            title_as_h1._on_articles(generator)

    def test_it_is_written_for_the_person_who_has_to_fix_it(self):
        # Czech, because the reader is the editor, not a developer reading a
        # stack trace. The same wording is what would go into a mail later.
        generator = _Generator([_Article("<p>Text.</p>")])
        with self.assertLogs("title_as_h1", level="WARNING") as captured:
            title_as_h1._on_articles(generator)
        self.assertIn("nadpis", "\n".join(captured.output).lower())


if __name__ == "__main__":
    unittest.main()
