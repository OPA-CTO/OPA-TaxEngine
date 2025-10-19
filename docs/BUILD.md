# OPA TaxEngine - Automated Build Process

## Overview

This document describes the automated build and validation process for the OPA TaxEngine project. The automation ensures code quality, validates Power Query modules, and maintains project standards.

## Build Status

The project uses GitHub Actions for continuous integration. The build status is checked on every push and pull request.

### Workflow Status
- **Workflow File**: `.github/workflows/validate-build.yml`
- **Trigger Events**: Push to `main` or `feature/**` branches, Pull Requests to `main`
- **Manual Trigger**: Available via GitHub Actions UI (workflow_dispatch)

## Build Components

### 1. Power Query Module Validation

**Script**: `scripts/validate_pqm.py`

Validates all `.pqm` files in the `powerquery/` directory:
- ✅ Basic syntax validation (balanced braces, parentheses, brackets)
- ✅ Required Power Query patterns (`let...in` structure)
- ✅ Common issues detection (unbalanced quotes, missing error handling)
- ✅ Parameter reference validation

**Run locally**:
```bash
python3 scripts/validate_pqm.py
```

### 2. Dependency Checking

**Script**: `scripts/check_dependencies.py`

Validates module dependencies and implementation status:
- ✅ Compares available modules against expected refresh order
- ✅ Identifies missing modules
- ✅ Detects modules not in documented refresh order
- ✅ Provides development progress tracking

**Expected Refresh Order** (from `docs/README_CTO.md`):
1. Taxability_Map
2. Jurisdiction_Rates
3. Machine_Map
4. OPA_SalesTax_Fact_Rows
5. OPA_SalesTax_Fact
6. Unmatched_Descriptions
7. Coverage_Summary
8. SalesTax_Summary

**Run locally**:
```bash
python3 scripts/check_dependencies.py
```

### 3. Configuration Validation

**Script**: `scripts/validate_config.py`

Validates configuration files:
- ✅ `config/Parameters.json` - JSON syntax and required fields
- ✅ `config/Column_Map.csv` - CSV structure and completeness

**Required Parameters.json fields**:
- `Imports_Folder_Path`
- `Filing_Frequency`
- `Allow_ZIP_Fallback`
- `Timezone`

**Run locally**:
```bash
python3 scripts/validate_config.py
```

### 4. Repository Structure Validation

Checks for required directories and files:
- Required directories: `powerquery/`, `config/`, `docs/`, `exports/`
- Required files: README.md, config files, documentation, GitHub templates

### 5. Documentation Validation

Ensures documentation completeness:
- ✅ README.md contains all required sections
- ✅ CTO implementation contract exists
- ✅ Refresh order is documented

## Running the Full Build Locally

You can run all validation steps locally before pushing:

### Using Make (Recommended)

```bash
# Navigate to repository root
cd /path/to/OPA-TaxEngine

# Run all validations
make validate

# Or run specific validations
make validate-pqm         # Power Query modules only
make validate-deps        # Dependencies only
make validate-config      # Configuration only
make validate-structure   # Structure only
make validate-docs        # Documentation only

# See all available targets
make help
```

### Using Python Scripts Directly

```bash
# Run all validation scripts
python3 scripts/validate_pqm.py
python3 scripts/check_dependencies.py
python3 scripts/validate_config.py
```

## Development Workflow

### Adding New Power Query Modules

1. Create your `.pqm` file in `powerquery/` directory
2. Follow the naming convention from `docs/README_CTO.md`
3. Use the `let...in` structure
4. Run `python3 scripts/validate_pqm.py` to validate syntax
5. Commit and push - GitHub Actions will run automatically

### Updating Configuration

1. Edit `config/Parameters.json` or `config/Column_Map.csv`
2. Run `python3 scripts/validate_config.py` to validate changes
3. Commit and push

### Before Submitting a Pull Request

1. Run all validation scripts locally
2. Ensure all checks pass
3. Review the PR template checklist
4. Provide validation evidence as required

## Validation Checklist

Based on `docs/Tests_Validation_Checklist.md`:

### Golden Scenarios
- [ ] Castle Rock food local-only: 0.052; full taxable: 0.081
- [ ] Lone Tree food local-only: 0.046; full taxable: 0.075
- [ ] Product taxability rules correctly applied
- [ ] Jurisdiction rates match expectations

### Pass Criteria
- [ ] Coverage_Summary ≥ 99%
- [ ] Unmatched_Descriptions has no critical reasons
- [ ] DR-0100 parity (jurisdiction totals) ≤ $0.02
- [ ] Component split available (state vs local)

## Build Artifacts

The build process does not generate artifacts automatically. Manual exports should be placed in the `exports/` directory (which is git-ignored).

## Continuous Improvement

The automated build process helps ensure:
1. **Code Quality**: All Power Query modules are syntactically valid
2. **Completeness**: All required modules are tracked
3. **Configuration Integrity**: Config files are valid and complete
4. **Documentation**: Project structure and requirements are maintained

## Troubleshooting

### Build Failures

**Power Query validation fails**:
- Check for balanced braces `{}`, brackets `[]`, parentheses `()`
- Ensure `let...in` structure is present
- Review error messages from `validate_pqm.py`

**Dependency check warnings**:
- This is expected during development as modules are being built
- Warnings indicate which modules still need implementation

**Configuration validation fails**:
- Check JSON syntax in `Parameters.json`
- Verify all required fields are present
- Ensure `Column_Map.csv` has proper headers

### Getting Help

Refer to:
- `README.md` - Main project documentation
- `docs/README_CTO.md` - Implementation contract and requirements
- `docs/Tests_Validation_Checklist.md` - Validation scenarios
- `.github/pull_request_template.md` - PR submission guidelines

## Version Information

- **Build System Version**: 1.0.0
- **Last Updated**: 2025-10-19
- **Maintainer**: CTO (On Point Amenities)

---

## Next Steps

As the project evolves, the build process will be enhanced with:
1. Automated testing of query outputs against test data
2. Performance profiling of Power Query refresh operations
3. Integration with Revenue Online export validation
4. Automated DR-0100 parity checking

For questions about the build process, contact the CTO team.
