"""A one-letter Czech word never ends a line (issue #70).

"Milonga u Brněnského draka" reaches the browser as "Milonga
u&nbsp;Brněnského draka" or the line can break after the "u", leaving the
reader's eye on a letter that means nothing alone. Nothing enforced that:
titles printed raw and bodies came straight out of Markdown. The join is one
function, used as a Jinja filter for titles and as a plugin pass over the
rendered body.
"""
import unittest

from markupsafe import Markup

from tests import plugin_path  # noqa: F401

import czech_typography


class _Article:
    def __init__(self, content):
        self._content = content
        self.translations = []


class _Generator:
    def __init__(self, articles):
        self.articles = articles


class Join(unittest.TestCase):
    def test_a_preposition_is_glued_to_the_next_word(self):
        self.assertEqual(
            czech_typography.nbsp_prepositions("Tango a pizza v Sesamu"),
            "Tango a&nbsp;pizza v&nbsp;Sesamu")

    def test_plain_text_without_any_tags(self):
        # A title is usually just a string; it is one text node.
        self.assertEqual(
            czech_typography.nbsp_prepositions("Milonga u Brněnského draka"),
            "Milonga u&nbsp;Brněnského draka")

    def test_upper_case_counts_too(self):
        # A heading starts with the preposition as often as it contains one.
        self.assertEqual(
            czech_typography.nbsp_prepositions("V Brně a okolí"),
            "V&nbsp;Brně a&nbsp;okolí")

    def test_every_letter_of_the_set(self):
        for letter in "aikousvz":
            self.assertEqual(
                czech_typography.nbsp_prepositions(f"x {letter} y"),
                f"x {letter}&nbsp;y", letter)

    def test_a_source_line_wrap_is_a_space_like_any_other(self):
        # Markdown wraps the source; the rendered text node keeps the
        # newline, and the join has to see through the one after the
        # preposition.
        self.assertEqual(
            czech_typography.nbsp_prepositions("dlouhé odpoledne\nk tanci"),
            "dlouhé odpoledne\nk&nbsp;tanci")


class LeavesAlone(unittest.TestCase):
    def test_multi_letter_words_starting_with_the_same_letters(self):
        text = "Advent se Vánocemi, viz obrázek, učitel učí, ani slovo, okolo rohu"
        self.assertEqual(czech_typography.nbsp_prepositions(text), text)

    def test_an_already_joined_pair(self):
        self.assertEqual(
            czech_typography.nbsp_prepositions(
                Markup("Tango a&nbsp;pizza v&nbsp;Sesamu")),
            Markup("Tango a&nbsp;pizza v&nbsp;Sesamu"))

    def test_it_is_idempotent(self):
        once = czech_typography.nbsp_prepositions("Tango a pizza v Sesamu")
        self.assertEqual(czech_typography.nbsp_prepositions(once), once)

    def test_entities_keep_their_escaping(self):
        # The & of an escaped title survives; the join adds its own entity
        # and eats nothing that was already there. An entity-bearing value
        # is HTML, so it arrives as Markup — a plain str is text and its &
        # would be escaped, not preserved.
        self.assertEqual(
            czech_typography.nbsp_prepositions(Markup("Tango &amp; pizza v Brně")),
            Markup("Tango &amp; pizza v&nbsp;Brně"))

    def test_a_preposition_with_nothing_after_it_in_the_node(self):
        # Nothing to glue to, so nothing changes.
        self.assertEqual(
            czech_typography.nbsp_prepositions("konec v "),
            "konec v ")

    def test_an_apostrophe_does_not_start_a_word(self):
        # "it's" ends in s, but that s belongs to the word. The English
        # pages are full of these; the a after it still joins. Markup, so
        # the apostrophe tests the preposition logic and not escape()'s
        # opinion of quotes.
        self.assertEqual(
            czech_typography.nbsp_prepositions(Markup("it's a milonga")),
            Markup("it's a&nbsp;milonga"))


class Escaping(unittest.TestCase):
    """The filter takes what a template hands it. A plain str is text —
    event.title, an organiser, a description — so it is escaped first and
    the & of "Tango & Pizza" reaches the page as the entity it is meant to
    be. A Markup is already HTML and is walked as it stands. Either way the
    answer is Markup, so Jinja's own escaping cannot re-escape the join."""

    def test_a_plain_str_is_escaped_before_the_walk(self):
        joined = czech_typography.nbsp_prepositions("Tango & Pizza v Sesamo")
        self.assertEqual(joined, "Tango &amp; Pizza v&nbsp;Sesamo")
        self.assertIsInstance(joined, Markup)

    def test_a_less_than_sign_in_a_plain_str_cannot_inject_html(self):
        self.assertEqual(
            czech_typography.nbsp_prepositions("a <b>"),
            "a&nbsp;&lt;b&gt;")

    def test_a_markup_value_is_walked_as_the_html_it_claims_to_be(self):
        # Tags stay tags, and the "v " keeps its space: its text node ends
        # at the <em>, and the filter does not join across an element
        # boundary it cannot see past.
        self.assertEqual(
            czech_typography.nbsp_prepositions(Markup("v <em>Brně</em>")),
            Markup("v <em>Brně</em>"))

    def test_something_that_is_not_a_string_passes_through(self):
        # None comes out of a missing field; templates render it as nothing.
        self.assertIsNone(czech_typography.nbsp_prepositions(None))


class Html(unittest.TestCase):
    """A value that is already HTML arrives as Markup and is walked as it
    stands; the same text handed over as a plain str would be escaped
    instead (see Escaping)."""

    def test_text_nodes_join_attributes_do_not(self):
        self.assertEqual(
            czech_typography.nbsp_prepositions(
                Markup('<a title="Tango a pizza" href="/x">Tango a pizza</a>')),
            Markup('<a title="Tango a pizza" href="/x">Tango a&nbsp;pizza</a>'))

    def test_a_greater_than_inside_a_quoted_attribute(self):
        # The tag has to be read quote-aware or its attribute text leaks
        # into a text node and gets "fixed".
        self.assertEqual(
            czech_typography.nbsp_prepositions(
                Markup('<abbr title="tango a pizza > vše">tango a pizza</abbr>')),
            Markup('<abbr title="tango a pizza > vše">tango a&nbsp;pizza</abbr>'))

    def test_script_and_style_are_untouched(self):
        for element in ("script", "style"):
            html = Markup(f"<{element}>var pair = 'a pizza';</{element}>")
            self.assertEqual(
                czech_typography.nbsp_prepositions(html), html, element)

    def test_pre_and_code_are_untouched(self):
        self.assertEqual(
            czech_typography.nbsp_prepositions(
                Markup("<pre>a pizza\nv Brně</pre> a pizza <code>s x</code>")),
            Markup("<pre>a pizza\nv Brně</pre> a&nbsp;pizza <code>s x</code>"))

    def test_verbatim_elements_nested_in_each_other(self):
        html = Markup("<pre>a b <code>c d</code> e f</pre>")
        self.assertEqual(czech_typography.nbsp_prepositions(html), html)

    def test_comments_are_untouched(self):
        html = Markup("<!-- a pizza --><p>a pizza</p>")
        self.assertEqual(
            czech_typography.nbsp_prepositions(html),
            Markup("<!-- a pizza --><p>a&nbsp;pizza</p>"))


class Hook(unittest.TestCase):
    """article_generator_finalized / page_generator_finalized reflow the
    rendered body, translations included — the /en/ pages i18n_fallback
    synthesizes are translations nobody authors."""

    def test_the_body_of_every_article_and_its_twin(self):
        article = _Article("<h1>Milonga u Brněnského draka</h1><p>Text.</p>")
        twin = _Article("<h1>Milonga u Brněnského draka</h1><p>Text.</p>")
        article.translations = [twin]
        czech_typography._on_articles(_Generator([article]))
        self.assertEqual(
            article._content, "<h1>Milonga u&nbsp;Brněnského draka</h1><p>Text.</p>")
        self.assertEqual(
            twin._content, "<h1>Milonga u&nbsp;Brněnského draka</h1><p>Text.</p>")

    def test_a_body_with_nothing_to_do_is_untouched(self):
        article = _Article("<p>Text bez předložek.</p>")
        czech_typography._on_articles(_Generator([article]))
        self.assertEqual(article._content, "<p>Text bez předložek.</p>")


if __name__ == "__main__":
    unittest.main()
