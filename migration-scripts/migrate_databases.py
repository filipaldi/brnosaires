#!/usr/bin/env python3
import json
import sys
from pathlib import Path
from notion_client import Client
sys.path.insert(0, str(Path(__file__).parent))
from config import NOTION_API_TOKEN, DATABASE_MAPPING_FILE, CONTENT_PATHS
from converters.events_converter import EventsConverter
from converters.announcements_converter import AnnouncementsConverter
from converters.curiosity_converter import CuriosityConverter
from converters.classes_converter import ClassesConverter
from converters.pages_converter import PagesConverter
from reporter import MigrationReporter


def load_mapping():
    if not DATABASE_MAPPING_FILE.exists():
        raise FileNotFoundError(f"Mapping file not found: {DATABASE_MAPPING_FILE}. Please run explore_databases.py first.")
    
    with open(DATABASE_MAPPING_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)


def get_converter_for_type(db_type: str, notion: Client, reporter: MigrationReporter):
    converters = {
        'events': EventsConverter,
        'announcements': AnnouncementsConverter,
        'curiosity': CuriosityConverter,
        'classes': ClassesConverter,
    }
    
    converter_class = converters.get(db_type)
    if converter_class:
        return converter_class(notion, reporter)
    return None


def migrate_database(notion: Client, db_id: str, db_type: str, reporter: MigrationReporter, mapping: dict):
    converter = get_converter_for_type(db_type, notion, reporter)
    if not converter:
        print(f"Warning: No converter found for type '{db_type}', skipping database {db_id}")
        return
    
    print(f"\nMigrating {db_type} database ({db_id})...")
    
    try:
        db_info = notion.databases.retrieve(database_id=db_id)
        data_sources = db_info.get('data_sources', [])
        
        all_pages = []
        
        for ds in data_sources:
            ds_id = ds.get('id')
            try:
                query_result = notion.data_sources.query(data_source_id=ds_id)
                pages = query_result.get('results', [])
                all_pages.extend(pages)
                
                while query_result.get('has_more'):
                    query_result = notion.data_sources.query(
                        data_source_id=ds_id,
                        start_cursor=query_result.get('next_cursor')
                    )
                    pages = query_result.get('results', [])
                    all_pages.extend(pages)
            except Exception as ds_err:
                print(f"  Warning: Could not query data source {ds_id[:8]}: {ds_err}")
        
        total = len(all_pages)
        reporter.set_total(db_type, total)
        
        for i, page in enumerate(all_pages, 1):
            page_id = page.get('id')
            print(f"  Converting page {i}/{total}: {page_id[:8]}...", end='\r')
            converter.convert_page(page_id, page)
        
        print(f"  Completed {total} pages")
    
    except Exception as e:
        print(f"\nError migrating database {db_id}: {e}")
        import traceback
        traceback.print_exc()
        reporter.add_failed(db_type, str(e))


def migrate_standalone_pages(notion: Client, page_ids: list, reporter: MigrationReporter):
    if not page_ids:
        return
    
    print(f"\nMigrating {len(page_ids)} standalone pages...")
    reporter.set_standalone_total(len(page_ids))
    
    converter = PagesConverter(notion, reporter)
    
    for i, page_id in enumerate(page_ids, 1):
        print(f"  Converting page {i}/{len(page_ids)}: {page_id[:8]}...", end='\r')
        try:
            page_data = notion.pages.retrieve(page_id=page_id)
            converter.convert_page(page_id, page_data)
        except Exception as e:
            error_msg = f"Error retrieving page {page_id}: {str(e)}"
            reporter.add_standalone_failed(error_msg)
    
    print(f"  Completed {len(page_ids)} pages")


def parse_migration_types():
    """Parse --type arguments from command line."""
    types = set()
    i = 0
    while i < len(sys.argv):
        if sys.argv[i] == '--type' and i + 1 < len(sys.argv):
            type_arg = sys.argv[i + 1].lower()
            if type_arg == 'all':
                return {'all'}
            types.add(type_arg)
            i += 2
        else:
            i += 1
    
    if '--announcements-only' in sys.argv or '--only-announcements' in sys.argv:
        types.add('announcements')
    
    if not types:
        return {'announcements', 'events'}
    
    return types


def main():
    notion = Client(auth=NOTION_API_TOKEN)
    
    print("Loading database mapping...")
    mapping = load_mapping()
    
    databases = mapping.get('databases', {})
    standalone_pages = mapping.get('standalone_pages', [])
    database_structures = mapping.get('database_structures', {})
    
    reporter = MigrationReporter()
    
    selected_types = parse_migration_types()
    migrate_all = 'all' in selected_types
    
    if not migrate_all:
        print(f"Running migration for selected types: {', '.join(sorted(selected_types))}")
    
    print(f"\nFound {len(databases)} databases and {len(standalone_pages)} standalone pages to migrate")
    
    for db_id, db_info in databases.items():
        db_type = db_info.get('type')
        if not db_type:
            if migrate_all:
                print(f"\nWarning: Database {db_id} has no type assigned. Skipping.")
                print(f"  Please update {DATABASE_MAPPING_FILE} to assign a type (events, announcements, curiosity, or classes)")
            continue
        
        if not migrate_all and db_type not in selected_types:
            continue
        
        migrate_database(notion, db_id, db_type, reporter, mapping)
    
    if migrate_all:
        migrate_standalone_pages(notion, standalone_pages, reporter)
    
    reporter.print_report()
    
    print("\nMigration complete!")


if __name__ == '__main__':
    main()
