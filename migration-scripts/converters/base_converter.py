from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, Any, Optional
from notion_client import Client
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from config import CONTENT_PATHS
from utils.block_converter import BlockConverter
from utils.image_handler import ImageHandler
from utils.frontmatter import FrontmatterGenerator
from utils.link_resolver import LinkResolver


class BaseConverter(ABC):
    def __init__(self, notion_client: Client, output_dir: Path):
        self.notion = notion_client
        self.output_dir = output_dir
        self.block_converter = BlockConverter()
        self.image_handler = ImageHandler()
        self.frontmatter_gen = FrontmatterGenerator()
        self.link_resolver = LinkResolver()
        self.output_dir.mkdir(parents=True, exist_ok=True)

    @abstractmethod
    def convert_page(self, page_id: str, page_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        pass

    def get_page_blocks(self, page_id: str) -> list:
        blocks = []
        cursor = None
        
        while True:
            response = self.notion.blocks.children.list(
                block_id=page_id,
                start_cursor=cursor
            )
            blocks.extend(response.get('results', []))
            
            if not response.get('has_more'):
                break
            cursor = response.get('next_cursor')
        
        return blocks

    def get_page_content(self, page_id: str) -> str:
        blocks = self.get_page_blocks(page_id)
        markdown = self.block_converter.convert_blocks(blocks)
        markdown = self.image_handler.update_image_references(markdown, page_id)
        markdown = self.link_resolver.resolve_links(markdown)
        return markdown

    def extract_properties(self, page_data: Dict[str, Any]) -> Dict[str, Any]:
        properties = {}
        page_props = page_data.get('properties', {})
        
        for prop_name, prop_data in page_props.items():
            prop_type = prop_data.get('type')
            prop_name_lower = prop_name.lower()
            
            if prop_type == 'title':
                title_parts = prop_data.get('title', [])
                if title_parts:
                    properties['title'] = ''.join([part.get('plain_text', '') for part in title_parts])
                    properties[prop_name] = properties['title']
                    properties[prop_name_lower] = properties['title']
            elif prop_type == 'rich_text':
                rich_text_parts = prop_data.get('rich_text', [])
                if rich_text_parts:
                    text = ''.join([part.get('plain_text', '') for part in rich_text_parts])
                    properties[prop_name] = text
                    properties[prop_name_lower] = text
            elif prop_type == 'date':
                date_data = prop_data.get('date')
                if date_data:
                    properties[prop_name] = date_data
                    properties[prop_name_lower] = date_data
            elif prop_type == 'select':
                select_data = prop_data.get('select')
                if select_data:
                    value = select_data.get('name')
                    properties[prop_name] = value
                    properties[prop_name_lower] = value
            elif prop_type == 'multi_select':
                multi_select = prop_data.get('multi_select', [])
                values = [item.get('name') for item in multi_select]
                properties[prop_name] = values
                properties[prop_name_lower] = values
            elif prop_type == 'checkbox':
                value = prop_data.get('checkbox', False)
                properties[prop_name] = value
                properties[prop_name_lower] = value
            elif prop_type == 'number':
                value = prop_data.get('number')
                if value is not None:
                    properties[prop_name] = value
                    properties[prop_name_lower] = value
            elif prop_type == 'url':
                value = prop_data.get('url')
                if value:
                    properties[prop_name] = value
                    properties[prop_name_lower] = value
            elif prop_type == 'relation':
                relation = prop_data.get('relation', [])
                properties[prop_name] = [item.get('id') for item in relation]
                properties[prop_name_lower] = properties[prop_name]
            elif prop_type == 'people':
                people = prop_data.get('people', [])
                properties[prop_name] = [person.get('name', person.get('id', '')) for person in people]
                properties[prop_name_lower] = properties[prop_name]
            elif prop_type == 'files':
                files = prop_data.get('files', [])
                file_urls = []
                for file_item in files:
                    if file_item.get('type') == 'external':
                        file_urls.append(file_item.get('external', {}).get('url', ''))
                    elif file_item.get('type') == 'file':
                        file_urls.append(file_item.get('file', {}).get('url', ''))
                properties[prop_name] = file_urls
                properties[prop_name_lower] = file_urls
        
        return properties

    def generate_slug(self, title: str, page_id: str) -> str:
        import re
        from unidecode import unidecode
        
        slug = unidecode(title.lower())
        slug = re.sub(r'[^a-z0-9]+', '-', slug)
        slug = re.sub(r'^-+|-+$', '', slug)
        if not slug:
            slug = page_id[:8]
        return slug

    def save_markdown_file(self, filename: str, frontmatter: str, content: str):
        file_path = self.output_dir / filename
        full_content = f"{frontmatter}\n\n{content}\n"
        file_path.write_text(full_content, encoding='utf-8')
