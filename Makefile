PYTHON ?= python3

.PHONY: setup-check
setup-check:
	$(PYTHON) tools/setup_check.py
