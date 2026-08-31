"""
Pelican plugin: LLM-targeted output (dumb renderer).

Two responsibilities, both editor-driven:

1. Per-page Markdown mirrors. For every public article and page whose
   frontmatter does NOT set `llm_mirror: false`, write `<slug>/index.md`
   alongside `<slug>/index.html`. Widget tags are rendered as plain-text
   bullets via widget_processor.render_widgets_in_text().

2. Editor-curated `.txt` outputs. For every `content/llm/<name>.md` file,
   strip the metadata header, expand widgets in text mode, and write
   `output/<name>.txt` plus `output/.well-known/<name>.txt`.

The plugin holds NO site-specific knowledge — no hardcoded categories,
no path excludes, no section structure. All editorial decisions live in
the editor surface (content/llm/*.md and per-content `llm_mirror`).
"""
import os
import re

from pelican import signals

# ORDER MATTERS: this reads `article.instructors`, which people_links attaches
# during the same `article_generator_finalized` signal. Handlers fire in
# PLUGINS order, so people_links must stay listed before llm_ally in
# pelicanconf.py - the same rule i18n_fallback documents for widget_processor.
import people_links
import recurring_events
import widget_processor


_FRONTMATTER_RE = re.compile(r"\A---\s*\n.*?\n---\s*\n", re.DOTALL)
_PELICAN_HEADER_RE = re.compile(r"\A([A-Za-z][A-Za-z0-9_-]*:\s.*\n)+\n", re.MULTILINE)

# The one field here that no file carries. An event names its teachers by slug
# in `instructor_slugs:`; the mirror prints the names those slugs resolve to,
# under a key that says what the value is. A slug would be a dangling
# reference in this corpus: every profile an event can point at sets
# `llm_mirror: false`, so none of them is mirrored to resolve one against.
# (Four profiles are mirrored - the marathon DJs - and no event teaches with
# them.) A name needs no lookup either way.
INSTRUCTOR_FIELD = "instructor"

EVENT_FRONTMATTER_FIELDS = (
    "event-type", "event-start", "event-end",
    "event-venue", "event-street", "event-locality",
    "event-organiser", INSTRUCTOR_FIELD, "recurrence", "series",
    "event-url",
)

# Stash for handoff between *_generator_finalized and finalized signals.
_state = {"settings": None, "env": None, "context": None}


# ---------- helpers ----------

def _read(path):
    try:
        with open(path, "r", encoding="utf-8") as fh:
            return fh.read()
    except (OSError, UnicodeDecodeError):
        return ""


def _strip_metadata_header(raw):
    if raw.startswith("---"):
        m = _FRONTMATTER_RE.match(raw)
        if m:
            return raw[m.end():]
    m = _PELICAN_HEADER_RE.match(raw)
    if m:
        return raw[m.end():]
    return raw


def _yaml_escape(value):
    s = str(value).replace('"', '\\"')
    return f'"{s}"'


def _is_opted_out(content_obj):
    meta = getattr(content_obj, "metadata", {}) or {}
    raw = meta.get("llm_mirror")
    if raw is None:
        return False
    return str(raw).strip().lower() in ("false", "no", "0")


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
    for field in EVENT_FRONTMATTER_FIELDS:
        if field == INSTRUCTOR_FIELD:
            value = people_links.instructor_names(
                getattr(content_obj, "instructors", None) or [],
                getattr(content_obj, "lang", "") or "")
        elif field == "recurrence":
            value = recurring_events.recurrence_rule(metadata)
        else:
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


def _write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(text)


# ---------- per-page .md mirrors ----------

def _emit_mirror(content_obj, settings, generator):
    if _is_opted_out(content_obj):
        return
    source_path = getattr(content_obj, "source_path", "") or ""
    if not source_path or not os.path.exists(source_path):
        return
    out_path = _output_md_path(content_obj, settings)
    if not out_path:
        return

    raw = _read(source_path)
    if not raw:
        return

    body = _strip_metadata_header(raw)
    context = generator.context.copy()
    context["all_articles"] = generator.context.get("articles", [])
    body = widget_processor.render_widgets_in_text(body, generator.env, context)
    body = body.strip() + "\n" if body.strip() else ""

    text = _marker(settings) + "\n" + _frontmatter(content_obj, settings) + "\n" + body
    _write(out_path, text)


# ---------- content/llm/*.md → output/*.txt ----------

def _emit_curation_files(settings, env, context):
    llm_dir = os.path.join(settings.get("PATH", "content"), "llm")
    if not os.path.isdir(llm_dir):
        return
    output_path = settings.get("OUTPUT_PATH", "output")
    for entry in sorted(os.listdir(llm_dir)):
        if not entry.endswith(".md"):
            continue
        src_path = os.path.join(llm_dir, entry)
        if not os.path.isfile(src_path):
            continue
        basename = entry[:-3]
        raw = _read(src_path)
        body = _strip_metadata_header(raw)
        rendered = widget_processor.render_widgets_in_text(body, env, context)
        text = rendered.strip() + "\n"
        _write(os.path.join(output_path, f"{basename}.txt"), text)
        _write(os.path.join(output_path, ".well-known", f"{basename}.txt"), text)


# ---------- hooks ----------

def _on_articles(generator):
    _state["settings"] = generator.settings
    _state["env"] = generator.env
    ctx = generator.context.copy()
    ctx["all_articles"] = list(generator.articles or [])
    _state["context"] = ctx
    for article in generator.articles:
        _emit_mirror(article, generator.settings, generator)


def _on_pages(generator):
    if _state["settings"] is None:
        _state["settings"] = generator.settings
    if _state["env"] is None:
        _state["env"] = generator.env
    if _state["context"] is None:
        ctx = generator.context.copy()
        ctx["all_articles"] = generator.context.get("articles", [])
        _state["context"] = ctx
    else:
        _state["context"]["all_articles"] = generator.context.get(
            "articles", _state["context"].get("all_articles", [])
        )
    for page in generator.pages:
        _emit_mirror(page, generator.settings, generator)


def on_finalized(pelican_obj):
    settings = _state["settings"] or pelican_obj.settings
    env = _state["env"]
    context = _state["context"] or {}
    if env is None:
        return
    _emit_curation_files(settings, env, context)


def register():
    signals.article_generator_finalized.connect(_on_articles)
    signals.page_generator_finalized.connect(_on_pages)
    signals.finalized.connect(on_finalized)
