SETTINGS=test_sqlite
VERBOSITY=1

.PHONY: help test-composite

help:
	@echo "Please use 'make <target>' where <target> is one of"
	@echo "  test-composite                    to run the composite test suite"
	@echo
	@echo "Use SETTINGS to test with a different database (default is SQLite)."
	@echo "Settings for different databases are in the djangotests directory."
	@echo
	@echo "Set VERBOSITY to control the verbosity of cruntests.py (default is 1)"

test-composite:
	ls -1 djangotests/composite_modeltests | grep -v "\.py" | xargs djangotests/cruntests.py --settings="$(SETTINGS)" -v$(VERBOSITY)

test-all-django:
	djangotests/cruntests.py --settings="$(SETTINGS)" -v$(VERBOSITY)
