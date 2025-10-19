# OPA-TaxEngine
On Point Amenities — Sales Tax Engine (CFO/CTO reconciled Q4-2025)

**Purpose**  
Authoritative Power Query (M) modules, reference workbooks, and validation assets to produce an audit-ready, jurisdiction-aware sales-tax fact and summary for vending/micromart operations in Colorado (initial focus: Douglas County — Castle Rock 80104, Lone Tree 80124).

**Status**  
Version: `v2025.10.15-CTO-CFO-Reconciled`  
Owners: CTO (architecture), CFO (policy), CPO (taxonomy), COO (device map)

## Contents
# OPA Tax Engine — Q4 Development (2025)

> **Repo:** `OPA-CTO/OPA-TaxEngine`  
> **Branch:** `feature/q4-pipeline`  
> **Maintainer:** CTO (On Point Amenities)  
> **Handoff Chain:** CTO → CFO → COO → CPO  

---

## Mission

The OPA Tax Engine automates **sales tax computation, jurisdictional mapping, and DR‑0100 reporting** for On Point Amenities vending and micromart operations.  
It unifies vendor catalogs, order exports, and local jurisdiction data into a transparent, auditable pipeline where **policy lives with Finance, computation with Engineering, and compliance with Operations.**

**Core Principle:**  
> Engineering computes. Finance governs. Operations confirms.

---

## Objectives (Q4 2025)

- Implement **effective‑date logic** for rate application.  
- Integrate `Vistar Cat. 2025` data from **`FV 2025.xlsx`** for GTIN accuracy.  
- Strengthen policy boundaries: all taxability rules originate in `Tax_Class`.  
- Maintain **sentinel jurisdictions** Castle Rock (80104) and Lone Tree (80124) for validation.  
- Deliver **CFO‑ready DR‑0100** jurisdiction exports for Revenue Online.  
- Enforce end‑to‑end reproducibility of Q4 results via version tagging.

---

## Source File Map

| File | Table | Owner | Purpose |
|------|--------|--------|----------|
| `SalesTax_Calculator_v4.xlsx` | — | CTO | Master workbook hosting Power Query logic. |
| `OPA_Tax_Class.xlsx` | `Tax_Class` | CFO | Policy source for class‑level taxability. |
| `OPA_Machine_Map.xlsx` | `Machine_Map` | COO | Maps devices to jurisdictions and ZIPs. |
| `Jurisdiction_Rates.xlsx` | `Jurisdiction_Rates` | CFO | Rate components with date windows. |
| `Inventory Tax Guide_Master_Current.xlsx` | — | CPO | Catalog of purchasable SKUs. |
| `FV 2025.xlsx` | `Vistar Cat. 2025` | CPO | Q4 SKU/GTIN refresh. |
| `OPA_Profit_Wiz_clean_values.xlsx` | — | CFO | Unit COGS + margin cross‑check. |

**Dynamic Paths:** All sources are discovered via `Column_Map` → column `Source`.  
No absolute file paths or hard‑coded drive locations are permitted.

---

## Architecture Overview

### 1. Load Sources
- Query `Column_Map` for all path references.
- Load `Tax_Class`, `Machine_Map`, `Jurisdiction_Rates`, order files (`Order details_*`), and device exports (`Device Sales Ranking Details_*`).
- Support `_refs` subfolder for static reference tables.

### 2. Normalize Orders
- Canonical schema: `Txn_Date`, `Device_Number`, `SKU`, `Product_Desc`, `Qty`, `Net_Sales`, `Txn_Status`.
- Filter status in `{PAID, APPROVED, SUCCESSFUL CHARGE}`.
- Parse timestamps → `yyyy‑mm‑dd` for date filtering.

### 3. SKU → GTIN → Class
- Merge with `Vistar Cat. 2025` for GTIN.
- Join to `Tax_Class` for `Class`, `Assumed_Taxability`, `Notes`.
- Any SKU without class = raise exception in `Mapping_Exceptions`.

### 4. Device → Jurisdiction
- Join to `Machine_Map` for `Jurisdiction_Code`, `Jurisdiction_Name`, `ZIP`.
- Match to `Jurisdiction_Rates` based on `Rate_Effective_From` ≤ `Txn_Date` ≤ `Rate_Effective_To`.

### 5. Tax Computation
- Apply CO rule: *food for home consumption via vending* → exempt from state 2.9%.  
- Taxable categories (e.g. soft drinks, candy w/out flour, supplements) → state + local.
- Compute per‑line: `Line_Tax = Net_Sales * EffectiveRate`.
- Decompose into components: state / county / city / RTD / special.

### 6. Outputs
- **OPA_SalesTax_Fact:** transaction‑level detail (device, class, jurisdiction, rate components).  
- **OPA_SalesTax_Summary:** jurisdiction/device roll‑up (taxable sales, exempt sales, DR‑0100 lines).  
- **Exports:** Revenue Online XLSX + CFO PDF snapshot + archived `_refs` bundle.

---

## Table Requirements

### `Tax_Class` (CFO)
| Column | Description |
|---------|--------------|
| `Class` | Product grouping |
| `Assumed_Taxability` | `Taxable`, `Exempt`, `Local Only` |
| `Notes` | Policy justification |
| `Last_Updated` | ISO date |
| `Policy_Source` | Legal or reference citation |

### `Jurisdiction_Rates` (CFO)
| Column | Description |
|---------|-------------|
| `Jurisdiction_Code` | Unique key |
| `Component` | State / County / City / RTD / Special |
| `Rate` | Decimal (e.g. 0.029) |
| `Rate_Effective_From` | Start date |
| `Rate_Effective_To` | End date |

### `Machine_Map` (COO)
| Column | Description |
|---------|-------------|
| `Device_Number` | Machine ID |
| `Jurisdiction_Code` | Key for rate join |
| `ZIP` | Postal verification |
| `Effective_From` / `To` | Optional activation window |

---

## Validation Workflow

| Role | Responsibility | Key Checkpoints |
|------|----------------|-----------------|
| **CTO** | Build queries & verify joins | Fact and Summary populate; no nulls |
| **CFO** | Validate policy & rates | 80104 = 8.1%, 80124 = 7.5%, DR‑0100 tie‑out |
| **COO** | Confirm mapping accuracy | Device → Jurisdiction consistency |
| **CPO** | Validate SKU/GTIN mapping | Exception table empty |

**Validation Sequence:**  
1. Confirm rows exist in `OPA_SalesTax_Fact`.  
2. Ensure 0 unmapped `Class` or `Jurisdiction_Code`.  
3. Verify effective‑date match coverage.  
4. Audit Castle Rock & Lone Tree totals.  
5. Export DR‑0100 and CFO PDF; archive snapshot.

---

## Repo Structure

```
OPA-TaxEngine/
├─ powerquery/
│   ├─ Taxability_Map.pqm
│   ├─ SalesTax_Fact.pqm
│   └─ SalesTax_Summary.pqm
├─ references/
│   ├─ OPA_Tax_Class.xlsx
│   ├─ OPA_Machine_Map.xlsx
│   ├─ Jurisdiction_Rates.xlsx
│   ├─ FV_2025.xlsx
│   └─ Inventory Tax Guide_Master_Current.xlsx
├─ docs/
│   ├─ README.md
│   └─ Tests_Validation_Checklist.md
├─ exports/     (ignored in Git)
└─ archives/
    └─ 2025_Q3/  (frozen CFO sign‑off)
```

---

## Branching & Release

- `main` → audited, CFO‑signed builds.  
- `feature/q4-pipeline` → active build.  
- `feature/taxability-map` → classification refinement.  
- Tag releases: `q4-dev.YYYYMMDD`.

---

## Risks & Mitigations

- **Missing GTINs:** escalate to CPO; tag `EXCEPTION_PENDING`.  
- **Rate Gaps:** CFO must populate missing `Rate_Effective_To/From`.  
- **Policy Drift:** updates logged via `Tax_Class` → `Last_Updated`.  
- **Empty Fact Table:** loosen status filter or audit import paths.

---

## Automated Build Process

The project includes automated validation and build checks via GitHub Actions:

- **Power Query Validation**: Syntax and structure checks for all `.pqm` modules
- **Dependency Analysis**: Tracks module implementation against expected refresh order
- **Configuration Validation**: Ensures `Parameters.json` and `Column_Map.csv` are valid
- **Documentation Checks**: Verifies required documentation is present

**Running locally**:
```bash
python3 scripts/validate_pqm.py       # Validate Power Query modules
python3 scripts/check_dependencies.py  # Check module dependencies
python3 scripts/validate_config.py     # Validate configuration files
```

See [`docs/BUILD.md`](docs/BUILD.md) for complete build documentation.

---

## Next Steps

1. Update `Column_Map` sources for Q4.  
2. Refresh queries.  
3. Validate Fact → Summary chain.  
4. Export DR‑0100 + PDF.  
5. Tag release → archive.  

---

## Change Log — Q4 Active

- Added effective‑date rate logic.  
- Replaced `Imports_Folder_Path` with `Column_Map` dynamic mapping.  
- Integrated `Vistar Cat. 2025` GTIN catalog.  
- Introduced `Mapping_Exceptions` table.  
- Q3 rates frozen for baseline.  

---

**Contacts:**  
CTO — System architecture & orchestration  
CFO — Tax policy & compliance audit  
COO — Jurisdiction verification  
CPO — Product data integrity  

---
