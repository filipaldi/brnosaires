"""
Inject articles into page template context.
"""
from pelican import signals


def add_articles_to_pages(generator):
    """Make articles available in page templates as 'all_articles'."""
    articles = generator.context.get('articles', [])
    generator.env.globals['all_articles'] = articles


def register():
    """Register the plugin with Pelican."""
    signals.page_generator_finalized.connect(add_articles_to_pages)
