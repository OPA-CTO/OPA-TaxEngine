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
    p.add_argument('--out', default='exports', help='Output folder')
    args = p.parse_args()

    src = Path(args.src)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    orders = read_table(src / 'sample_orders.csv')
    tax_class = read_table(src / 'sample_tax_class.csv')
    machine_map = read_table(src / 'sample_machine_map.csv')
    jurisdiction_rates = read_table(src / 'sample_jurisdiction_rates.csv')

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
