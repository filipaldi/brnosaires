"""
Gallery widget plugin: scans image folders and reads optional .md files for alt text.
Input: folder path relative to content/images/. Output: list of image dicts with paths and alt text.
"""
import os
from pathlib import Path


def get_gallery_images(folder, content_path):
    if not folder:
        return []
    
    images_dir = Path(content_path) / "images" / folder
    
    if not images_dir.exists() or not images_dir.is_dir():
        return []
    
    image_extensions = {'.avif', '.jpg', '.jpeg', '.png', '.avif'}
    images = []
    
    for file_path in sorted(images_dir.iterdir()):
        if not file_path.is_file():
            continue
        
        if file_path.suffix.lower() not in image_extensions:
            continue
        
        md_file = file_path.with_suffix('.md')
        alt_text = ""
        
        if md_file.exists():
            try:
                with open(md_file, 'r', encoding='utf-8') as f:
                    alt_text = f.read().strip()
            except Exception:
                alt_text = ""
        
        if not alt_text:
            alt_text = file_path.stem
        
        relative_path = f"images/{folder}/{file_path.name}"
        
        images.append({
            'filename': file_path.name,
            'path': relative_path,
            'alt': alt_text
        })
    
    return images
