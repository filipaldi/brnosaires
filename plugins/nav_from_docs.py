"""
Reads nav documents from content/navigation/ (marathon.md, main.md), parses label,link lines,
resolves slugs to URLs from generator.pages, and sets context['nav_items'] for templates.
"""
import os
from pelican import signals

NAV_FILES = ("marathon.md", "main.md")


def _parse_nav_file(path):
    if not os.path.isfile(path):
        return []
    items = []
    with open(path, "r", encoding="utf-8") as f:
        for raw in f:
            line = raw.strip()
            if not line or line.lstrip().startswith("#"):
                continue
            idx = line.find(",")
            if idx < 0:
                continue
            label = line[:idx].strip()
            link = line[idx + 1 :].strip()
            if not label or not link:
                continue
            items.append({"label": label, "link": link})
    return items


def _resolve_items(items, pages_by_slug):
    result = []
    for item in items:
        label = item["label"]
        link = item["link"]
        if link.startswith("http://") or link.startswith("https://"):
            result.append(
                {
                    "label": label,
                    "url": link,
                    "slug": None,
                    "external": True,
                }
            )
        else:
            page = pages_by_slug.get(link)
            url = page.url if page else link + "/"
            result.append(
                {
                    "label": label,
                    "url": url,
                    "slug": link,
                    "external": False,
                }
            )
    return result


def build_nav_items(generator):
    settings = generator.settings
    path = settings.get("NAVIGATION_PATH")
    if path is None:
        path = os.path.join(settings["PATH"], "navigation")
    if not os.path.isdir(path):
        generator.context["nav_items"] = {"marathon": [], "main": []}
        return
    pages_by_slug = {p.slug: p for p in generator.pages}
    nav_items = {}
    for filename in NAV_FILES:
        key = filename.replace(".md", "").lower()
        filepath = os.path.join(path, filename)
        raw_items = _parse_nav_file(filepath)
        nav_items[key] = _resolve_items(raw_items, pages_by_slug)
    generator.context["nav_items"] = nav_items


def register():
    signals.page_generator_finalized.connect(build_nav_items)
