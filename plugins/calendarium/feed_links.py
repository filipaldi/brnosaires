"""
Calendar link feed discovery and management.
"""
import hashlib
import re
from . import config
from . import attrs


def _slugify_feed_id(s):
    if not s:
        return ""
    s = str(s).strip().lower()
    s = re.sub(r'[^a-z0-9\-]+', '-', s)
    s = re.sub(r'-+', '-', s).strip('-')
    return s or "all"


def _feed_fingerprint(attrs):
    filter_keys = ('type', 'days', 'start', 'end', 'path', 'category', 'tags')
    parts = []
    for k in sorted(filter_keys):
        v = attrs.get(k)
        if v is not None and str(v).strip():
            parts.append(f"{k}={str(v).strip()}")
    return " ".join(parts)


def _derive_feed_id(attrs, fingerprint):
    feed_id_attr = (attrs.get('feed_id') or "").strip()
    if feed_id_attr:
        return _slugify_feed_id(feed_id_attr)
    if not fingerprint:
        return "all"
    h = hashlib.md5(fingerprint.encode("utf-8")).hexdigest()[:8]
    return f"feed_{h}"


def discover_calendar_link_feeds(generator):
    feed_specs = {}
    feed_id_map = {}

    def scan_content(content):
        if not content or "<widget-calendar-link" not in content:
            return
        for match in config.CALENDAR_LINK_PATTERN.finditer(content):
            attrs_str = match.group(1)
            tag_content = f"calendar-link{attrs_str}"
            parsed_attrs = attrs.parse_calendar_link_attrs(tag_content)
            fp = _feed_fingerprint(parsed_attrs)
            feed_id = _derive_feed_id(parsed_attrs, fp)
            if fp not in feed_specs:
                feed_specs[fp] = {"feed_id": feed_id, "filter": parsed_attrs}
            feed_id_map[fp] = feed_id

    for page in getattr(generator, "pages", []):
        if hasattr(page, "_content") and page._content:
            scan_content(page._content)
    for article in getattr(generator, "articles", []):
        if hasattr(article, "_content") and article._content:
            scan_content(article._content)

    feeds = list(feed_specs.values())
    seen_feed_id = set()
    unique_feeds = []
    for item in feeds:
        fid = item["feed_id"]
        if fid in seen_feed_id:
            continue
        seen_feed_id.add(fid)
        unique_feeds.append(item)

    generator.context["calendar_feeds"] = unique_feeds
    generator.context["calendar_feed_id_map"] = feed_id_map
    
    config._GENERATOR_CACHE["generator"] = generator
    config._GENERATOR_CACHE["feeds"] = unique_feeds


def get_feed_id_for_tag_content(tag_content, feed_map):
    parsed_attrs = attrs.parse_calendar_link_attrs(tag_content)
    fp = _feed_fingerprint(parsed_attrs)
    feed_id = feed_map.get(fp, "all")
    label = parsed_attrs.get("label")
    return feed_id, label


def get_calendar_subscribe_url(feed_id, siteurl, output_dir="calendars"):
    calendar_path = f"/{output_dir}/{feed_id}.ics"
    if not siteurl or not str(siteurl).strip():
        return calendar_path
    full_url = str(siteurl).rstrip("/") + calendar_path
    if full_url.startswith("https://"):
        return "webcal://" + full_url[8:]
    if full_url.startswith("http://"):
        return "webcal://" + full_url[7:]
    return full_url
