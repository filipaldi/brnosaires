"""English UI strings. British English, no em-dashes, light touch of attitude
on the user-facing bits, plain and clear on the aria-labels.

Keep key-for-key in sync with cs.py."""

STRINGS = {
    # --- site-level ---
    "site_description": "Argentine tango in Brno, kept current and clear",

    # --- navigation (aria-labels in base.html) ---
    "main_navigation": "Main navigation",
    "marathon_navigation": "Marathon navigation",
    "open_menu": "Open menu",
    "close_menu": "Close menu",
    "quick_links": "Quick links",
    # Language switcher: the visible label is the *target* language's own name
    # (an endonym — same in any UI language); the aria-label spells out the action.
    "lang_name_cs": "Čeština",
    "lang_name_en": "English",
    "switch_to_cs": "Přepnout na češtinu",
    "switch_to_en": "Switch to English",

    # --- page.html: series hub "upcoming dates" block ---
    "series_upcoming_heading": "Next dates",
    "series_upcoming_aria": "Upcoming dates in this series",
    "no_upcoming_dates": "Nothing on the calendar just yet. Keep an eye on our socials so you don't miss the next one.",

    # --- article.html: recurring-series note ---
    "part_of_series": "Part of a recurring series:",

    # --- article.html: first-timer nudge on milonga/praktika events ---
    "first_milonga_prompt": "First time at a milonga?",
    "first_milonga_link": "Here's how it goes.",
    "event_entry_label": "Entry",
    "event_url_label": "More info & tickets",
    # event header <dl> labels (article.html semantic rework)
    "event_type_label": "Event type",
    "event_when_label": "When",
    "event_instructor_label": "Teachers",
    "event_organiser_label": "Organiser",
    "event_location_label": "Venue",
    # Screen readers otherwise announce the venue link as a bare address.
    "open_in_maps": "Open in maps",
    # localised event-type words (keyed by the raw event-type metadata value)
    "event_type_class": "Class",
    "event_type_milonga": "Milonga",
    "event_type_neolonga": "Neolonga",
    "event_type_praktika": "Praktika",
    "event_type_workshop": "Workshop",

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

    # --- components/footer.html ---
    "footer_tagline": "Argentine tango in Brno — milongas, classes, events.",
    "footer_h_events": "What's on",
    "footer_h_read": "Have a read",
    "footer_h_learn": "Learn it",
    "footer_months_label": "Milongas by month",
    "footer_subscribe_label": "Pop it in your calendar",
    "footer_ics_milongas": "milongas .ics",
    "footer_ics_classes": "classes .ics",
    "footer_ics_all": "all .ics",

    # --- page.html: evergreen month pages (/milongy-brno-<month>/) ---
    "month_page_empty": "No milongas listed for this month yet.",
    "month_page_full_calendar": "Full calendar →",
    "month_page_prev": "← {month}",   # prev-month link; {month} = the month name
    "month_page_next": "{month} →",   # next-month link
    "month_page_other_months_label": "Milongas month by month:",

    # --- base.html: copy-link confirmation prefix ---
    "copied_prefix": "✓ ",
}
