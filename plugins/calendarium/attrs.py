"""
Widget attribute parsing utilities.
"""
from . import config


def parse_widget_attrs(tag_content, defaults=None):
    if defaults is None:
        defaults = config.CALENDAR_DEFAULTS
    result = dict(defaults)
    if not tag_content:
        return result
    for match in config.ATTR_PATTERN.finditer(tag_content):
        key = match.group(1).lower().replace('-', '_')
        value = match.group(2)
        if key not in result:
            continue
        if key == 'hide_empty_days':
            result[key] = value.lower() in ('true', 'yes', '1')
        elif key == 'days':
            try:
                result[key] = int(value)
            except (ValueError, TypeError):
                pass
        else:
            result[key] = value if value else None
    return result


def parse_calendar_link_attrs(tag_content, defaults=None):
    if defaults is None:
        defaults = config.CALENDAR_LINK_DEFAULTS
    result = dict(defaults)
    if not tag_content:
        return result
    for match in config.ATTR_PATTERN.finditer(tag_content):
        key = match.group(1).lower().replace('-', '_')
        value = match.group(2)
        if key not in result:
            continue
        if key == 'days':
            try:
                result[key] = int(value)
            except (ValueError, TypeError):
                pass
        else:
            result[key] = value if value else None
    return result
