"""
Pelican plugin: calendarium filter (type, days, start, end, sort, limit) and group_events for calendar widget.
Input: articles + options. Output: filtered/sorted event list. group_events(events, group_by, lang) for grouping.
Also: iCal feed discovery from widget-calendar-link, .ics generation, feed_id map for subscribe link.
"""
from pelican import signals
from . import feed_links
from . import ics


def register():
    signals.page_generator_finalized.connect(feed_links.discover_calendar_link_feeds)
    signals.finalized.connect(ics.write_ics_feeds)
