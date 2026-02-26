"""
Pelican plugin: widget_processor detects <widget-*> tags in content and renders them via Jinja templates.
Input: page/article content with widget tags. Output: content with widgets rendered to HTML.
"""
import re
from pelican import signals

WIDGET_PATTERN = re.compile(r'<widget-([\w-]+)([^>]*)>(?:</widget-\1>)?', re.DOTALL)

WIDGET_TEMPLATES = {
    'calendar': 'components/widget_calendar.html',
    'calendar-link': 'components/widget_calendar_link.html',
    'articles': 'components/widget_articles.html',
    'gallery': 'components/widget_gallery.html',
}


def process_widgets(generator, content_object):
    if not hasattr(content_object, '_content') or not content_object._content:
        return
    if '<widget-' not in content_object._content:
        return

    env = generator.env
    articles = generator.context.get('articles', [])

    context = generator.context.copy()
    context['all_articles'] = articles

    def replace_widget(match):
        widget_name = match.group(1)
        attrs_str = match.group(2)
        tag_content = f"{widget_name}{attrs_str}"

        template_path = WIDGET_TEMPLATES.get(widget_name)
        if not template_path:
            return match.group(0)

        render_context = context.copy()
        render_context['tag_content'] = tag_content

        if widget_name == 'calendar-link':
            from calendarium.feed_links import (
                get_feed_id_for_tag_content,
                get_calendar_subscribe_url,
                get_feed_url_https,
                get_google_calendar_add_url,
            )
            from calendarium import attrs as calendarium_attrs
            feed_map = context.get('calendar_feed_id_map') or {}
            feed_id, label = get_feed_id_for_tag_content(tag_content, feed_map)
            siteurl = context.get('SITEURL', '') or ''
            parsed_attrs = calendarium_attrs.parse_calendar_link_attrs(tag_content)
            https_url = get_feed_url_https(feed_id, siteurl)
            webcal_url = get_calendar_subscribe_url(feed_id, siteurl)
            google_url = get_google_calendar_add_url(webcal_url)
            subscribe_links = [
                {"id": "webcal", "url": webcal_url, "label": parsed_attrs.get("label_webcal") or "Apple / default calendar"},
                {"id": "google", "url": google_url, "label": parsed_attrs.get("label_google") or "Google Calendar"},
                {"id": "outlook", "url": https_url, "label": parsed_attrs.get("label_outlook") or "Copy link"},
            ]
            render_context['label'] = label
            render_context['subscribe_links'] = subscribe_links

        try:
            template = env.get_template(template_path)
            return template.render(render_context)
        except Exception as e:
            return f"<!-- Widget error: {e} -->"

    content_object._content = WIDGET_PATTERN.sub(replace_widget, content_object._content)


def process_page_widgets(generator):
    for page in generator.pages:
        process_widgets(generator, page)


def process_article_widgets(generator):
    for article in generator.articles:
        process_widgets(generator, article)


def register():
    signals.page_generator_finalized.connect(process_page_widgets)
    signals.article_generator_finalized.connect(process_article_widgets)
