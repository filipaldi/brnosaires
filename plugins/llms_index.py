"""
Pelican plugin: emit /llms.txt and /llms-full.txt at build time.

Hooks the global `finalized` signal, walks the corpus, and writes:

- output/llms.txt           — curated Key Pages + dynamic Upcoming Events /
                              Regular Series Hubs / Recent Updates
- output/llms-full.txt      — full bodies + recurring lessons expanded
                              ~12 weeks ahead
- output/.well-known/llms.txt
- output/.well-known/llms-full.txt
                            — byte-identical copies (IETF well-known)

Replaces the static content/extra/llms.txt whose hardcoded dates went stale.
"""
import os
from datetime import datetime, timedelta

from pelican import signals

try:
    from md_mirror import strip_widget_tags
except ImportError:
    def strip_widget_tags(text):
        return text

try:
    from recurring_events import expand_recurring
except ImportError:
    def expand_recurring(events, start, end):
        return list(events or [])


WINDOW_WEEKS_AHEAD = 12
RECENT_ANNOUNCEMENTS = 8


KEY_PAGES = [
    ("Calendar", "tango-kalendar-brno", "Upcoming milongas, workshops, practicas, and classes from all local organizers"),
    ("Classes", "tango-lekce-brno", "Regular class schedules from all tango schools in Brno"),
    ("Milongas", "tango-milongy-brno", "Upcoming milongas in Brno"),
    ("About", "o-nas", "About Brnos Aires, the people behind it, and iCal subscription links"),
]


def _abs(siteurl, path):
    siteurl = (siteurl or "").rstrip("/")
    path = path.lstrip("/")
    return f"{siteurl}/{path}" if siteurl else f"/{path}"


def _today():
    return datetime.now()


def _is_event(article):
    source = (getattr(article, "source_path", "") or "").replace("\\", "/")
    return "/content/events/" in source


def _is_announcement(article):
    cat = getattr(article, "category", None)
    name = getattr(cat, "name", "") if cat else ""
    return name.lower() == "announcement"


def _series_slugs(articles):
    out = set()
    for a in articles or []:
        meta = getattr(a, "metadata", None) or {}
        s = meta.get("series")
        if s:
            out.add(s)
    return out


def _hub_pages(pages, articles):
    series = _series_slugs(articles)
    if not series:
        return []
    return [p for p in pages or [] if getattr(p, "slug", None) in series]


def _read_source_body(content_obj):
    path = getattr(content_obj, "source_path", "") or ""
    if not path or not os.path.exists(path):
        return ""
    try:
        with open(path, "r", encoding="utf-8") as fh:
            raw = fh.read()
    except (OSError, UnicodeDecodeError):
        return ""
    if raw.startswith("---"):
        end = raw.find("\n---", 3)
        if end != -1:
            raw = raw[end + 4:]
    return strip_widget_tags(raw).strip()


def _format_event_line(siteurl, occ):
    when = occ.date.strftime("%Y-%m-%d %H:%M") if occ.date else ""
    title = occ.title or occ.slug or ""
    location = (occ.metadata or {}).get("event-location", "")
    url = _abs(siteurl, f"{occ.slug}/")
    parts = [when, title]
    if location:
        parts.append(str(location))
    return f"- [{' — '.join(p for p in parts if p)}]({url})"


def _build_llms_index(siteurl, sitename, sitedescription, pages, articles):
    today = _today()
    horizon = today + timedelta(weeks=WINDOW_WEEKS_AHEAD)
    start_str = today.strftime("%Y-%m-%d")
    end_str = horizon.strftime("%Y-%m-%d")

    events = [a for a in articles if _is_event(a)]
    announcements = [a for a in articles if _is_announcement(a)]
    hubs = _hub_pages(pages, articles)

    occurrences = expand_recurring(events, start_str, end_str)
    occurrences = [o for o in occurrences if o and getattr(o, "date", None)]
    occurrences.sort(key=lambda o: o.date)

    lines = [f"# {sitename}", ""]
    if sitedescription:
        lines += [f"> {sitedescription}", ""]
    lines.append("> For a complete page index, fetch this file. For full bodies, fetch /llms-full.txt.")
    lines.append("")

    lines.append("## Key Pages")
    lines.append("")
    for name, slug, desc in KEY_PAGES:
        lines.append(f"- [{name}]({_abs(siteurl, slug + '/')}): {desc}")
    lines.append("")

    if hubs:
        lines.append("## Regular Series Hubs")
        lines.append("")
        for hub in hubs:
            url = _abs(siteurl, f"{hub.slug}/")
            desc = (getattr(hub, "metadata", {}) or {}).get("description", "") or ""
            suffix = f": {desc}" if desc else ""
            lines.append(f"- [{hub.title}]({url}){suffix}")
        lines.append("")

    if occurrences:
        lines.append("## Upcoming Events")
        lines.append("")
        for occ in occurrences[:60]:
            lines.append(_format_event_line(siteurl, occ))
        lines.append("")

    if announcements:
        lines.append("## Recent Updates")
        lines.append("")
        recent = sorted(announcements, key=lambda a: getattr(a, "date", today), reverse=True)[:RECENT_ANNOUNCEMENTS]
        for a in recent:
            url = _abs(siteurl, f"{a.slug}/")
            when = a.date.strftime("%Y-%m-%d") if getattr(a, "date", None) else ""
            prefix = f"{when} — " if when else ""
            lines.append(f"- [{prefix}{a.title}]({url})")
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def _build_llms_full(siteurl, sitename, sitedescription, pages, articles):
    today = _today()
    horizon = today + timedelta(weeks=WINDOW_WEEKS_AHEAD)
    start_str = today.strftime("%Y-%m-%d")
    end_str = horizon.strftime("%Y-%m-%d")

    events = [a for a in articles if _is_event(a)]
    announcements = [a for a in articles if _is_announcement(a)]
    hubs = _hub_pages(pages, articles)
    other_pages = [p for p in (pages or []) if p not in hubs]

    occurrences = expand_recurring(events, start_str, end_str)
    occurrences = [o for o in occurrences if o and getattr(o, "date", None)]
    occurrences.sort(key=lambda o: o.date)

    blocks = [f"# {sitename}", ""]
    if sitedescription:
        blocks += [f"> {sitedescription}", ""]

    def emit_obj(title, url, body):
        if not body:
            return
        blocks.append(f"## {title}")
        blocks.append(f"<{url}>")
        blocks.append("")
        blocks.append(body)
        blocks.append("")

    if hubs:
        blocks.append("# Regular Series Hubs")
        blocks.append("")
        for hub in hubs:
            emit_obj(hub.title, _abs(siteurl, f"{hub.slug}/"), _read_source_body(hub))

    if other_pages:
        blocks.append("# Pages")
        blocks.append("")
        for p in other_pages:
            emit_obj(p.title, _abs(siteurl, f"{p.slug}/"), _read_source_body(p))

    if occurrences:
        blocks.append("# Upcoming Events")
        blocks.append("")
        seen_articles = set()
        for occ in occurrences:
            if occ.slug in seen_articles:
                continue
            seen_articles.add(occ.slug)
            article = next((a for a in events if getattr(a, "slug", None) == occ.slug), None)
            body = _read_source_body(article) if article else ""
            when = occ.date.strftime("%Y-%m-%d %H:%M") if occ.date else ""
            title = f"{when} — {occ.title}" if when else occ.title
            emit_obj(title, _abs(siteurl, f"{occ.slug}/"), body)

    if announcements:
        blocks.append("# Recent Updates")
        blocks.append("")
        recent = sorted(announcements, key=lambda a: getattr(a, "date", today), reverse=True)[:RECENT_ANNOUNCEMENTS]
        for a in recent:
            emit_obj(a.title, _abs(siteurl, f"{a.slug}/"), _read_source_body(a))

    return "\n".join(blocks).rstrip() + "\n"


def _write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(text)


_collected = {"articles": [], "pages": [], "settings": None}


def _on_articles(article_generator):
    _collected["articles"] = list(article_generator.articles or [])
    _collected["settings"] = article_generator.settings


def _on_pages(page_generator):
    _collected["pages"] = list(page_generator.pages or [])
    if _collected["settings"] is None:
        _collected["settings"] = page_generator.settings


def on_finalized(pelican_obj):
    settings = _collected["settings"] or pelican_obj.settings
    output_path = settings.get("OUTPUT_PATH", "output")
    siteurl = settings.get("SITEURL", "")
    sitename = settings.get("SITENAME", "")
    sitedescription = settings.get("SITEDESCRIPTION", "")

    articles = _collected["articles"]
    pages = _collected["pages"]

    index_text = _build_llms_index(siteurl, sitename, sitedescription, pages, articles)
    full_text = _build_llms_full(siteurl, sitename, sitedescription, pages, articles)

    _write(os.path.join(output_path, "llms.txt"), index_text)
    _write(os.path.join(output_path, "llms-full.txt"), full_text)
    _write(os.path.join(output_path, ".well-known", "llms.txt"), index_text)
    _write(os.path.join(output_path, ".well-known", "llms-full.txt"), full_text)


def register():
    signals.article_generator_finalized.connect(_on_articles)
    signals.page_generator_finalized.connect(_on_pages)
    signals.finalized.connect(on_finalized)
