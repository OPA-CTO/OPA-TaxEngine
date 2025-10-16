# Tests & Validation — Q4-2025

## Golden Scenarios (from /validation/OPA_Tax_TestData_Sample.xlsx)
- Castle Rock food local-only: 0.052; full taxable: 0.081
- Lone Tree food local-only: 0.046; full taxable: 0.075
- Twix/KitKat (flour): local-only
- Skittles/Gum (no flour): full
- Supplement (Supplement Facts): full
- Bottled water: 0
- Hot coffee: full
- Menstrual/diaper: state 0; locals per city rules

## Pass Criteria
- Coverage_Summary ≥ 99%
- Unmatched_Descriptions has no critical reasons
- DR-0100 parity (jurisdiction totals) ≤ $0.02
- Component split available (state vs local)
