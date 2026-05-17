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
    'month': None,
    'limit': None,
    'sort': None,
    'group_by': None,
    'headers': None,
    'hide_empty_days': False,
    'card_mode': 'solid',
    'card_width': 's',
    'text_size': 's',
    'image_ratio': '1x1',
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

# Month names → 1..12, including the Czech genitive/locative forms that show up
# in month-page titles ("v lednu", "ledna", "v červnu", "v prosinci"…). Used to
# resolve the `month=` widget attribute. Unknown → None (the widget falls back to
# its normal days=/start=/end= behaviour).
MONTH_NAME_TO_NUM = {
    "leden": 1, "ledna": 1, "lednu": 1,
    "unor": 2, "únor": 2, "unora": 2, "února": 2, "unoru": 2, "únoru": 2,
    "brezen": 3, "březen": 3, "brezna": 3, "března": 3, "breznu": 3, "březnu": 3,
    "duben": 4, "dubna": 4, "dubnu": 4,
    "kveten": 5, "květen": 5, "kvetna": 5, "května": 5, "kvetnu": 5, "květnu": 5,
    "cerven": 6, "červen": 6, "cervna": 6, "června": 6, "cervnu": 6, "červnu": 6,
    "cervenec": 7, "červenec": 7, "cervence": 7, "července": 7, "cervenci": 7, "červenci": 7,
    "srpen": 8, "srpna": 8, "srpnu": 8,
    "zari": 9, "září": 9,
    "rijen": 10, "říjen": 10, "rijna": 10, "října": 10, "rijnu": 10, "říjnu": 10,
    "listopad": 11, "listopadu": 11,
    "prosinec": 12, "prosince": 12, "prosinci": 12,
    "january": 1, "february": 2, "march": 3, "april": 4, "may": 5, "june": 6,
    "july": 7, "august": 8, "september": 9, "october": 10, "november": 11, "december": 12,
}
