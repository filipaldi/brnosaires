import os
import sys
import requests
from pathlib import Path
from typing import Optional, Dict, Any
from urllib.parse import urlparse
sys.path.insert(0, str(Path(__file__).parent.parent))
from config import CONTENT_PATHS


class ImageHandler:
    def __init__(self):
        self.images_dir = CONTENT_PATHS['images']
        self.images_dir.mkdir(parents=True, exist_ok=True)
        self.downloaded_images: Dict[str, str] = {}

    def download_image(self, url: str, page_id: str, image_index: int = 0) -> Optional[str]:
        if not url:
            return None

        if url in self.downloaded_images:
            return self.downloaded_images[url]

        try:
            parsed_url = urlparse(url)
            filename = os.path.basename(parsed_url.path)
            if not filename or '.' not in filename:
                ext = self._get_extension_from_url(url)
                filename = f"{page_id}_{image_index}{ext}"

            local_path = self.images_dir / filename
            if local_path.exists():
                relative_path = f"images/{filename}"
                self.downloaded_images[url] = relative_path
                return relative_path

            response = requests.get(url, timeout=30)
            response.raise_for_status()

            local_path.write_bytes(response.content)
            relative_path = f"images/{filename}"
            self.downloaded_images[url] = relative_path
            return relative_path

        except Exception as e:
            print(f"Warning: Could not download image from {url}: {e}")
            return url

    def _get_extension_from_url(self, url: str) -> str:
        parsed = urlparse(url)
        path = parsed.path.lower()
        if '.jpg' in path or '.jpeg' in path:
            return '.jpg'
        elif '.png' in path:
            return '.png'
        elif '.gif' in path:
            return '.gif'
        elif '.webp' in path:
            return '.webp'
        return '.jpg'

    def update_image_references(self, markdown: str, page_id: str) -> str:
        import re
        pattern = r'!\[([^\]]*)\]\(([^)]+)\)'
        
        def replace_image(match):
            alt_text = match.group(1)
            url = match.group(2)
            if url.startswith('http'):
                local_path = self.download_image(url, page_id)
                if local_path:
                    return f"![{alt_text}]({{static}}/{local_path})"
            elif url.startswith('images/'):
                return f"![{alt_text}]({{static}}/{url})"
            return match.group(0)

        return re.sub(pattern, replace_image, markdown)
