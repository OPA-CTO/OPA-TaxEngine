## Summary
Implement Power Query module(s) per CTO contract.

## Checklist
- [ ] Reads correct /references workbook + sheet
- [ ] Emits columns in exact order per contract
- [ ] DQ surfaced in companion *_DQ query
- [ ] No regex; native Text.* only
- [ ] Unit tests pass using /validation
- [ ] Coverage_Summary ≥ 99% on sample

## Validation Evidence
- Screenshot of output table
- Screenshot of DQ table (empty on pass)
- Short note confirming DR-0100 parity (≤ $0.02 delta)
