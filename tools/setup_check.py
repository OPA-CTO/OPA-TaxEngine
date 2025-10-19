#!/usr/bin/env python3
"""Simple setup validation for OPA-TaxEngine.

Checks presence of required reference files and basic config sanity based on README.
"""
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

REQUIRED_REFERENCES = [
    "references/OPA_Tax_Class.xlsx",
    "references/OPA_Machine_Map.xlsx",
    "references/Jurisdiction_Rates.xlsx",
    "references/FV_2025.xlsx",
    "references/Inventory Tax Guide_Master_Current.xlsx",
]


def check_files():
    missing = []
    for rel in REQUIRED_REFERENCES:
        p = ROOT / rel
        if not p.exists():
            missing.append(rel)
    return missing


def check_parameters():
    params_file = ROOT / "config" / "Parameters.json"
    if not params_file.exists():
        return False, "config/Parameters.json missing"
    try:
        data = json.loads(params_file.read_text())
    except Exception as e:
        return False, f"Parameters.json parse error: {e}"
    required_keys = ["Imports_Folder_Path", "Filing_Frequency", "Timezone"]
    missing = [k for k in required_keys if k not in data]
    if missing:
        return False, f"Missing keys in Parameters.json: {', '.join(missing)}"
    return True, data


def check_column_map():
    col_file = ROOT / "config" / "Column_Map.csv"
    if not col_file.exists():
        return False, "config/Column_Map.csv missing"
    text = col_file.read_text()
    if "SKU" not in text and "sku" not in text:
        return False, "Column_Map.csv appears to be missing SKU mapping"
    return True, None


def main():
    print(f"Root: {ROOT}")
    missing = check_files()
    if missing:
        print("\nMissing reference files:")
        for m in missing:
            print(f" - {m}")
        print("\nPlace the Q4 reference workbooks into the `references/` folder as listed in the README.")
    else:
        print("All reference files present.")

    ok, params = check_parameters()
    if not ok:
        print(f"\nParameters.json check: FAIL - {params}")
    else:
        print("\nParameters.json: OK")
        print(f" Imports_Folder_Path: {params.get('Imports_Folder_Path')}")

    ok, col_err = check_column_map()
    if not ok:
        print(f"\nColumn_Map.csv check: FAIL - {col_err}")
    else:
        print("\nColumn_Map.csv: OK")

    print("\nSetup check complete.")


if __name__ == '__main__':
    main()
