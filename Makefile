# OPA TaxEngine - Makefile for local validation

.PHONY: help validate validate-pqm validate-deps validate-config validate-structure validate-docs all clean

help:
	@echo "OPA TaxEngine - Build Automation"
	@echo ""
	@echo "Available targets:"
	@echo "  make validate          - Run all validation checks"
	@echo "  make validate-pqm      - Validate Power Query modules"
	@echo "  make validate-deps     - Check module dependencies"
	@echo "  make validate-config   - Validate configuration files"
	@echo "  make validate-structure - Check repository structure"
	@echo "  make validate-docs     - Validate documentation"
	@echo "  make all               - Run all validations (same as validate)"
	@echo ""
	@echo "For more information, see docs/BUILD.md"

validate: validate-pqm validate-deps validate-config validate-structure validate-docs
	@echo ""
	@echo "=========================================="
	@echo "✓ All validations completed successfully"
	@echo "=========================================="

all: validate

validate-pqm:
	@echo "=========================================="
	@echo "Validating Power Query Modules"
	@echo "=========================================="
	@python3 scripts/validate_pqm.py

validate-deps:
	@echo ""
	@echo "=========================================="
	@echo "Checking Module Dependencies"
	@echo "=========================================="
	@python3 scripts/check_dependencies.py

validate-config:
	@echo ""
	@echo "=========================================="
	@echo "Validating Configuration Files"
	@echo "=========================================="
	@python3 scripts/validate_config.py

validate-structure:
	@echo ""
	@echo "=========================================="
	@echo "Validating Repository Structure"
	@echo "=========================================="
	@echo "Checking required directories..."
	@for dir in powerquery config docs exports; do \
		if [ ! -d "$$dir" ]; then \
			echo "❌ ERROR: Required directory '$$dir' is missing"; \
			exit 1; \
		fi; \
		echo "  ✓ Directory '$$dir' exists"; \
	done
	@echo "Checking required files..."
	@for file in README.md config/Parameters.json config/Column_Map.csv \
	             docs/Tests_Validation_Checklist.md .github/CODEOWNERS \
	             .github/pull_request_template.md; do \
		if [ ! -f "$$file" ]; then \
			echo "❌ ERROR: Required file '$$file' is missing"; \
			exit 1; \
		fi; \
		echo "  ✓ File '$$file' exists"; \
	done

validate-docs:
	@echo ""
	@echo "=========================================="
	@echo "Validating Documentation"
	@echo "=========================================="
	@echo "Checking README.md sections..."
	@for section in "Mission" "Objectives" "Source File Map" \
	                "Architecture Overview" "Validation Workflow" \
	                "Repo Structure"; do \
		if grep -q "$$section" README.md; then \
			echo "  ✓ Section '$$section' found"; \
		else \
			echo "  ⚠️  WARNING: Section '$$section' not found"; \
		fi; \
	done
	@echo "Checking CTO documentation..."
	@if [ -f "docs/README_CTO.md" ]; then \
		echo "  ✓ CTO implementation contract found"; \
		if grep -q "Refresh Order" docs/README_CTO.md; then \
			echo "  ✓ Refresh order documented"; \
		fi; \
	else \
		echo "  ⚠️  WARNING: docs/README_CTO.md not found"; \
	fi

clean:
	@echo "Cleaning up temporary files..."
	@find . -type f -name "*.pyc" -delete
	@find . -type d -name "__pycache__" -delete
	@echo "✓ Cleanup complete"
PYTHON ?= python3

.PHONY: setup-check
setup-check:
	$(PYTHON) tools/setup_check.py
