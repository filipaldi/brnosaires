from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime, timezone
from notion_client import Client
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from config import CONTENT_PATHS
from converters.base_converter import BaseConverter
from reporter import MigrationReporter


class PagesConverter(BaseConverter):
    def __init__(self, notion_client: Client, reporter: MigrationReporter):
        super().__init__(notion_client, CONTENT_PATHS['pages'])
        self.reporter = reporter

    def convert_page(self, page_id: str, page_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        try:
            properties = self.extract_properties(page_data)
            
            title = 'Untitled Page'
            if 'title' in properties:
                title = properties['title']
            elif page_data.get('properties'):
                for prop_name, prop_data in page_data['properties'].items():
                    if prop_data.get('type') == 'title':
                        title_parts = prop_data.get('title', [])
                        if title_parts:
                            title = ''.join([part.get('plain_text', '') for part in title_parts])
                            break
            
            if not title or title == 'Untitled Page':
                title = page_data.get('id', 'Untitled Page')[:8]
            
            slug = self.generate_slug(title, page_id)
            
            content = self.get_page_content(page_id)
            
            created_time = page_data.get('created_time')
            event_date = None
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
            }
            
            if event_date:
                metadata['date'] = event_date
            
            if 'tags' in properties:
                tags = properties.get('tags')
                if isinstance(tags, list):
                    metadata['tags'] = tags
                elif tags:
                    metadata['tags'] = [tags]

            frontmatter = self.frontmatter_gen.generate(metadata)
            filename = f"{slug}.md"
            self.save_markdown_file(filename, frontmatter, content)
            
            self.reporter.add_standalone_converted()
            return {'slug': slug, 'filename': filename}
            
        except Exception as e:
            error_msg = f"Error converting standalone page {page_id}: {str(e)}"
            self.reporter.add_standalone_failed(error_msg)
            return None
