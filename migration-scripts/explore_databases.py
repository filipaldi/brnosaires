#!/usr/bin/env python3
import json
import sys
from pathlib import Path
from notion_client import Client
sys.path.insert(0, str(Path(__file__).parent))
from config import NOTION_API_TOKEN, DATABASE_MAPPING_FILE, CONTENT_DIR
from utils.directory_manager import DirectoryManager


def discover_databases(notion: Client):
    databases = []
    standalone_pages = []
    database_ids = set()
    
    try:
        search_results = notion.search(filter={"value": "data_source", "property": "object"})
        data_sources = search_results.get('results', [])
        
        while search_results.get('has_more'):
            search_results = notion.search(
                filter={"value": "data_source", "property": "object"},
                start_cursor=search_results.get('next_cursor')
            )
            data_sources.extend(search_results.get('results', []))
        
        for ds in data_sources:
            if ds.get('object') == 'database':
                databases.append(ds)
                database_ids.add(ds.get('id'))
        
        search_results = notion.search(filter={"value": "page", "property": "object"})
        all_pages = search_results.get('results', [])
        
        while search_results.get('has_more'):
            search_results = notion.search(
                filter={"value": "page", "property": "object"},
                start_cursor=search_results.get('next_cursor')
            )
            all_pages.extend(search_results.get('results', []))
        
        for page in all_pages:
            parent = page.get('parent', {})
            parent_type = parent.get('type')
            db_id = None
            
            if parent_type == 'database_id':
                db_id = parent.get('database_id')
            elif parent_type == 'data_source_id':
                db_id = parent.get('database_id')
            
            if db_id:
                if db_id not in database_ids:
                    try:
                        db_info = notion.databases.retrieve(database_id=db_id)
                        databases.append(db_info)
                        database_ids.add(db_id)
                    except Exception as db_err:
                        print(f"  Note: Could not retrieve database {db_id[:8]}: {db_err}")
            elif parent_type in ['page_id', 'workspace', 'block_id']:
                standalone_pages.append(page)
            else:
                standalone_pages.append(page)
    
    except Exception as e:
        print(f"Error discovering databases: {e}")
        import traceback
        traceback.print_exc()
        return [], []
    
    return databases, standalone_pages


def analyze_database(notion: Client, database_id: str, database_title: str):
    structure = {
        'id': database_id,
        'title': database_title,
        'properties': {},
        'data_sources': []
    }
    
    try:
        db_info = notion.databases.retrieve(database_id=database_id)
        data_sources = db_info.get('data_sources', [])
        
        all_properties = {}
        total_pages = 0
        
        for ds in data_sources:
            ds_id = ds.get('id')
            structure['data_sources'].append({
                'id': ds_id,
                'name': ds.get('name', 'Unnamed')
            })
            
            try:
                ds_info = notion.data_sources.retrieve(data_source_id=ds_id)
                properties = ds_info.get('properties', {})
                
                for prop_name, prop_data in properties.items():
                    if prop_name not in all_properties:
                        prop_type = prop_data.get('type')
                        all_properties[prop_name] = {
                            'type': prop_type,
                            'id': prop_data.get('id')
                        }
                
                try:
                    query_result = notion.data_sources.query(data_source_id=ds_id, page_size=5)
                    sample_pages = query_result.get('results', [])
                    if sample_pages:
                        total_pages += len(sample_pages)
                        while query_result.get('has_more'):
                            query_result = notion.data_sources.query(
                                data_source_id=ds_id,
                                start_cursor=query_result.get('next_cursor'),
                                page_size=100
                            )
                            total_pages += len(query_result.get('results', []))
                except Exception as query_err:
                    pass
            except Exception as ds_err:
                pass
        
        structure['properties'] = all_properties
        structure['total_count'] = total_pages
        structure['sample_count'] = min(5, total_pages) if total_pages > 0 else 0
    
    except Exception as e:
        print(f"Error analyzing database {database_id}: {e}")
        import traceback
        traceback.print_exc()
    
    return structure


def print_exploration_report(databases, standalone_pages, database_structures):
    print("\n" + "=" * 60)
    print("DATABASE EXPLORATION REPORT")
    print("=" * 60)
    
    print(f"\nTotal databases found: {len(databases)}")
    print(f"Total standalone pages found: {len(standalone_pages)}")
    
    print("\n" + "-" * 60)
    print("DATABASES:")
    print("-" * 60)
    
    for db in databases:
        db_id = db.get('id', 'Unknown')
        db_title = db.get('title', [])
        if db_title:
            title_text = ''.join([part.get('plain_text', '') for part in db_title])
        else:
            title_text = 'Untitled'
        
        structure = database_structures.get(db_id, {})
        prop_count = len(structure.get('properties', {}))
        total_count = structure.get('total_count', 0)
        
        print(f"\n  Database: {title_text}")
        print(f"    ID: {db_id}")
        print(f"    Properties: {prop_count}")
        print(f"    Total pages: {total_count}")
        
        if structure.get('properties'):
            print(f"    Property details:")
            for prop_name, prop_info in structure['properties'].items():
                print(f"      - {prop_name}: {prop_info['type']}")
    
    print("\n" + "-" * 60)
    print("STANDALONE PAGES:")
    print("-" * 60)
    print(f"  Total: {len(standalone_pages)}")
    if standalone_pages:
        print(f"  Sample titles:")
        for page in standalone_pages[:5]:
            props = page.get('properties', {})
            title = 'Untitled'
            for prop_name, prop_data in props.items():
                if prop_data.get('type') == 'title':
                    title_parts = prop_data.get('title', [])
                    if title_parts:
                        title = ''.join([part.get('plain_text', '') for part in title_parts])
                        break
            print(f"    - {title}")
        if len(standalone_pages) > 5:
            print(f"    ... and {len(standalone_pages) - 5} more")
    
    print("\n" + "=" * 60 + "\n")


def main():
    notion = Client(auth=NOTION_API_TOKEN)
    
    print("Discovering Notion databases and pages...")
    databases, standalone_pages = discover_databases(notion)
    
    print("Analyzing database structures...")
    database_structures = {}
    for db in databases:
        db_id = db.get('id')
        db_title = db.get('title', [])
        if db_title:
            title_text = ''.join([part.get('plain_text', '') for part in db_title])
        else:
            title_text = 'Untitled'
        structure = analyze_database(notion, db_id, title_text)
        database_structures[db_id] = structure
    
    print_exploration_report(databases, standalone_pages, database_structures)
    
    mapping_data = {
        'databases': {},
        'standalone_pages': [page.get('id') for page in standalone_pages],
        'database_structures': database_structures
    }
    
    for db in databases:
        db_id = db.get('id')
        mapping_data['databases'][db_id] = {
            'title': ''.join([part.get('plain_text', '') for part in db.get('title', [])]) if db.get('title') else 'Untitled',
            'type': None
        }
    
    DATABASE_MAPPING_FILE.write_text(json.dumps(mapping_data, indent=2), encoding='utf-8')
    print(f"Database mapping saved to {DATABASE_MAPPING_FILE}")
    
    database_types = set()
    for db_id, db_info in mapping_data['databases'].items():
        db_type = db_info.get('type')
        if db_type:
            database_types.add(db_type)
    
    if not database_types:
        print("\nNote: Database types not yet identified. Please review the mapping file and update type fields.")
        print("Expected types: events, announcements, curiosity, classes")
    
    dir_manager = DirectoryManager()
    dir_manager.set_required_directories(database_types)
    changes = dir_manager.update_directory_structure(interactive=True)
    
    print("\nDirectory structure changes:")
    print(dir_manager.get_changes_report())
    
    print("\nExploration complete!")
    print(f"Next steps:")
    print(f"1. Review {DATABASE_MAPPING_FILE}")
    print(f"2. Update database type mappings in the file")
    print(f"3. Run migrate_databases.py to perform the migration")


if __name__ == '__main__':
    main()
