---
title: Brnos Aires — full corpus index
description: Comprehensive listing of upcoming events, regular classes, and recent updates
---

> Comprehensive Brnos Aires listing — every upcoming event, every regular class, every recent announcement.
> Fetch /llms.txt for the curated short index.

## Key Pages
- [Calendar](/tango-kalendar-brno/): Upcoming milongas, workshops, practicas, classes
- [Classes](/tango-lekce-brno/): Regular class schedules
- [Milongas](/tango-milongy-brno/): Upcoming milongas in Brno
- [Workshops](/tango-workshopy-brno/): Upcoming workshops in Brno
- [Practicas](/tango-praktiky-brno/): Upcoming practicas in Brno
- [Curiosities](/tango-pikosky/): Articles about Argentine tango culture
- [Announcements](/lenka-pise-oznamy/): Latest announcements
- [About](/o-nas/): About Brnos Aires

## Upcoming Milongas
<widget-calendar
    start="today"
    filter_by_type="milonga"
    days="84"
    dedupe-recurring="true">
</widget-calendar>

## Upcoming Workshops
<widget-calendar
    start="today"
    filter_by_type="workshop"
    days="84"
    dedupe-recurring="true">
</widget-calendar>

## Upcoming Practicas
<widget-calendar
    start="today"
    filter_by_type="praktika"
    days="84"
    dedupe-recurring="true">
</widget-calendar>

## Regular Classes
<widget-calendar
    start="today"
    filter_by_type="class"
    days="14"
    dedupe-recurring="true">
</widget-calendar>

## Recent Announcements
<widget-articles category="announcement" limit="20"></widget-articles>

## Subscribe
<widget-calendar-link
    cal_file_name="events"
    filter_by_path="events"
    label="Subscribe to all events">
</widget-calendar-link>
