KNOWN_SOURCES = {
    # exact filenames from README + common variants
    "SalesTax_Calculator": [
        "SalesTax_Calculator_v4.xlsx",
        "SalesTax_Calculator.xlsx",
    ],
    "tax_class": [
        "OPA_Tax_Class.xlsx",
        "OPA_Tax_Class.csv",
        "Tax_Class.xlsx",
    ],
    "machine_map": [
        "OPA_Machine_Map.xlsx",
        "OPA_Machine_Map.csv",
        "Machine_Map.xlsx",
    ],
    "jurisdiction_rates": [
        "Jurisdiction_Rates.xlsx",
        "Jurisdiction_Rates.csv",
        "JurisdictionRates.xlsx",
    ],
    "fv": ["FV 2025.xlsx", "FV_2025.xlsx", "FV2025.xlsx"],
    "inventory_guide": ["Inventory Tax Guide_Master_Current.xlsx", "Inventory_Tax_Guide_Master_Current.xlsx"],
    "profit_wiz": ["OPA_Profit_Wiz_clean_values.xlsx"],
    "sample_workbook": ["OPA_Tax_TestData_Sample.xlsx", "OPA_Tax_TestData_Sample.xls"],
}

KNOWN_SHEETS = {
    "orders": ["Orders", "Order details", "Order Details", "Order details_*"],
    "tax_class": ["Tax_Class", "Tax Class", "TaxClass"],
    "machine_map": ["Machine_Map", "Machine Map", "Machines"],
    "jurisdiction_rates": ["Jurisdiction_Rates", "Rates", "Jurisdiction Rates"],
    "vistar": ["Vistar Cat. 2025", "Vistar Cat 2025", "Vistar Cat"],
    "fact": ["SalesTax_Fact", "SalesTax Fact"],
    "summary": ["SalesTax_Summary", "SalesTax Summary"],
}

EXACT_REQUIRED = [
    "OPA_Tax_Class.xlsx",
    "OPA_Machine_Map.xlsx",
    "Jurisdiction_Rates.xlsx",
]
#!/usr/bin/env python3
"""Simple runner for the pipeline engine. Intended for development and CI.

It reads sources from a source directory (defaults to tests/data for now) and writes outputs to exports/.
"""
from pathlib import Path
import argparse
import sys
from pathlib import Path as _P
# ensure repo root is on sys.path so local package imports work when running this script
sys.path.insert(0, str(_P(__file__).resolve().parents[1]))
from pipeline.engine import read_table, build_fact, build_summary


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--src', default='tests/data', help='Source data folder')
    p.add_argument('--use-params', action='store_true', help='Use Imports_Folder_Path from config/Parameters.json as source')
    p.add_argument('--copy-workbook', help='Copy a single workbook into references/ and run from there. Accepts absolute path or folder:filename')
    p.add_argument('--out', default='exports', help='Output folder')
    args = p.parse_args()

    src = Path(args.src)
    if getattr(args, 'use_params', False):
        # try to read config/Parameters.json
        params_file = Path(__file__).resolve().parents[1] / 'config' / 'Parameters.json'
        if params_file.exists():
            try:
                import json
                params = json.loads(params_file.read_text())
                imports_path = params.get('Imports_Folder_Path')
                if imports_path:
                    # use the imports folder as the source; support Windows paths
                    src = Path(imports_path)
                    print('Using Imports_Folder_Path from Parameters.json:', src)
            except Exception as e:
                print('Failed to read Parameters.json:', e)
        else:
            print('Parameters.json not found; continuing with --src or default')
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    # If copy-workbook provided, copy it into references/ and set src to references/
    if getattr(args, 'copy_workbook', None):
        wb_arg = args.copy_workbook
        # handle 'folder:filename' case
        candidate = None
        if Path(wb_arg).exists():
            candidate = Path(wb_arg)
        elif ':' in wb_arg:
            # split on last ':' to support Windows drive letters
            idx = wb_arg.rfind(':')
            folder = wb_arg[:idx]
            filename = wb_arg[idx+1:]
            candidate = Path(folder) / filename
        if candidate is None or not candidate.exists():
            print(f"Workbook to copy not found: {wb_arg} -> {candidate}")
            raise SystemExit(2)
        refs = Path(__file__).resolve().parents[1] / 'references'
        refs.mkdir(parents=True, exist_ok=True)
        dst = refs / candidate.name
        import shutil
        shutil.copy2(candidate, dst)
        print(f"Copied workbook {candidate} -> {dst}")
        src = refs

    # Attempt to load CSV files first; if not present, look for Excel workbooks and load sheets
    def load_or_none_csv(name):
        p = src / name
        return read_table(p) if p.exists() else None

    orders = load_or_none_csv('sample_orders.csv')
    tax_class = load_or_none_csv('sample_tax_class.csv')
    machine_map = load_or_none_csv('sample_machine_map.csv')
    jurisdiction_rates = load_or_none_csv('sample_jurisdiction_rates.csv')

    # If any are missing, try to find an Excel workbook and read sheets
    if orders is None or tax_class is None or machine_map is None or jurisdiction_rates is None:
        # look for known workbook names in src
        workbook = None
        for key, names in KNOWN_SOURCES.items():
            for nm in names:
                candidate = src / nm
                if candidate.exists():
                    workbook = candidate
                    break
            if workbook:
                break
        # fallback: pick first xlsx in the folder
        if workbook is None:
            xs = list(src.glob('*.xlsx'))
            if xs:
                workbook = xs[0]

        if workbook is not None:
            import pandas as _pd
            print(f"Reading workbook {workbook}")
            xl = _pd.ExcelFile(workbook)

            def read_sheet_by_candidates(candidates):
                for s in candidates:
                    if s in xl.sheet_names:
                        return _pd.read_excel(xl, sheet_name=s)
                # try lower-case matching
                lnames = [ss.lower() for ss in xl.sheet_names]
                for s in candidates:
                    if s.lower() in lnames:
                        idx = lnames.index(s.lower())
                        return _pd.read_excel(xl, sheet_name=xl.sheet_names[idx])
                # fallback: try first sheet
                return _pd.read_excel(xl, sheet_name=xl.sheet_names[0])

            if orders is None:
                orders = read_sheet_by_candidates(KNOWN_SHEETS.get('orders', ['Orders']))
            if tax_class is None:
                tax_class = read_sheet_by_candidates(KNOWN_SHEETS.get('tax_class', ['Tax_Class']))
            if machine_map is None:
                machine_map = read_sheet_by_candidates(KNOWN_SHEETS.get('machine_map', ['Machine_Map']))
            if jurisdiction_rates is None:
                jurisdiction_rates = read_sheet_by_candidates(KNOWN_SHEETS.get('jurisdiction_rates', ['Jurisdiction_Rates']))

    # final check
    if orders is None or tax_class is None or machine_map is None or jurisdiction_rates is None:
        print('Missing one or more required sources. Found:')
        print(' orders=', orders is not None, ' tax_class=', tax_class is not None, ' machine_map=', machine_map is not None, ' jurisdiction_rates=', jurisdiction_rates is not None)
        raise SystemExit(2)

    fact, validations = build_fact(orders, tax_class, machine_map, jurisdiction_rates)
    summary = build_summary(fact)

    fact.to_csv(out / 'OPA_SalesTax_Fact.csv', index=False)
    summary.to_csv(out / 'OPA_SalesTax_Summary.csv', index=False)

    print('Wrote outputs to', out)
    if validations['unmapped_skus'].shape[0] > 0:
        print('Unmapped SKUs:')
        print(validations['unmapped_skus'].to_string(index=False))


if __name__ == '__main__':
    main()
