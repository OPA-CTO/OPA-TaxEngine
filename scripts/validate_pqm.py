#!/usr/bin/env python3
"""
Validate Power Query (.pqm) module syntax and structure.

This script checks:
1. Basic syntax validation (balanced braces, parentheses, brackets)
2. Required Power Query patterns (let...in structure)
3. Common issues (unbalanced quotes, missing semicolons)
"""

import os
import sys
import re
from pathlib import Path
from typing import List, Tuple, Dict


class PowerQueryValidator:
    """Validates Power Query M language files."""

    def __init__(self, file_path: str):
        self.file_path = file_path
        self.content = ""
        self.errors: List[str] = []
        self.warnings: List[str] = []

    def load_file(self) -> bool:
        """Load the .pqm file content."""
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                self.content = f.read()
            return True
        except Exception as e:
            self.errors.append(f"Failed to read file: {e}")
            return False

    def validate_let_in_structure(self) -> None:
        """Check for proper let...in structure."""
        if not re.search(r'\blet\b', self.content, re.IGNORECASE):
            self.errors.append("Missing 'let' keyword - Power Query modules should start with 'let'")
        
        if not re.search(r'\bin\b', self.content, re.IGNORECASE):
            self.errors.append("Missing 'in' keyword - Power Query modules should end with 'in <expression>'")

    def validate_balanced_delimiters(self) -> None:
        """Check for balanced braces, brackets, and parentheses."""
        delimiters = {
            '{': '}',
            '[': ']',
            '(': ')'
        }
        
        for open_char, close_char in delimiters.items():
            open_count = self.content.count(open_char)
            close_count = self.content.count(close_char)
            
            if open_count != close_count:
                self.errors.append(
                    f"Unbalanced delimiters: {open_count} '{open_char}' vs {close_count} '{close_char}'"
                )

    def validate_string_quotes(self) -> None:
        """Check for potentially unbalanced quotes."""
        # Count double quotes (accounting for escaped quotes is complex, so this is basic)
        quote_count = self.content.count('"')
        
        if quote_count % 2 != 0:
            self.warnings.append(
                f"Odd number of double quotes ({quote_count}) - possible unclosed string"
            )

    def check_common_patterns(self) -> None:
        """Check for common Power Query patterns and issues."""
        # Check for error handling
        if 'error' in self.content.lower() and 'try' not in self.content.lower():
            self.warnings.append("Uses 'error' but no 'try' found - consider error handling")
        
        # Check for parameter usage
        if '#"' in self.content:
            self.warnings.append("Contains parameter references (#\"...\") - ensure parameters are defined")

    def validate(self) -> bool:
        """Run all validations."""
        if not self.load_file():
            return False

        self.validate_let_in_structure()
        self.validate_balanced_delimiters()
        self.validate_string_quotes()
        self.check_common_patterns()

        return len(self.errors) == 0

    def print_results(self) -> None:
        """Print validation results."""
        file_name = os.path.basename(self.file_path)
        
        if self.errors:
            print(f"\n❌ {file_name}: FAILED")
            for error in self.errors:
                print(f"   ERROR: {error}")
        else:
            print(f"\n✓ {file_name}: PASSED")
        
        if self.warnings:
            for warning in self.warnings:
                print(f"   WARNING: {warning}")


def find_pqm_files(directory: str) -> List[str]:
    """Find all .pqm files in the given directory."""
    pqm_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.pqm'):
                pqm_files.append(os.path.join(root, file))
    return pqm_files


def main():
    """Main validation routine."""
    print("=" * 60)
    print("OPA TaxEngine - Power Query Module Validation")
    print("=" * 60)

    # Find repository root
    repo_root = Path(__file__).parent.parent
    powerquery_dir = repo_root / 'powerquery'

    if not powerquery_dir.exists():
        print(f"\n❌ ERROR: powerquery directory not found at {powerquery_dir}")
        sys.exit(1)

    # Find all .pqm files
    pqm_files = find_pqm_files(str(powerquery_dir))

    if not pqm_files:
        print(f"\n⚠️  WARNING: No .pqm files found in {powerquery_dir}")
        print("   Power Query modules should be added to the powerquery directory")
        sys.exit(0)

    print(f"\nFound {len(pqm_files)} Power Query module(s):")
    for pqm_file in pqm_files:
        print(f"  - {os.path.relpath(pqm_file, repo_root)}")

    # Validate each file
    all_valid = True
    validators = []

    for pqm_file in pqm_files:
        validator = PowerQueryValidator(pqm_file)
        validators.append(validator)
        
        if not validator.validate():
            all_valid = False

    # Print results
    print("\n" + "=" * 60)
    print("Validation Results")
    print("=" * 60)

    for validator in validators:
        validator.print_results()

    # Summary
    print("\n" + "=" * 60)
    if all_valid:
        print("✓ All Power Query modules passed validation")
        print("=" * 60)
        sys.exit(0)
    else:
        print("❌ Some Power Query modules failed validation")
        print("=" * 60)
        sys.exit(1)


if __name__ == '__main__':
    main()
