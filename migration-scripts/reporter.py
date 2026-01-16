from typing import Dict, List, Optional
from dataclasses import dataclass, field


@dataclass
class DatabaseStats:
    total: int = 0
    converted: int = 0
    skipped: int = 0
    failed: int = 0
    errors: List[str] = field(default_factory=list)
    skip_reasons: Dict[str, int] = field(default_factory=dict)

    def add_converted(self):
        self.converted += 1

    def add_skipped(self, reason: str = "Unknown"):
        self.skipped += 1
        self.skip_reasons[reason] = self.skip_reasons.get(reason, 0) + 1

    def add_failed(self, error: str):
        self.failed += 1
        self.errors.append(error)


class MigrationReporter:
    def __init__(self):
        self.database_stats: Dict[str, DatabaseStats] = {}
        self.standalone_pages_stats = DatabaseStats()
        self.overall_stats = DatabaseStats()

    def get_or_create_stats(self, database_name: str) -> DatabaseStats:
        if database_name not in self.database_stats:
            self.database_stats[database_name] = DatabaseStats()
        return self.database_stats[database_name]

    def set_total(self, database_name: str, total: int):
        stats = self.get_or_create_stats(database_name)
        stats.total = total
        self.overall_stats.total += total

    def add_converted(self, database_name: str):
        stats = self.get_or_create_stats(database_name)
        stats.add_converted()
        self.overall_stats.add_converted()

    def add_skipped(self, database_name: str, reason: str = "Unknown"):
        stats = self.get_or_create_stats(database_name)
        stats.add_skipped(reason)
        self.overall_stats.add_skipped(reason)

    def add_failed(self, database_name: str, error: str):
        stats = self.get_or_create_stats(database_name)
        stats.add_failed(error)
        self.overall_stats.add_failed(error)

    def set_standalone_total(self, total: int):
        self.standalone_pages_stats.total = total
        self.overall_stats.total += total

    def add_standalone_converted(self):
        self.standalone_pages_stats.add_converted()
        self.overall_stats.add_converted()

    def add_standalone_skipped(self, reason: str = "Unknown"):
        self.standalone_pages_stats.add_skipped(reason)
        self.overall_stats.add_skipped(reason)

    def add_standalone_failed(self, error: str):
        self.standalone_pages_stats.add_failed(error)
        self.overall_stats.add_failed(error)

    def print_report(self):
        print("\n" + "=" * 60)
        print("MIGRATION REPORT")
        print("=" * 60)

        for db_name, stats in self.database_stats.items():
            print(f"\nDatabase: {db_name}")
            print(f"  Total pages: {stats.total}")
            print(f"  Converted: {stats.converted}")
            if stats.skipped > 0:
                skip_details = ", ".join([f"{reason} ({count})" for reason, count in stats.skip_reasons.items()])
                print(f"  Skipped: {stats.skipped} ({skip_details})")
            else:
                print(f"  Skipped: {stats.skipped}")
            print(f"  Failed: {stats.failed}")
            if stats.errors:
                print(f"  Errors:")
                for error in stats.errors[:5]:
                    print(f"    - {error}")
                if len(stats.errors) > 5:
                    print(f"    ... and {len(stats.errors) - 5} more errors")

        if self.standalone_pages_stats.total > 0:
            print(f"\nStandalone Pages")
            print(f"  Total pages: {self.standalone_pages_stats.total}")
            print(f"  Converted: {self.standalone_pages_stats.converted}")
            if self.standalone_pages_stats.skipped > 0:
                skip_details = ", ".join([f"{reason} ({count})" for reason, count in self.standalone_pages_stats.skip_reasons.items()])
                print(f"  Skipped: {self.standalone_pages_stats.skipped} ({skip_details})")
            else:
                print(f"  Skipped: {self.standalone_pages_stats.skipped}")
            print(f"  Failed: {self.standalone_pages_stats.failed}")

        print(f"\n{'---' * 20}")
        print(f"Overall Summary:")
        print(f"  Total databases: {len(self.database_stats)}")
        print(f"  Total database pages: {sum(s.total for s in self.database_stats.values())}")
        print(f"  Total standalone pages: {self.standalone_pages_stats.total}")
        print(f"  Total pages: {self.overall_stats.total}")
        print(f"  Successfully converted: {self.overall_stats.converted}")
        print(f"  Skipped: {self.overall_stats.skipped}")
        print(f"  Failed: {self.overall_stats.failed}")
        print("=" * 60 + "\n")
