# CTO Implementation Contract — Q4-2025 Baseline

## Scope
Build eight Power Query queries that produce row-level tax math and jurisdiction rollups from vending telemetry. Deterministic, audit-ready, no hidden rules.

## Refresh Order
Taxability_Map → Jurisdiction_Rates → Machine_Map → OPA_SalesTax_Fact_Rows → OPA_SalesTax_Fact → Unmatched_Descriptions → Coverage_Summary → SalesTax_Summary

## Core Inputs
- `/references/OPA_Tax_Class.xlsx::Tax_Class`
- `/references/OPA_Machine_Map.xlsx::Machine_Map`
- `/references/Jurisdiction_Rates.xlsx::Jurisdiction_Rates`
- `Imports_Folder_Path` folder with `Device Sales Ranking Details_*`

## Global Constraints
- No regex; use native `Text.*`
- Row-level "tax-in" back-out, bankers-round to cents post 4+ decimal math
- Effective-dated joins where applicable (rates; device move windows)
- DQ surfaced in explicit *_DQ queries; no silent drops

## Deliverables
- Eight .pqm modules in `/powerquery/`
- DQ companions as needed (e.g., `Taxability_Map_DQ`)
- Load-to-Table enabled for all top-level queries
