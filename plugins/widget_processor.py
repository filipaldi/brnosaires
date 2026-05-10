"""
Pelican plugin: widget_processor detects <widget-*> tags in content and renders them via Jinja templates.
Input: page/article content with widget tags. Output: content with widgets rendered to HTML (or text).
"""
import re
from pelican import signals

WIDGET_PATTERN = re.compile(r'<widget-([\w-]+)([^>]*?)/?>(?:\s*</widget-\1>)?', re.DOTALL)

WIDGET_TEMPLATES = {
    'calendar': 'components/widget_calendar.html',
    'calendar-link': 'components/widget_calendar_link.html',
    'articles': 'components/widget_articles.html',
    'gallery': 'components/widget_gallery.html',
}


def _enrich_calendar_link_context(tag_content, render_context, context):
    from calendarium.feed_links import (
        get_feed_id_for_tag_content,
        get_feed_url_https,
        get_calendar_subscribe_url,
        get_google_calendar_add_url,
    )
    from calendarium import attrs as calendarium_attrs
    feed_map = context.get('calendar_feed_id_map') or {}
    feed_id, label = get_feed_id_for_tag_content(tag_content, feed_map)
    siteurl = context.get('SITEURL', '') or ''
    parsed_attrs = calendarium_attrs.parse_calendar_link_attrs(tag_content)
    https_url = get_feed_url_https(feed_id, siteurl)
    webcal_url = get_calendar_subscribe_url(feed_id, siteurl)
    google_url = get_google_calendar_add_url(https_url)
    subscribe_links = [
        {"id": "webcal", "url": webcal_url, "label": parsed_attrs.get("label_webcal") or "Apple / default calendar"},
        {"id": "google", "url": google_url, "label": parsed_attrs.get("label_google") or "Google Calendar"},
        {"id": "outlook", "url": https_url, "label": parsed_attrs.get("label_outlook") or "Copy link", "is_copy": True},
    ]
    render_context['label'] = label
    render_context['subscribe_links'] = subscribe_links


def _substitute(text, env, context, template_suffix):
    if not text or '<widget-' not in text:
        return text

    def replace_widget(match):
        widget_name = match.group(1)
        attrs_str = match.group(2)
        tag_content = f"{widget_name}{attrs_str}"

        html_template_path = WIDGET_TEMPLATES.get(widget_name)
        if not html_template_path:
            return match.group(0)

        if template_suffix == '.html':
            template_path = html_template_path
        else:
            # Swap .html -> requested suffix (e.g. .txt.j2). Missing text-mode
            # template renders empty string — never fall back to HTML, that
            # would inject markup into Markdown.
            if not html_template_path.endswith('.html'):
                return ''
            template_path = html_template_path[: -len('.html')] + template_suffix

        render_context = context.copy()
        render_context['tag_content'] = tag_content

        if widget_name == 'calendar-link':
            _enrich_calendar_link_context(tag_content, render_context, context)

        try:
            template = env.get_template(template_path)
            return template.render(render_context)
        except Exception as e:
            if template_suffix == '.html':
                return f"<!-- Widget error: {e} -->"
            return ''

    return WIDGET_PATTERN.sub(replace_widget, text)


def _page_lang_for(content_object, settings):
    """Mirror base.html's page_lang: marathon section -> 'en', else the
    content object's Lang: (default DEFAULT_LANG). Widget templates need this
    because Pelican's render context doesn't carry the template-level
    `page_lang` set."""
    url = getattr(content_object, "url", "") or ""
    section = getattr(content_object, "section", None)
    src = (getattr(content_object, "source_path", "") or "").replace("\\", "/")
    if "marathon" in url or section == "marathon" or "/pages/marathon/" in src:
        return "en"
    lang = (getattr(content_object, "lang", "") or "").lower()
    return lang or (settings.get("DEFAULT_LANG", "cs") if settings else "cs")


def process_widgets(generator, content_object):
    if not hasattr(content_object, '_content') or not content_object._content:
        return
    if '<widget-' not in content_object._content:
        return

    env = generator.env
    articles = generator.context.get('articles', [])
    context = generator.context.copy()
    context['all_articles'] = articles
    context['page_lang'] = _page_lang_for(content_object, getattr(generator, "settings", None))

    content_object._content = _substitute(content_object._content, env, context, '.html')


def render_widgets_in_text(text, env, context):
    """Render <widget-*> tags as plain-text/Markdown.

    Used by the llm_ally plugin for per-page .md mirrors and the curated
    /llms.txt index page. `context` should already include `all_articles`
    when the caller is outside an `*_generator_finalized` signal handler.
    """
    if context is None:
        context = {}
    else:
        context = dict(context)
    if 'all_articles' not in context:
        context['all_articles'] = context.get('articles', [])
    return _substitute(text, env, context, '.txt.j2')


def process_page_widgets(generator):
    # `generator.pages` holds default-lang pages; authored translations
    # (e.g. `*.en.md` files) land in `generator.translations` instead, so we
    # must process those too or their <widget-*> tags ship raw to the page.
    # (The i18n_fallback plugin's synthesized clones are built from an
    # already-substituted cs `_content`, so they don't need this — but it
    # runs *after* widget_processor and skips cs pages that already have an
    # authored translation, so there's no double processing.)
    for page in list(generator.pages) + list(getattr(generator, 'translations', []) or []):
        process_widgets(generator, page)


def process_article_widgets(generator):
    for article in list(generator.articles) + list(getattr(generator, 'translations', []) or []):
        process_widgets(generator, article)


def register():
    signals.page_generator_finalized.connect(process_page_widgets)
    signals.article_generator_finalized.connect(process_article_widgets)
