from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime
from notion_client import Client
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from config import CONTENT_PATHS
from converters.base_converter import BaseConverter
from reporter import MigrationReporter


class ClassesConverter(BaseConverter):
    def __init__(self, notion_client: Client, reporter: MigrationReporter):
        super().__init__(notion_client, CONTENT_PATHS['classes'])
        self.reporter = reporter

    def convert_page(self, page_id: str, page_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        try:
            properties = self.extract_properties(page_data)
            
            title = (properties.get('title') or properties.get('class_name') or 
                    properties.get('class name') or properties.get('name') or 'Untitled Class')
            slug = self.generate_slug(title, page_id)
            
            content = self.get_page_content(page_id)
            
            metadata = {
                'title': title,
                'slug': slug,
                'category': 'class',
            }
            
            instructor_keys = ['instructor', 'teacher', 'teacher_name', 'teacher name']
            for key in instructor_keys:
                if key in properties and properties[key]:
                    metadata['instructor'] = properties[key]
                    break
            
            day_keys = ['day', 'weekday', 'day_of_week', 'day of week']
            for key in day_keys:
                if key in properties and properties[key]:
                    metadata['day'] = properties[key]
                    break
            
            time_keys = ['time', 'start_time', 'start time', 'schedule']
            for key in time_keys:
                if key in properties and properties[key]:
                    metadata['time'] = properties[key]
                    break
            
            level_keys = ['level', 'difficulty', 'class_level', 'class level']
            for key in level_keys:
                if key in properties and properties[key]:
                    metadata['level'] = properties[key]
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
            
            self.reporter.add_converted('classes')
            return {'slug': slug, 'filename': filename}
            
        except Exception as e:
            error_msg = f"Error converting class {page_id}: {str(e)}"
            self.reporter.add_failed('classes', error_msg)
            return None
