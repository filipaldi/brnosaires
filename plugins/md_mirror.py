"""
Pelican plugin: emit a Markdown mirror at every public page's sibling URL.

For an article at /tango-pizza-sesamo-2026-04-29/index.html, write
/tango-pizza-sesamo-2026-04-29/index.md alongside it. LLM-driven
assistants can fetch raw Markdown instead of scraping HTML/CSS noise.

Each .md starts with a Mintlify-style discovery marker pointing at
/llms.txt, has YAML frontmatter (title, date, url, key event metadata,
series), and a body with widget tags stripped.

Scope:
- include: events, pages, announcements
- exclude: curiosities, people
"""
import os
import re

from pelican import signals


_FRONTMATTER_RE = re.compile(r"\A---\s*\n.*?\n---\s*\n", re.DOTALL)
_WIDGET_RE = re.compile(r"<widget-[^>]*?>.*?</widget-[^>]*?>|<widget-[^/]*?/>", re.DOTALL)
_PELICAN_HEADER_RE = re.compile(r"\A([A-Za-z][A-Za-z0-9_-]*:\s.*\n)+\n", re.MULTILINE)

_EVENT_FRONTMATTER_FIELDS = (
    "event-type",
    "event-start",
    "event-end",
    "event-location",
    "event-organiser",
    "instructor",
    "recurrence",
    "series",
)


def strip_widget_tags(text):
    if not text:
        return text
    return _WIDGET_RE.sub("", text)


def _strip_metadata_header(raw):
    if raw.startswith("---"):
        m = _FRONTMATTER_RE.match(raw)
        if m:
            return raw[m.end():]
    m = _PELICAN_HEADER_RE.match(raw)
    if m:
        return raw[m.end():]
    return raw


def _read_source(path):
    try:
        with open(path, "r", encoding="utf-8") as fh:
            return fh.read()
    except (OSError, UnicodeDecodeError):
        return ""


def _yaml_escape(value):
    s = str(value).replace('"', '\\"')
    return f'"{s}"'


def _frontmatter(content_obj, settings):
    siteurl = settings.get("SITEURL", "").rstrip("/")
    url_path = getattr(content_obj, "url", "") or ""
    full_url = f"{siteurl}/{url_path}" if siteurl else f"/{url_path}"

    lines = ["---"]
    title = getattr(content_obj, "title", "") or ""
    lines.append(f"title: {_yaml_escape(title)}")

    date = getattr(content_obj, "date", None)
    if date is not None and hasattr(date, "isoformat"):
        lines.append(f"date: {date.isoformat()}")

    lines.append(f"url: {_yaml_escape(full_url)}")

    metadata = getattr(content_obj, "metadata", {}) or {}
    for field in _EVENT_FRONTMATTER_FIELDS:
        value = metadata.get(field)
        if value is None or value == "":
            continue
        if hasattr(value, "isoformat"):
            value = value.isoformat()
        lines.append(f"{field}: {_yaml_escape(value)}")

    lines.append("---")
    return "\n".join(lines) + "\n"


def _marker(settings):
    siteurl = settings.get("SITEURL", "").rstrip("/")
    target = f"{siteurl}/llms.txt" if siteurl else "/llms.txt"
    return f"> For a complete page index, fetch {target}\n"


def _output_md_path(content_obj, settings):
    output_path = settings.get("OUTPUT_PATH", "output")
    save_as = getattr(content_obj, "save_as", "") or ""
    if not save_as.endswith(".html"):
        return None
    md_save_as = save_as[: -len(".html")] + ".md"
    return os.path.join(output_path, md_save_as)


def _is_excluded(content_obj):
    source_path = getattr(content_obj, "source_path", "") or ""
    norm = source_path.replace("\\", "/")
    if "/content/curiosities/" in norm or "/content/people/" in norm:
        return True
    category = getattr(content_obj, "category", None)
    cat_name = getattr(category, "name", None) if category else None
    if cat_name and cat_name.lower() in ("curiosity", "people"):
        return True
    return False


def _emit_mirror(content_obj, settings):
    source_path = getattr(content_obj, "source_path", "") or ""
    if not source_path or not os.path.exists(source_path):
        return
    if _is_excluded(content_obj):
        return

    out_path = _output_md_path(content_obj, settings)
    if not out_path:
        return

    raw = _read_source(source_path)
    if not raw:
        return

    body = _strip_metadata_header(raw)
    body = strip_widget_tags(body)
    body = body.strip() + "\n" if body.strip() else ""

    text = _marker(settings) + "\n" + _frontmatter(content_obj, settings) + "\n" + body

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as fh:
        fh.write(text)


def _on_articles(article_generator):
    settings = article_generator.settings
    for article in article_generator.articles:
        _emit_mirror(article, settings)


def _on_pages(page_generator):
    settings = page_generator.settings
    for page in page_generator.pages:
        _emit_mirror(page, settings)


def register():
    signals.article_generator_finalized.connect(_on_articles)
    signals.page_generator_finalized.connect(_on_pages)
