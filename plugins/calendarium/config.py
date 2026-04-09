"""
Configuration constants and patterns for calendarium plugin.
"""
import re

EXCLUDED_CATEGORIES = ["announcement", "curiosity"]

CALENDAR_LINK_DEFAULTS = {
    'cal_file_name': None,
    'filter_by_type': None,
    'days': None,
    'start': None,
    'end': None,
    'filter_by_path': None,
    'category': None,
    'tags': None,
    'label': None,
    'label_webcal': None,
    'label_google': None,
    'label_outlook': None,
}

CALENDAR_LINK_PATTERN = re.compile(r'<widget-calendar-link([^>]*)>(?:</widget-calendar-link>)?', re.DOTALL)

_GENERATOR_CACHE = {}

CALENDAR_DEFAULTS = {
    'filter_by_type': None,
    'days': None,
    'start': None,
    'end': None,
    'limit': None,
    'sort': None,
    'group_by': None,
    'headers': None,
    'hide_empty_days': False,
    'card_size': 's',
}

ATTR_PATTERN = re.compile(r'(\w+)="([^"]*)"')

MONTH_NAMES_CS = [
    "leden", "únor", "březen", "duben", "květen", "červen",
    "červenec", "srpen", "září", "říjen", "listopad", "prosinec"
]
MONTH_NAMES_EN = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December"
]
