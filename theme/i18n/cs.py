"""Czech UI strings. The default language — must contain every key."""

STRINGS = {
    # --- site-level ---
    "site_description": "Přehledně a aktuálně o argentinském tangu v Brně",

    # --- navigation (aria-labels in base.html) ---
    "main_navigation": "Hlavní navigace",
    "marathon_navigation": "Navigace maratonu",
    "open_menu": "Otevřít menu",
    "close_menu": "Zavřít menu",
    "quick_links": "Rychlé odkazy",
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
    "event_entry_label": "Vstupné",
    "event_url_label": "Více info a vstupenky",
    # event header <dl> labels (article.html semantic rework)
    "event_type_label": "Typ akce",
    "event_when_label": "Kdy",
    "event_instructor_label": "Lektoři",
    # What goes between the last two teachers of an event. The spacing is part
    # of the string because it is part of the language: Czech does not leave a
    # one-letter conjunction at the end of a line, so the space after "a" is a
    # hard one. Three or more names get commas before it — "X, Y a Z".
    "event_instructor_and": " a\u00a0",
    "event_organiser_label": "Pořadatel",
    "event_location_label": "Místo",
    # Screen readers otherwise announce the venue link as a bare address.
    "open_in_maps": "Otevřít v mapách",
    "skip_to_content": "Přeskočit na obsah",
    "copied_status": "Odkaz zkopírován do schránky",
    # localised event-type words (keyed by the raw event-type metadata value)
    "event_type_class": "Lekce",
    "event_type_milonga": "Milonga",
    "event_type_neolonga": "Neolonga",
    "event_type_praktika": "Praktika",
    "event_type_workshop": "Workshop",

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
    "footer_h_events": "Co se chystá",
    "footer_h_read": "Mrkni",
    "footer_h_learn": "Nauč se",
    "footer_months_label": "Milongy podle měsíce",
    "footer_subscribe_label": "Nech si to v kalendáři",
    "footer_ics_milongas": "milongy .ics",
    "footer_ics_classes": "lekce .ics",
    "footer_ics_all": "vše .ics",
    "footer_feed": "novinky RSS",

    # --- page.html: evergreen month pages (/milongy-brno-<měsíc>/) ---
    "month_page_empty": "Na tenhle měsíc zatím žádné milongy vypsané nejsou.",
    "month_page_full_calendar": "Celý kalendář →",
    "month_page_prev": "← {month}",   # prev-month link; {month} = the month name (nominative)
    "month_page_next": "{month} →",   # next-month link
    "month_page_other_months_label": "Milongy po měsících:",

    # --- base.html: copy-link confirmation prefix ---

    # --- a repeating event, said out loud on its own page ---
    # The whole phrase per weekday, not a word slotted into a template: Czech
    # weekday nouns take three different forms after "každý" (každé pondělí,
    # každou středu, každý čtvrtek). Assembling that from parts needs a
    # grammar; a string table needs seven lines.
    "event_every_monday": "každé pondělí",
    "event_every_tuesday": "každé úterý",
    "event_every_wednesday": "každou středu",
    "event_every_thursday": "každý čtvrtek",
    "event_every_friday": "každý pátek",
    "event_every_saturday": "každou sobotu",
    "event_every_sunday": "každou neděli",
    "event_series_from": "od",
    "event_series_until": "do",

    "copied_prefix": "✓ ",
}
