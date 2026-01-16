import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

NOTION_API_TOKEN = os.getenv('NOTION_API_TOKEN')
if not NOTION_API_TOKEN:
    raise ValueError('NOTION_API_TOKEN not found in .env file')

PROJECT_ROOT = Path(__file__).parent.parent
CONTENT_DIR = PROJECT_ROOT / 'content'
MIGRATION_SCRIPTS_DIR = Path(__file__).parent

DATABASE_MAPPING_FILE = MIGRATION_SCRIPTS_DIR / 'database_mapping.json'

CONTENT_PATHS = {
    'events': CONTENT_DIR / 'events',
    'announcements': CONTENT_DIR / 'announcements',
    'curiosity': CONTENT_DIR / 'curiosities',
    'classes': CONTENT_DIR / 'classes',
    'pages': CONTENT_DIR / 'pages',
    'images': CONTENT_DIR / 'images',
}

DATE_FILTER_MONTHS = 2
