from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime, timedelta, timezone
from notion_client import Client
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from config import CONTENT_PATHS, DATE_FILTER_MONTHS
from converters.base_converter import BaseConverter
from reporter import MigrationReporter


class EventsConverter(BaseConverter):
    def __init__(self, notion_client: Client, reporter: MigrationReporter):
        super().__init__(notion_client, CONTENT_PATHS['events'])
        self.reporter = reporter
        self.cutoff_date = datetime.now(timezone.utc) - timedelta(days=DATE_FILTER_MONTHS * 30)

    def convert_page(self, page_id: str, page_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        try:
            properties = self.extract_properties(page_data)
            
            date_value = (properties.get('date') or properties.get('Date') or 
                         properties.get('start_date') or properties.get('start date') or
                         properties.get('event_date') or properties.get('event date'))
            
            event_date = None
            event_end_date = None
            
            if date_value:
                parsed = self._parse_date(date_value)
                if isinstance(date_value, dict):
                    event_date = parsed
                    end_date_value = date_value.get('end')
                    if end_date_value:
                        event_end_date = self._parse_date({'start': end_date_value})
                else:
                    event_date = parsed
            
            if event_end_date and event_end_date < self.cutoff_date:
                self.reporter.add_skipped('events', f'Event ended more than {DATE_FILTER_MONTHS} months ago')
                return None
            elif event_date and event_end_date is None and event_date < self.cutoff_date:
                self.reporter.add_skipped('events', f'Event older than {DATE_FILTER_MONTHS} months')
                return None

            title = properties.get('title') or 'Untitled Event'
            slug = self.generate_slug(title, page_id)
            
            content = self.get_page_content(page_id)
            
            metadata = {
                'title': title,
                'slug': slug,
            }
            
            if event_date:
                metadata['event-start'] = event_date
                metadata['date'] = event_date
            elif page_data.get('created_time'):
                try:
                    created_time = page_data.get('created_time')
                    fallback_date = datetime.fromisoformat(created_time.replace('Z', '+00:00'))
                    if fallback_date.tzinfo is None:
                        fallback_date = fallback_date.replace(tzinfo=timezone.utc)
                    metadata['event-start'] = fallback_date
                    metadata['date'] = fallback_date
                except:
                    pass
            
            if event_end_date:
                metadata['event-end'] = event_end_date
            
            venue_keys = ['venue', 'location', 'place', 'where']
            for key in venue_keys:
                if key in properties and properties[key]:
                    metadata['venue'] = properties[key]
                    break
            
            category_keys = ['category', 'type', 'event_type', 'event type']
            for key in category_keys:
                if key in properties and properties[key]:
                    metadata['category'] = properties[key]
                    break
            
            tags_keys = ['tags', 'tag']
            for key in tags_keys:
                if key in properties:
                    tags = properties[key]
                    if isinstance(tags, list) and tags:
                        metadata['tags'] = tags
                        break
                    elif tags:
                        metadata['tags'] = [tags] if isinstance(tags, str) else tags
                        break

            frontmatter = self.frontmatter_gen.generate(metadata)
            filename = f"{slug}.md"
            self.save_markdown_file(filename, frontmatter, content)
            
            self.reporter.add_converted('events')
            return {'slug': slug, 'filename': filename}
            
        except Exception as e:
            error_msg = f"Error converting event {page_id}: {str(e)}"
            self.reporter.add_failed('events', error_msg)
            return None

    def _parse_date(self, date_value: Any) -> Optional[datetime]:
        if isinstance(date_value, dict):
            start = date_value.get('start')
            if start:
                try:
                    dt = datetime.fromisoformat(start.replace('Z', '+00:00'))
                    if dt.tzinfo is None:
                        dt = dt.replace(tzinfo=timezone.utc)
                    return dt
                except:
                    pass
        elif isinstance(date_value, str):
            try:
                dt = datetime.fromisoformat(date_value.replace('Z', '+00:00'))
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=timezone.utc)
                return dt
            except:
                pass
        return None
