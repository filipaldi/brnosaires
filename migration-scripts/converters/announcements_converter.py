from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime, timezone
from notion_client import Client
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from config import CONTENT_PATHS
from converters.base_converter import BaseConverter
from reporter import MigrationReporter


class AnnouncementsConverter(BaseConverter):
    def __init__(self, notion_client: Client, reporter: MigrationReporter):
        super().__init__(notion_client, CONTENT_PATHS['announcements'])
        self.reporter = reporter

    def convert_page(self, page_id: str, page_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        try:
            properties = self.extract_properties(page_data)
            
            title = properties.get('Nadpis') or properties.get('nadpis') or 'Untitled Announcement'
            slug = self.generate_slug(title, page_id)
            
            content = self.get_page_content(page_id)
            
            date_value = properties.get('Datum') or properties.get('datum')
            event_date = None
            if date_value:
                parsed = self._parse_date(date_value)
                if isinstance(date_value, dict):
                    event_date = parsed
                else:
                    event_date = parsed
            
            if not event_date:
                created_time = page_data.get('created_time')
                if created_time:
                    try:
                        event_date = datetime.fromisoformat(created_time.replace('Z', '+00:00'))
                        if event_date.tzinfo is None:
                            event_date = event_date.replace(tzinfo=timezone.utc)
                    except:
                        pass
            
            metadata = {
                'title': title,
                'slug': slug,
                'category': 'announcement',
            }
            
            if event_date:
                metadata['date'] = event_date
            
            files_value = properties.get('files') or properties.get('Files')
            if files_value and isinstance(files_value, list) and len(files_value) > 0:
                featured_image_url = files_value[0]
                image_path = self.image_handler.download_image(featured_image_url, page_id)
                if image_path:
                    metadata['image'] = f"{{static}}/{image_path}"

            frontmatter = self.frontmatter_gen.generate(metadata)
            filename = f"{slug}.md"
            self.save_markdown_file(filename, frontmatter, content)
            
            self.reporter.add_converted('announcements')
            return {'slug': slug, 'filename': filename}
            
        except Exception as e:
            error_msg = f"Error converting announcement {page_id}: {str(e)}"
            self.reporter.add_failed('announcements', error_msg)
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
