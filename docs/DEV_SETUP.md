# Developer Setup

This file describes the minimal steps to get a developer environment ready for working on OPA-TaxEngine.

1) Obtain the quarterly reference workbooks

- Place the following files (provided by Finance / Operations / Product) into the `references/` folder at repository root:
  - `OPA_Tax_Class.xlsx`
  - `OPA_Machine_Map.xlsx`
  - `Jurisdiction_Rates.xlsx`
  - `FV_2025.xlsx`
  - `Inventory Tax Guide_Master_Current.xlsx`

2) Configure `config/Parameters.json`

- Edit `config/Parameters.json` and set `Imports_Folder_Path` to the path where order exports live on your machine.
- Keep the path out of source control — the repo uses `Column_Map` and `Parameters.json` for dynamic discovery.

3) Quick local validation

Run the provided quick-check to validate that required reference files and config are present:

```bash
make setup-check
```

4) Notes on automating Power Query refresh

- The repository contains Power Query (`.pqm`) logic which is authored for Excel/Power BI. Automating an actual workbook refresh and export typically requires Windows and Excel/Power BI Desktop (COM automation or PowerShell). If CI automation is required, there are two viable approaches:
  - Use a self-hosted Windows runner with Excel/Power BI installed and drive refresh via PowerShell/COM.
  - Re-implement the transformation logic in a cross-platform language (Python) so CI can run on Linux/macOS.

5) Running tests

Install dev dependencies and run tests:

```bash
python3 -m pip install -r requirements.txt
pytest -q
```
