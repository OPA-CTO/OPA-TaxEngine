# Validation Scripts

This directory contains automated validation scripts for the OPA TaxEngine project.

## Scripts

### validate_pqm.py
Validates Power Query module (.pqm) syntax and structure.

**Usage**:
```bash
python3 scripts/validate_pqm.py
```

**Checks**:
- Basic M language syntax validation
- Balanced delimiters (braces, brackets, parentheses)
- Required `let...in` structure
- String quote balance
- Parameter references

### check_dependencies.py
Analyzes Power Query module dependencies and implementation status.

**Usage**:
```bash
python3 scripts/check_dependencies.py
```

**Checks**:
- Compares available modules against expected refresh order
- Identifies missing/incomplete modules
- Tracks development progress

### validate_config.py
Validates configuration files for syntax and completeness.

**Usage**:
```bash
python3 scripts/validate_config.py
```

**Checks**:
- `config/Parameters.json` - JSON validity and required fields
- `config/Column_Map.csv` - CSV structure and data completeness

## Requirements

- Python 3.7 or higher
- No external dependencies (uses only standard library)

## Integration

These scripts are automatically executed by GitHub Actions on every push and pull request. See `.github/workflows/validate-build.yml` for the CI/CD configuration.

## Exit Codes

All scripts follow standard conventions:
- `0` - Validation passed
- `1` - Validation failed with errors
- Warnings do not cause failure

## Development

To add new validation checks:
1. Add your check as a method in the appropriate class
2. Call it from the `main()` function
3. Update this README with the new functionality
4. Test locally before committing
