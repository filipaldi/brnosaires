from typing import Dict, Any, Optional
from datetime import datetime


class FrontmatterGenerator:
    def __init__(self):
        pass

    def generate(self, metadata: Dict[str, Any], content_type: str = 'page') -> str:
        frontmatter_lines = ['---']
        
        if 'title' in metadata:
            title_value = metadata['title']
            frontmatter_lines.append(f"title: {self._escape_yaml(title_value, always_quote=True)}")
        
        if 'date' in metadata:
            date_str = self._format_date(metadata['date'])
            if date_str:
                frontmatter_lines.append(f"date: {date_str}")
        
        if 'event-start' in metadata:
            date_str = self._format_date(metadata['event-start'])
            if date_str:
                frontmatter_lines.append(f"event-start: {date_str}")
        
        if 'event-end' in metadata:
            date_str = self._format_date(metadata['event-end'])
            if date_str:
                frontmatter_lines.append(f"event-end: {date_str}")
        
        if 'end_date' in metadata:
            date_str = self._format_date(metadata['end_date'])
            if date_str:
                frontmatter_lines.append(f"end_date: {date_str}")
        
        if 'slug' in metadata:
            frontmatter_lines.append(f"slug: {metadata['slug']}")
        
        if 'category' in metadata:
            frontmatter_lines.append(f"category: {self._escape_yaml(metadata['category'])}")
        
        if 'tags' in metadata:
            tags = metadata['tags']
            if isinstance(tags, list):
                tags_str = ', '.join([self._escape_yaml(tag) for tag in tags])
                frontmatter_lines.append(f"tags: [{tags_str}]")
            elif tags:
                frontmatter_lines.append(f"tags: [{self._escape_yaml(tags)}]")
        
        if 'author' in metadata:
            frontmatter_lines.append(f"author: {self._escape_yaml(metadata['author'], always_quote=True)}")
        
        for key, value in metadata.items():
            if key not in ['title', 'date', 'end_date', 'event-start', 'event-end', 'slug', 'category', 'tags', 'author']:
                if value is not None:
                    frontmatter_lines.append(f"{key}: {self._escape_yaml(str(value))}")
        
        frontmatter_lines.append('---')
        return '\n'.join(frontmatter_lines)

    def _escape_yaml(self, value: str, always_quote: bool = False) -> str:
        if not isinstance(value, str):
            value = str(value)
        
        special_chars = [':', ',', '[', ']', '{', '}', '&', '*', '#', '?', '|', '<', '>', '=', '!', '%', '@', '`', "'"]
        
        if always_quote or any(char in value for char in special_chars):
            return f'"{value.replace('"', '\\"')}"'
        return value

    def _format_date(self, date_value: Any) -> Optional[str]:
        import pytz
        
        if isinstance(date_value, datetime):
            if date_value.tzinfo is not None:
                prague_tz = pytz.timezone('Europe/Prague')
                date_value = date_value.astimezone(prague_tz)
                date_value = date_value.replace(tzinfo=None)
            return date_value.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(date_value, str):
            try:
                dt = datetime.fromisoformat(date_value.replace('Z', '+00:00'))
                if dt.tzinfo:
                    prague_tz = pytz.timezone('Europe/Prague')
                    dt = dt.astimezone(prague_tz).replace(tzinfo=None)
                return dt.strftime('%Y-%m-%d %H:%M:%S')
            except:
                return date_value
        elif hasattr(date_value, 'start'):
            if hasattr(date_value.start, 'isoformat'):
                dt = datetime.fromisoformat(date_value.start.isoformat())
                if dt.tzinfo:
                    prague_tz = pytz.timezone('Europe/Prague')
                    dt = dt.astimezone(prague_tz).replace(tzinfo=None)
                return dt.strftime('%Y-%m-%d %H:%M:%S')
            return str(date_value.start)
        return None
