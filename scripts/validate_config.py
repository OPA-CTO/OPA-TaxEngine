#!/usr/bin/env python3
"""
Validate configuration files (Parameters.json, Column_Map.csv).

This script checks:
1. JSON syntax validity
2. Required configuration fields
3. CSV structure and format
"""

import os
import sys
import json
import csv
from pathlib import Path
from typing import Dict, List


class ConfigValidator:
    """Validates configuration files."""

    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
        self.config_dir = repo_root / 'config'
        self.errors: List[str] = []
        self.warnings: List[str] = []

    def validate_parameters_json(self) -> bool:
        """Validate Parameters.json."""
        params_file = self.config_dir / 'Parameters.json'
        
        print(f"\nValidating {params_file.name}...")
        
        if not params_file.exists():
            self.errors.append(f"Missing file: {params_file}")
            return False

        try:
            with open(params_file, 'r', encoding='utf-8') as f:
                params = json.load(f)
            
            print("  ✓ Valid JSON syntax")

            # Check for expected fields (based on current Parameters.json)
            expected_fields = [
                'Imports_Folder_Path',
                'Filing_Frequency',
                'Allow_ZIP_Fallback',
                'Timezone'
            ]

            for field in expected_fields:
                if field in params:
                    print(f"  ✓ Field '{field}' present: {params[field]}")
                else:
                    self.warnings.append(f"Expected field '{field}' not found in Parameters.json")

            return True

        except json.JSONDecodeError as e:
            self.errors.append(f"Invalid JSON in Parameters.json: {e}")
            return False
        except Exception as e:
            self.errors.append(f"Error reading Parameters.json: {e}")
            return False

    def validate_column_map_csv(self) -> bool:
        """Validate Column_Map.csv."""
        csv_file = self.config_dir / 'Column_Map.csv'
        
        print(f"\nValidating {csv_file.name}...")
        
        if not csv_file.exists():
            self.errors.append(f"Missing file: {csv_file}")
            return False

        try:
            with open(csv_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                
                # Check headers
                if reader.fieldnames:
                    print(f"  ✓ Headers: {', '.join(reader.fieldnames)}")
                    
                    expected_headers = ['Raw_Header', 'Target_Header']
                    for header in expected_headers:
                        if header not in reader.fieldnames:
                            self.errors.append(f"Missing expected header '{header}' in Column_Map.csv")
                else:
                    self.errors.append("Column_Map.csv has no headers")
                    return False

                # Count rows
                rows = list(reader)
                print(f"  ✓ Contains {len(rows)} mapping(s)")

                # Check for empty values
                empty_count = 0
                for i, row in enumerate(rows, 1):
                    for header in reader.fieldnames:
                        if not row.get(header, '').strip():
                            empty_count += 1
                            self.warnings.append(
                                f"Empty value in row {i}, column '{header}'"
                            )

                if empty_count == 0:
                    print("  ✓ No empty values found")

            return True

        except Exception as e:
            self.errors.append(f"Error reading Column_Map.csv: {e}")
            return False

    def validate_all(self) -> bool:
        """Run all configuration validations."""
        print("=" * 60)
        print("Configuration Validation")
        print("=" * 60)

        if not self.config_dir.exists():
            self.errors.append(f"Config directory not found: {self.config_dir}")
            return False

        results = []
        results.append(self.validate_parameters_json())
        results.append(self.validate_column_map_csv())

        return all(results)

    def print_summary(self) -> None:
        """Print validation summary."""
        print("\n" + "=" * 60)
        print("Configuration Validation Summary")
        print("=" * 60)

        if self.errors:
            print("\n❌ Errors:")
            for error in self.errors:
                print(f"   - {error}")

        if self.warnings:
            print("\n⚠️  Warnings:")
            for warning in self.warnings:
                print(f"   - {warning}")

        if not self.errors and not self.warnings:
            print("\n✓ All configuration files are valid")


def main():
    """Main validation routine."""
    print("=" * 60)
    print("OPA TaxEngine - Configuration Validation")
    print("=" * 60)

    repo_root = Path(__file__).parent.parent
    validator = ConfigValidator(repo_root)

    is_valid = validator.validate_all()
    validator.print_summary()

    print("=" * 60)

    if is_valid and not validator.errors:
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == '__main__':
    main()
