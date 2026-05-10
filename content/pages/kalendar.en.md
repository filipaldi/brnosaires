---
title: Brno Tango Calendar - Tango Brno
date: 2026-01-17 18:00:00
lang: en
slug: tango-kalendar-brno
description: The calendar of Brno tango events. Milongas, praktikas and classes in one place, laid out month by month.
author: Filip Paldia
preview_image: /images/milonga-hned-vedle.avif
---

# Brno Tango Calendar

The current calendar of Brno tango events. Milongas, praktikas and classes, all in one place.

<widget-calendar-link 
    cal_file_name="events" 
    filter_by_type="milonga praktika workshop"
    filter_by_path="events" 
    label="📆 Subscribe to events in your calendar" 
    label_webcal="Apple" 
    label_google="Google" 
    label_outlook="Copy for others">
</widget-calendar-link>


<widget-calendar 
    start="this-week" 
    group_by="week day" 
    headers="week day" 
    filter_by_type="milonga praktika workshop" 
    days="120"
    hide_empty_days="true"
    card_size="s">
</widget-calendar>
