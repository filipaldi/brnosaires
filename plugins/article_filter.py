"""
Pelican plugin: article_filter for filtering articles by category, slugs, sort, limit.
Input: articles + options. Output: filtered/sorted article list with requested metadata.
"""
import re
from datetime import datetime

ARTICLE_DEFAULTS = {
    'category': None,
    'slugs': None,
    'sort': None,
    'limit': None,
    'columns': None,
    'metadata': None,
    'card_size': None,
    'link': None,
    'frame': None,
}

ATTR_PATTERN = re.compile(r'(\w+)="([^"]*)"')


def parse_article_attrs(tag_content, defaults=None):
    if defaults is None:
        defaults = ARTICLE_DEFAULTS
    result = dict(defaults)
    if not tag_content:
        return result
    for match in ATTR_PATTERN.finditer(tag_content):
        key = match.group(1).lower().replace('-', '_')
        value = match.group(2)
        if key not in result:
            continue
        result[key] = value if value else None
    return result


def _filter_by_category(articles, category):
    if not category:
        return list(articles) if articles else []
    category_lower = category.strip().lower()
    out = []
    for a in articles or []:
        cat = getattr(a, "category", None)
        if cat and getattr(cat, "name", "").lower() == category_lower:
            out.append(a)
    return out


def _filter_by_slugs(articles, slugs):
    if not slugs:
        return None
    slug_list = slugs.split()
    if not slug_list:
        return None
    slug_to_article = {}
    for a in articles or []:
        slug = getattr(a, "slug", None)
        if slug:
            slug_to_article[slug] = a
    result = []
    for target_slug in slug_list:
        if target_slug in slug_to_article:
            result.append(slug_to_article[target_slug])
    return result


def _sort_articles(articles, sort):
    if not articles:
        return []
    sort_val = (sort or "").strip().lower()
    if sort_val == "oldest":
        return sorted(articles, key=lambda a: getattr(a, "date", None) or datetime.min)
    elif sort_val == "title":
        return sorted(articles, key=lambda a: getattr(a, "title", "") or "")
    else:
        return sorted(articles, key=lambda a: getattr(a, "date", None) or datetime.min, reverse=True)


def _apply_limit(articles, limit):
    if limit is None or not articles:
        return list(articles) if articles else []
    s = str(limit).strip().lower()
    if s == "all":
        return list(articles)
    if "last" in s:
        try:
            n = int(s.replace("last", "").replace(" ", ""))
            return list(articles)[-n:] if n > 0 else list(articles)
        except (ValueError, TypeError):
            return list(articles)
    try:
        n = int(limit)
        return list(articles)[: max(0, n)]
    except (ValueError, TypeError):
        return list(articles)


def _extract_metadata(article, metadata_fields):
    if not metadata_fields:
        return {}
    fields = metadata_fields.split()
    meta = getattr(article, "metadata", None) or {}
    result = {}
    for field in fields:
        field_normalized = field.lower().replace('-', '_')
        value = meta.get(field) or meta.get(field_normalized)
        if not value:
            value = getattr(article, field, None) or getattr(article, field_normalized, None)
        if value:
            result[field] = value
    return result


def article_filter(articles, category=None, slugs=None, sort=None, limit=None, metadata=None):
    filtered = _filter_by_category(articles, category)
    if slugs:
        by_slugs = _filter_by_slugs(filtered, slugs)
        if by_slugs is not None:
            display = by_slugs
        else:
            display = _apply_limit(_sort_articles(filtered, sort), limit)
    else:
        display = _apply_limit(_sort_articles(filtered, sort), limit)
    result = []
    for article in display:
        result.append({
            'article': article,
            'extra_metadata': _extract_metadata(article, metadata),
        })
    return result


def register():
    pass
