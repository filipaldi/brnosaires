from typing import Dict, Optional
import re


class LinkResolver:
    def __init__(self, page_id_to_slug: Optional[Dict[str, str]] = None):
        self.page_id_to_slug = page_id_to_slug or {}

    def resolve_links(self, markdown: str) -> str:
        pattern = r'\[([^\]]+)\]\(([^)]+)\)'
        
        def replace_link(match):
            link_text = match.group(1)
            url = match.group(2)
            
            if url.startswith('http'):
                return match.group(0)
            
            notion_page_id = self._extract_notion_page_id(url)
            if notion_page_id and notion_page_id in self.page_id_to_slug:
                slug = self.page_id_to_slug[notion_page_id]
                return f"[{link_text}]({slug}.html)"
            
            return match.group(0)

        return re.sub(pattern, replace_link, markdown)

    def _extract_notion_page_id(self, url: str) -> Optional[str]:
        if 'notion.so' in url:
            parts = url.split('/')
            for part in parts:
                if len(part) == 32:
                    return part.replace('-', '')
        return None

    def add_mapping(self, page_id: str, slug: str):
        self.page_id_to_slug[page_id] = slug
