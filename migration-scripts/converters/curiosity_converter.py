from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime, timezone
from notion_client import Client
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from config import CONTENT_PATHS
from converters.base_converter import BaseConverter
from reporter import MigrationReporter


class CuriosityConverter(BaseConverter):
    def __init__(self, notion_client: Client, reporter: MigrationReporter):
        super().__init__(notion_client, CONTENT_PATHS['curiosity'])
        self.reporter = reporter

    def convert_page(self, page_id: str, page_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        try:
            properties = self.extract_properties(page_data)
            
            title = properties.get('title') or 'Untitled Article'
            slug = self.generate_slug(title, page_id)
            
            content = self.get_page_content(page_id)
            
            date_value = (properties.get('date') or properties.get('Date') or 
                         properties.get('published_date') or properties.get('published date') or
                         properties.get('published'))
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
                'category': 'curiosity',
            }
            
            if event_date:
                metadata['date'] = event_date
            
            author_keys = ['author', 'writer', 'by']
            for key in author_keys:
                if key in properties and properties[key]:
                    metadata['author'] = properties[key]
                    break
            
            tags_keys = ['tags', 'tag', 'categories']
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
            
            self.reporter.add_converted('curiosity')
            return {'slug': slug, 'filename': filename}
            
        except Exception as e:
            error_msg = f"Error converting curiosity article {page_id}: {str(e)}"
            self.reporter.add_failed('curiosity', error_msg)
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
