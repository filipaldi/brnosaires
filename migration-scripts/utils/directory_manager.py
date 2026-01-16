import os
import shutil
from pathlib import Path
from typing import List, Dict, Set
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from config import CONTENT_DIR, CONTENT_PATHS


class DirectoryManager:
    def __init__(self):
        self.content_dir = CONTENT_DIR
        self.required_dirs = set()
        self.changes = {
            'created': [],
            'removed': [],
            'renamed': [],
            'existing': []
        }

    def set_required_directories(self, database_types: Set[str]):
        self.required_dirs = {'pages', 'images'}
        for db_type in database_types:
            if db_type in CONTENT_PATHS:
                self.required_dirs.add(db_type)

    def update_directory_structure(self, interactive: bool = True) -> Dict[str, List[str]]:
        if not self.content_dir.exists():
            self.content_dir.mkdir(parents=True, exist_ok=True)

        existing_dirs = {d.name for d in self.content_dir.iterdir() if d.is_dir()}

        for dir_name in self.required_dirs:
            dir_path = self.content_dir / dir_name
            if not dir_path.exists():
                dir_path.mkdir(parents=True, exist_ok=True)
                self.changes['created'].append(dir_name)
            else:
                self.changes['existing'].append(dir_name)

        dirs_to_remove = existing_dirs - self.required_dirs
        for dir_name in dirs_to_remove:
            dir_path = self.content_dir / dir_name
            if dir_path.exists():
                has_files = any(dir_path.iterdir())
                if has_files and interactive:
                    response = input(
                        f"Directory '{dir_name}' contains files but doesn't match any discovered database. "
                        f"Remove it? (yes/no): "
                    )
                    if response.lower() != 'yes':
                        continue
                try:
                    shutil.rmtree(dir_path)
                    self.changes['removed'].append(dir_name)
                except Exception as e:
                    print(f"Warning: Could not remove directory '{dir_name}': {e}")

        return self.changes

    def get_changes_report(self) -> str:
        report = []
        if self.changes['created']:
            report.append(f"Created directories: {', '.join(self.changes['created'])}")
        if self.changes['removed']:
            report.append(f"Removed directories: {', '.join(self.changes['removed'])}")
        if self.changes['renamed']:
            report.append(f"Renamed directories: {', '.join(self.changes['renamed'])}")
        if self.changes['existing']:
            report.append(f"Existing directories: {', '.join(self.changes['existing'])}")
        return '\n'.join(report) if report else "No directory changes needed"
