#!/usr/bin/env python3
"""
Check Power Query module dependencies and refresh order.

This script validates that the documented refresh order in README_CTO.md
matches the available modules and checks for potential dependency issues.
"""

import os
import sys
import re
from pathlib import Path
from typing import List, Set, Dict


class DependencyChecker:
    """Checks Power Query module dependencies."""

    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
        self.powerquery_dir = repo_root / 'powerquery'
        self.docs_dir = repo_root / 'docs'
        self.expected_modules: List[str] = []
        self.available_modules: Set[str] = set()

    def load_expected_refresh_order(self) -> bool:
        """Load the expected refresh order from README_CTO.md."""
        readme_cto = self.docs_dir / 'README_CTO.md'
        
        if not readme_cto.exists():
            print(f"⚠️  WARNING: {readme_cto} not found")
            return False

        try:
            with open(readme_cto, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Look for refresh order line
            match = re.search(
                r'Refresh Order[:\s]+(.+?)(?:\n|$)',
                content,
                re.IGNORECASE
            )
            
            if match:
                order_text = match.group(1)
                # Split by arrow and clean up (handles → and ->)
                modules = [m.strip() for m in re.split(r'[→\->]+', order_text)]
                self.expected_modules = [m for m in modules if m]
                return True
            else:
                print("⚠️  WARNING: Could not find 'Refresh Order' in README_CTO.md")
                return False
                
        except Exception as e:
            print(f"⚠️  WARNING: Error reading README_CTO.md: {e}")
            return False

    def scan_available_modules(self) -> None:
        """Scan for available .pqm files."""
        if not self.powerquery_dir.exists():
            return

        for file in self.powerquery_dir.glob('*.pqm'):
            # Get module name without extension
            module_name = file.stem
            self.available_modules.add(module_name)

    def check_dependencies(self) -> bool:
        """Check for dependency issues."""
        print("\n" + "=" * 60)
        print("Power Query Dependency Analysis")
        print("=" * 60)

        # Load expected order
        has_order = self.load_expected_refresh_order()
        
        if has_order and self.expected_modules:
            print(f"\nExpected refresh order ({len(self.expected_modules)} modules):")
            for i, module in enumerate(self.expected_modules, 1):
                print(f"  {i}. {module}")

        # Scan available modules
        self.scan_available_modules()
        
        print(f"\nAvailable modules ({len(self.available_modules)} .pqm files):")
        if self.available_modules:
            for module in sorted(self.available_modules):
                print(f"  ✓ {module}.pqm")
        else:
            print("  (none)")

        # Compare if we have expected order
        if has_order and self.expected_modules:
            print("\nModule Status:")
            all_present = True
            
            for module in self.expected_modules:
                if module in self.available_modules:
                    print(f"  ✓ {module} - implemented")
                else:
                    print(f"  ⚠️  {module} - NOT YET IMPLEMENTED")
                    all_present = False

            # Check for extra modules not in order
            extra_modules = self.available_modules - set(self.expected_modules)
            if extra_modules:
                print("\nAdditional modules (not in documented refresh order):")
                for module in sorted(extra_modules):
                    print(f"  ? {module}")

            return all_present
        else:
            # No expected order to check against
            return True

    def analyze_module_references(self, module_path: Path) -> List[str]:
        """Analyze a module to find references to other modules/tables."""
        references = []
        
        try:
            with open(module_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Look for common reference patterns in Power Query
            # This is a simple heuristic - actual M language parsing is complex
            
            # Pattern 1: Direct table references (e.g., Tax_Class, Machine_Map)
            table_pattern = r'\b([A-Z][a-zA-Z_0-9]+)\s*(?:=|,|\[)'
            matches = re.findall(table_pattern, content)
            
            # Pattern 2: Excel.Workbook references
            excel_pattern = r'Excel\.Workbook\([^)]*"([^"]+)"'
            excel_matches = re.findall(excel_pattern, content)
            
            if excel_matches:
                references.extend([f"File: {m}" for m in excel_matches])
            
            return references
            
        except Exception as e:
            print(f"  ⚠️  Error analyzing {module_path.name}: {e}")
            return []


def main():
    """Main dependency checking routine."""
    print("=" * 60)
    print("OPA TaxEngine - Dependency Check")
    print("=" * 60)

    repo_root = Path(__file__).parent.parent
    checker = DependencyChecker(repo_root)

    # Run checks
    all_modules_present = checker.check_dependencies()

    # Summary
    print("\n" + "=" * 60)
    
    if not checker.expected_modules:
        print("⚠️  No expected module order found - check docs/README_CTO.md")
        print("=" * 60)
        sys.exit(0)
    
    if len(checker.available_modules) == 0:
        print("⚠️  No Power Query modules implemented yet")
        print("   Modules should be added to powerquery/ directory")
        print("=" * 60)
        sys.exit(0)
    
    if all_modules_present:
        print("✓ All expected modules are implemented")
        print("=" * 60)
        sys.exit(0)
    else:
        print("⚠️  Some expected modules are not yet implemented")
        print("   This is expected during development")
        print("=" * 60)
        sys.exit(0)


if __name__ == '__main__':
    main()
