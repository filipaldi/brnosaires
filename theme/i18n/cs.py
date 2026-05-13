"""Czech UI strings. The default language — must contain every key."""

STRINGS = {
    # --- site-level ---
    "site_description": "Přehledně a aktuálně o argentinském tangu v Brně",

    # --- navigation (aria-labels in base.html) ---
    "main_navigation": "Hlavní navigace",
    "marathon_navigation": "Navigace maratonu",
    # Language switcher: the visible label is the *target* language's own name
    # (an endonym — same in any UI language); the aria-label spells out the action.
    "lang_name_cs": "Čeština",
    "lang_name_en": "English",
    "switch_to_cs": "Přepnout na češtinu",
    "switch_to_en": "Switch to English",

    # --- page.html: series hub "upcoming dates" block ---
    "series_upcoming_heading": "Nejbližší termíny",
    "series_upcoming_aria": "Nejbližší termíny série",
    "no_upcoming_dates": "Zatím nic naplánovaného. Sleduj nás na sociálních sítích, ať ti nic neuteče.",

    # --- article.html: recurring-series note ---
    "part_of_series": "Součást pravidelné série:",

    # --- article.html: first-timer nudge on milonga/praktika events ---
    "first_milonga_prompt": "Poprvé na milonze?",
    "first_milonga_link": "Mrkni, jak na to.",
    "event_entry_label": "Vstupné:",

    # --- category.html ---
    "category_announcement": "Oznámení",
    "category_curiosity": "Pikošky",
    "pagination_aria": "Stránkování",
    "pagination_prev": "← Předchozí",
    "pagination_next": "Další →",
    # rendered as: "Strana {n} / {total}"
    "pagination_page_of": "Strana {n} / {total}",

    # --- widget_calendar_link.html ---
    "subscribe_calendar": "Odebírej do kalendáře",

    # --- widget_calendar.html ---
    "event_calendar_aria": "Kalendář akcí",

    # --- components/footer.html ---
    "footer_tagline": "Argentinské tango v Brně — milongy, lekce, akce.",
    "footer_links_label": "Odkazy v patičce",
    "footer_months_label": "Milongy po měsících:",
    "footer_subscribe_label": "Odebírej do kalendáře:",
    "footer_ics_milongas": "milongy .ics",
    "footer_ics_classes": "lekce .ics",
    "footer_ics_all": "vše .ics",

    # --- page.html: evergreen month pages (/milongy-brno-<měsíc>/) ---
    "month_page_empty": "Na tenhle měsíc zatím žádné milongy vypsané nejsou.",
    "month_page_full_calendar": "Celý kalendář →",
    "month_page_prev": "← {month}",   # prev-month link; {month} = the month name (nominative)
    "month_page_next": "{month} →",   # next-month link
    "month_page_other_months_label": "Milongy po měsících:",

    # --- base.html: copy-link confirmation prefix ---
    "copied_prefix": "✓ ",
}
