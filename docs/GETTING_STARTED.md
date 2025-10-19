# Getting Started with OPA TaxEngine

This guide helps you get started with the OPA Tax Engine, whether you're contributing code, validating outputs, or understanding the system.

## Prerequisites

- **Python 3.7+** - For running validation scripts
- **Make** (optional) - For convenient build automation
- **Power BI Desktop** or **Excel with Power Query** - For developing and testing `.pqm` modules
- **Git** - For version control

## Initial Setup

### 1. Clone the Repository

```bash
git clone https://github.com/OPA-CTO/OPA-TaxEngine.git
cd OPA-TaxEngine
```

### 2. Verify Your Setup

Run the automated validation to ensure everything is configured correctly:

```bash
make validate
```

Or if you don't have Make installed:

```bash
python3 scripts/validate_pqm.py
python3 scripts/check_dependencies.py
python3 scripts/validate_config.py
```

### 3. Understand the Project Structure

```
OPA-TaxEngine/
├── powerquery/              # Power Query M modules (.pqm files)
│   └── Taxability_Map.pqm   # Classification logic
├── config/                  # Configuration files
│   ├── Parameters.json      # Runtime parameters
│   └── Column_Map.csv       # Field mapping definitions
├── docs/                    # Documentation
│   ├── BUILD.md            # Build automation guide
│   ├── README_CTO.md       # Implementation contract
│   ├── Tests_Validation_Checklist.md  # Validation scenarios
│   └── GETTING_STARTED.md  # This file
├── exports/                # Output files (git-ignored)
├── scripts/                # Validation scripts
│   ├── validate_pqm.py     # Power Query validation
│   ├── check_dependencies.py  # Dependency checks
│   └── validate_config.py  # Config validation
└── .github/
    └── workflows/          # GitHub Actions CI/CD
        └── validate-build.yml
```

## Understanding the Workflow

### The Tax Computation Pipeline

The OPA Tax Engine follows this data flow:

1. **Load Sources** → Configuration + Reference Tables
2. **Normalize Orders** → Clean transaction data
3. **SKU → GTIN → Class** → Product classification
4. **Device → Jurisdiction** → Location mapping
5. **Tax Computation** → Apply rates with effective dates
6. **Outputs** → Fact tables + Summary + DR-0100 exports

### Power Query Refresh Order

Modules must be refreshed in this specific order (per `docs/README_CTO.md`):

1. `Taxability_Map`
2. `Jurisdiction_Rates`
3. `Machine_Map`
4. `OPA_SalesTax_Fact_Rows`
5. `OPA_SalesTax_Fact`
6. `Unmatched_Descriptions`
7. `Coverage_Summary`
8. `SalesTax_Summary`

**Current Status**: Check with `make validate-deps` to see which modules are implemented.

## Common Tasks

### Working with Power Query Modules

#### Creating a New Module

1. Create a `.pqm` file in `powerquery/` directory:
   ```bash
   touch powerquery/MyNewModule.pqm
   ```

2. Use the standard Power Query structure:
   ```m
   let
       // Define your data transformations here
       Source = ...,
       
       // Your steps...
       
       FinalStep = ...
   in
       FinalStep
   ```

3. Validate your module:
   ```bash
   make validate-pqm
   ```

4. Test in Power BI Desktop or Excel:
   - Open `SalesTax_Calculator_v4.xlsx` (if available)
   - Import your `.pqm` module
   - Test with sample data

#### Editing Existing Modules

1. Open the `.pqm` file in your text editor
2. Make your changes
3. Validate:
   ```bash
   make validate-pqm
   ```
4. Test your changes in Power BI/Excel
5. Commit and push

### Updating Configuration

#### Parameters.json

Contains runtime parameters like:
- `Imports_Folder_Path` - Where to find source data
- `Filing_Frequency` - Tax filing schedule
- `Allow_ZIP_Fallback` - Jurisdiction mapping options
- `Timezone` - For date/time handling

To update:
```bash
# Edit the file
nano config/Parameters.json

# Validate
make validate-config
```

#### Column_Map.csv

Maps raw data columns to standardized names. To add new mappings:

1. Edit `config/Column_Map.csv`
2. Add a row with `Raw_Header` and `Target_Header`
3. Validate:
   ```bash
   make validate-config
   ```

### Running Validations

#### Before Committing Code

Always run validations locally:
```bash
make validate
```

This runs all checks:
- ✅ Power Query syntax validation
- ✅ Dependency and refresh order check
- ✅ Configuration file validation
- ✅ Repository structure verification
- ✅ Documentation completeness check

#### Individual Validations

```bash
make validate-pqm         # Just Power Query modules
make validate-deps        # Just dependencies
make validate-config      # Just configuration files
make validate-structure   # Just directory/file structure
make validate-docs        # Just documentation
```

### Testing Your Changes

1. **Syntax Validation**:
   ```bash
   make validate-pqm
   ```

2. **Module Testing** (in Power BI/Excel):
   - Load your module
   - Use test data from validation scenarios
   - Verify outputs match expectations

3. **Validation Scenarios** (see `docs/Tests_Validation_Checklist.md`):
   - Castle Rock rates: local-only 5.2%, full 8.1%
   - Lone Tree rates: local-only 4.6%, full 7.5%
   - Product classification accuracy
   - DR-0100 parity within $0.02

## Development Workflow

### Feature Development

1. **Create a feature branch**:
   ```bash
   git checkout -b feature/my-new-feature
   ```

2. **Make your changes**:
   - Add/edit Power Query modules
   - Update configuration if needed
   - Update documentation

3. **Validate locally**:
   ```bash
   make validate
   ```

4. **Commit and push**:
   ```bash
   git add .
   git commit -m "Add new feature: description"
   git push origin feature/my-new-feature
   ```

5. **Create a Pull Request**:
   - GitHub Actions will automatically validate your changes
   - Fill out the PR template
   - Wait for review from code owners

### Pull Request Checklist

From `.github/pull_request_template.md`:

- [ ] Reads correct /references workbook + sheet
- [ ] Emits columns in exact order per contract
- [ ] DQ surfaced in companion *_DQ query
- [ ] No regex; native Text.* only
- [ ] Unit tests pass using /validation
- [ ] Coverage_Summary ≥ 99% on sample

Include:
- Screenshot of output table
- Screenshot of DQ table (empty on pass)
- Note confirming DR-0100 parity (≤ $0.02 delta)

## Troubleshooting

### Common Issues

#### "Module not found" errors
- Check that the module name matches the expected refresh order
- Ensure the file is in `powerquery/` directory
- Verify the filename matches conventions (no spaces, .pqm extension)

#### Validation script errors
- Ensure Python 3.7+ is installed: `python3 --version`
- Check file permissions: `chmod +x scripts/*.py`
- Run scripts with full path if needed

#### Power Query syntax errors
- Check balanced delimiters: `{}`, `[]`, `()`
- Ensure `let...in` structure is present
- Verify all strings are properly quoted
- Run `make validate-pqm` for specific error messages

#### Configuration validation failures
- Validate JSON syntax in Parameters.json using an online validator
- Check CSV format in Column_Map.csv (must have headers)
- Ensure no empty required fields

## Resources

### Documentation
- [`README.md`](../README.md) - Project overview and architecture
- [`docs/BUILD.md`](BUILD.md) - Build automation and CI/CD
- [`docs/README_CTO.md`](README_CTO.md) - Implementation contract
- [`docs/Data_Dictionary.md`](Data_Dictionary.md) - Field definitions
- [`docs/Tests_Validation_Checklist.md`](Tests_Validation_Checklist.md) - Test scenarios

### Power Query Resources
- [Power Query M Formula Language Reference](https://docs.microsoft.com/en-us/powerquery-m/)
- [Power Query M function reference](https://docs.microsoft.com/en-us/powerquery-m/power-query-m-function-reference)

### Project Contacts
- **CTO** - System architecture & orchestration
- **CFO** - Tax policy & compliance audit
- **COO** - Jurisdiction verification
- **CPO** - Product data integrity

## Next Steps

1. **Review the documentation** thoroughly
2. **Run `make validate`** to verify your setup
3. **Explore existing Power Query modules** in `powerquery/`
4. **Check the implementation status** with `make validate-deps`
5. **Start contributing** by picking a module from the refresh order

For questions or issues, refer to the project README or contact the appropriate owner (CTO, CFO, COO, or CPO) based on the area of concern.

---

**Last Updated**: 2025-10-19  
**Maintainer**: CTO (On Point Amenities)
