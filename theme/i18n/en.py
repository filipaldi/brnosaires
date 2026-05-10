"""English UI strings. British English, no em-dashes, light touch of attitude
on the user-facing bits, plain and clear on the aria-labels.

Keep key-for-key in sync with cs.py."""

STRINGS = {
    # --- site-level ---
    "site_description": "Argentine tango in Brno, kept current and clear",

    # --- navigation (aria-labels in base.html) ---
    "main_navigation": "Main navigation",
    "marathon_navigation": "Marathon navigation",
    "language_switcher": "Switch language",

    # --- page.html: series hub "upcoming dates" block ---
    "series_upcoming_heading": "Next dates",
    "series_upcoming_aria": "Upcoming dates in this series",
    "no_upcoming_dates": "Nothing on the calendar just yet. Keep an eye on our socials so you don't miss the next one.",

    # --- article.html: recurring-series note ---
    "part_of_series": "Part of a recurring series:",

    # --- category.html ---
    "category_announcement": "Announcements",
    "category_curiosity": "Curiosities",
    "pagination_aria": "Pagination",
    "pagination_prev": "← Previous",
    "pagination_next": "Next →",
    # rendered as: "Page {n} of {total}"
    "pagination_page_of": "Page {n} of {total}",

    # --- widget_calendar_link.html ---
    "subscribe_calendar": "Subscribe to the calendar",

    # --- widget_calendar.html ---
    "event_calendar_aria": "Event calendar",

    # --- base.html: copy-link confirmation prefix ---
    "copied_prefix": "✓ ",
}
